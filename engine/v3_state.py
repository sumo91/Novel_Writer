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
    _update_open_threads(root, chapter_number, updates.get("open_thread_updates", []))
    _update_payoff_ledger(root, chapter_number, updates.get("payoff_updates", []))
    _update_hook_index(root, chapter_number, updates.get("next_hook", {}))
    _update_memory_index(root, chapter_number, updates)


def _update_character_states(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    path = root / "canon" / "character_states.yaml"
    data = read_yaml(path)
    characters = data.setdefault("characters", {})
    update_ids = {
        update["character_id"]
        for update in updates
        if "character_id" in update
    }

    for character_id in list(characters):
        character = characters[character_id]
        _seed_snapshot_history(character, "last_updated_chapter")
        _remove_history_chapter(character, chapter_number)
        if character_id not in update_ids:
            _restore_from_snapshot_history(character)
        if not character.get("history"):
            del characters[character_id]

    for update in updates:
        character_id = update["character_id"]
        character = characters.get(character_id, {})
        _seed_snapshot_history(character, "last_updated_chapter")
        _remove_history_chapter(character, chapter_number)
        state = dict(update)
        state.pop("character_id", None)
        state["last_updated_chapter"] = chapter_number
        state["chapter"] = chapter_number
        character.setdefault("history", []).append(state)
        _restore_from_snapshot_history(character)
        state = character
        state.pop("chapter", None)
        characters[character_id] = state

    write_yaml(path, data)


def _update_resource_ledger(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    path = root / "canon" / "resource_ledger.yaml"
    data = read_yaml(path)
    resources = data.setdefault("resources", [])
    by_id = {resource.get("id"): resource for resource in resources}
    grouped_updates: dict[str, list[dict[str, Any]]] = {}

    for resource in resources:
        if "base_amount" not in resource and not resource.get("history"):
            resource["base_amount"] = resource.get("current_amount", 0)
            resource["base_chapter"] = resource.get("last_updated_chapter")
        history = resource.setdefault("history", [])
        prior_deltas = [
            entry.get("delta", 0)
            for entry in history
            if entry.get("chapter") == chapter_number and _is_number(entry.get("delta"))
        ]
        if prior_deltas:
            resource["current_amount"] = resource.get("current_amount", 0) - sum(prior_deltas)
        resource["history"] = [
            entry
            for entry in history
            if entry.get("chapter") != chapter_number
        ]
        _recompute_resource(resource)

    data["resources"] = [
        resource
        for resource in resources
        if resource.get("history")
        or "base_amount" in resource
        or (
            resource.get("last_updated_chapter") != chapter_number
            and resource.get("current_amount") not in (None, 0)
        )
    ]
    resources = data["resources"]
    by_id = {resource.get("id"): resource for resource in resources}

    for update in updates:
        resource_id = update.get("id") or _resource_id(update.get("owner"), update.get("item"))
        grouped_updates.setdefault(resource_id, []).append(update)

    for resource_id, resource_updates in grouped_updates.items():
        first_update = resource_updates[0]
        resource = by_id.get(resource_id)
        if resource is None:
            resource = {
                "id": resource_id,
                "owner": first_update.get("owner"),
                "name": first_update.get("item"),
                "category": first_update.get("category"),
                "unit": first_update.get("unit"),
                "current_amount": 0,
                "history": [],
            }
            resources.append(resource)
            by_id[resource_id] = resource

        resource["last_updated_chapter"] = chapter_number
        resource.setdefault("history", [])
        for update in resource_updates:
            delta = update.get("delta", 0)
            resource["owner"] = update.get("owner", resource.get("owner"))
            resource["name"] = update.get("item", resource.get("name"))
            resource["category"] = update.get("category", resource.get("category"))
            resource["unit"] = update.get("unit", resource.get("unit"))
            if _is_number(delta):
                resource["current_amount"] = resource.get("current_amount", 0) + delta
            resource["history"].append(
                {
                    "chapter": chapter_number,
                    "delta": delta,
                    "reason": update.get("reason", ""),
                }
            )
        _recompute_resource(resource)

    write_yaml(path, data)


def _update_open_threads(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    path = root / "canon" / "open_threads.yaml"
    data = read_yaml(path)
    threads = data.setdefault("threads", [])
    update_ids = {update["id"] for update in updates if "id" in update}
    kept_threads = []
    for thread in threads:
        had_history = bool(thread.get("history"))
        had_chapter_marker = thread.get("last_touched") is not None or thread.get("source_chapter") is not None
        if not had_history and not had_chapter_marker and thread.get("id") not in update_ids:
            kept_threads.append(thread)
            continue
        _seed_snapshot_history(thread, "last_touched", fallback_field="source_chapter")
        _remove_history_chapter(thread, chapter_number)
        if thread.get("id") not in update_ids:
            _restore_from_snapshot_history(thread)
        if thread.get("history") or (not had_history and not had_chapter_marker):
            kept_threads.append(thread)
    threads = kept_threads
    data["threads"] = threads
    by_id = {thread.get("id"): thread for thread in threads}

    for update in updates:
        thread_id = update["id"]
        thread = by_id.get(thread_id)
        if thread is None:
            thread = {"id": thread_id}
            threads.append(thread)
            by_id[thread_id] = thread
        _seed_snapshot_history(thread, "last_touched", fallback_field="source_chapter")
        _remove_history_chapter(thread, chapter_number)
        snapshot = dict(update)
        snapshot["chapter"] = chapter_number
        thread.setdefault("history", []).append(snapshot)
        _restore_from_snapshot_history(thread)

    write_yaml(path, data)


def _update_payoff_ledger(
    root: Path,
    chapter_number: int,
    updates: list[dict[str, Any]],
) -> None:
    path = root / "canon" / "payoff_ledger.yaml"
    data = read_yaml(path)
    entries = [
        entry
        for entry in data.get("entries", [])
        if entry.get("chapter") != chapter_number
    ]
    entries.extend(dict(update, chapter=chapter_number) for update in updates)
    data["entries"] = entries
    write_yaml(path, data)


def _update_hook_index(root: Path, chapter_number: int, next_hook: dict[str, Any]) -> None:
    path = root / "state" / "hook_index.json"
    data = read_json(path)
    hooks = data.setdefault("hooks", [])
    data["hooks"] = [existing for existing in hooks if existing.get("chapter") != chapter_number]
    hooks = data["hooks"]
    hook = next_hook.get("hook") if isinstance(next_hook, dict) else None
    if not hook:
        write_json(path, data)
        return

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
        _remove_chapter(data[field], chapter_number)

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


def _remove_chapter(index: dict[str, list[int]], chapter_number: int) -> None:
    for key in list(index):
        chapters = [chapter for chapter in index[key] if chapter != chapter_number]
        if chapters:
            index[key] = chapters
        else:
            del index[key]


def _seed_snapshot_history(
    item: dict[str, Any],
    chapter_field: str,
    fallback_field: str | None = None,
) -> None:
    if item.get("history"):
        return

    chapter = item.get(chapter_field)
    if chapter is None and fallback_field:
        chapter = item.get(fallback_field)
    if chapter is None:
        return

    snapshot = {
        key: value
        for key, value in item.items()
        if key not in {"history", "base_amount", "base_chapter"}
    }
    snapshot["chapter"] = chapter
    item["history"] = [snapshot]


def _remove_history_chapter(item: dict[str, Any], chapter_number: int) -> None:
    item["history"] = [
        entry
        for entry in item.get("history", [])
        if entry.get("chapter") != chapter_number
    ]


def _restore_from_snapshot_history(item: dict[str, Any]) -> None:
    history = item.get("history", [])
    preserved = {"history": history}
    latest = max(history, key=lambda entry: entry.get("chapter", 0), default=None)
    item.clear()
    if latest:
        item.update({key: value for key, value in latest.items() if key != "chapter"})
    item.update(preserved)


def _recompute_resource(resource: dict[str, Any]) -> None:
    amount = resource.get("base_amount", 0)
    last_chapter = resource.get("base_chapter")
    for entry in resource.get("history", []):
        if _is_number(entry.get("delta")):
            amount += entry["delta"]
        if entry.get("chapter") is not None:
            if last_chapter is None or entry["chapter"] > last_chapter:
                last_chapter = entry["chapter"]

    resource["current_amount"] = amount
    if last_chapter is not None:
        resource["last_updated_chapter"] = last_chapter
    elif "last_updated_chapter" in resource:
        del resource["last_updated_chapter"]


def _resource_id(owner: Any, item: Any) -> str:
    return f"res_{_slug(owner)}_{_slug(item)}"


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _slug(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    return text.strip("_").lower()
