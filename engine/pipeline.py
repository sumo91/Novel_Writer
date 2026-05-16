from dataclasses import dataclass
from pathlib import Path

from engine.paths import books_dir

BOOKS_DIR = books_dir()


@dataclass(frozen=True)
class PipelinePaths:
    root: Path
    pipeline_dir: Path
    context_path: Path
    manifest_path: Path
    handoff_dir: Path


def pipeline_paths(book_id: str, chapter_number: int) -> PipelinePaths:
    root = BOOKS_DIR / book_id
    pipeline_dir = root / "pipeline" / f"ch_{chapter_number:04d}"
    return PipelinePaths(
        root=root,
        pipeline_dir=pipeline_dir,
        context_path=pipeline_dir / "context.md",
        manifest_path=pipeline_dir / "manifest.json",
        handoff_dir=pipeline_dir / "handoffs",
    )
