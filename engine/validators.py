from pathlib import Path

from engine.paths import book_path, books_dir

BOOKS_DIR = books_dir()

REQUIRED_BOOK_FILES = [
    "book.yaml",
    "canon/novel_bible.yaml",
    "canon/characters.yaml",
    "canon/relationships.yaml",
    "canon/world_rules.yaml",
    "canon/timeline.yaml",
    "canon/open_threads.yaml",
    "canon/forbidden_rules.yaml",
    "outlines/master_outline.yaml",
    "outlines/arc_001.yaml",
    "state/current_state.json",
    "state/chapter_index.json",
    "state/change_log.jsonl",
]


def validate_score(score: int) -> bool:
    return 0 <= score <= 100


def validate_book(book_id: str) -> list[str]:
    root = BOOKS_DIR / book_id
    errors: list[str] = []

    if not root.exists():
        return [f"Missing book project: {book_id}"]

    for relative_path in REQUIRED_BOOK_FILES:
        if not (root / relative_path).exists():
            errors.append(f"Missing required file: {relative_path}")

    return errors
