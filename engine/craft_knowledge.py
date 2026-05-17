from typing import Any

from engine.io_utils import read_yaml
from engine.paths import knowledge_dir

KNOWLEDGE_DIR = knowledge_dir()
CRAFT_CARD_SEVERITIES = {"hard", "soft", "genre-specific"}
REQUIRED_CRAFT_CARD_FIELDS = {
    "id",
    "scope",
    "applies_to",
    "use_when",
    "principle",
    "checks",
    "failure_modes",
    "severity",
}


def load_craft_cards(applies_to: str | None = None) -> list[dict[str, Any]]:
    card_dir = KNOWLEDGE_DIR / "craft_cards"
    if not card_dir.exists():
        return []

    cards: list[dict[str, Any]] = []
    for path in sorted(card_dir.glob("*.yaml")):
        data = read_yaml(path)
        if not isinstance(data, dict) or not data.get("id"):
            continue
        if applies_to and not _applies_to(data, applies_to):
            continue
        card = dict(data)
        card["source"] = path.relative_to(KNOWLEDGE_DIR).as_posix()
        cards.append(card)
    return cards


def render_craft_cards(cards: list[dict[str, Any]]) -> list[str]:
    if not cards:
        return []

    lines = ["## Craft Knowledge Cards", ""]
    for card in cards:
        lines.append(f"- {card.get('id')}: {card.get('principle', '')}")
        if card.get("use_when"):
            lines.append(f"  - Use when: {card['use_when']}")
        for check in _as_list(card.get("checks")):
            lines.append(f"  - Check: {check}")
        for failure in _as_list(card.get("failure_modes")):
            lines.append(f"  - Failure mode: {failure}")
    lines.append("")
    return lines


def validate_craft_cards() -> list[str]:
    card_dir = KNOWLEDGE_DIR / "craft_cards"
    if not card_dir.exists():
        return []

    errors: list[str] = []
    for path in sorted(card_dir.glob("*.yaml")):
        relative_path = path.relative_to(KNOWLEDGE_DIR).as_posix()
        data = read_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{relative_path}: root must be a mapping.")
            continue

        missing = sorted(field for field in REQUIRED_CRAFT_CARD_FIELDS if field not in data)
        for field in missing:
            errors.append(f"{relative_path}: missing required field {field}.")

        for field in ("id", "scope", "use_when", "principle"):
            if field in data and not _non_empty_string(data[field]):
                errors.append(f"{relative_path}: {field} is required.")

        for field in ("applies_to", "checks", "failure_modes"):
            if field in data and not isinstance(data[field], list):
                errors.append(f"{relative_path}: {field} must be a list.")

        severity = data.get("severity")
        if "severity" in data and severity not in CRAFT_CARD_SEVERITIES:
            errors.append(
                f"{relative_path}: severity must be hard, soft, or genre-specific."
            )

    return errors


def _applies_to(card: dict[str, Any], target: str) -> bool:
    applications = card.get("applies_to", [])
    if isinstance(applications, str):
        applications = [applications]
    if not isinstance(applications, list):
        return False
    return target in applications or "all" in applications


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
