from pathlib import Path
from typing import Any

import yaml

from engine.io_utils import read_json, read_text, read_yaml
from engine.outline_gate import validate_chapter_brief_text

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
APPROVAL_STATUSES = {"draft", "approved", "rejected", "superseded"}

MASTER_OUTLINE_REQUIRED_FIELDS = {
    "logline",
    "story_promise",
    "opening_state",
    "ending_state",
    "three_act_structure",
    "protagonist_growth_curve",
    "core_mystery",
    "core_rules_locked",
    "volume_plan",
    "major_turning_points",
    "ending_direction",
    "approval",
}

VOLUME_REQUIRED_FIELDS = {
    "volume_id",
    "title",
    "chapter_range",
    "volume_goal",
    "reader_promise",
    "main_pressure",
    "protagonist_progress",
    "core_payoffs",
    "major_reveal",
    "volume_climax",
    "ending_hook",
    "required_threads",
    "approval",
}

ARC_REQUIRED_FIELDS = {
    "arc_id",
    "title",
    "chapter_range",
    "parent_volume",
    "arc_goal",
    "main_conflict",
    "stage_enemy_or_pressure",
    "protagonist_move",
    "required_payoffs",
    "required_threads",
    "major_reveal_or_reversal",
    "exit_state",
    "chapters",
    "approval",
}

UNIT_REQUIRED_FIELDS = {
    "unit",
    "chapter_range",
    "parent_arc",
    "unit_goal",
    "stage_enemy",
    "stage_payoffs",
    "stage_end_hook",
    "required_threads",
    "chapters",
    "approval",
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
    "acceptance_contract",
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

REQUIRED_ACCEPTANCE_CONTRACT_FIELDS = {
    "quality_gate_summary",
    "outline_alignment",
    "state_updates",
}

REQUIRED_QUALITY_GATE_SUMMARY_FIELDS = {
    "continuity_review_present",
    "continuity_blockers",
    "pacing_review_present",
    "pacing_score",
    "revised_pacing_score",
    "revision_required",
    "waiver_required",
}

REQUIRED_OUTLINE_ALIGNMENT_FIELDS = {
    "reference_chain",
    "volume_id",
    "arc_id",
    "unit_id",
    "required_unit_obligations",
    "claimed_fulfilled_unit_obligations",
    "pending_unit_obligations",
}

REQUIRED_ACCEPTANCE_STATE_FIELDS = {
    "timeline_event",
    "character_state_changes",
    "resource_changes",
    "open_thread_updates",
    "payoff_updates",
    "next_hook",
    "pending_approvals",
    "economy_changes",
    "faction_changes",
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

    acceptance_contract = packet.get("acceptance_contract")
    if isinstance(acceptance_contract, dict):
        missing_contract = sorted(
            field
            for field in REQUIRED_ACCEPTANCE_CONTRACT_FIELDS
            if field not in acceptance_contract
        )
        if missing_contract:
            errors.append(
                "Acceptance packet acceptance_contract is missing fields: "
                + ", ".join(missing_contract)
                + "."
            )
        errors.extend(validate_acceptance_contract(acceptance_contract, packet))
    elif "acceptance_contract" in packet:
        errors.append("Acceptance packet acceptance_contract must be a mapping.")

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


def validate_acceptance_contract(
    contract: dict[str, Any],
    packet: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not contract:
        errors.append(
            "Acceptance packet acceptance_contract is missing fields: "
            + ", ".join(sorted(REQUIRED_ACCEPTANCE_CONTRACT_FIELDS))
            + "."
        )
        return errors

    quality_gate_summary = contract.get("quality_gate_summary", {})
    if "quality_gate_summary" in contract and not isinstance(quality_gate_summary, dict):
        errors.append("acceptance_contract.quality_gate_summary must be a mapping.")
    elif isinstance(quality_gate_summary, dict):
        missing_quality = sorted(
            field
            for field in REQUIRED_QUALITY_GATE_SUMMARY_FIELDS
            if field not in quality_gate_summary
        )
        if missing_quality:
            errors.append(
                "acceptance_contract.quality_gate_summary is missing fields: "
                + ", ".join(missing_quality)
                + "."
            )
        for field in ("continuity_review_present", "pacing_review_present", "revision_required", "waiver_required"):
            if field in quality_gate_summary and not isinstance(quality_gate_summary[field], bool):
                errors.append(f"acceptance_contract.quality_gate_summary.{field} must be a bool.")
        for field in ("continuity_blockers",):
            if field in quality_gate_summary and not isinstance(quality_gate_summary[field], list):
                errors.append(f"acceptance_contract.quality_gate_summary.{field} must be a list.")
        for field in ("pacing_score", "revised_pacing_score"):
            value = quality_gate_summary.get(field)
            if value is not None and not _score_in_range(value, 0, 100):
                errors.append(
                    f"acceptance_contract.quality_gate_summary.{field} must be an integer from 0 to 100."
                )

    outline_alignment = contract.get("outline_alignment", {})
    if "outline_alignment" in contract and not isinstance(outline_alignment, dict):
        errors.append("acceptance_contract.outline_alignment must be a mapping.")
    elif isinstance(outline_alignment, dict):
        missing_outline = sorted(
            field
            for field in REQUIRED_OUTLINE_ALIGNMENT_FIELDS
            if field not in outline_alignment
        )
        if missing_outline:
            errors.append(
                "acceptance_contract.outline_alignment is missing fields: "
                + ", ".join(missing_outline)
                + "."
            )
        for field in (
            "required_unit_obligations",
            "claimed_fulfilled_unit_obligations",
            "pending_unit_obligations",
        ):
            if field in outline_alignment and not isinstance(outline_alignment[field], list):
                errors.append(f"acceptance_contract.outline_alignment.{field} must be a list.")

    state_updates = contract.get("state_updates", {})
    if "state_updates" in contract and not isinstance(state_updates, dict):
        errors.append("acceptance_contract.state_updates must be a mapping.")
    elif isinstance(state_updates, dict):
        missing_state = sorted(
            field
            for field in REQUIRED_ACCEPTANCE_STATE_FIELDS
            if field not in state_updates
        )
        if missing_state:
            errors.append(
                "acceptance_contract.state_updates is missing fields: "
                + ", ".join(missing_state)
                + "."
            )
        for field in (
            "character_state_changes",
            "resource_changes",
            "open_thread_updates",
            "payoff_updates",
            "pending_approvals",
            "economy_changes",
            "faction_changes",
        ):
            if field in state_updates and not isinstance(state_updates[field], list):
                errors.append(f"acceptance_contract.state_updates.{field} must be a list.")
        timeline_event = state_updates.get("timeline_event")
        if "timeline_event" in state_updates and not isinstance(timeline_event, dict):
            errors.append("acceptance_contract.state_updates.timeline_event must be a mapping.")
        next_hook = state_updates.get("next_hook")
        if next_hook not in ({}, None) and not isinstance(next_hook, dict):
            errors.append("acceptance_contract.state_updates.next_hook must be a mapping.")

        if packet is not None and isinstance(packet.get("v3_state_updates"), dict):
            errors.extend(
                _validate_acceptance_contract_state_update_mirror(
                    state_updates,
                    packet["v3_state_updates"],
                )
            )

    return errors


def _validate_acceptance_contract_state_update_mirror(
    state_updates: dict[str, Any],
    v3_updates: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    mirrors = {
        "character_state_changes": "character_states",
        "resource_changes": "resource_changes",
        "open_thread_updates": "open_thread_updates",
        "payoff_updates": "payoff_updates",
        "next_hook": "next_hook",
        "pending_approvals": "pending_approvals",
    }
    for contract_field, v3_field in mirrors.items():
        if state_updates.get(contract_field) != v3_updates.get(v3_field):
            errors.append(
                f"acceptance_contract.state_updates.{contract_field} must mirror "
                f"v3_state_updates.{v3_field}."
            )
    return errors


def validate_acceptance_contract_snapshot(
    root: Path,
    packet: dict[str, Any],
    chapter_number: int | None = None,
) -> list[str]:
    contract = packet.get("acceptance_contract")
    if not isinstance(contract, dict):
        return []

    expected = _build_acceptance_contract_snapshot(root, packet, chapter_number)
    if contract != expected:
        return ["Acceptance packet acceptance_contract snapshot does not match source state."]
    return []


def _build_acceptance_contract_snapshot(
    root: Path,
    packet: dict[str, Any],
    chapter_number: int | None,
) -> dict[str, Any]:
    chapter = chapter_number if chapter_number is not None else int(packet.get("chapter", 0))
    review_dir = root / "reviews" / f"ch_{chapter:04d}"
    continuity_path = review_dir / "continuity_review.json"
    pacing_path = review_dir / "pacing_review.json"
    continuity = read_json(continuity_path) if continuity_path.exists() else {}
    pacing = read_json(pacing_path) if pacing_path.exists() else {}
    volume = read_yaml(root / "outlines" / "volumes" / "volume_001.yaml")
    arc = read_yaml(root / "outlines" / "arc_001.yaml")
    unit = read_yaml(root / "outlines" / "units" / "unit_0001.yaml")
    unit_chapter = _unit_chapter(unit, chapter)
    required_obligations = list(unit_chapter.get("state_obligation", []))
    current_state = packet.get("current_state", {})
    v3_updates = packet.get("v3_state_updates", {})
    timeline_event = packet.get("timeline_event", {})

    return {
        "quality_gate_summary": {
            "continuity_review_present": continuity_path.exists(),
            "continuity_blockers": list(continuity.get("required_fixes", [])),
            "pacing_review_present": pacing_path.exists(),
            "pacing_score": pacing.get("score"),
            "revised_pacing_score": pacing.get("revised_score"),
            "revision_required": bool(continuity.get("required_fixes"))
            or not isinstance(pacing.get("score"), int)
            or pacing.get("score", 0) < 80,
            "waiver_required": bool(
                isinstance(pacing.get("revised_score"), int)
                and pacing.get("revised_score") < 80
            ),
        },
        "outline_alignment": {
            "reference_chain": "master -> volume -> arc -> unit -> chapter brief",
            "volume_id": volume.get("volume_id", "volume_001"),
            "arc_id": arc.get("arc_id", "arc_001"),
            "unit_id": f"unit_{int(unit.get('unit', 1)):04d}"
            if isinstance(unit.get("unit"), int)
            else str(unit.get("unit", "unit_0001")),
            "required_unit_obligations": required_obligations,
            "claimed_fulfilled_unit_obligations": list(required_obligations),
            "pending_unit_obligations": [],
        },
        "state_updates": {
            "timeline_event": {
                "id": timeline_event.get("id"),
                "when": timeline_event.get("when"),
                "summary": timeline_event.get("summary"),
            },
            "character_state_changes": list(v3_updates.get("character_states", [])),
            "resource_changes": list(v3_updates.get("resource_changes", [])),
            "open_thread_updates": list(v3_updates.get("open_thread_updates", [])),
            "payoff_updates": list(v3_updates.get("payoff_updates", [])),
            "next_hook": dict(v3_updates.get("next_hook", {})),
            "pending_approvals": list(current_state.get("pending_approvals", [])),
            "economy_changes": [],
            "faction_changes": [],
        },
    }


def _unit_chapter(unit: dict[str, Any], chapter_number: int) -> dict[str, Any]:
    for chapter in unit.get("chapters", []):
        if isinstance(chapter, dict) and chapter.get("chapter") == chapter_number:
            return chapter
    return {}


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
    data = _read_yaml_root(path)
    if not isinstance(data, dict):
        return ["canon/open_threads.yaml: root must be a mapping."]
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
    data = _read_yaml_root(path)
    if not isinstance(data, dict):
        return ["canon/payoff_ledger.yaml: root must be a mapping."]
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
    data = _read_yaml_root(path)
    if not isinstance(data, dict):
        return ["canon/character_states.yaml: root must be a mapping."]
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
    data = _read_yaml_root(path)
    if not isinstance(data, dict):
        return ["canon/resource_ledger.yaml: root must be a mapping."]
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
    if not isinstance(data, dict):
        return ["state/hook_index.json: root must be a mapping."]
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
    if not isinstance(data, dict):
        return ["state/memory_index.json: root must be a mapping."]

    errors: list[str] = []
    for field in ("by_character", "by_thread", "by_location", "by_resource"):
        if not isinstance(data.get(field), dict):
            errors.append(f"state/memory_index.json: {field} must be a mapping.")
    return errors


def validate_v3_1_outline_architecture(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_master_outline(root))
    errors.extend(validate_volume_outline(root / "outlines" / "volumes" / "volume_001.yaml"))
    errors.extend(validate_arc_outline(root))
    errors.extend(validate_unit_outline(root))
    errors.extend(validate_economy(root))
    errors.extend(validate_factions(root))
    errors.extend(validate_chapter_briefs(root))
    return errors


def validate_chapter_briefs(root: Path) -> list[str]:
    brief_dir = root / "outlines" / "chapter_briefs"
    if not brief_dir.exists():
        return []

    errors: list[str] = []
    for path in sorted(brief_dir.glob("ch_*_brief.md")):
        relative_path = path.relative_to(root).as_posix()
        errors.extend(
            f"{relative_path}: {error}"
            for error in validate_chapter_brief_text(read_text(path))
        )
    return errors


def validate_master_outline(root: Path) -> list[str]:
    relative_path = "outlines/master_outline.yaml"
    data = _read_mapping_file(root / relative_path, relative_path)
    if not isinstance(data, dict):
        return data

    errors = _missing_required_field_errors(relative_path, data, MASTER_OUTLINE_REQUIRED_FIELDS)
    errors.extend(_validate_approval_block(relative_path, data))
    return errors


def validate_volume_outline(path: Path) -> list[str]:
    relative_path = "outlines/volumes/volume_001.yaml"
    data = _read_mapping_file(path, relative_path)
    if not isinstance(data, dict):
        return data

    errors = _missing_required_field_errors(relative_path, data, VOLUME_REQUIRED_FIELDS)
    errors.extend(_validate_approval_block(relative_path, data))
    errors.extend(_validate_chapter_range(relative_path, data.get("chapter_range")))
    return errors


def validate_arc_outline(root: Path) -> list[str]:
    relative_path = "outlines/arc_001.yaml"
    data = _read_mapping_file(root / relative_path, relative_path)
    if not isinstance(data, dict):
        return data

    errors = _missing_required_field_errors(relative_path, data, ARC_REQUIRED_FIELDS)
    errors.extend(_validate_approval_block(relative_path, data))
    errors.extend(_validate_chapter_range(relative_path, data.get("chapter_range")))
    parent_volume = data.get("parent_volume")
    if parent_volume and not (root / "outlines" / "volumes" / f"{parent_volume}.yaml").exists():
        errors.append(f"{relative_path}: parent_volume {parent_volume} does not exist.")
    return errors


def validate_unit_outline(root: Path) -> list[str]:
    relative_path = "outlines/units/unit_0001.yaml"
    data = _read_mapping_file(root / relative_path, relative_path)
    if not isinstance(data, dict):
        return data

    errors = _missing_required_field_errors(relative_path, data, UNIT_REQUIRED_FIELDS)
    errors.extend(_validate_approval_block(relative_path, data))
    errors.extend(_validate_chapter_range(relative_path, data.get("chapter_range")))
    parent_arc = data.get("parent_arc")
    if parent_arc and not (root / "outlines" / f"{parent_arc}.yaml").exists():
        errors.append(f"{relative_path}: parent_arc {parent_arc} does not exist.")

    chapter_range = data.get("chapter_range")
    start = chapter_range.get("start") if isinstance(chapter_range, dict) else None
    end = chapter_range.get("end") if isinstance(chapter_range, dict) else None
    chapters = data.get("chapters")
    if isinstance(chapters, list):
        for index, chapter in enumerate(chapters, start=1):
            if not isinstance(chapter, dict):
                errors.append(f"{relative_path}: chapters[{index}] must be a mapping.")
                continue
            chapter_number = chapter.get("chapter")
            if isinstance(start, int) and isinstance(end, int):
                if not isinstance(chapter_number, int) or not start <= chapter_number <= end:
                    errors.append(
                        f"{relative_path}: chapters[{index}].chapter must fit inside chapter_range."
                    )
    elif "chapters" in data:
        errors.append(f"{relative_path}: chapters must be a list.")
    return errors


def validate_economy(root: Path) -> list[str]:
    relative_path = "canon/economy.yaml"
    data = _read_mapping_file(root / relative_path, relative_path)
    if not isinstance(data, dict):
        return data

    errors: list[str] = []
    for field in ("currencies", "price_index", "trade_rules", "locked_constraints"):
        if not isinstance(data.get(field), list):
            errors.append(f"{relative_path}: {field} must be a list.")
    if not isinstance(data.get("real_world_money"), dict):
        errors.append(f"{relative_path}: real_world_money must be a mapping.")
    errors.extend(_validate_approval_block(relative_path, data))
    return errors


def validate_factions(root: Path) -> list[str]:
    relative_path = "canon/factions.yaml"
    data = _read_mapping_file(root / relative_path, relative_path)
    if not isinstance(data, dict):
        return data

    errors: list[str] = []
    if not isinstance(data.get("factions"), list):
        errors.append(f"{relative_path}: factions must be a list.")
    errors.extend(_validate_approval_block(relative_path, data))
    return errors


def _read_mapping_file(path: Path, relative_path: str) -> dict[str, Any] | list[str]:
    if not path.exists():
        return []
    data = _read_yaml_root(path)
    if not isinstance(data, dict):
        return [f"{relative_path}: root must be a mapping."]
    return data


def _missing_required_field_errors(
    relative_path: str,
    data: dict[str, Any],
    required_fields: set[str],
) -> list[str]:
    return [
        f"{relative_path}: missing required field {field}."
        for field in sorted(required_fields)
        if field not in data
    ]


def _validate_approval_block(relative_path: str, data: dict[str, Any]) -> list[str]:
    approval = data.get("approval")
    if not isinstance(approval, dict):
        return [f"{relative_path}: approval must be a mapping."]
    if approval.get("status") not in APPROVAL_STATUSES:
        return [
            f"{relative_path}: approval.status must be draft, approved, rejected, or superseded."
        ]
    return []


def _validate_chapter_range(relative_path: str, chapter_range: Any) -> list[str]:
    if not isinstance(chapter_range, dict):
        return [f"{relative_path}: chapter_range must be a mapping."]
    errors: list[str] = []
    for field in ("start", "end"):
        if not isinstance(chapter_range.get(field), int):
            errors.append(f"{relative_path}: chapter_range.{field} must be an integer.")
    start = chapter_range.get("start")
    end = chapter_range.get("end")
    if isinstance(start, int) and isinstance(end, int) and start > end:
        errors.append(f"{relative_path}: chapter_range.start must be <= end.")
    return errors


def _read_yaml_root(path: Path) -> Any:
    return yaml.safe_load(read_text(path))


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
