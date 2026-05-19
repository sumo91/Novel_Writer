import shutil
from dataclasses import dataclass
from pathlib import Path

from engine.acceptance_packet import draft_acceptance_packet
from engine.chapter_acceptance import accept_chapter
from engine.context_builder import build_context
from engine.craft_knowledge import load_craft_cards, render_craft_cards
from engine.html_utils import markdown_to_html_page
from engine.hardening import (
    stale_acceptance_text_errors,
    validate_acceptance_packet,
    validate_acceptance_contract_snapshot,
    validate_pacing_review,
)
from engine.io_utils import read_json, read_text, read_yaml, write_json, write_text, write_yaml
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
    manifest_artifacts = {
        **_manifest(book_id, chapter_number)["artifacts"],
        **manifest["artifacts"],
    }
    artifacts = {}
    for name, relative_path in manifest_artifacts.items():
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
    revised_source = f"drafts/ch_{chapter_number:04d}_revised.md"
    revised_path = paths.root / revised_source
    if not revised_path.exists():
        raise FileNotFoundError(f"Missing revised draft: {revised_source}")

    if not allow_missing_reviews:
        review_dir = paths.root / "reviews" / f"ch_{chapter_number:04d}"
        required_reviews = [
            review_dir / "continuity_review.json",
            review_dir / "pacing_review.json",
            review_dir / "prose_quality_review.json",
        ]
        missing_reviews = [
            path.relative_to(paths.root).as_posix()
            for path in required_reviews
            if not path.exists()
        ]
        if missing_reviews:
            raise FileNotFoundError(f"Missing review files: {', '.join(missing_reviews)}")

    source_draft = f"drafts/ch_{chapter_number:04d}_final_candidate.md"
    final_candidate_path = paths.root / source_draft
    if not final_candidate_path.exists():
        raise FileNotFoundError(f"Missing final candidate draft: {source_draft}")

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
    paths = pipeline_paths(book_id, chapter_number)
    packet_path = paths.root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
    return pipeline_accept_update_file(
        book_id,
        packet_path,
        approved=approved,
        force=force,
        chapter_number=chapter_number,
    )


def pipeline_accept_update_file(
    book_id: str,
    packet_path: Path,
    approved: bool,
    force: bool = False,
    chapter_number: int | None = None,
) -> Path:
    if not approved:
        raise PermissionError("Human approval is required before pipeline acceptance.")

    paths = pipeline_paths(book_id, chapter_number or 0)
    if not packet_path.exists():
        raise FileNotFoundError(f"Missing acceptance packet: {packet_path}")
    packet = read_yaml(packet_path)
    resolved_chapter = chapter_number if chapter_number is not None else int(packet.get("chapter", 0))
    packet_errors = [
        f"{packet_path.relative_to(paths.root).as_posix()}: {error}"
        for error in validate_acceptance_packet(packet, resolved_chapter)
        + stale_acceptance_text_errors(packet_path)
    ]
    if packet_errors:
        raise ValueError("Invalid acceptance packet: " + "; ".join(packet_errors))
    contract_errors = validate_acceptance_contract_snapshot(
        paths.root,
        packet,
        resolved_chapter,
    )
    if contract_errors:
        raise ValueError("Invalid acceptance packet: " + "; ".join(contract_errors))

    result = accept_chapter(book_id, packet_path, force=force)
    return result.chapter_path


def pipeline_quality_gate(book_id: str, chapter_number: int) -> dict:
    paths = pipeline_paths(book_id, chapter_number)
    review_dir = paths.root / "reviews" / f"ch_{chapter_number:04d}"
    continuity_path = review_dir / "continuity_review.json"
    pacing_path = review_dir / "pacing_review.json"
    if not continuity_path.exists():
        raise FileNotFoundError(f"Missing continuity review: {continuity_path}")
    if not pacing_path.exists():
        raise FileNotFoundError(f"Missing pacing review: {pacing_path}")

    continuity = read_json(continuity_path)
    pacing = read_json(pacing_path)
    acceptance_packet = paths.root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
    waiver = _quality_gate_waiver(acceptance_packet)

    continuity_blockers = _continuity_blockers(continuity)
    initial_score = pacing.get("score")
    revised_score = pacing.get("revised_score")
    revised_path = paths.root / "drafts" / f"ch_{chapter_number:04d}_revised.md"
    revision_required = bool(continuity_blockers) or _score_below_gate(initial_score)
    waiver_required = False
    reasons: list[str] = []

    score_errors = _total_score_errors(initial_score, revised_score)
    if score_errors:
        reasons.extend(score_errors)
        return {
            "book_id": book_id,
            "chapter": chapter_number,
            "passed": False,
            "status": "invalid_review",
            "revision_required": revision_required,
            "waiver_required": waiver_required,
            "initial_pacing_score": initial_score,
            "revised_pacing_score": revised_score,
            "continuity_blockers": continuity_blockers,
            "reasons": reasons,
        }

    if continuity_blockers and not waiver:
        reasons.append("Continuity review has unresolved blockers.")
        return {
            "book_id": book_id,
            "chapter": chapter_number,
            "passed": False,
            "status": "blocked",
            "revision_required": True,
            "waiver_required": False,
            "initial_pacing_score": initial_score,
            "revised_pacing_score": revised_score,
            "continuity_blockers": continuity_blockers,
            "reasons": reasons,
        }

    if _score_below_gate(initial_score):
        reasons.append(f"Pacing score {initial_score} is below 80.")
        if not revised_path.exists():
            return {
                "book_id": book_id,
                "chapter": chapter_number,
                "passed": False,
                "status": "needs_revision",
                "revision_required": True,
                "waiver_required": False,
                "initial_pacing_score": initial_score,
                "revised_pacing_score": revised_score,
                "continuity_blockers": continuity_blockers,
                "reasons": reasons,
            }
        if revised_score is None:
            reasons.append("Missing revised pacing score after revision.")
            return {
                "book_id": book_id,
                "chapter": chapter_number,
                "passed": False,
                "status": "needs_revision",
                "revision_required": True,
                "waiver_required": False,
                "initial_pacing_score": initial_score,
                "revised_pacing_score": revised_score,
                "continuity_blockers": continuity_blockers,
                "reasons": reasons,
            }
        if _score_below_gate(revised_score):
            waiver_required = True
            reasons.append(f"Revised pacing score {revised_score} is still below 80.")
            if not waiver:
                return {
                    "book_id": book_id,
                    "chapter": chapter_number,
                    "passed": False,
                    "status": "needs_waiver",
                    "revision_required": True,
                    "waiver_required": True,
                    "initial_pacing_score": initial_score,
                    "revised_pacing_score": revised_score,
                    "continuity_blockers": continuity_blockers,
                    "reasons": reasons,
                }

    dimension_errors = _dimension_score_errors(pacing)
    if dimension_errors:
        reasons.extend(dimension_errors)
        return {
            "book_id": book_id,
            "chapter": chapter_number,
            "passed": False,
            "status": "invalid_review",
            "revision_required": revision_required,
            "waiver_required": waiver_required,
            "initial_pacing_score": initial_score,
            "revised_pacing_score": revised_score,
            "continuity_blockers": continuity_blockers,
            "reasons": reasons,
        }

    status = "passed_with_waiver" if waiver else "passed"
    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "passed": True,
        "status": status,
        "revision_required": revision_required,
        "waiver_required": waiver_required,
        "initial_pacing_score": initial_score,
        "revised_pacing_score": revised_score,
        "continuity_blockers": continuity_blockers,
        "reasons": reasons,
    }


PROSE_QUALITY_DIMENSIONS = {
    "opening_hook": 10,
    "conflict_pressure": 10,
    "protagonist_agency": 10,
    "payoff_execution": 15,
    "dialogue_tension": 10,
    "scene_specificity": 10,
    "voice_distinction": 10,
    "rhythm_variation": 10,
    "ending_pull": 10,
    "style_slop_control": 5,
}


def write_author_direction_scaffold(
    book_id: str,
    chapter_number: int,
    force: bool = False,
) -> Path:
    paths = pipeline_paths(book_id, chapter_number)
    output = paths.root / "authoring" / f"ch_{chapter_number:04d}_author_direction.yaml"
    if output.exists() and not force:
        raise FileExistsError(f"Author direction already exists: {output}")
    data = {
        "chapter": chapter_number,
        "author_intent": [],
        "must_change": [],
        "approved_lines": [],
        "rejected_patterns": [
            "Avoid generic inner monologue explanations.",
            "Avoid interchangeable dialogue.",
            "Avoid vague cliffhangers without a concrete next pressure.",
        ],
        "ai_assistance": {
            "expected": True,
            "human_role": "direction, taste, key edits, final approval",
        },
        "approved_for_final_candidate": False,
    }
    write_yaml(output, data)
    html_lines = [
        f"# Chapter {chapter_number} Author Direction",
        "",
        "- AI may draft most prose.",
        "- Human direction should state taste, intent, must-change points, and rejected patterns.",
        "- Set approved_for_final_candidate only after the human direction is ready.",
    ]
    write_text(
        output.with_suffix(".html"),
        markdown_to_html_page(
            f"Chapter {chapter_number} Author Direction",
            "\n".join(html_lines),
        ),
    )
    return output


def pipeline_prose_quality_gate(book_id: str, chapter_number: int) -> dict:
    paths = pipeline_paths(book_id, chapter_number)
    review_path = paths.root / "reviews" / f"ch_{chapter_number:04d}" / "prose_quality_review.json"
    if not review_path.exists():
        raise FileNotFoundError(f"Missing prose quality review: {review_path}")

    review = read_json(review_path)
    score = review.get("score")
    dimension_scores = review.get("dimension_scores", {})
    reasons: list[str] = []
    if not isinstance(score, int) or not 0 <= score <= 100:
        reasons.append("Prose quality score must be an integer from 0 to 100.")
    if not isinstance(dimension_scores, dict):
        reasons.append("Prose quality dimension_scores must be a mapping.")
        dimension_scores = {}
    for dimension, max_score in PROSE_QUALITY_DIMENSIONS.items():
        value = dimension_scores.get(dimension)
        if not isinstance(value, int) or not 0 <= value <= max_score:
            reasons.append(f"{dimension} must be an integer from 0 to {max_score}.")
        elif value < _prose_dimension_floor(max_score):
            reasons.append(f"{dimension} is below {_prose_dimension_floor(max_score)}.")
    for issue in review.get("blocking_issues", []):
        reasons.append(str(issue))

    rewrite_required = bool(review.get("rewrite_required"))
    if isinstance(score, int) and score < 85:
        rewrite_required = True
        reasons.append(f"Prose quality score {score} is below 85.")
    if reasons:
        rewrite_required = True

    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "passed": not rewrite_required,
        "status": "passed" if not rewrite_required else "needs_rewrite",
        "score": score,
        "rewrite_required": rewrite_required,
        "reasons": list(dict.fromkeys(reasons)),
    }


def _prose_dimension_floor(max_score: int) -> int:
    if max_score == 15:
        return 10
    if max_score == 5:
        return 3
    return 7


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
            "author_direction": f"authoring/{chapter_slug}_author_direction.yaml",
            "continuity_review": f"reviews/{chapter_slug}/continuity_review.json",
            "pacing_review": f"reviews/{chapter_slug}/pacing_review.json",
            "prose_quality_review": f"reviews/{chapter_slug}/prose_quality_review.json",
            "final_candidate": f"drafts/{chapter_slug}_final_candidate.md",
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
    if not artifacts["author_direction"]["present"]:
        return "needs_author_direction", "Create or approve author direction notes."
    if not artifacts["prose_quality_review"]["present"]:
        return "needs_prose_quality_review", "Create prose quality review."
    if not artifacts["final_candidate"]["present"]:
        return "needs_final_candidate", "Create AI-assisted final candidate draft."
    if not artifacts["acceptance_packet"]["present"]:
        return "needs_acceptance_packet", "Draft and review acceptance packet."
    if not artifacts["accepted_chapter"]["present"]:
        return "ready_for_acceptance", "Run pipeline-accept after human approval."
    return "accepted", "Chapter has been accepted."


def _continuity_blockers(continuity: dict) -> list[str]:
    blockers: list[str] = []
    blockers.extend(str(item) for item in continuity.get("required_fixes", []))
    for issue in continuity.get("issues", []):
        if issue.get("severity") == "high":
            evidence = issue.get("evidence") or issue.get("suggested_fix") or issue.get("type")
            if evidence:
                blockers.append(str(evidence))
    return list(dict.fromkeys(blockers))


def _score_below_gate(score: object) -> bool:
    return not isinstance(score, int) or score < 80


def _total_score_errors(initial_score: object, revised_score: object) -> list[str]:
    scores = [initial_score]
    if revised_score is not None:
        scores.append(revised_score)
    if any(not isinstance(score, int) or not 0 <= score <= 100 for score in scores):
        return ["Pacing score must be an integer from 0 to 100."]
    return []


def _dimension_score_errors(pacing: dict) -> list[str]:
    return [
        error
        for error in validate_pacing_review(pacing)
        if "score must be an integer from 0 to 100" not in error
        and "revised_score must be an integer from 0 to 100" not in error
    ]


def _quality_gate_waiver(packet_path: Path) -> bool:
    if not packet_path.exists():
        return False
    packet = read_yaml(packet_path)
    waiver = packet.get("quality_gate", {}).get("waiver", {})
    return bool(
        waiver.get("required")
        and waiver.get("type")
        and waiver.get("reason")
        and waiver.get("approved_by")
    )


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
        lines = [
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
            "V3 state updates remain proposed until the acceptance packet is approved.",
            "",
            "## V3.1 outline obligations",
            "",
            "Use the active outline reference chain: master -> volume -> arc -> unit -> chapter brief.",
            "The chapter brief must state which master, volume, arc, and unit obligations it serves.",
            "Reviews must check whether the chapter served the active unit and arc function.",
            "Draft outline layers are assumptions; approved outline layers are hard constraints.",
            "",
        ]
        if output_key in {"brief", "continuity_review", "pacing_review"}:
            lines.extend(render_craft_cards(load_craft_cards(_craft_target(output_key))))
        lines.extend(
            [
                "## Agent Prompt",
                "",
                prompt_text.rstrip(),
                "",
            ]
        )
        content = "\n".join(lines)
        write_text(paths.handoff_dir / file_name, content)


def _craft_target(output_key: str) -> str:
    return "brief" if output_key == "brief" else "review"


def write_quality_gate_html(book_id: str, chapter_number: int, result: dict) -> Path:
    paths = pipeline_paths(book_id, chapter_number)
    output = paths.root / "reviews" / f"ch_{chapter_number:04d}" / "quality_gate.html"
    lines = [
        f"# Chapter {chapter_number} Quality Gate",
        "",
        f"- Status: {result.get('status')}",
        f"- Passed: {result.get('passed')}",
        f"- Continuity blockers: {len(result.get('continuity_blockers', []))}",
        f"- Initial pacing score: {result.get('initial_pacing_score')}",
        f"- Revised pacing score: {result.get('revised_pacing_score')}",
        f"- Revision required: {result.get('revision_required')}",
        f"- Waiver required: {result.get('waiver_required')}",
        "",
        "## Reasons",
        "",
    ]
    reasons = result.get("reasons", [])
    if reasons:
        lines.extend(f"- {reason}" for reason in reasons)
    else:
        lines.append("- None")
    lines.extend(["", "## Continuity Blockers", ""])
    blockers = result.get("continuity_blockers", [])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_text(output, markdown_to_html_page(f"Chapter {chapter_number} Quality Gate", "\n".join(lines)))
    return output
