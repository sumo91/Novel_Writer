import copy
import html
from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_text, write_yaml
from engine.outline_resolver import (
    BRIEF_REFERENCE_CHAIN,
    active_outline_data,
    unit_chapter,
    unit_id,
)
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
    v3_state_updates = _draft_v3_state_updates(
        chapter_number,
        summary,
        pending_approvals,
    )
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
        "v3_state_updates": v3_state_updates,
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
            v3_state_updates,
        ),
    }

    write_yaml(output, packet)
    write_text(output.with_suffix(".html"), render_acceptance_packet_html(packet))
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
    v3_state_updates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "quality_gate_summary": _quality_gate_summary(root, chapter_number),
        "outline_alignment": _outline_alignment(root, chapter_number),
        "state_updates": _acceptance_state_updates(
            chapter_number,
            timeline_id,
            summary,
            v3_state_updates,
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
    active = active_outline_data(root, chapter_number)
    volume = active["volume"]
    arc = active["arc"]
    unit = active["unit"]
    active_unit_chapter = unit_chapter(unit, chapter_number)
    required = list(active_unit_chapter.get("state_obligation", []))
    return {
        "reference_chain": f"{BRIEF_REFERENCE_CHAIN} -> chapter brief",
        "volume_id": volume.get("volume_id", "volume_001"),
        "arc_id": arc.get("arc_id", "arc_001"),
        "unit_id": unit_id(unit),
        "required_unit_obligations": required,
        "claimed_fulfilled_unit_obligations": list(required),
        "pending_unit_obligations": [],
    }


def _acceptance_state_updates(
    chapter_number: int,
    timeline_id: str,
    summary: str,
    v3_state_updates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "timeline_event": {
            "id": timeline_id,
            "when": f"第 {chapter_number} 章",
            "summary": summary,
        },
        "character_state_changes": copy.deepcopy(v3_state_updates.get("character_states", [])),
        "resource_changes": copy.deepcopy(v3_state_updates.get("resource_changes", [])),
        "open_thread_updates": copy.deepcopy(v3_state_updates.get("open_thread_updates", [])),
        "payoff_updates": copy.deepcopy(v3_state_updates.get("payoff_updates", [])),
        "next_hook": copy.deepcopy(v3_state_updates.get("next_hook", {})),
        "pending_approvals": copy.deepcopy(v3_state_updates.get("pending_approvals", [])),
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


def render_acceptance_packet_html(packet: dict[str, Any]) -> str:
    contract = packet.get("acceptance_contract", {})
    quality = contract.get("quality_gate_summary", {}) if isinstance(contract, dict) else {}
    outline = contract.get("outline_alignment", {}) if isinstance(contract, dict) else {}
    state_updates = contract.get("state_updates", {}) if isinstance(contract, dict) else {}

    lines = [
        "<!doctype html>",
        "<html lang=\"zh-CN\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<title>Acceptance Packet</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;line-height:1.6;max-width:960px;margin:32px auto;padding:0 20px;color:#1f2937;}",
        "h1,h2{line-height:1.2;}",
        "section{margin:24px 0;padding:16px;border:1px solid #e5e7eb;border-radius:8px;}",
        "table{width:100%;border-collapse:collapse;}",
        "th,td{border:1px solid #e5e7eb;padding:8px;vertical-align:top;text-align:left;}",
        "code{background:#f3f4f6;padding:2px 4px;border-radius:4px;}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Acceptance Packet</h1>",
        f"<p><strong>Chapter:</strong> {html.escape(str(packet.get('chapter', '')))}</p>",
        f"<p><strong>Title:</strong> {html.escape(str(packet.get('title', '')))}</p>",
        f"<p><strong>Summary:</strong> {html.escape(str(packet.get('summary', '')))}</p>",
        _section_html("Quality Gate Summary", _mapping_table(quality)),
        _section_html("Outline Alignment", _mapping_table(outline)),
        _section_html("State Updates", _mapping_table(state_updates)),
        _section_html("Timeline Event", _list_html(packet.get("timeline_event"))),
        _section_html("V3 State Updates", _list_html(packet.get("v3_state_updates"))),
        _section_html("Change Log", _list_html(packet.get("change_log"))),
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(lines)


def _section_html(title: str, body: str) -> str:
    return f"<section><h2>{html.escape(title)}</h2>{body}</section>"


def _mapping_table(data: Any) -> str:
    if not isinstance(data, dict):
        return "<p>None</p>"
    rows = [
        "<table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>"
    ]
    for key, value in data.items():
        rows.append(
            f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(_stringify(value))}</td></tr>"
        )
    rows.append("</tbody></table>")
    return "".join(rows)


def _list_html(data: Any) -> str:
    if isinstance(data, list):
        if not data:
            return "<p>None</p>"
        items = "".join(f"<li>{html.escape(_stringify(item))}</li>" for item in data)
        return f"<ul>{items}</ul>"
    if isinstance(data, dict):
        return _mapping_table(data)
    return f"<p>{html.escape(_stringify(data))}</p>"


def _stringify(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return repr(value)
    return str(value)
