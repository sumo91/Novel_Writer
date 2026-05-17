from pathlib import Path

from engine.craft_knowledge import validate_craft_cards
from engine.hardening import (
    validate_pending_approvals_registry,
    validate_acceptance_packet_file,
    validate_review_files,
    validate_v3_ledgers,
    validate_v3_1_outline_architecture,
)
from engine.paths import books_dir

BOOKS_DIR = books_dir()

REQUIRED_BOOK_FILES = [
    "book.yaml",
    "canon/novel_bible.yaml",
    "canon/characters.yaml",
    "canon/relationships.yaml",
    "canon/world_rules.yaml",
    "canon/timeline.yaml",
    "canon/open_threads.yaml",
    "canon/character_states.yaml",
    "canon/resource_ledger.yaml",
    "canon/payoff_ledger.yaml",
    "canon/economy.yaml",
    "canon/factions.yaml",
    "canon/forbidden_rules.yaml",
    "outlines/master_outline.yaml",
    "outlines/volumes/volume_001.yaml",
    "outlines/arc_001.yaml",
    "outlines/units/unit_0001.yaml",
    "state/current_state.json",
    "state/chapter_index.json",
    "state/change_log.jsonl",
    "state/hook_index.json",
    "state/memory_index.json",
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

    errors.extend(_validate_existing_pipeline_artifacts(root))
    errors.extend(validate_pending_approvals_registry(root))
    errors.extend(validate_v3_ledgers(root))
    errors.extend(validate_v3_1_outline_architecture(root))
    errors.extend(f"knowledge/{error}" for error in validate_craft_cards())

    return errors


def _validate_existing_pipeline_artifacts(root: Path) -> list[str]:
    errors: list[str] = []
    chapter_numbers = set()
    for parent in (root / "reviews", root / "state_updates"):
        if not parent.exists():
            continue
        for path in parent.iterdir():
            number = _chapter_number_from_name(path.name)
            if number is not None:
                chapter_numbers.add(number)

    for chapter_number in sorted(chapter_numbers):
        errors.extend(validate_review_files(root, chapter_number))
        errors.extend(validate_acceptance_packet_file(root, chapter_number))

    return errors


def _chapter_number_from_name(name: str) -> int | None:
    marker = "ch_"
    if marker not in name:
        return None
    start = name.find(marker) + len(marker)
    digits = name[start : start + 4]
    if digits.isdigit():
        return int(digits)
    return None
