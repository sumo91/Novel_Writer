from pathlib import Path
from typing import Any

from engine.html_utils import markdown_to_html_page
from engine.io_utils import read_yaml, write_text, write_yaml
from engine.paths import books_dir, knowledge_dir

BOOKS_DIR = books_dir()
KNOWLEDGE_DIR = knowledge_dir()

STYLE_CARD_SEVERITIES = {"hard", "soft", "genre-specific"}
REQUIRED_STYLE_CARD_FIELDS = {
    "id",
    "scope",
    "applies_to",
    "use_when",
    "principle",
    "checks",
    "failure_modes",
    "severity",
}
REQUIRED_STYLE_BIBLE_FIELDS = {
    "book_id",
    "style_id",
    "approval",
    "narration",
    "dialogue",
    "protagonist_voice",
    "payoff_style",
    "banned_patterns",
    "style_cards",
}


def write_style_bible_scaffold(book_id: str, force: bool = False) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    output = root / "style" / "style_bible.yaml"
    if output.exists() and not force:
        raise FileExistsError(f"Style bible already exists: {output}")

    data = {
        "book_id": book_id,
        "style_id": f"{book_id}_style",
        "approval": {
            "status": "draft",
            "approved_by": "",
            "note": "Draft style bible; human may edit before treating as hard style.",
        },
        "narration": {
            "pace": "",
            "texture": "",
            "exposition": "",
            "emotion_delivery": "",
        },
        "dialogue": {
            "density": "",
            "tension_source": "",
            "subtext": "",
        },
        "protagonist_voice": {},
        "payoff_style": {
            "pattern": "",
            "cost_or_risk": "",
        },
        "banned_patterns": [],
        "style_cards": [],
    }
    write_yaml(output, data)
    write_text(
        output.with_suffix(".html"),
        markdown_to_html_page(
            "Style Bible",
            "\n".join(
                [
                    "# Style Bible",
                    "",
                    f"- Book: {book_id}",
                    "- Edit the YAML contract first; this HTML is only a readable sidecar.",
                    "- Keep rules abstract: define texture, rhythm, voice, and banned patterns without copying a living author's style.",
                ]
            ),
        ),
    )
    return output


def check_style_bible(book_id: str) -> dict[str, Any]:
    root = BOOKS_DIR / book_id
    path = root / "style" / "style_bible.yaml"
    if not path.exists():
        return {
            "book_id": book_id,
            "path": "style/style_bible.yaml",
            "passed": False,
            "status": "missing",
            "errors": ["style/style_bible.yaml: missing style bible."],
            "warnings": [],
        }
    errors = validate_style_bible_file(path, root)
    return {
        "book_id": book_id,
        "path": "style/style_bible.yaml",
        "passed": not errors,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": [],
    }


def validate_style_bible_file(path: Path, root: Path | None = None) -> list[str]:
    relative_path = _relative_style_path(path, root)
    data = read_yaml(path)
    if not isinstance(data, dict):
        return [f"{relative_path}: root must be a mapping."]
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_STYLE_BIBLE_FIELDS if field not in data)
    for field in missing:
        errors.append(f"{relative_path}: missing required field {field}.")
    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append(f"{relative_path}: approval must be a mapping.")
    elif approval.get("status") not in {"draft", "approved", "rejected", "superseded"}:
        errors.append(
            f"{relative_path}: approval.status must be draft, approved, rejected, or superseded."
        )
    for field in ("narration", "dialogue", "protagonist_voice", "payoff_style"):
        if field in data and not isinstance(data[field], dict):
            errors.append(f"{relative_path}: {field} must be a mapping.")
    for field in ("banned_patterns", "style_cards"):
        if field in data and not isinstance(data[field], list):
            errors.append(f"{relative_path}: {field} must be a list.")
    return errors


def load_style_cards(applies_to: str | list[str] | None = None) -> list[dict[str, Any]]:
    card_dir = KNOWLEDGE_DIR / "style_cards"
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


def render_style_cards(cards: list[dict[str, Any]]) -> list[str]:
    if not cards:
        return []
    lines = ["## Style Cards", ""]
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


def validate_style_cards() -> list[str]:
    card_dir = KNOWLEDGE_DIR / "style_cards"
    if not card_dir.exists():
        return []
    errors: list[str] = []
    for path in sorted(card_dir.glob("*.yaml")):
        relative_path = path.relative_to(KNOWLEDGE_DIR).as_posix()
        data = read_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{relative_path}: root must be a mapping.")
            continue
        missing = sorted(field for field in REQUIRED_STYLE_CARD_FIELDS if field not in data)
        for field in missing:
            errors.append(f"{relative_path}: missing required field {field}.")
        for field in ("id", "scope", "use_when", "principle"):
            if field in data and not _non_empty_string(data[field]):
                errors.append(f"{relative_path}: {field} is required.")
        for field in ("applies_to", "checks", "failure_modes"):
            if field in data and not isinstance(data[field], list):
                errors.append(f"{relative_path}: {field} must be a list.")
        severity = data.get("severity")
        if "severity" in data and severity not in STYLE_CARD_SEVERITIES:
            errors.append(
                f"{relative_path}: severity must be hard, soft, or genre-specific."
            )
    return errors


def _relative_style_path(path: Path, root: Path | None) -> str:
    if root is None:
        return path.as_posix()
    return path.relative_to(root).as_posix()


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
