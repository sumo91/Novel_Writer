from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def books_dir() -> Path:
    return project_root() / "books"


def book_path(book_id: str) -> Path:
    return books_dir() / book_id


def knowledge_dir() -> Path:
    return project_root() / "knowledge"
