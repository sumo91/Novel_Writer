import json
from pathlib import Path
from typing import Any

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
