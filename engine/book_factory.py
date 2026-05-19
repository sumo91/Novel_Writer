import shutil
from datetime import UTC, datetime
from pathlib import Path

from engine.io_utils import read_yaml, write_yaml
from engine.paths import books_dir, project_root

TEMPLATE_DIR = project_root() / "engine" / "templates" / "book"
BOOKS_DIR = books_dir()


def create_book(book_id: str, title: str, force: bool = False) -> Path:
    if Path(book_id).name != book_id or not book_id.strip():
        raise ValueError("book_id must be a single directory name")

    target = BOOKS_DIR / book_id
    if target.exists():
        if not force:
            raise FileExistsError(f"Book already exists: {book_id}")
        shutil.rmtree(target)

    shutil.copytree(TEMPLATE_DIR, target)
    metadata_path = target / "book.yaml"
    metadata = read_yaml(metadata_path)
    metadata.update(
        {
            "book_id": book_id,
            "title": title,
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    write_yaml(metadata_path, metadata)
    style_bible_path = target / "style" / "style_bible.yaml"
    if style_bible_path.exists():
        style_bible = read_yaml(style_bible_path)
        style_bible["book_id"] = book_id
        style_bible.setdefault("style_id", f"{book_id}_style")
        write_yaml(style_bible_path, style_bible)
    return target
