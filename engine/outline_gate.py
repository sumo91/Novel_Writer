from pathlib import Path
from typing import Any

from engine.io_utils import read_text, read_yaml, write_yaml
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
    if not isinstance(approval, dict):
        approval = {}
        data["approval"] = approval
    approval["status"] = status
    if note is not None:
        approval["note"] = note
    write_yaml(path, data)
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


def _book_root(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    return root
