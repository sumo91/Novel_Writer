import json
from pathlib import Path
from typing import Any

from engine.craft_knowledge import load_craft_cards
from engine.io_utils import read_json, read_yaml, write_text
from engine.pending_approvals import collect_pending_approvals_from_root
from engine.paths import books_dir

BOOKS_DIR = books_dir()


def generate_drift_report(
    book_id: str,
    start_chapter: int,
    end_chapter: int,
    output_path: Path | None = None,
) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    output = output_path or root / "reports" / (
        f"ch_{start_chapter:04d}_{end_chapter:04d}_drift_review.md"
    )
    content = _render_report(root, start_chapter, end_chapter)
    write_text(output, content)
    return output


def _render_report(root: Path, start_chapter: int, end_chapter: int) -> str:
    chapter_index = read_json(root / "state" / "chapter_index.json")
    current_state = read_json(root / "state" / "current_state.json")
    timeline = read_yaml(root / "canon" / "timeline.yaml")
    open_threads = read_yaml(root / "canon" / "open_threads.yaml")

    chapters = [
        chapter
        for chapter in chapter_index.get("chapters", [])
        if start_chapter <= int(chapter.get("chapter", 0)) <= end_chapter
    ]

    lines = [f"# Chapter {start_chapter}-{end_chapter} Drift Review", ""]
    lines.extend(_event_timeline(chapters))
    lines.extend(_character_state(current_state))
    lines.extend(_open_threads(open_threads))
    lines.extend(_payoff_hook_ledger(chapters))
    lines.extend(_pending_approvals(root))
    lines.extend(_v3_state_machine_warnings(root, current_state, open_threads, end_chapter))
    lines.extend(_outline_alignment(root, chapters, start_chapter, end_chapter))
    lines.extend(_unit_review(root, chapters, current_state, open_threads, start_chapter, end_chapter))
    lines.extend(_craft_knowledge_checks())
    lines.extend(_continuity_risks(root, start_chapter, end_chapter))
    lines.extend(_pacing_scores(root, start_chapter, end_chapter))
    lines.extend(_chapter_recommendation(current_state, timeline))
    return "\n".join(lines).rstrip() + "\n"


def _event_timeline(chapters: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Event Timeline",
        "",
        "| Chapter | Event | Durable State Change |",
        "| --- | --- | --- |",
    ]
    for chapter in chapters:
        state_changes = chapter.get("state_changes", [])
        durable_change = state_changes[-1] if state_changes else ""
        lines.append(
            f"| {chapter.get('chapter')} | {chapter.get('summary', '')} | {durable_change} |"
        )
    lines.append("")
    return lines


def _character_state(current_state: dict[str, Any]) -> list[str]:
    lines = [
        "## Character State",
        "",
        "| Character | Physical State | Social State | Emotional State | Open Questions |",
        "| --- | --- | --- | --- | --- |",
    ]
    location = current_state.get("latest_location", "")
    conflicts = "；".join(current_state.get("active_conflicts", []))
    for character in current_state.get("active_characters", []):
        lines.append(f"| {character} | {location} | {conflicts} | 未自动推断 | 待人工补充 |")
    lines.append("")
    return lines


def _open_threads(open_threads: dict[str, Any]) -> list[str]:
    lines = [
        "## Open Threads",
        "",
        "| Thread | Status | Last Touched | Next Obligation |",
        "| --- | --- | --- | --- |",
    ]
    for thread in open_threads.get("threads", []):
        lines.append(
            "| {id} {promise} | {status} | {latest} | 待人工确认下一阶段义务 |".format(
                id=thread.get("id", ""),
                promise=thread.get("promise", ""),
                status=thread.get("status", ""),
                latest=thread.get("latest_note", ""),
            )
        )
    lines.append("")
    return lines


def _payoff_hook_ledger(chapters: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Payoff And Hook Ledger",
        "",
        "| Chapter | Hook | Payoff | Next-Chapter Pull |",
        "| --- | --- | --- | --- |",
    ]
    for chapter in chapters:
        state_changes = chapter.get("state_changes", [])
        hook = state_changes[0] if state_changes else ""
        payoff = state_changes[-1] if state_changes else ""
        lines.append(f"| {chapter.get('chapter')} | {hook} | {payoff} | 待人工细化 |")
    lines.append("")
    return lines


def _pending_approvals(root: Path) -> list[str]:
    lines = [
        "## Pending Approvals",
        "",
        "| Approval | Source Chapter | Decision Needed |",
        "| --- | --- | --- |",
    ]
    for approval in collect_pending_approvals_from_root(root):
        chapters = ", ".join(str(chapter) for chapter in approval.source_chapters)
        lines.append(f"| {approval.text} | {chapters} | 待人工决策 |")
    lines.append("")
    return lines


def _v3_state_machine_warnings(
    root: Path,
    current_state: dict[str, Any],
    open_threads: dict[str, Any],
    end_chapter: int,
) -> list[str]:
    current_chapter = _numeric(current_state.get("current_chapter"))
    if current_chapter is None:
        current_chapter = end_chapter

    hook_index = _read_json_if_present(root / "state" / "hook_index.json")
    payoff_ledger = _read_yaml_if_present(root / "canon" / "payoff_ledger.yaml")
    resource_ledger = _read_yaml_if_present(root / "canon" / "resource_ledger.yaml")
    character_states = _read_yaml_if_present(root / "canon" / "character_states.yaml")

    warnings: list[tuple[str, str, str, str]] = []
    warnings.extend(_stale_thread_warnings(open_threads, current_chapter))
    warnings.extend(_overdue_hook_warnings(hook_index, current_chapter))
    warnings.extend(_high_frustration_warnings(payoff_ledger))
    warnings.extend(_stale_character_state_warnings(current_state, character_states))
    warnings.extend(_resource_missing_history_warnings(resource_ledger))

    lines = [
        "## V3 State Machine Warnings",
        "",
        "| Type | Item | Evidence | Recommended Action |",
        "| --- | --- | --- | --- |",
    ]
    if warnings:
        for warning_type, item, evidence, action in warnings:
            lines.append(
                f"| {_cell(warning_type)} | {_cell(item)} | {_cell(evidence)} | {_cell(action)} |"
            )
    else:
        lines.append("| None | - | No mechanical V3 warning found. | Continue. |")
    lines.append("")
    return lines


def _stale_thread_warnings(
    open_threads: dict[str, Any],
    current_chapter: int | float,
) -> list[tuple[str, str, str, str]]:
    warnings = []
    for thread in _as_list(open_threads.get("threads")):
        if not isinstance(thread, dict):
            continue
        deadline = _numeric(thread.get("payoff_deadline"))
        if (
            thread.get("status") in {"open", "advanced"}
            and deadline is not None
            and deadline < current_chapter
        ):
            item = str(thread.get("id") or thread.get("promise") or "thread")
            evidence = f"payoff_deadline {deadline:g} is before current_chapter {current_chapter:g}"
            warnings.append(
                (
                    "stale_thread",
                    item,
                    evidence,
                    "Resolve, advance, or revise the thread deadline.",
                )
            )
    return warnings


def _overdue_hook_warnings(
    hook_index: dict[str, Any],
    current_chapter: int | float,
) -> list[tuple[str, str, str, str]]:
    warnings = []
    for hook in _as_list(hook_index.get("hooks")):
        if not isinstance(hook, dict):
            continue
        target_chapter = _numeric(hook.get("target_chapter"))
        if (
            hook.get("status") == "open"
            and target_chapter is not None
            and target_chapter < current_chapter
        ):
            item = str(hook.get("hook") or "hook")
            evidence = f"target_chapter {target_chapter:g} is before current_chapter {current_chapter:g}"
            warnings.append(
                (
                    "overdue_hook",
                    item,
                    evidence,
                    "Pay off, escalate, or retarget the hook.",
                )
            )
    return warnings


def _high_frustration_warnings(
    payoff_ledger: dict[str, Any],
) -> list[tuple[str, str, str, str]]:
    warnings = []
    streak: list[dict[str, Any]] = []
    for entry in _as_list(payoff_ledger.get("entries")):
        if not isinstance(entry, dict):
            streak = []
            continue
        if entry.get("frustration_level") in {"high", "overdue"}:
            streak.append(entry)
            continue
        warnings.extend(_frustration_streak_warnings(streak))
        streak = []
    warnings.extend(_frustration_streak_warnings(streak))
    return warnings


def _frustration_streak_warnings(
    streak: list[dict[str, Any]],
) -> list[tuple[str, str, str, str]]:
    if len(streak) < 2:
        return []
    chapters = [
        str(entry.get("chapter"))
        for entry in streak
        if entry.get("chapter") is not None
    ]
    item = "chapters " + ", ".join(chapters) if chapters else "payoff entries"
    evidence = f"{len(streak)} consecutive payoff entries are high or overdue."
    return [
        (
            "high_frustration",
            item,
            evidence,
            "Deliver a concrete payoff or reset reader expectations.",
        )
    ]


def _stale_character_state_warnings(
    current_state: dict[str, Any],
    character_states: dict[str, Any],
) -> list[tuple[str, str, str, str]]:
    characters = _as_dict(character_states.get("characters"))
    warnings = []
    for character in _as_list(current_state.get("active_characters")):
        character_id = str(character)
        if character_id and character_id not in characters:
            warnings.append(
                (
                    "stale_character_state",
                    character_id,
                    "active character has no character_states entry.",
                    "Add or confirm the character state snapshot.",
                )
            )
    return warnings


def _resource_missing_history_warnings(
    resource_ledger: dict[str, Any],
) -> list[tuple[str, str, str, str]]:
    warnings = []
    for resource in _as_list(resource_ledger.get("resources")):
        if not isinstance(resource, dict):
            continue
        if not resource.get("history"):
            item = str(resource.get("id") or resource.get("name") or "resource")
            warnings.append(
                (
                    "resource_missing_history",
                    item,
                    "resource item has no history entries.",
                    "Add provenance/history or remove the stale resource.",
                )
            )
    return warnings


def _outline_alignment(
    root: Path,
    chapters: list[dict[str, Any]],
    start_chapter: int,
    end_chapter: int,
) -> list[str]:
    units = _approved_units(root)
    warnings: list[tuple[str, str, str, str]] = []
    warnings.extend(_chapter_outside_approved_unit_warnings(units, start_chapter, end_chapter))
    for unit_path, unit in units:
        if not _as_list(unit.get("chapters")):
            warnings.append(
                (
                    "empty_unit_chapters",
                    unit_path,
                    "approved unit has no chapter function map.",
                    "Fill chapter obligations before drafting more chapters.",
                )
            )
        required_threads = [str(thread) for thread in _as_list(unit.get("required_threads"))]
        if required_threads:
            touched = {
                str(thread)
                for chapter in chapters
                for thread in _as_list(chapter.get("open_threads_touched"))
            }
            for thread in required_threads:
                if thread not in touched:
                    warnings.append(
                        (
                            "missing_required_thread",
                            thread,
                            f"{unit_path} requires this thread, but chapters {start_chapter}-{end_chapter} did not touch it.",
                            "Advance, pay off, or explicitly defer the thread.",
                        )
                    )

    lines = [
        "## Outline Alignment",
        "",
        "| Type | Item | Evidence | Recommended Action |",
        "| --- | --- | --- | --- |",
    ]
    if warnings:
        for warning_type, item, evidence, action in warnings:
            lines.append(
                f"| {_cell(warning_type)} | {_cell(item)} | {_cell(evidence)} | {_cell(action)} |"
            )
    else:
        lines.append("| None | - | No mechanical outline alignment warning found. | Continue. |")
    lines.append("")
    return lines


def _approved_units(root: Path) -> list[tuple[str, dict[str, Any]]]:
    units_dir = root / "outlines" / "units"
    if not units_dir.exists():
        return []
    units: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(units_dir.glob("unit_*.yaml")):
        unit = _read_yaml_if_present(path)
        approval = unit.get("approval")
        status = approval.get("status") if isinstance(approval, dict) else None
        if status == "approved":
            units.append((path.relative_to(root).as_posix(), unit))
    return units


def _chapter_outside_approved_unit_warnings(
    units: list[tuple[str, dict[str, Any]]],
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    if not units:
        return []
    warnings = []
    for chapter_number in range(start_chapter, end_chapter + 1):
        if not any(_unit_contains_chapter(unit, chapter_number) for _, unit in units):
            warnings.append(
                (
                    "chapter_outside_approved_unit",
                    f"chapter {chapter_number}",
                    "chapter is outside all approved unit chapter ranges.",
                    "Approve or create the active unit plan before continuing.",
                )
            )
    return warnings


def _unit_contains_chapter(unit: dict[str, Any], chapter_number: int) -> bool:
    chapter_range = unit.get("chapter_range")
    if not isinstance(chapter_range, dict):
        return False
    start = chapter_range.get("start")
    end = chapter_range.get("end")
    return isinstance(start, int) and isinstance(end, int) and start <= chapter_number <= end


def _unit_review(
    root: Path,
    chapters: list[dict[str, Any]],
    current_state: dict[str, Any],
    open_threads: dict[str, Any],
    start_chapter: int,
    end_chapter: int,
) -> list[str]:
    payoff_ledger = _read_yaml_if_present(root / "canon" / "payoff_ledger.yaml")
    resource_ledger = _read_yaml_if_present(root / "canon" / "resource_ledger.yaml")
    character_states = _read_yaml_if_present(root / "canon" / "character_states.yaml")

    warnings: list[tuple[str, str, str, str]] = []
    warnings.extend(_unit_pacing_warnings(root, start_chapter, end_chapter))
    warnings.extend(_repeated_payoff_warnings(payoff_ledger, start_chapter, end_chapter))
    warnings.extend(_stalled_foreshadowing_warnings(open_threads, start_chapter, end_chapter))
    warnings.extend(_resource_inflation_warnings(resource_ledger, start_chapter, end_chapter))
    warnings.extend(
        _protagonist_growth_gap_warnings(
            current_state,
            character_states,
            start_chapter,
            end_chapter,
        )
    )

    lines = [
        "## Unit Review",
        "",
        f"Scope: chapters {start_chapter}-{end_chapter} ({len(chapters)} accepted/indexed chapters).",
        "",
        "| Type | Item | Evidence | Recommended Action |",
        "| --- | --- | --- | --- |",
    ]
    if warnings:
        for warning_type, item, evidence, action in warnings:
            lines.append(
                f"| {_cell(warning_type)} | {_cell(item)} | {_cell(evidence)} | {_cell(action)} |"
            )
    else:
        lines.append("| None | - | No mechanical unit-level warning found. | Continue. |")
    lines.append("")
    return lines


def _unit_pacing_warnings(
    root: Path,
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    low_scores = []
    for chapter_number in range(start_chapter, end_chapter + 1):
        path = root / "reviews" / f"ch_{chapter_number:04d}" / "pacing_review.json"
        if not path.exists():
            continue
        pacing = read_json(path)
        score = pacing.get("revised_score")
        if score is None:
            score = pacing.get("score")
        if _numeric(score) is not None and score < 80:
            low_scores.append(f"ch{chapter_number}: {score}")
    if not low_scores:
        return []
    return [
        (
            "pacing_risk",
            f"chapters {start_chapter}-{end_chapter}",
            "low pacing scores: " + ", ".join(low_scores),
            "Revise the weak chapter or make the waiver explicit before extending the unit.",
        )
    ]


def _repeated_payoff_warnings(
    payoff_ledger: dict[str, Any],
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    counts: dict[str, int] = {}
    for entry in _as_list(payoff_ledger.get("entries")):
        if not isinstance(entry, dict):
            continue
        chapter = _numeric(entry.get("chapter"))
        if chapter is None or not (start_chapter <= chapter <= end_chapter):
            continue
        for payoff_type in _as_list(entry.get("payoff_types")):
            key = str(payoff_type)
            counts[key] = counts.get(key, 0) + 1
    warnings = []
    for payoff_type, count in sorted(counts.items()):
        if count >= 3:
            warnings.append(
                (
                    "repeated_payoff_type",
                    payoff_type,
                    f"{count} payoff entries in chapters {start_chapter}-{end_chapter}.",
                    "Vary the payoff shape or escalate the repeated pleasure point.",
                )
            )
    return warnings


def _stalled_foreshadowing_warnings(
    open_threads: dict[str, Any],
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    warnings = []
    for thread in _as_list(open_threads.get("threads")):
        if not isinstance(thread, dict):
            continue
        if thread.get("status") not in {"open", "advanced"}:
            continue
        last_touched = _numeric(thread.get("last_touched"))
        deadline = _numeric(thread.get("payoff_deadline"))
        if last_touched is None:
            continue
        if last_touched <= start_chapter and (deadline is None or deadline <= end_chapter):
            item = str(thread.get("id") or thread.get("promise") or "thread")
            warnings.append(
                (
                    "stalled_foreshadowing",
                    item,
                    f"last_touched {last_touched:g}; unit ends at chapter {end_chapter}.",
                    "Advance, pay off, or explicitly defer this thread in the next brief.",
                )
            )
    return warnings


def _resource_inflation_warnings(
    resource_ledger: dict[str, Any],
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    warnings = []
    for resource in _as_list(resource_ledger.get("resources")):
        if not isinstance(resource, dict):
            continue
        deltas = [
            entry.get("delta")
            for entry in _as_list(resource.get("history"))
            if isinstance(entry, dict)
            and _numeric(entry.get("chapter")) is not None
            and start_chapter <= _numeric(entry.get("chapter")) <= end_chapter
            and _numeric(entry.get("delta")) is not None
        ]
        positive = [delta for delta in deltas if delta > 0]
        negative = [delta for delta in deltas if delta < 0]
        if len(positive) >= 3 and sum(deltas) > 0 and not negative:
            item = str(resource.get("id") or resource.get("name") or "resource")
            warnings.append(
                (
                    "resource_inflation",
                    item,
                    f"net change +{sum(deltas):g} across {len(positive)} positive entries.",
                    "Add cost, scarcity, tradeoff, or a ledger note explaining why growth is controlled.",
                )
            )
    return warnings


def _protagonist_growth_gap_warnings(
    current_state: dict[str, Any],
    character_states: dict[str, Any],
    start_chapter: int,
    end_chapter: int,
) -> list[tuple[str, str, str, str]]:
    active = [str(character) for character in _as_list(current_state.get("active_characters"))]
    protagonist_id = "chen_an" if "chen_an" in active else active[0] if active else ""
    if not protagonist_id:
        return []
    character = _as_dict(_as_dict(character_states.get("characters")).get(protagonist_id))
    history = [
        entry
        for entry in _as_list(character.get("history"))
        if isinstance(entry, dict)
        and _numeric(entry.get("chapter")) is not None
        and start_chapter <= _numeric(entry.get("chapter")) <= end_chapter
    ]
    if history:
        return []
    return [
        (
            "protagonist_growth_gap",
            protagonist_id,
            f"no character state history entry inside chapters {start_chapter}-{end_chapter}.",
            "Record a concrete agency, relationship, goal, or worldview shift for the protagonist.",
        )
    ]


def _craft_knowledge_checks() -> list[str]:
    cards = load_craft_cards("drift")
    if not cards:
        return []
    lines = [
        "## Craft Knowledge Checks",
        "",
        "| Card | Principle | Checks | Failure Modes |",
        "| --- | --- | --- | --- |",
    ]
    for card in cards:
        checks = "; ".join(str(check) for check in _as_list(card.get("checks")))
        failures = "; ".join(str(mode) for mode in _as_list(card.get("failure_modes")))
        lines.append(
            f"| {_cell(card.get('id', ''))} | {_cell(card.get('principle', ''))} | "
            f"{_cell(checks)} | {_cell(failures)} |"
        )
    lines.append("")
    return lines


def _read_json_if_present(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def _read_yaml_if_present(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = read_yaml(path)
    return data if isinstance(data, dict) else {}


def _numeric(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return value
    return None


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _continuity_risks(root: Path, start_chapter: int, end_chapter: int) -> list[str]:
    lines = [
        "## Continuity Risks",
        "",
        "| Risk | Evidence | Recommended Fix |",
        "| --- | --- | --- |",
    ]
    for chapter_number in range(start_chapter, end_chapter + 1):
        path = root / "reviews" / f"ch_{chapter_number:04d}" / "continuity_review.json"
        if not path.exists():
            continue
        review = read_json(path)
        for issue in review.get("issues", []):
            if issue.get("severity") in {"high", "medium"}:
                lines.append(
                    "| {risk} | {evidence} | {fix} |".format(
                        risk=issue.get("type", ""),
                        evidence=issue.get("evidence", ""),
                        fix=issue.get("suggested_fix", ""),
                    )
                )
    lines.append("")
    return lines


def _pacing_scores(root: Path, start_chapter: int, end_chapter: int) -> list[str]:
    lines = [
        "## Pacing Score Trend",
        "",
        "| Chapter | Initial Score | Revised Score | Waiver |",
        "| --- | --- | --- | --- |",
    ]
    for chapter_number in range(start_chapter, end_chapter + 1):
        review_path = root / "reviews" / f"ch_{chapter_number:04d}" / "pacing_review.json"
        if not review_path.exists():
            continue
        pacing = read_json(review_path)
        packet = read_yaml(
            root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
        )
        waiver = packet.get("quality_gate", {}).get("waiver", {}).get("required", False)
        lines.append(
            f"| {chapter_number} | {pacing.get('score', '')} | "
            f"{pacing.get('revised_score', '') or ''} | {waiver} |"
        )
    lines.append("")
    return lines


def _chapter_recommendation(
    current_state: dict[str, Any],
    timeline: dict[str, Any],
) -> list[str]:
    conflicts = current_state.get("active_conflicts", [])
    events = timeline.get("events", [])
    last_event = events[-1].get("summary", "") if events else ""
    recommendation = (
        "Use the next unit to resolve or advance the active conflicts while preserving "
        "the newest long-arc hook. Latest event: " + last_event
    )
    if conflicts:
        recommendation += " Active conflicts: " + "；".join(conflicts)
    return ["## Chapter 11-20 Recommendation", "", recommendation, ""]
