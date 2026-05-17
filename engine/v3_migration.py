import copy
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.io_utils import read_yaml, write_yaml
from engine.hardening import OPEN_THREAD_STATUSES
from engine.paths import books_dir, project_root

TEMPLATE_DIR = project_root() / "engine" / "templates" / "book"
BOOKS_DIR = books_dir()

V3_TEMPLATE_PATHS = [
    "canon/character_states.yaml",
    "canon/resource_ledger.yaml",
    "canon/payoff_ledger.yaml",
    "outlines/units/unit_0001.yaml",
    "state/hook_index.json",
    "state/memory_index.json",
]

V3_1_TEMPLATE_PATHS = [
    "outlines/volumes/volume_001.yaml",
    "canon/economy.yaml",
    "canon/factions.yaml",
]

OPEN_THREAD_DEFAULTS = {
    "source_chapter": 0,
    "status": "open",
    "last_touched": 0,
    "next_obligation": "Legacy migration needs human review.",
    "payoff_deadline": "",
    "risk_if_ignored": "Legacy migration needs human review.",
    "related_characters": [],
    "related_locations": [],
    "payoff_chapter": "",
    "notes": [],
}


@dataclass(frozen=True)
class V3MigrationResult:
    book_id: str
    created: list[str]
    updated: list[str]


def migrate_book_to_v3(book_id: str) -> V3MigrationResult:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    created = _copy_missing_v3_templates(root)
    updated = _upgrade_open_threads(root)
    updated.extend(_upgrade_acceptance_packets(root))
    return V3MigrationResult(book_id=book_id, created=created, updated=updated)


def migrate_book_to_v3_1(book_id: str) -> V3MigrationResult:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    created = _copy_missing_templates(root, V3_1_TEMPLATE_PATHS)
    updated = []
    updated.extend(_upgrade_mapping_from_template(root, "outlines/master_outline.yaml"))
    updated.extend(_upgrade_mapping_from_template(root, "outlines/arc_001.yaml"))
    updated.extend(_upgrade_mapping_from_template(root, "outlines/units/unit_0001.yaml"))
    return V3MigrationResult(book_id=book_id, created=created, updated=updated)


def _copy_missing_v3_templates(root):
    return _copy_missing_templates(root, V3_TEMPLATE_PATHS)


def _copy_missing_templates(root: Path, relative_paths: list[str]) -> list[str]:
    created = []
    for relative_path in relative_paths:
        target = root / relative_path
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATE_DIR / relative_path, target)
        created.append(relative_path)
    return created


def _upgrade_mapping_from_template(root: Path, relative_path: str) -> list[str]:
    path = root / relative_path
    template_path = TEMPLATE_DIR / relative_path
    if not path.exists() or not template_path.exists():
        return []

    data = read_yaml(path)
    template = read_yaml(template_path)
    if not isinstance(data, dict) or not isinstance(template, dict):
        return []

    merged = _merge_missing_mapping_keys(data, template)
    if merged == data:
        return []

    write_yaml(path, merged)
    return [relative_path]


def _merge_missing_mapping_keys(
    data: dict[str, Any],
    template: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(data)
    for key, value in template.items():
        if key not in merged:
            merged[key] = value
            continue
        if isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_missing_mapping_keys(merged[key], value)
    return merged


def _upgrade_open_threads(root):
    relative_path = "canon/open_threads.yaml"
    path = root / relative_path
    if not path.exists():
        return []

    data = read_yaml(path)
    threads = data.get("threads")
    if not isinstance(threads, list):
        return []

    changed = False
    for thread in threads:
        if not isinstance(thread, dict):
            continue
        if thread.get("status") not in OPEN_THREAD_STATUSES:
            thread["status"] = "open"
            changed = True
        if not thread.get("promise"):
            thread["promise"] = _legacy_thread_promise(thread)
            changed = True
        for key, default in OPEN_THREAD_DEFAULTS.items():
            if key not in thread or thread[key] in (None, ""):
                thread[key] = list(default) if isinstance(default, list) else default
                changed = True

    if not changed:
        return []

    write_yaml(path, data)
    return [relative_path]


def _upgrade_acceptance_packets(root: Path) -> list[str]:
    state_updates_dir = root / "state_updates"
    if not state_updates_dir.exists():
        return []

    updated = []
    for path in sorted(state_updates_dir.glob("ch_????_acceptance.yaml")):
        packet = read_yaml(path)
        if not isinstance(packet, dict):
            continue
        changed = False
        chapter = packet.get("chapter")
        current_state = packet.get("current_state")
        if isinstance(current_state, dict) and current_state.get("current_chapter") in (None, ""):
            current_state["current_chapter"] = chapter
            changed = True
        if "v3_state_updates" not in packet:
            packet["v3_state_updates"] = _minimal_v3_state_updates(
                chapter,
                packet.get("summary", ""),
                _pending_approvals_from_packet(packet),
            )
            changed = True
        if "acceptance_contract" not in packet:
            packet["acceptance_contract"] = _minimal_acceptance_contract(
                root,
                chapter,
                packet.get("summary", ""),
                _pending_approvals_from_packet(packet),
            )
            changed = True
        if _sync_acceptance_contract_state_updates(packet):
            changed = True
        if changed:
            write_yaml(path, packet)
            updated.append(path.relative_to(root).as_posix())
    return updated


def _minimal_v3_state_updates(
    chapter: Any,
    summary: Any,
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "timeline": {
            "occurred_events": [
                {
                    "id": f"ev_{int(chapter):04d}_01",
                    "summary": str(summary),
                    "location": "",
                    "involved_characters": [],
                    "source_chapter": chapter,
                }
            ],
        },
        "character_states": [],
        "resource_changes": [],
        "open_thread_updates": [],
        "payoff_updates": [
            {
                "chapter": chapter,
                "promises_made": [],
                "payoffs_delivered": [str(summary)],
                "frustration_level": "controlled",
                "payoff_types": [],
                "delayed_payoffs": [],
                "risks": [],
            }
        ],
        "conflict_updates": {"active": []},
        "next_hook": {},
        "pending_approvals": list(pending_approvals),
    }


def _minimal_acceptance_contract(
    root: Path,
    chapter: Any,
    summary: Any,
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "quality_gate_summary": {
            "continuity_review_present": False,
            "continuity_blockers": [],
            "pacing_review_present": False,
            "pacing_score": 0,
            "revised_pacing_score": 0,
            "revision_required": False,
            "waiver_required": False,
        },
        "outline_alignment": {
            "reference_chain": "master -> volume -> arc -> unit -> chapter brief",
            "volume_id": "volume_001",
            "arc_id": "arc_001",
            "unit_id": "unit_0001",
            "required_unit_obligations": [],
            "claimed_fulfilled_unit_obligations": [],
            "pending_unit_obligations": [],
        },
        "state_updates": {
            "timeline_event": {
                "id": f"t{int(chapter):03d}" if isinstance(chapter, int) else "t000",
                "when": f"第 {chapter} 章",
                "summary": str(summary),
            },
            "character_state_changes": [],
            "resource_changes": [],
            "open_thread_updates": [],
            "payoff_updates": [],
            "next_hook": {},
            "pending_approvals": list(pending_approvals),
            "economy_changes": [],
            "faction_changes": [],
        },
    }


def _pending_approvals_from_packet(packet: dict[str, Any]) -> list[str]:
    current_state = packet.get("current_state")
    if not isinstance(current_state, dict):
        return []
    pending_approvals = current_state.get("pending_approvals")
    if not isinstance(pending_approvals, list):
        return []
    return pending_approvals


def _sync_acceptance_contract_state_updates(packet: dict[str, Any]) -> bool:
    contract = packet.get("acceptance_contract")
    v3_updates = packet.get("v3_state_updates")
    if not isinstance(contract, dict) or not isinstance(v3_updates, dict):
        return False

    state_updates = contract.setdefault("state_updates", {})
    if not isinstance(state_updates, dict):
        contract["state_updates"] = {}
        state_updates = contract["state_updates"]

    mirrors = {
        "character_state_changes": "character_states",
        "resource_changes": "resource_changes",
        "open_thread_updates": "open_thread_updates",
        "payoff_updates": "payoff_updates",
        "next_hook": "next_hook",
        "pending_approvals": "pending_approvals",
    }
    changed = False
    for contract_field, v3_field in mirrors.items():
        expected = copy.deepcopy(v3_updates.get(v3_field, {} if contract_field == "next_hook" else []))
        if state_updates.get(contract_field) != expected:
            state_updates[contract_field] = expected
            changed = True
    return changed


def _legacy_thread_promise(thread: dict[str, Any]) -> str:
    for key in ("promise", "text", "id"):
        value = thread.get(key)
        if value not in (None, ""):
            return str(value)
    return "Migrated legacy thread"
