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
        "v3_state_updates": _draft_v3_state_updates(
            chapter_number,
            summary,
            pending_approvals,
        ),
        "open_thread_updates": [],
        "change_log": {
            "summary": (
                f"Accepted revised chapter {chapter_number} as "
                f"chapters/ch_{chapter_number:04d}.md."
            ),
            "canon_updates": [f"timeline:{timeline_id}"],
            "pending_approvals": list(pending_approvals),
        },
        "acceptance_contract": _draft_acceptance_contract(
            root,
            chapter_number,
            timeline_id,
            summary,
            current_state,
            pending_approvals,
        ),
    }

    write_yaml(output, packet)
    return output


def _draft_current_state(root: Path, chapter_number: int) -> dict[str, Any]:
    state = read_json(root / "state" / "current_state.json")
    return {
        "current_chapter": chapter_number,
        "current_arc": state.get("current_arc", ""),
        "latest_location": state.get("latest_location", ""),
        "active_characters": state.get("active_characters", []),
        "active_conflicts": state.get("active_conflicts", []),
        "pending_approvals": state.get("pending_approvals", []),
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


def _draft_v3_state_updates(
    chapter_number: int,
    summary: str,
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "timeline": {
            "occurred_events": [
                {
                    "id": f"ev_{chapter_number:04d}_01",
                    "summary": summary,
                    "location": "",
                    "involved_characters": [],
                    "source_chapter": chapter_number,
                },
            ],
        },
        "character_states": [],
        "resource_changes": [],
        "open_thread_updates": [],
        "payoff_updates": [
            {
                "chapter": chapter_number,
                "promises_made": [],
                "payoffs_delivered": [summary],
                "frustration_level": "controlled",
                "payoff_types": [],
                "delayed_payoffs": [],
                "risks": [],
            },
        ],
        "conflict_updates": {"active": []},
        "next_hook": {},
        "pending_approvals": list(pending_approvals),
    }


def _draft_acceptance_contract(
    root: Path,
    chapter_number: int,
    timeline_id: str,
    summary: str,
    current_state: dict[str, Any],
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "quality_gate_summary": _quality_gate_summary(root, chapter_number),
        "outline_alignment": _outline_alignment(root, chapter_number),
        "state_updates": _acceptance_state_updates(
            chapter_number,
            timeline_id,
            summary,
            current_state,
            pending_approvals,
        ),
    }


def _quality_gate_summary(root: Path, chapter_number: int) -> dict[str, Any]:
    review_dir = root / "reviews" / f"ch_{chapter_number:04d}"
    continuity_path = review_dir / "continuity_review.json"
    pacing_path = review_dir / "pacing_review.json"
    continuity = read_json(continuity_path) if continuity_path.exists() else {}
    pacing = read_json(pacing_path) if pacing_path.exists() else {}
    score = pacing.get("score")
    revised_score = pacing.get("revised_score")
    return {
        "continuity_review_present": continuity_path.exists(),
        "continuity_blockers": list(continuity.get("required_fixes", [])),
        "pacing_review_present": pacing_path.exists(),
        "pacing_score": score,
        "revised_pacing_score": revised_score,
        "revision_required": bool(continuity.get("required_fixes"))
        or not isinstance(score, int)
        or score < 80,
        "waiver_required": bool(isinstance(revised_score, int) and revised_score < 80),
    }


def _outline_alignment(root: Path, chapter_number: int) -> dict[str, Any]:
    volume = read_yaml(root / "outlines" / "volumes" / "volume_001.yaml")
    arc = read_yaml(root / "outlines" / "arc_001.yaml")
    unit = read_yaml(root / "outlines" / "units" / "unit_0001.yaml")
    unit_chapter = _unit_chapter(unit, chapter_number)
    required = list(unit_chapter.get("state_obligation", []))
    return {
        "reference_chain": "master -> volume -> arc -> unit -> chapter brief",
        "volume_id": volume.get("volume_id", "volume_001"),
        "arc_id": arc.get("arc_id", "arc_001"),
        "unit_id": f"unit_{int(unit.get('unit', 1)):04d}"
        if isinstance(unit.get("unit"), int)
        else str(unit.get("unit", "unit_0001")),
        "required_unit_obligations": required,
        "claimed_fulfilled_unit_obligations": list(required),
        "pending_unit_obligations": [],
    }


def _unit_chapter(unit: dict[str, Any], chapter_number: int) -> dict[str, Any]:
    for chapter in unit.get("chapters", []):
        if isinstance(chapter, dict) and chapter.get("chapter") == chapter_number:
            return chapter
    return {}


def _acceptance_state_updates(
    chapter_number: int,
    timeline_id: str,
    summary: str,
    current_state: dict[str, Any],
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "timeline_event": {
            "id": timeline_id,
            "when": f"第 {chapter_number} 章",
            "summary": summary,
        },
        "character_state_changes": [],
        "resource_changes": [],
        "open_thread_updates": [],
        "payoff_updates": [
            {
                "chapter": chapter_number,
                "promises_made": [],
                "payoffs_delivered": [summary],
                "frustration_level": "controlled",
                "payoff_types": [],
                "delayed_payoffs": [],
                "risks": [],
            },
        ],
        "next_hook": {},
        "pending_approvals": list(pending_approvals),
        "economy_changes": [],
        "faction_changes": [],
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
