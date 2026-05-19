from pathlib import Path
from typing import Any

from engine.io_utils import read_yaml


BRIEF_REFERENCE_CHAIN = "master -> volume -> arc -> unit"


def active_outline_paths(root: Path, chapter_number: int) -> dict[str, str]:
    return {
        "volume": _first_ranged_yaml(
            root,
            "outlines/volumes",
            chapter_number,
            fallback="outlines/volumes/volume_001.yaml",
        ),
        "arc": _first_ranged_yaml(
            root,
            "outlines",
            chapter_number,
            fallback="outlines/arc_001.yaml",
            glob_pattern="arc_*.yaml",
        ),
        "unit": _first_ranged_yaml(
            root,
            "outlines/units",
            chapter_number,
            fallback="outlines/units/unit_0001.yaml",
        ),
    }


def active_outline_data(root: Path, chapter_number: int) -> dict[str, dict[str, Any]]:
    paths = active_outline_paths(root, chapter_number)
    return {
        layer: read_yaml(root / relative_path)
        for layer, relative_path in paths.items()
    }


def active_outline_layers(root: Path, chapter_number: int) -> list[dict[str, Any]]:
    paths = active_outline_paths(root, chapter_number)
    layers = [{"layer": "master", "path": "outlines/master_outline.yaml"}]
    layers.extend({"layer": layer, "path": paths[layer]} for layer in ("volume", "arc", "unit"))
    layers.extend(
        [
            {"layer": "economy", "path": "canon/economy.yaml"},
            {"layer": "factions", "path": "canon/factions.yaml"},
        ]
    )

    for layer in layers:
        path = root / layer["path"]
        exists = path.exists()
        approval_status = "missing"
        if exists:
            data = read_yaml(path)
            approval = data.get("approval")
            if isinstance(approval, dict):
                approval_status = approval.get("status") or "missing"
        layer["exists"] = exists
        layer["approval_status"] = approval_status
    return layers


def unit_id(unit: dict[str, Any]) -> str:
    value = unit.get("unit")
    if value in (None, ""):
        return "unit_0001"
    if isinstance(value, int):
        return f"unit_{value:04d}"
    return str(value)


def unit_chapter(unit: dict[str, Any], chapter_number: int) -> dict[str, Any]:
    for chapter in unit.get("chapters", []):
        if isinstance(chapter, dict) and chapter.get("chapter") == chapter_number:
            return chapter
    return {}


def _first_ranged_yaml(
    root: Path,
    relative_dir: str,
    chapter_number: int,
    fallback: str,
    glob_pattern: str = "*.yaml",
) -> str:
    directory = root / relative_dir
    if not directory.exists():
        return fallback
    candidates: list[tuple[int, int, Path]] = []
    for path in sorted(directory.glob(glob_pattern)):
        data = read_yaml(path)
        chapter_range = data.get("chapter_range")
        if not isinstance(chapter_range, dict):
            continue
        start = chapter_range.get("start")
        end = chapter_range.get("end")
        if isinstance(start, int) and isinstance(end, int) and start <= chapter_number <= end:
            candidates.append((start, end - start, path))
    if candidates:
        _, _, selected = max(candidates, key=lambda candidate: (candidate[0], -candidate[1]))
        return selected.relative_to(root).as_posix()
    return fallback
