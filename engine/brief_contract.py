from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_text, read_yaml
from engine.outline_gate import BRIEF_REFERENCE_CHAIN, chapter_brief_gate
from engine.paths import books_dir

BOOKS_DIR = books_dir()

REQUIRED_BRIEF_SECTIONS = [
    "## V3.3 Outline Contract",
    "## Chapter Goal",
    "## Opening Hook",
    "## Required Beats",
    "## Character Movement",
    "## Payoff Design",
    "## State Update Expectations",
    "## Economy And Faction Constraints",
    "## Ending Pull",
    "## Continuity Notes",
]


def build_chapter_brief_scaffold(book_id: str, chapter_number: int) -> str:
    root = _book_root(book_id)
    active = _active_outline_data(root, chapter_number)
    unit_chapter = _unit_chapter(active["unit"], chapter_number)
    open_threads = _open_threads(root, active["arc"].get("required_threads", []))
    payoff_lines = _payoff_lines(root, chapter_number)
    hook_lines = _hook_lines(root)
    economy = read_yaml(root / "canon" / "economy.yaml")
    factions = read_yaml(root / "canon" / "factions.yaml")

    lines = [
        f"# Chapter {chapter_number} Brief Scaffold",
        "",
        "## V3.3 Outline Contract",
        "",
        f"- Reference chain: {BRIEF_REFERENCE_CHAIN} -> chapter_{chapter_number:04d}.",
        f"- Required literal chain: {BRIEF_REFERENCE_CHAIN} -> chapter brief.",
        f"- Volume obligation: {_id(active['volume'], 'volume_id', 'volume_001')}: {_field(active['volume'], 'volume_goal')}",
        f"- Arc obligation: {_id(active['arc'], 'arc_id', 'arc_001')}: {_field(active['arc'], 'arc_goal')}",
        f"- Unit obligation: {_unit_id(active['unit'])}: {_field(active['unit'], 'unit_goal')}",
        f"- Chapter {chapter_number} function:{unit_chapter.get('function', '')}",
        "",
        "## Chapter Goal",
        "",
        f"- Serve the unit function: {unit_chapter.get('function', '')}",
        "",
        "## Opening Hook",
        "",
        f"- {unit_chapter.get('opening_hook', '')}",
        "",
        "## Required Beats",
        "",
        "- [ ] Establish the immediate negotiation or scene pressure.",
        "- [ ] Advance the active outline obligation.",
        "- [ ] Deliver a visible payoff or meaningful reversal.",
        "",
        "## Character Movement",
        "",
        "- Protagonist movement:",
        "- Key supporting character movement:",
        "",
        "## Payoff Design",
        "",
        f"- Unit payoff target: {unit_chapter.get('main_payoff', '')}",
    ]
    lines.extend(f"- {line}" for line in payoff_lines)
    lines.extend(
        [
            "",
            "## State Update Expectations",
            "",
            "- Timeline event:",
            "- Character state changes:",
            "- Resource changes:",
            "- Open threads to update:",
        ]
    )
    lines.extend(f"  - {thread}" for thread in open_threads)
    lines.extend(
        [
            "- Hook continuity:",
        ]
    )
    lines.extend(f"  - {hook}" for hook in hook_lines)
    lines.extend(
        [
            "",
            "## Economy And Faction Constraints",
            "",
        ]
    )
    lines.extend(f"- Economy: {item}" for item in _ids_from_list(economy, "currencies"))
    lines.extend(f"- Faction: {item}" for item in _ids_from_list(factions, "factions"))
    lines.extend(
        [
            "",
            "## Ending Pull",
            "",
            f"- {unit_chapter.get('next_hook', '')}",
            "",
            "## Continuity Notes",
            "",
            "- Keep new facts proposed until acceptance.",
            "- Record approvals for major canon or outline changes.",
            "",
        ]
    )
    return "\n".join(lines)


def check_chapter_brief(book_id: str, chapter_number: int) -> dict[str, Any]:
    root = _book_root(book_id)
    path = root / "outlines" / "chapter_briefs" / f"ch_{chapter_number:04d}_brief.md"
    if not path.exists():
        return {
            "book_id": book_id,
            "chapter": chapter_number,
            "status": "missing",
            "passed": False,
            "errors": [f"Missing chapter brief: {path.relative_to(root).as_posix()}"],
            "warnings": [],
        }

    content = read_text(path)
    errors = [
        f"Missing required section: {section}"
        for section in REQUIRED_BRIEF_SECTIONS
        if section not in content
    ]
    if BRIEF_REFERENCE_CHAIN not in content:
        errors.append(f"Missing reference chain: {BRIEF_REFERENCE_CHAIN}")

    gate = chapter_brief_gate(book_id, chapter_number)
    errors.extend(gate["blocking_errors"])
    warnings = gate["warnings"]
    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "status": "passed" if not errors else "failed",
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def default_brief_path(book_id: str, chapter_number: int) -> Path:
    return (
        _book_root(book_id)
        / "outlines"
        / "chapter_briefs"
        / f"ch_{chapter_number:04d}_brief.md"
    )


def _book_root(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    return root


def _active_outline_data(root: Path, chapter_number: int) -> dict[str, dict[str, Any]]:
    return {
        "volume": read_yaml(root / "outlines" / "volumes" / "volume_001.yaml"),
        "arc": read_yaml(root / "outlines" / "arc_001.yaml"),
        "unit": read_yaml(root / "outlines" / "units" / "unit_0001.yaml"),
    }


def _unit_chapter(unit: dict[str, Any], chapter_number: int) -> dict[str, Any]:
    for chapter in unit.get("chapters", []):
        if isinstance(chapter, dict) and chapter.get("chapter") == chapter_number:
            return chapter
    return {}


def _open_threads(root: Path, required_thread_ids: list[str]) -> list[str]:
    ledger = read_yaml(root / "canon" / "open_threads.yaml")
    threads = ledger.get("threads", [])
    lines = []
    for thread in threads:
        if not isinstance(thread, dict):
            continue
        thread_id = thread.get("id", "")
        if required_thread_ids and thread_id not in required_thread_ids:
            continue
        promise = thread.get("promise", "")
        lines.append(f"{thread_id}: {promise}")
    return lines


def _payoff_lines(root: Path, chapter_number: int) -> list[str]:
    ledger = read_yaml(root / "canon" / "payoff_ledger.yaml")
    lines = []
    for entry in ledger.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("chapter") not in (None, chapter_number):
            continue
        for promise in entry.get("promises_made", []):
            lines.append(str(promise))
        for payoff in entry.get("payoffs_delivered", []):
            lines.append(str(payoff))
    return lines


def _hook_lines(root: Path) -> list[str]:
    path = root / "state" / "hook_index.json"
    data = read_json(path) if path.exists() else {}
    hooks = data.get("hooks", [])
    lines = []
    for hook in hooks:
        if isinstance(hook, dict):
            text = hook.get("text") or hook.get("hook") or hook.get("summary")
            if text:
                lines.append(str(text))
        elif isinstance(hook, str):
            lines.append(hook)
    return lines[-3:]


def _field(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    return str(value)


def _id(data: dict[str, Any], key: str, fallback: str) -> str:
    value = data.get(key) or fallback
    return str(value)


def _unit_id(unit: dict[str, Any]) -> str:
    value = unit.get("unit")
    if value in (None, ""):
        return "unit_0001"
    if isinstance(value, int):
        return f"unit_{value:04d}"
    return str(value)


def _ids_from_list(data: dict[str, Any], key: str) -> list[str]:
    items = data.get(key, [])
    results = []
    for item in items:
        if isinstance(item, dict):
            results.append(str(item.get("id") or item.get("name") or item))
        else:
            results.append(str(item))
    return results
