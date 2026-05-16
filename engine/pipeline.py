import shutil
from dataclasses import dataclass
from pathlib import Path

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
