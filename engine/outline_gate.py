from pathlib import Path
from typing import Any

from engine.io_utils import read_text, read_yaml, write_text
from engine.paths import books_dir

BOOKS_DIR = books_dir()

APPROVAL_STATUSES = {"draft", "approved", "rejected", "superseded"}

OUTLINE_LAYERS = {
    "master": "outlines/master_outline.yaml",
    "volume": "outlines/volumes/volume_001.yaml",
    "arc": "outlines/arc_001.yaml",
    "unit": "outlines/units/unit_0001.yaml",
    "economy": "canon/economy.yaml",
    "factions": "canon/factions.yaml",
}

BRIEF_REFERENCE_CHAIN = "master -> volume -> arc -> unit"


def get_outline_status(book_id: str) -> dict[str, Any]:
    root = _book_root(book_id)
    layers = []
    for layer, relative_path in OUTLINE_LAYERS.items():
        path = root / relative_path
        exists = path.exists()
        approval_status = "missing"
        if exists:
            data = read_yaml(path)
            approval = data.get("approval")
            if isinstance(approval, dict):
                approval_status = approval.get("status") or "missing"
            else:
                approval_status = "missing"
        layers.append(
            {
                "layer": layer,
                "path": relative_path,
                "exists": exists,
                "approval_status": approval_status,
            }
        )
    return {"book_id": book_id, "layers": layers}


def update_outline_approval(
    book_id: str,
    layer: str,
    *,
    status: str,
    note: str | None = None,
) -> dict[str, Any]:
    if layer not in OUTLINE_LAYERS:
        raise ValueError(f"Unknown outline layer: {layer}")
    if status not in APPROVAL_STATUSES:
        raise ValueError(f"Invalid approval status: {status}")

    root = _book_root(book_id)
    relative_path = OUTLINE_LAYERS[layer]
    path = root / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing outline layer file: {relative_path}")

    data = read_yaml(path)
    approval = data.get("approval")
    if "approval" in data and not isinstance(approval, dict):
        raise ValueError(f"Outline layer approval must be a mapping: {relative_path}")
    write_text(path, _update_approval_block(read_text(path), status=status, note=note))
    return {"layer": layer, "path": relative_path, "approval_status": status}


def chapter_brief_gate(
    book_id: str,
    chapter_number: int,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    status = get_outline_status(book_id)
    blocking_errors: list[str] = []
    warnings: list[str] = []

    for layer in status["layers"]:
        if not layer["exists"]:
            blocking_errors.append(f"Missing V3.1 layer file: {layer['path']}")
            continue
        approval_status = layer["approval_status"]
        if approval_status != "approved":
            message = (
                f"{layer['layer']} ({layer['path']}) is {approval_status}, not approved."
            )
            if strict:
                blocking_errors.append(message)
            else:
                warnings.append(f"{message} Treat as draft assumption.")

    root = _book_root(book_id)
    brief_path = root / "outlines" / "chapter_briefs" / f"ch_{chapter_number:04d}_brief.md"
    brief_errors: list[str] = []
    if brief_path.exists():
        brief_errors = validate_chapter_brief_text(read_text(brief_path))
        blocking_errors.extend(
            f"{brief_path.relative_to(root).as_posix()}: {error}" for error in brief_errors
        )

    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "strict": strict,
        "allowed": not blocking_errors,
        "blocking_errors": blocking_errors,
        "warnings": warnings,
        "brief_path": brief_path.relative_to(root).as_posix(),
    }


def validate_chapter_brief_text(content: str) -> list[str]:
    lowered = content.lower()
    errors: list[str] = []
    if BRIEF_REFERENCE_CHAIN not in content:
        errors.append(f"Chapter brief must cite `{BRIEF_REFERENCE_CHAIN}`.")
    if "outline obligation" not in lowered and "outline obligations" not in lowered:
        errors.append("Chapter brief must describe outline obligations.")
    for term in ("unit", "arc", "volume"):
        if term not in lowered:
            errors.append(f"Chapter brief must mention {term}.")
    return errors


def _update_approval_block(content: str, *, status: str, note: str | None) -> str:
    lines = content.splitlines(keepends=True)
    approval_index = _find_top_level_key(lines, "approval")
    if approval_index is None:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] = lines[-1] + "\n"
        lines.append("approval:\n")
        lines.append(f"  status: {status}\n")
        if note is not None:
            lines.append(f"  note: {note}\n")
        return "".join(lines)

    block_end = _find_next_top_level_key(lines, approval_index + 1)
    if block_end is None:
        block_end = len(lines)

    block = lines[approval_index:block_end]
    updated_block, status_written, note_written = _rewrite_approval_lines(
        block,
        status=status,
        note=note,
    )
    insert_at = _approval_insert_index(updated_block)
    if not status_written:
        updated_block.insert(insert_at, f"  status: {status}\n")
        insert_at += 1
    if note is not None and not note_written:
        updated_block.insert(insert_at, f"  note: {note}\n")

    return "".join(lines[:approval_index] + updated_block + lines[block_end:])


def _rewrite_approval_lines(
    block: list[str],
    *,
    status: str,
    note: str | None,
) -> tuple[list[str], bool, bool]:
    updated = []
    status_written = False
    note_written = False
    for line in block:
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        newline = _line_ending(line)
        if indent == 2 and stripped.startswith("status:"):
            updated.append(f"  status: {status}{newline}")
            status_written = True
        elif indent == 2 and stripped.startswith("note:") and note is not None:
            updated.append(f"  note: {note}{newline}")
            note_written = True
        else:
            updated.append(line)
    return updated, status_written, note_written


def _approval_insert_index(block: list[str]) -> int:
    for index, line in enumerate(block[1:], start=1):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent == 2 and stripped.startswith("notes:"):
            return index
    return len(block)


def _find_top_level_key(lines: list[str], key: str) -> int | None:
    marker = f"{key}:"
    for index, line in enumerate(lines):
        if line.startswith(marker):
            return index
    return None


def _find_next_top_level_key(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "-", "\t", "\r", "\n")):
            return index
    return None


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _book_root(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    return root
