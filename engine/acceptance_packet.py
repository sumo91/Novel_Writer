from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_yaml
from engine.paths import books_dir

BOOKS_DIR = books_dir()


def draft_acceptance_packet(
    book_id: str,
    chapter_number: int,
    title: str,
    source_draft: str,
    summary: str,
    output_path: Path | None = None,
    force: bool = False,
) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    draft_path = root / source_draft
    if not draft_path.exists():
        raise FileNotFoundError(f"Missing source draft: {source_draft}")

    output = output_path or root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
    if output.exists() and not force:
        raise FileExistsError(f"Acceptance packet already exists: {output.name}")

    current_state = _draft_current_state(root, chapter_number)
    review_data = _load_review_data(root, chapter_number)
    pending_approvals = _dedupe(
        current_state.get("pending_approvals", [])
        + review_data["human_approval_needed"]
    )
    current_state["pending_approvals"] = pending_approvals

    timeline_id = _next_timeline_id(root)
    packet = {
        "chapter": chapter_number,
        "title": title,
        "source_draft": source_draft,
        "accepted_chapter_path": f"chapters/ch_{chapter_number:04d}.md",
        "summary": summary,
        "current_state": current_state,
        "state_changes": review_data["proposed_state_updates"],
        "open_threads_touched": [],
        "timeline_event": {
            "id": timeline_id,
            "when": f"第 {chapter_number} 章",
            "summary": summary,
        },
        "open_thread_updates": [],
        "change_log": {
            "summary": (
                f"Accepted revised chapter {chapter_number} as "
                f"chapters/ch_{chapter_number:04d}.md."
            ),
            "canon_updates": [f"timeline:{timeline_id}"],
            "pending_approvals": list(pending_approvals),
        },
    }

    write_yaml(output, packet)
    return output


def _draft_current_state(root: Path, chapter_number: int) -> dict[str, Any]:
    state = read_json(root / "state" / "current_state.json")
    return {
        "current_arc": state.get("current_arc", ""),
        "latest_location": state.get("latest_location", ""),
        "active_characters": state.get("active_characters", []),
        "active_conflicts": state.get("active_conflicts", []),
        "pending_approvals": state.get("pending_approvals", []),
        "draft_note": (
            f"TODO: review and edit current_state before accepting chapter {chapter_number}."
        ),
    }


def _load_review_data(root: Path, chapter_number: int) -> dict[str, list[str]]:
    review_dir = root / "reviews" / f"ch_{chapter_number:04d}"
    proposed_state_updates: list[str] = []
    human_approval_needed: list[str] = []

    for file_name in ("continuity_review.json", "pacing_review.json"):
        path = review_dir / file_name
        if not path.exists():
            continue
        review = read_json(path)
        proposed_state_updates.extend(review.get("proposed_state_updates", []))
        human_approval_needed.extend(review.get("human_approval_needed", []))

    return {
        "proposed_state_updates": _dedupe(proposed_state_updates),
        "human_approval_needed": _dedupe(human_approval_needed),
    }


def _next_timeline_id(root: Path) -> str:
    timeline = read_yaml(root / "canon" / "timeline.yaml")
    max_number = 0
    for event in timeline.get("events", []):
        event_id = str(event.get("id", ""))
        if event_id.startswith("t") and event_id[1:].isdigit():
            max_number = max(max_number, int(event_id[1:]))
    return f"t{max_number + 1:03d}"


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
