import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_json, write_text, write_yaml
from engine.paths import books_dir

BOOKS_DIR = books_dir()


@dataclass(frozen=True)
class AcceptanceResult:
    chapter_path: Path
    update_file: Path


def accept_chapter(
    book_id: str,
    update_file: Path,
    force: bool = False,
) -> AcceptanceResult:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    packet = read_yaml(update_file)
    _require(packet, "chapter")
    _require(packet, "title")
    _require(packet, "source_draft")
    _require(packet, "summary")

    chapter_number = int(packet["chapter"])
    source_draft = root / packet["source_draft"]
    if not source_draft.exists():
        raise FileNotFoundError(f"Missing source draft: {packet['source_draft']}")

    chapter_path = root / packet.get(
        "accepted_chapter_path",
        f"chapters/ch_{chapter_number:04d}.md",
    )
    if chapter_path.exists() and not force:
        raise FileExistsError(f"Chapter already exists: {chapter_path.relative_to(root)}")

    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_draft, chapter_path)

    _update_chapter_index(root, packet, chapter_number, chapter_path)
    _update_current_state(root, packet, chapter_number)
    _append_timeline_event(root, packet.get("timeline_event"))
    _update_open_threads(root, packet.get("open_thread_updates", []))
    _append_change_log(root, packet, chapter_number)

    return AcceptanceResult(chapter_path=chapter_path, update_file=update_file)


def _require(packet: dict[str, Any], key: str) -> None:
    if key not in packet or packet[key] in (None, ""):
        raise ValueError(f"Acceptance update missing required field: {key}")


def _update_chapter_index(
    root: Path,
    packet: dict[str, Any],
    chapter_number: int,
    chapter_path: Path,
) -> None:
    index_path = root / "state" / "chapter_index.json"
    index = read_json(index_path)
    chapters = [
        chapter
        for chapter in index.get("chapters", [])
        if chapter.get("chapter") != chapter_number
    ]
    chapters.append(
        {
            "chapter": chapter_number,
            "title": packet["title"],
            "path": chapter_path.relative_to(root).as_posix(),
            "summary": packet["summary"],
            "state_changes": packet.get("state_changes", []),
            "open_threads_touched": packet.get("open_threads_touched", []),
        }
    )
    index["chapters"] = sorted(chapters, key=lambda chapter: chapter["chapter"])
    write_json(index_path, index)


def _update_current_state(
    root: Path,
    packet: dict[str, Any],
    chapter_number: int,
) -> None:
    state_path = root / "state" / "current_state.json"
    state = read_json(state_path)
    state["current_chapter"] = chapter_number

    for key, value in packet.get("current_state", {}).items():
        state[key] = value

    write_json(state_path, state)


def _append_timeline_event(root: Path, event: dict[str, Any] | None) -> None:
    if not event:
        return

    timeline_path = root / "canon" / "timeline.yaml"
    timeline = read_yaml(timeline_path)
    events = [item for item in timeline.get("events", []) if item.get("id") != event["id"]]
    events.append(event)
    timeline["events"] = events
    write_yaml(timeline_path, timeline)


def _update_open_threads(root: Path, updates: list[dict[str, Any]]) -> None:
    if not updates:
        return

    threads_path = root / "canon" / "open_threads.yaml"
    data = read_yaml(threads_path)
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

    write_yaml(threads_path, data)


def _append_change_log(
    root: Path,
    packet: dict[str, Any],
    chapter_number: int,
) -> None:
    change_log = packet.get("change_log", {})
    entry = {
        "chapter": chapter_number,
        "type": "chapter_acceptance",
        "summary": change_log.get("summary", f"Accepted chapter {chapter_number}."),
        "canon_updates": change_log.get("canon_updates", []),
        "pending_approvals": change_log.get("pending_approvals", []),
    }
    path = root / "state" / "change_log.jsonl"
    entries = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))

    entries = [
        existing
        for existing in entries
        if not (
            existing.get("chapter") == chapter_number
            and existing.get("type") == "chapter_acceptance"
        )
    ]
    entries.append(entry)

    content = "\n".join(json.dumps(item, ensure_ascii=False) for item in entries)
    write_text(path, content + "\n")
