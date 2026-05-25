from typing import Any

from engine.io_utils import read_yaml
from engine.paths import knowledge_dir

KNOWLEDGE_DIR = knowledge_dir()
CRAFT_CARD_SEVERITIES = {"hard", "soft", "genre-specific"}
CRAFT_CARD_TEXT_LIMITS = {
    "scope": 120,
    "use_when": 240,
    "principle": 300,
    "checks": 240,
    "failure_modes": 240,
}
SOURCE_COPY_MIN_CHARS = 40
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


def load_craft_cards(applies_to: str | list[str] | None = None) -> list[dict[str, Any]]:
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
    grouped = _group_cards_by_severity(cards)
    for heading in ("hard", "soft", "genre-specific"):
        section_cards = grouped.get(heading, [])
        if not section_cards:
            continue
        lines.append(_severity_heading(heading))
        lines.append("")
        for card in section_cards:
            lines.append(f"- {card.get('id')}: {card.get('principle', '')}")
            if card.get("scope"):
                lines.append(f"  - Scope: {card['scope']}")
            if card.get("severity"):
                lines.append(f"  - Severity: {card['severity']}")
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

        errors.extend(validate_craft_card_quality(data, relative_path))

    return errors


def validate_craft_card_quality(
    card: dict[str, Any],
    relative_path: str,
    *,
    source_text: str | None = None,
) -> list[str]:
    errors: list[str] = []
    for field in ("scope", "use_when", "principle"):
        value = card.get(field)
        if isinstance(value, str) and len(value.strip()) > CRAFT_CARD_TEXT_LIMITS[field]:
            errors.append(f"{relative_path}: {field} must be concise.")

    for field in ("checks", "failure_modes"):
        value = card.get(field)
        if isinstance(value, list):
            if not value:
                errors.append(f"{relative_path}: {field} must contain at least one item.")
            for index, item in enumerate(value):
                if isinstance(item, str) and len(item.strip()) > CRAFT_CARD_TEXT_LIMITS[field]:
                    errors.append(f"{relative_path}: {field}[{index}] must be concise.")

    if source_text:
        normalized_source = _normalize_for_copy_check(source_text)
        for field in ("scope", "use_when", "principle"):
            _append_source_copy_error(errors, relative_path, field, card.get(field), normalized_source)
        for field in ("checks", "failure_modes"):
            value = card.get(field)
            if isinstance(value, list):
                for index, item in enumerate(value):
                    _append_source_copy_error(
                        errors,
                        relative_path,
                        f"{field}[{index}]",
                        item,
                        normalized_source,
                    )
    return errors


def _applies_to(card: dict[str, Any], target: str | list[str]) -> bool:
    targets = {target} if isinstance(target, str) else set(target)
    applications = card.get("applies_to", [])
    if isinstance(applications, str):
        applications = [applications]
    if not isinstance(applications, list):
        return False
    return bool(targets.intersection(applications)) or "all" in applications


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _append_source_copy_error(
    errors: list[str],
    relative_path: str,
    field: str,
    value: Any,
    normalized_source: str,
) -> None:
    if not isinstance(value, str):
        return
    normalized_value = _normalize_for_copy_check(value)
    if len(normalized_value) < SOURCE_COPY_MIN_CHARS:
        return
    if normalized_value in normalized_source:
        errors.append(f"{relative_path}: {field} appears to copy a long source excerpt.")


def _normalize_for_copy_check(value: str) -> str:
    return "".join(value.split()).lower()


def _group_cards_by_severity(cards: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {severity: [] for severity in ("hard", "soft", "genre-specific")}
    for card in cards:
        severity = card.get("severity")
        if severity in grouped:
            grouped[severity].append(card)
        else:
            grouped["soft"].append(card)
    return grouped


def _severity_heading(severity: str) -> str:
    return {
        "hard": "### Hard Rules",
        "soft": "### Soft Heuristics",
        "genre-specific": "### Genre-Specific Patterns",
    }.get(severity, "### Soft Heuristics")
