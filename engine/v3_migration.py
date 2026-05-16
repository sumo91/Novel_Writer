import shutil
from dataclasses import dataclass

from engine.io_utils import read_yaml, write_yaml
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

OPEN_THREAD_DEFAULTS = {
    "promise": "",
    "source_chapter": "",
    "status": "open",
    "last_touched": "",
    "next_obligation": "",
    "payoff_deadline": "",
    "risk_if_ignored": "",
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
    return V3MigrationResult(book_id=book_id, created=created, updated=updated)


def _copy_missing_v3_templates(root):
    created = []
    for relative_path in V3_TEMPLATE_PATHS:
        target = root / relative_path
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATE_DIR / relative_path, target)
        created.append(relative_path)
    return created


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
        for key, default in OPEN_THREAD_DEFAULTS.items():
            if key not in thread:
                thread[key] = list(default) if isinstance(default, list) else default
                changed = True

    if not changed:
        return []

    write_yaml(path, data)
    return [relative_path]
