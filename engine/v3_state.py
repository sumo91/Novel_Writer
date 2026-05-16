import re
from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_json, write_yaml


def apply_v3_state_updates(root: Path, packet: dict[str, Any]) -> None:
    updates = packet.get("v3_state_updates")
    if not isinstance(updates, dict):
        return

    chapter_number = int(packet["chapter"])
    _update_character_states(root, chapter_number, updates.get("character_states", []))
    _update_resource_ledger(root, chapter_number, updates.get("resource_changes", []))
    _update_open_threads(root, updates.get("open_thread_updates", []))
    _update_payoff_ledger(root, chapter_number, updates.get("payoff_updates", []))
    _update_hook_index(root, chapter_number, updates.get("next_hook", {}))
    _update_memory_index(root, chapter_number, updates)


def _update_character_states(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    if not updates:
        return

    path = root / "canon" / "character_states.yaml"
    data = read_yaml(path)
    characters = data.setdefault("characters", {})

    for update in updates:
        character_id = update["character_id"]
        state = dict(update)
        state.pop("character_id", None)
        state["last_updated_chapter"] = chapter_number
        characters[character_id] = state

    write_yaml(path, data)


def _update_resource_ledger(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    if not updates:
        return

    path = root / "canon" / "resource_ledger.yaml"
    data = read_yaml(path)
    resources = data.setdefault("resources", [])
    by_id = {resource.get("id"): resource for resource in resources}

    for update in updates:
        resource_id = update.get("id") or _resource_id(update.get("owner"), update.get("item"))
        resource = by_id.get(resource_id)
        if resource is None:
            resource = {
                "id": resource_id,
                "owner": update.get("owner"),
                "name": update.get("item"),
                "category": update.get("category"),
                "unit": update.get("unit"),
                "current_amount": 0,
                "history": [],
            }
            resources.append(resource)
            by_id[resource_id] = resource

        delta = update.get("delta", 0)
        resource["owner"] = update.get("owner", resource.get("owner"))
        resource["name"] = update.get("item", resource.get("name"))
        resource["category"] = update.get("category", resource.get("category"))
        resource["unit"] = update.get("unit", resource.get("unit"))
        resource["current_amount"] = resource.get("current_amount", 0) + delta
        resource["last_updated_chapter"] = chapter_number
        resource.setdefault("history", []).append(
            {
                "chapter": chapter_number,
                "delta": delta,
                "reason": update.get("reason", ""),
            }
        )

    write_yaml(path, data)


def _update_open_threads(root: Path, updates: list[dict[str, Any]]) -> None:
    if not updates:
        return

    path = root / "canon" / "open_threads.yaml"
    data = read_yaml(path)
    threads = data.setdefault("threads", [])
    by_id = {thread.get("id"): thread for thread in threads}

    for update in updates:
        thread_id = update["id"]
        thread = by_id.get(thread_id)
        if thread is None:
            thread = {"id": thread_id}
            threads.append(thread)
            by_id[thread_id] = thread
        thread.update(update)

    write_yaml(path, data)


def _update_payoff_ledger(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    if not updates:
        return

    path = root / "canon" / "payoff_ledger.yaml"
    data = read_yaml(path)
    entries = [
        entry
        for entry in data.get("entries", [])
        if entry.get("chapter") != chapter_number
    ]
    entries.extend(dict(update, chapter=update.get("chapter", chapter_number)) for update in updates)
    data["entries"] = entries
    write_yaml(path, data)


def _update_hook_index(root: Path, chapter_number: int, next_hook: dict[str, Any]) -> None:
    hook = next_hook.get("hook") if isinstance(next_hook, dict) else None
    if not hook:
        return

    path = root / "state" / "hook_index.json"
    data = read_json(path)
    hooks = data.setdefault("hooks", [])
    hooks.append(
        {
            "chapter": chapter_number,
            "hook": hook,
            "obligation": next_hook.get("obligation", ""),
            "target_chapter": next_hook.get("target_chapter"),
            "status": next_hook.get("status", "open"),
        }
    )
    write_json(path, data)


def _update_memory_index(root: Path, chapter_number: int, updates: dict[str, Any]) -> None:
    path = root / "state" / "memory_index.json"
    data = read_json(path)
    for field in ("by_character", "by_thread", "by_location", "by_resource"):
        data.setdefault(field, {})

    for event in updates.get("timeline", {}).get("occurred_events", []):
        for character_id in event.get("involved_characters", []):
            _add_chapter(data["by_character"], character_id, chapter_number)
        if event.get("location"):
            _add_chapter(data["by_location"], event["location"], chapter_number)

    for character_state in updates.get("character_states", []):
        if character_state.get("character_id"):
            _add_chapter(data["by_character"], character_state["character_id"], chapter_number)

    for thread in updates.get("open_thread_updates", []):
        if thread.get("id"):
            _add_chapter(data["by_thread"], thread["id"], chapter_number)

    for resource in updates.get("resource_changes", []):
        if resource.get("item"):
            _add_chapter(data["by_resource"], resource["item"], chapter_number)

    write_json(path, data)


def _add_chapter(index: dict[str, list[int]], key: str, chapter_number: int) -> None:
    chapters = index.setdefault(key, [])
    chapters.append(chapter_number)
    index[key] = sorted(set(chapters))


def _resource_id(owner: Any, item: Any) -> str:
    return f"res_{_slug(owner)}_{_slug(item)}"


def _slug(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    return text.strip("_").lower()
