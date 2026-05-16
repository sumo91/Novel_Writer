from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_text, read_yaml

DIMENSION_SCORE_KEYS = {
    "hook_strength",
    "conflict_clarity",
    "protagonist_agency",
    "emotional_payoff",
    "pacing",
    "character_consistency",
    "continuity_safety",
    "chapter_end_pull",
    "mainline_relevance",
    "fresh_information_or_expectation",
}

REQUIRED_ACCEPTANCE_FIELDS = {
    "chapter",
    "title",
    "source_draft",
    "accepted_chapter_path",
    "summary",
    "current_state",
    "state_changes",
    "open_threads_touched",
    "timeline_event",
    "open_thread_updates",
    "change_log",
}

REQUIRED_CURRENT_STATE_FIELDS = {
    "current_chapter",
    "current_arc",
    "latest_location",
    "active_characters",
    "active_conflicts",
    "pending_approvals",
}

STALE_ACCEPTANCE_PHRASES = {
    "ready_for_acceptance",
    "pending human acceptance",
    "TODO: review",
    "draft_note",
}


def validate_review_files(root: Path, chapter_number: int) -> list[str]:
    chapter_slug = f"ch_{chapter_number:04d}"
    review_dir = root / "reviews" / chapter_slug
    errors: list[str] = []

    continuity_path = review_dir / "continuity_review.json"
    if continuity_path.exists():
        errors.extend(
            f"{continuity_path.relative_to(root).as_posix()}: {error}"
            for error in validate_continuity_review(read_json(continuity_path))
        )

    pacing_path = review_dir / "pacing_review.json"
    if pacing_path.exists():
        errors.extend(
            f"{pacing_path.relative_to(root).as_posix()}: {error}"
            for error in validate_pacing_review(read_json(pacing_path))
        )

    return errors


def validate_continuity_review(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(review.get("passed"), bool):
        errors.append("Continuity review field 'passed' must be boolean.")
    score = review.get("score")
    if score is not None and not _score_in_range(score, 0, 100):
        errors.append("Continuity review score must be an integer from 0 to 100.")
    for list_field in (
        "issues",
        "required_fixes",
        "proposed_state_updates",
        "human_approval_needed",
    ):
        if list_field in review and not isinstance(review[list_field], list):
            errors.append(f"Continuity review field '{list_field}' must be a list.")
    return errors


def validate_pacing_review(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not _score_in_range(review.get("score"), 0, 100):
        errors.append("Pacing review score must be an integer from 0 to 100.")

    revised_score = review.get("revised_score")
    if revised_score is not None and not _score_in_range(revised_score, 0, 100):
        errors.append("Pacing review revised_score must be an integer from 0 to 100.")

    dimension_scores = review.get("dimension_scores")
    if not isinstance(dimension_scores, dict):
        errors.append("Pacing review is missing dimension_scores.")
        return errors

    missing = sorted(DIMENSION_SCORE_KEYS.difference(dimension_scores))
    if missing:
        errors.append(f"Pacing review is missing dimension scores: {', '.join(missing)}.")

    invalid = [
        key
        for key in sorted(DIMENSION_SCORE_KEYS.intersection(dimension_scores))
        if not _score_in_range(dimension_scores.get(key), 0, 10)
    ]
    if invalid:
        errors.append(f"Pacing review has invalid dimension scores: {', '.join(invalid)}.")

    return errors


def validate_acceptance_packet_file(root: Path, chapter_number: int) -> list[str]:
    packet_path = root / "state_updates" / f"ch_{chapter_number:04d}_acceptance.yaml"
    if not packet_path.exists():
        return []

    packet = read_yaml(packet_path)
    errors = validate_acceptance_packet(packet, chapter_number)
    stale = stale_acceptance_text_errors(packet_path)
    relative_path = packet_path.relative_to(root).as_posix()
    return [f"{relative_path}: {error}" for error in errors + stale]


def validate_pending_approvals_registry(root: Path) -> list[str]:
    registry_path = root / "state" / "pending_approvals.yaml"
    if not registry_path.exists():
        return []
    registry = read_yaml(registry_path)
    approvals = registry.get("approvals")
    if not isinstance(approvals, list):
        return ["state/pending_approvals.yaml: approvals must be a list."]

    errors: list[str] = []
    seen_ids = set()
    for index, approval in enumerate(approvals, start=1):
        prefix = f"state/pending_approvals.yaml: approvals[{index}]"
        if not isinstance(approval, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        approval_id = approval.get("id")
        if not isinstance(approval_id, str) or not approval_id.startswith("pa_"):
            errors.append(f"{prefix}.id must be a pa_ identifier.")
        elif approval_id in seen_ids:
            errors.append(f"{prefix}.id is duplicated: {approval_id}.")
        else:
            seen_ids.add(approval_id)
        if approval.get("status") not in {"open", "approved", "rejected", "deferred"}:
            errors.append(f"{prefix}.status must be open, approved, rejected, or deferred.")
        if not approval.get("text"):
            errors.append(f"{prefix}.text is required.")
        for list_field in ("source_chapters", "variants", "sources"):
            if not isinstance(approval.get(list_field), list):
                errors.append(f"{prefix}.{list_field} must be a list.")
    return errors


def validate_acceptance_packet(
    packet: dict[str, Any],
    chapter_number: int | None = None,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_ACCEPTANCE_FIELDS if field not in packet)
    if missing:
        errors.append(f"Acceptance packet is missing fields: {', '.join(missing)}.")

    if chapter_number is not None and packet.get("chapter") != chapter_number:
        errors.append(f"Acceptance packet chapter must be {chapter_number}.")

    current_state = packet.get("current_state")
    if isinstance(current_state, dict):
        missing_state = sorted(
            field for field in REQUIRED_CURRENT_STATE_FIELDS if field not in current_state
        )
        if missing_state:
            errors.append(
                "Acceptance packet current_state is missing fields: "
                + ", ".join(missing_state)
                + "."
            )
    elif "current_state" in packet:
        errors.append("Acceptance packet current_state must be a mapping.")

    timeline_event = packet.get("timeline_event")
    if isinstance(timeline_event, dict):
        for field in ("id", "when", "summary"):
            if not timeline_event.get(field):
                errors.append(f"Acceptance packet timeline_event.{field} is required.")
    elif "timeline_event" in packet:
        errors.append("Acceptance packet timeline_event must be a mapping.")

    change_log = packet.get("change_log")
    if isinstance(change_log, dict):
        if not change_log.get("summary"):
            errors.append("Acceptance packet change_log.summary is required.")
        if "canon_updates" in change_log and not isinstance(
            change_log["canon_updates"], list
        ):
            errors.append("Acceptance packet change_log.canon_updates must be a list.")
        if "pending_approvals" in change_log and not isinstance(
            change_log["pending_approvals"], list
        ):
            errors.append("Acceptance packet change_log.pending_approvals must be a list.")
    elif "change_log" in packet:
        errors.append("Acceptance packet change_log must be a mapping.")

    for list_field in ("state_changes", "open_threads_touched", "open_thread_updates"):
        if list_field in packet and not isinstance(packet[list_field], list):
            errors.append(f"Acceptance packet {list_field} must be a list.")

    return errors


def stale_acceptance_text_errors(path: Path) -> list[str]:
    content = read_text(path)
    lowered = content.lower()
    return [
        f"Acceptance packet contains stale text: {phrase}."
        for phrase in sorted(STALE_ACCEPTANCE_PHRASES)
        if phrase.lower() in lowered
    ]


def _score_in_range(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and low <= value <= high
