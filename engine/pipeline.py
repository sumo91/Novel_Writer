import shutil
from dataclasses import dataclass
from pathlib import Path

from engine.acceptance_packet import draft_acceptance_packet
from engine.chapter_acceptance import accept_chapter
from engine.context_builder import build_context
from engine.io_utils import read_text, write_json, write_text
from engine.paths import books_dir

BOOKS_DIR = books_dir()


@dataclass(frozen=True)
class PipelinePaths:
    root: Path
    pipeline_dir: Path
    context_path: Path
    manifest_path: Path
    handoff_dir: Path


def pipeline_paths(book_id: str, chapter_number: int) -> PipelinePaths:
    root = BOOKS_DIR / book_id
    pipeline_dir = root / "pipeline" / f"ch_{chapter_number:04d}"
    return PipelinePaths(
        root=root,
        pipeline_dir=pipeline_dir,
        context_path=pipeline_dir / "context.md",
        manifest_path=pipeline_dir / "manifest.json",
        handoff_dir=pipeline_dir / "handoffs",
    )


def prepare_chapter(book_id: str, chapter_number: int, force: bool = False) -> PipelinePaths:
    paths = pipeline_paths(book_id, chapter_number)
    if not paths.root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    if paths.pipeline_dir.exists():
        if not force:
            raise FileExistsError(f"Pipeline workspace already exists: {paths.pipeline_dir}")
        shutil.rmtree(paths.pipeline_dir)

    paths.handoff_dir.mkdir(parents=True, exist_ok=True)
    write_text(paths.context_path, build_context(book_id, chapter_number))
    manifest = _manifest(book_id, chapter_number)
    write_json(paths.manifest_path, manifest)
    _write_handoffs(paths, manifest)
    return paths


def pipeline_status(book_id: str, chapter_number: int) -> dict:
    paths = pipeline_paths(book_id, chapter_number)
    if not paths.manifest_path.exists():
        raise FileNotFoundError(f"Missing pipeline manifest: {paths.manifest_path}")

    import json

    manifest = json.loads(read_text(paths.manifest_path))
    artifacts = {}
    for name, relative_path in manifest["artifacts"].items():
        path = paths.root / relative_path
        artifacts[name] = {
            "path": relative_path,
            "present": path.exists(),
        }

    status, next_action = _derive_status(artifacts)
    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "status": status,
        "artifacts": artifacts,
        "next_action": next_action,
    }


def pipeline_draft_acceptance(
    book_id: str,
    chapter_number: int,
    title: str,
    summary: str,
    force: bool = False,
    allow_missing_reviews: bool = False,
) -> Path:
    paths = pipeline_paths(book_id, chapter_number)
    source_draft = f"drafts/ch_{chapter_number:04d}_revised.md"
    revised_path = paths.root / source_draft
    if not revised_path.exists():
        raise FileNotFoundError(f"Missing revised draft: {source_draft}")

    if not allow_missing_reviews:
        review_dir = paths.root / "reviews" / f"ch_{chapter_number:04d}"
        required_reviews = [
            review_dir / "continuity_review.json",
            review_dir / "pacing_review.json",
        ]
        missing_reviews = [
            path.relative_to(paths.root).as_posix()
            for path in required_reviews
            if not path.exists()
        ]
        if missing_reviews:
            raise FileNotFoundError(f"Missing review files: {', '.join(missing_reviews)}")

    return draft_acceptance_packet(
        book_id,
        chapter_number,
        title=title,
        source_draft=source_draft,
        summary=summary,
        force=force,
    )


def pipeline_accept(
    book_id: str,
    chapter_number: int,
    approved: bool,
    force: bool = False,
) -> Path:
    if not approved:
        raise PermissionError("Human approval is required before pipeline acceptance.")

    paths = pipeline_paths(book_id, chapter_number)
    packet_path = paths.root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
    if not packet_path.exists():
        raise FileNotFoundError(f"Missing acceptance packet: {packet_path}")

    result = accept_chapter(book_id, packet_path, force=force)
    return result.chapter_path


def _manifest(book_id: str, chapter_number: int) -> dict:
    chapter_slug = f"ch_{chapter_number:04d}"
    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "status": "prepared",
        "artifacts": {
            "context": f"pipeline/{chapter_slug}/context.md",
            "brief": f"outlines/chapter_briefs/{chapter_slug}_brief.md",
            "draft": f"drafts/{chapter_slug}_draft.md",
            "revised": f"drafts/{chapter_slug}_revised.md",
            "continuity_review": f"reviews/{chapter_slug}/continuity_review.json",
            "pacing_review": f"reviews/{chapter_slug}/pacing_review.json",
            "acceptance_packet": f"state_updates/{chapter_slug}_acceptance.yaml",
            "accepted_chapter": f"chapters/{chapter_slug}.md",
        },
    }


def _derive_status(artifacts: dict) -> tuple[str, str]:
    if not artifacts["brief"]["present"]:
        return "needs_brief", "Create chapter brief."
    if not artifacts["draft"]["present"]:
        return "needs_draft", "Create chapter draft."
    if not (
        artifacts["continuity_review"]["present"]
        and artifacts["pacing_review"]["present"]
    ):
        return "needs_reviews", "Create continuity and pacing reviews."
    if not artifacts["revised"]["present"]:
        return "needs_revised_draft", "Create revised chapter draft."
    if not artifacts["acceptance_packet"]["present"]:
        return "needs_acceptance_packet", "Draft and review acceptance packet."
    if not artifacts["accepted_chapter"]["present"]:
        return "ready_for_acceptance", "Run pipeline-accept after human approval."
    return "accepted", "Chapter has been accepted."


HANDOFFS = [
    (
        "01_plot_planner.md",
        "engine/prompts/agents/plot_planner.md",
        "Create the chapter brief.",
        "brief",
    ),
    (
        "02_chapter_writer.md",
        "engine/prompts/agents/chapter_writer.md",
        "Draft the chapter from the approved brief.",
        "draft",
    ),
    (
        "03_continuity_editor.md",
        "engine/prompts/agents/continuity_editor.md",
        "Review the draft for canon and state continuity.",
        "continuity_review",
    ),
    (
        "04_tomato_pacing_editor.md",
        "engine/prompts/agents/tomato_pacing_editor.md",
        "Review the draft for Tomato-style pacing and payoff.",
        "pacing_review",
    ),
    (
        "05_reviser.md",
        "engine/prompts/agents/reviser.md",
        "Revise from human-approved review notes.",
        "revised",
    ),
]


def _write_handoffs(paths: PipelinePaths, manifest: dict) -> None:
    for file_name, prompt_path, task, output_key in HANDOFFS:
        prompt_text = read_text(Path(prompt_path))
        content = "\n".join(
            [
                f"# {file_name.removesuffix('.md').replace('_', ' ').title()}",
                "",
                f"Prompt source: `{prompt_path}`",
                f"Context: `{manifest['artifacts']['context']}`",
                f"Expected output: `{manifest['artifacts'][output_key]}`",
                "",
                "## Task",
                "",
                task,
                "",
                "## Human Approval",
                "",
                "Do not treat generated canon or state changes as approved until the human accepts them.",
                "",
                "## Agent Prompt",
                "",
                prompt_text.rstrip(),
                "",
            ]
        )
        write_text(paths.handoff_dir / file_name, content)
