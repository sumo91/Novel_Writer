from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_text, read_yaml

OPEN_THREAD_STATUSES = {"open", "advanced", "paid_off", "deferred", "dropped"}
HOOK_STATUSES = {"open", "answered", "deferred", "dropped"}
FRUSTRATION_LEVELS = {"low", "controlled", "high", "overdue"}
RESOURCE_CATEGORIES = {
    "money",
    "item",
    "trade_good",
    "power",
    "debt",
    "relationship_asset",
    "knowledge",
}

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
    "v3_state_updates",
}

REQUIRED_CURRENT_STATE_FIELDS = {
    "current_chapter",
    "current_arc",
    "latest_location",
    "active_characters",
    "active_conflicts",
    "pending_approvals",
}

REQUIRED_V3_STATE_UPDATE_FIELDS = {
    "timeline",
    "character_states",
    "resource_changes",
    "open_thread_updates",
    "payoff_updates",
    "conflict_updates",
    "next_hook",
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

    v3_updates = packet.get("v3_state_updates")
    if isinstance(v3_updates, dict):
        missing_v3 = sorted(
            field for field in REQUIRED_V3_STATE_UPDATE_FIELDS if field not in v3_updates
        )
        if missing_v3:
            errors.append(
                "Acceptance packet v3_state_updates is missing fields: "
                + ", ".join(missing_v3)
                + "."
            )
        errors.extend(validate_v3_state_updates(v3_updates))
    elif "v3_state_updates" in packet:
        errors.append("Acceptance packet v3_state_updates must be a mapping.")

    return errors


def validate_v3_state_updates(updates: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for list_field in (
        "character_states",
        "resource_changes",
        "open_thread_updates",
        "payoff_updates",
        "pending_approvals",
    ):
        if list_field in updates and not isinstance(updates[list_field], list):
            errors.append(f"v3_state_updates.{list_field} must be a list.")

    timeline = updates.get("timeline", {})
    if "timeline" in updates and not isinstance(timeline, dict):
        errors.append("v3_state_updates.timeline must be a mapping.")
    elif isinstance(timeline, dict) and not isinstance(timeline.get("occurred_events", []), list):
        errors.append("v3_state_updates.timeline.occurred_events must be a list.")

    conflict_updates = updates.get("conflict_updates", {})
    if "conflict_updates" in updates and not isinstance(conflict_updates, dict):
        errors.append("v3_state_updates.conflict_updates must be a mapping.")
    elif isinstance(conflict_updates, dict) and "active" in conflict_updates:
        if not isinstance(conflict_updates["active"], list):
            errors.append("v3_state_updates.conflict_updates.active must be a list.")

    open_thread_updates = updates.get("open_thread_updates", [])
    if isinstance(open_thread_updates, list):
        for thread in open_thread_updates:
            if not isinstance(thread, dict):
                errors.append("v3_state_updates.open_thread_updates items must be mappings.")
                continue
            if thread.get("status") not in OPEN_THREAD_STATUSES:
                errors.append("v3_state_updates.open_thread_updates.status is invalid.")
            for field in ("id", "promise", "source_chapter", "last_touched"):
                if field not in thread or thread[field] in (None, ""):
                    errors.append(f"v3_state_updates.open_thread_updates.{field} is required.")

    payoff_updates = updates.get("payoff_updates", [])
    if isinstance(payoff_updates, list):
        for payoff in payoff_updates:
            if not isinstance(payoff, dict):
                errors.append("v3_state_updates.payoff_updates items must be mappings.")
                continue
            if payoff.get("frustration_level") not in FRUSTRATION_LEVELS:
                errors.append("v3_state_updates.payoff_updates.frustration_level is invalid.")
            if not payoff.get("promises_made") and not payoff.get("payoffs_delivered"):
                errors.append("v3_state_updates.payoff_updates needs a promise or payoff.")

    next_hook = updates.get("next_hook")
    if next_hook not in ({}, None) and not isinstance(next_hook, dict):
        errors.append("v3_state_updates.next_hook must be a mapping.")

    return errors


def validate_v3_ledgers(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_open_threads_ledger(root))
    errors.extend(validate_payoff_ledger(root))
    errors.extend(validate_character_states_ledger(root))
    errors.extend(validate_resource_ledger(root))
    errors.extend(validate_hook_index(root))
    errors.extend(validate_memory_index(root))
    return errors


def validate_open_threads_ledger(root: Path) -> list[str]:
    path = root / "canon" / "open_threads.yaml"
    if not path.exists():
        return []
    data = read_yaml(path)
    threads = data.get("threads")
    if not isinstance(threads, list):
        return ["canon/open_threads.yaml: threads must be a list."]

    errors: list[str] = []
    for index, thread in enumerate(threads, start=1):
        prefix = f"canon/open_threads.yaml: threads[{index}]"
        if not isinstance(thread, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        for field in ("id", "promise", "source_chapter", "status", "last_touched"):
            if field not in thread or thread[field] in (None, ""):
                errors.append(f"{prefix}.{field} is required.")
        if thread.get("status") not in OPEN_THREAD_STATUSES:
            errors.append(f"{prefix}.status must be one of {sorted(OPEN_THREAD_STATUSES)}.")
    return errors


def validate_payoff_ledger(root: Path) -> list[str]:
    path = root / "canon" / "payoff_ledger.yaml"
    if not path.exists():
        return []
    data = read_yaml(path)
    entries = data.get("entries")
    if not isinstance(entries, list):
        return ["canon/payoff_ledger.yaml: entries must be a list."]

    errors: list[str] = []
    for index, entry in enumerate(entries, start=1):
        prefix = f"canon/payoff_ledger.yaml: entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        frustration_level = entry.get("frustration_level")
        if frustration_level is not None and frustration_level not in FRUSTRATION_LEVELS:
            errors.append(f"{prefix}.frustration_level must be one of {sorted(FRUSTRATION_LEVELS)}.")
        if not entry.get("promises_made") and not entry.get("payoffs_delivered"):
            errors.append(f"{prefix} needs at least one promise or payoff.")
    return errors


def validate_character_states_ledger(root: Path) -> list[str]:
    path = root / "canon" / "character_states.yaml"
    if not path.exists():
        return []
    data = read_yaml(path)
    characters = data.get("characters")
    if not isinstance(characters, dict):
        return ["canon/character_states.yaml: characters must be a mapping."]

    errors: list[str] = []
    for character_id, state in characters.items():
        prefix = f"canon/character_states.yaml: characters.{character_id}"
        if not isinstance(state, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        if state and state.get("last_updated_chapter") in (None, ""):
            errors.append(f"{prefix}.last_updated_chapter is required.")
    return errors


def validate_resource_ledger(root: Path) -> list[str]:
    path = root / "canon" / "resource_ledger.yaml"
    if not path.exists():
        return []
    data = read_yaml(path)
    resources = data.get("resources")
    if not isinstance(resources, list):
        return ["canon/resource_ledger.yaml: resources must be a list."]

    errors: list[str] = []
    for index, resource in enumerate(resources, start=1):
        prefix = f"canon/resource_ledger.yaml: resources[{index}]"
        if not isinstance(resource, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        for field in ("id", "owner", "name", "category", "last_updated_chapter"):
            if field not in resource or resource[field] in (None, ""):
                errors.append(f"{prefix}.{field} is required.")
        if resource.get("category") not in RESOURCE_CATEGORIES:
            errors.append(f"{prefix}.category must be one of {sorted(RESOURCE_CATEGORIES)}.")
    return errors


def validate_hook_index(root: Path) -> list[str]:
    path = root / "state" / "hook_index.json"
    if not path.exists():
        return []
    data = read_json(path)
    hooks = data.get("hooks")
    if not isinstance(hooks, list):
        return ["state/hook_index.json: hooks must be a list."]

    errors: list[str] = []
    for index, hook in enumerate(hooks, start=1):
        prefix = f"state/hook_index.json: hooks[{index}]"
        if not isinstance(hook, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        status = hook.get("status")
        if status is not None and status not in HOOK_STATUSES:
            errors.append(f"{prefix}.status must be one of {sorted(HOOK_STATUSES)}.")
    return errors


def validate_memory_index(root: Path) -> list[str]:
    path = root / "state" / "memory_index.json"
    if not path.exists():
        return []
    data = read_json(path)

    errors: list[str] = []
    for field in ("by_character", "by_thread", "by_location", "by_resource"):
        if not isinstance(data.get(field), dict):
            errors.append(f"state/memory_index.json: {field} must be a mapping.")
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
