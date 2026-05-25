from pathlib import Path
from typing import Any

from engine.craft_knowledge import load_craft_cards, render_craft_cards
from engine.html_utils import write_markdown_html_sidecar
from engine.io_utils import read_yaml, write_text
from engine.outline_gate import _validate_active_unit_chapter_map
from engine.outline_resolver import active_outline_data, unit_chapter
from engine.paths import books_dir

BOOKS_DIR = books_dir()


def generate_outline_map_review(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    output = root / "reports" / "outline_map_review.md"
    content = render_outline_map_review(root)
    write_text(output, content)
    write_markdown_html_sidecar(output, "Outline Map Review", content)
    return output


def render_outline_map_review(root: Path) -> str:
    master = _read_yaml(root / "outlines" / "master_outline.yaml")
    volume = _read_yaml(root / "outlines" / "volumes" / "volume_001.yaml")
    arc = _read_yaml(root / "outlines" / "arc_001.yaml")
    unit = _read_yaml(root / "outlines" / "units" / "unit_0001.yaml")
    open_threads = _read_yaml(root / "canon" / "open_threads.yaml")
    payoff_ledger = _read_yaml(root / "canon" / "payoff_ledger.yaml")
    active = active_outline_data(root, 1)
    active_unit_chapter = unit_chapter(active["unit"], 1)

    lines = [
        "# Outline Minimum Map Review",
        "",
        "This is a mechanical minimum-map report, not a full human approval packet.",
        "",
    ]
    lines.extend(_minimum_map(master, volume, arc, unit))
    lines.extend(_book_overview(master))
    lines.extend(_volume_map(volume))
    lines.extend(_arc_map(arc))
    lines.extend(_unit_map(unit, active_unit_chapter))
    lines.extend(
        _outline_warnings(root, master, volume, arc, unit, open_threads, payoff_ledger)
    )
    lines.extend(render_craft_cards(load_craft_cards("outline")))
    return "\n".join(lines).rstrip() + "\n"


def _book_overview(master: dict[str, Any]) -> list[str]:
    return [
        "## Book Overview",
        "",
        f"- Story promise: {master.get('story_promise', '')}",
        f"- Core mystery: {master.get('core_mystery', {}).get('question', '')}",
        f"- End state: {master.get('ending_state', {}).get('protagonist', '')}",
        "",
    ]


def _minimum_map(
    master: dict[str, Any],
    volume: dict[str, Any],
    arc: dict[str, Any],
    unit: dict[str, Any],
) -> list[str]:
    protagonist_progress = _as_dict(volume.get("protagonist_progress"))
    return [
        "## Outline Minimum Map",
        "",
        "| Layer | Core Conflict | Turning Point | Payoff Or Climax | Stage Ending | Protagonist Change |",
        "| --- | --- | --- | --- | --- | --- |",
        "| Book | {book_conflict} | {book_turn} | {book_payoff} | {book_end} | {book_growth} |".format(
            book_conflict=_cell(master.get("story_promise", "")),
            book_turn=_cell(", ".join(str(item) for item in _as_list(master.get("major_turning_points")))),
            book_payoff=_cell(master.get("ending_direction", "")),
            book_end=_cell(_as_dict(master.get("ending_state")).get("protagonist", "")),
            book_growth=_cell(_as_dict(master.get("protagonist_growth_curve")).get("end", "")),
        ),
        "| Volume | {conflict} | {turn} | {payoff} | {end} | {growth} |".format(
            conflict=_cell(_as_dict(volume.get("main_pressure")).get("antagonist_or_force", "")),
            turn=_cell(volume.get("major_reveal", "")),
            payoff=_cell(volume.get("volume_climax", "")),
            end=_cell(volume.get("ending_hook", "")),
            growth=_cell(protagonist_progress.get("end_state", "")),
        ),
        "| Arc | {conflict} | {turn} | {payoff} | {end} | {growth} |".format(
            conflict=_cell(arc.get("main_conflict", "")),
            turn=_cell(arc.get("major_reveal_or_reversal", "")),
            payoff=_cell("; ".join(str(item) for item in _as_list(arc.get("required_payoffs")))),
            end=_cell(arc.get("exit_state", "")),
            growth=_cell(arc.get("protagonist_move", "")),
        ),
        "| Unit | {conflict} | {turn} | {payoff} | {end} | {growth} |".format(
            conflict=_cell(unit.get("stage_enemy", "")),
            turn=_cell(unit.get("stage_end_hook", "")),
            payoff=_cell("; ".join(str(item) for item in _as_list(unit.get("stage_payoffs")))),
            end=_cell(unit.get("stage_end_hook", "")),
            growth=_cell(unit.get("unit_goal", "")),
        ),
        "",
    ]


def _volume_map(volume: dict[str, Any]) -> list[str]:
    return [
        "## Volume Map",
        "",
        f"- Volume goal: {volume.get('volume_goal', '')}",
        f"- Main pressure: {volume.get('main_pressure', {}).get('antagonist_or_force', '')}",
        f"- Ending hook: {volume.get('ending_hook', '')}",
        "",
    ]


def _arc_map(arc: dict[str, Any]) -> list[str]:
    return [
        "## Arc Map",
        "",
        f"- Arc goal: {arc.get('arc_goal', '')}",
        f"- Main conflict: {arc.get('main_conflict', '')}",
        f"- Major reveal or reversal: {arc.get('major_reveal_or_reversal', '')}",
        "",
    ]


def _unit_map(unit: dict[str, Any], active_unit_chapter: dict[str, Any]) -> list[str]:
    return [
        "## Unit Map",
        "",
        f"- Unit goal: {unit.get('unit_goal', '')}",
        f"- Stage enemy: {unit.get('stage_enemy', '')}",
        f"- Stage end hook: {unit.get('stage_end_hook', '')}",
        f"- Chapter 1 function: {active_unit_chapter.get('function', '')}",
        "",
    ]


def _outline_warnings(
    root: Path,
    master: dict[str, Any],
    volume: dict[str, Any],
    arc: dict[str, Any],
    unit: dict[str, Any],
    open_threads: dict[str, Any],
    payoff_ledger: dict[str, Any],
) -> list[str]:
    warnings = []
    if not master.get("story_promise"):
        warnings.append("missing_story_promise")
    if not master.get("core_mystery", {}).get("question"):
        warnings.append("missing_core_mystery")
    if not master.get("story_promise") or not master.get("ending_direction"):
        warnings.append("missing_core")
    if not volume.get("volume_goal"):
        warnings.append("missing_volume_goal")
    if not volume.get("main_pressure", {}).get("antagonist_or_force"):
        warnings.append("missing_volume_pressure")
    if not volume.get("volume_climax") or not volume.get("ending_hook"):
        warnings.append("missing_stage_map")
    if not arc.get("main_conflict"):
        warnings.append("missing_arc_conflict")
    if not arc.get("major_reveal_or_reversal"):
        warnings.append("missing_arc_reveal")
    if not unit.get("unit_goal"):
        warnings.append("missing_unit_goal")
    if not unit.get("stage_payoffs"):
        warnings.append("missing_unit_payoff")
    if not unit.get("stage_payoffs") or not unit.get("stage_end_hook") or not unit.get("chapters"):
        warnings.append("missing_unit_flow")
    warnings.extend(
        f"incomplete_active_unit_chapter_map: {error}"
        for error in _validate_active_unit_chapter_map(root, 1)
    )
    warnings.extend(_unmapped_thread_warnings(volume, arc, unit, open_threads))
    warnings.extend(_unmapped_payoff_warnings(arc, unit, payoff_ledger))

    lines = [
        "## Outline Map Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.append("")
    return lines


def _unmapped_thread_warnings(
    volume: dict[str, Any],
    arc: dict[str, Any],
    unit: dict[str, Any],
    open_threads: dict[str, Any],
) -> list[str]:
    mapped = {
        str(thread_id)
        for layer in (volume, arc, unit)
        for thread_id in _as_list(layer.get("required_threads"))
    }
    warnings = []
    for thread in _as_list(open_threads.get("threads")):
        if not isinstance(thread, dict):
            continue
        thread_id = str(thread.get("id") or "")
        if thread_id and thread_id not in mapped and thread.get("status") in {"open", "advanced", None}:
            warnings.append(f"unmapped_open_thread: {thread_id}")
    return warnings


def _unmapped_payoff_warnings(
    arc: dict[str, Any],
    unit: dict[str, Any],
    payoff_ledger: dict[str, Any],
) -> list[str]:
    outline_text = " ".join(
        [
            " ".join(str(item) for item in _as_list(arc.get("required_payoffs"))),
            " ".join(str(item) for item in _as_list(unit.get("stage_payoffs"))),
        ]
    )
    warnings = []
    for entry in _as_list(payoff_ledger.get("entries")):
        if not isinstance(entry, dict):
            continue
        for promise in _as_list(entry.get("promises_made")):
            promise_text = str(promise)
            if promise_text and promise_text not in outline_text:
                warnings.append(f"unmapped_payoff_promise: {promise_text}")
    return warnings


def _read_yaml(path: Path) -> dict[str, Any]:
    data = read_yaml(path) if path.exists() else {}
    return data if isinstance(data, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
