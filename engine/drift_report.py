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

