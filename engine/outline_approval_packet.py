from pathlib import Path
from typing import Any

from engine.html_utils import write_markdown_html_sidecar
from engine.io_utils import read_yaml, write_text
from engine.paths import books_dir

BOOKS_DIR = books_dir()

SUPPORTED_LAYERS = {"master"}


def generate_outline_approval_packet(book_id: str, *, layer: str) -> Path:
    if layer not in SUPPORTED_LAYERS:
        raise ValueError(f"Unknown outline approval packet layer: {layer}")
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    output = root / "reports" / f"{layer}_outline_approval_packet.md"
    content = render_master_approval_packet(root)
    write_text(output, content)
    write_markdown_html_sidecar(output, "Master Outline Approval Packet", content)
    return output


def render_master_approval_packet(root: Path) -> str:
    master = _read_yaml(root / "outlines" / "master_outline.yaml")
    lines = [
        "# Master Outline Approval Packet",
        "",
        "This is a human review packet, not a mechanical minimum-map report.",
        "",
        "## Full Book Direction",
        "",
        f"- Logline: {master.get('logline', '')}",
        f"- Story promise: {master.get('story_promise', '')}",
        f"- Full book arc: {master.get('full_book_arc', '')}",
        f"- Ending direction: {master.get('ending_direction', '')}",
        "",
    ]
    lines.extend(_state_section("Opening State", _as_dict(master.get("opening_state"))))
    lines.extend(_state_section("Ending State", _as_dict(master.get("ending_state"))))
    lines.extend(_three_act_section(master))
    lines.extend(_growth_section(master))
    lines.extend(_core_mystery_section(master))
    lines.extend(_list_section("Core Rules Locked", _as_list(master.get("core_rules_locked"))))
    lines.extend(_volume_plan_section(master))
    lines.extend(_list_section("Major Turning Points", _as_list(master.get("major_turning_points"))))
    lines.extend(_list_section("Open Story Spaces", _as_list(master.get("open_story_spaces"))))
    lines.extend(
        [
            "## Approval Questions",
            "",
            "- Approve the full-book endpoint and final choice?",
            "- Approve the protagonist growth curve?",
            "- Approve the volume plan as the next outline layer to detail?",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _state_section(title: str, state: dict[str, Any]) -> list[str]:
    lines = [f"## {title}", ""]
    if not state:
        lines.append("- Empty")
    else:
        lines.extend(f"- {key}: {value}" for key, value in state.items())
    lines.append("")
    return lines


def _three_act_section(master: dict[str, Any]) -> list[str]:
    acts = _as_dict(master.get("three_act_structure"))
    lines = ["## Three-Act Structure", ""]
    for act_id in ("act_1", "act_2", "act_3"):
        act = _as_dict(acts.get(act_id))
        if not act:
            continue
        lines.extend(
            [
                f"### {act_id}",
                "",
                f"- Chapter range: {act.get('chapter_range', '')}",
                f"- Function: {act.get('function', '')}",
            ]
        )
        lines.extend(f"- Turning point: {item}" for item in _as_list(act.get("major_turning_points")))
        for key in ("midpoint", "act_climax", "final_climax", "ending"):
            if act.get(key):
                lines.append(f"- {key}: {act[key]}")
        lines.append("")
    return lines


def _growth_section(master: dict[str, Any]) -> list[str]:
    growth = _as_dict(master.get("protagonist_growth_curve"))
    lines = ["## Protagonist Growth Curve", ""]
    for key in ("start", "act_1_end", "midpoint", "act_2_end", "end"):
        lines.append(f"- {key}: {growth.get(key, '')}")
    lines.append("")
    return lines


def _core_mystery_section(master: dict[str, Any]) -> list[str]:
    mystery = _as_dict(master.get("core_mystery"))
    lines = [
        "## Core Mystery",
        "",
        f"- Question: {mystery.get('question', '')}",
        f"- Answer direction: {mystery.get('answer_direction', '')}",
    ]
    lines.extend(f"- Reveal stage: {stage}" for stage in _as_list(mystery.get("reveal_stages")))
    lines.append("")
    return lines


def _volume_plan_section(master: dict[str, Any]) -> list[str]:
    lines = ["## Volume Plan", ""]
    for volume in _as_list(master.get("volume_plan")):
        if not isinstance(volume, dict):
            continue
        title = volume.get("title", "")
        index = volume.get("volume", "")
        lines.extend(
            [
                f"### Volume {index}: {title}",
                "",
                f"- Chapter range: {volume.get('chapter_range', '')}",
                f"- Function: {volume.get('function', '')}",
                f"- Endpoint: {volume.get('endpoint', '')}",
                "",
            ]
        )
    if len(lines) == 2:
        lines.extend(["- Empty", ""])
    return lines


def _list_section(title: str, items: list[Any]) -> list[str]:
    lines = [f"## {title}", ""]
    if items:
        lines.extend(f"- {item}" for item in items)
    else:
        lines.append("- Empty")
    lines.append("")
    return lines


def _read_yaml(path: Path) -> dict[str, Any]:
    data = read_yaml(path) if path.exists() else {}
    return data if isinstance(data, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
