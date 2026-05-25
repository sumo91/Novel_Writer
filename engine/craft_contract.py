from pathlib import Path
from typing import Any

from engine.craft_knowledge import load_craft_cards
from engine.html_utils import markdown_to_html_page
from engine.io_utils import read_yaml, write_text, write_yaml
from engine.paths import books_dir

BOOKS_DIR = books_dir()

REQUIRED_CRAFT_CONTRACT_FIELDS = {
    "book_id",
    "approval",
    "concept_focus",
    "selected_cards",
    "stage_rules",
}
APPROVAL_STATUSES = {"draft", "approved", "rejected", "superseded"}
CARD_MODES = {"hard_rule", "soft_heuristic", "diagnostic"}


def write_craft_contract_scaffold(book_id: str, force: bool = False) -> Path:
    root = _book_root(book_id)
    output = root / "craft" / "craft_contract.yaml"
    if output.exists() and not force:
        raise FileExistsError(f"Craft contract already exists: {output}")

    data = {
        "book_id": book_id,
        "approval": {
            "status": "draft",
            "approved_by": "",
            "note": (
                "Draft book-local craft contract; human may edit selected cards "
                "before treating them as hard writing constraints."
            ),
        },
        "concept_focus": {
            "genre": "",
            "tone": "",
            "golden_finger": "",
            "protagonist_appeal": "",
            "repeatable_engine": "",
            "first_three_chapter_promise": "",
        },
        "selected_cards": [_contract_entry(card) for card in _default_cards()],
        "stage_rules": [
            {
                "stage": "concept",
                "required_outputs": [
                    "golden finger necessity and uniqueness",
                    "protagonist early appeal hook",
                    "repeatable promise-payoff loop",
                    "first three chapter promise",
                ],
            },
            {
                "stage": "chapter_brief",
                "required_outputs": [
                    "craft alignment section",
                    "card-specific checks answered when relevant",
                ],
            },
            {
                "stage": "review",
                "required_outputs": [
                    "craft alignment risks",
                    "rewrite-required judgment for hard-rule violations",
                ],
            },
        ],
    }
    write_yaml(output, data)
    write_text(
        output.with_suffix(".html"),
        markdown_to_html_page(
            "Craft Contract",
            "\n".join(
                [
                    "# Craft Contract",
                    "",
                    f"- Book: {book_id}",
                    "- This readable sidecar is for human review; the YAML is the machine contract.",
                    "- Select only the craft cards this book should actively obey.",
                    "- Keep source theory in knowledge cards; keep book-specific decisions here.",
                ]
            ),
        ),
    )
    return output


def check_craft_contract(book_id: str) -> dict[str, Any]:
    root = _book_root(book_id)
    path = root / "craft" / "craft_contract.yaml"
    if not path.exists():
        return {
            "book_id": book_id,
            "path": "craft/craft_contract.yaml",
            "passed": False,
            "status": "missing",
            "errors": ["craft/craft_contract.yaml: missing craft contract."],
            "warnings": [],
        }
    errors = validate_craft_contract_file(path, root)
    return {
        "book_id": book_id,
        "path": "craft/craft_contract.yaml",
        "passed": not errors,
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": [],
    }


def validate_craft_contract_file(path: Path, root: Path | None = None) -> list[str]:
    relative_path = _relative_path(path, root)
    data = read_yaml(path)
    if not isinstance(data, dict):
        return [f"{relative_path}: root must be a mapping."]

    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_CRAFT_CONTRACT_FIELDS if field not in data)
    for field in missing:
        errors.append(f"{relative_path}: missing required field {field}.")

    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append(f"{relative_path}: approval must be a mapping.")
    elif approval.get("status") not in APPROVAL_STATUSES:
        errors.append(
            f"{relative_path}: approval.status must be draft, approved, rejected, or superseded."
        )

    if "concept_focus" in data and not isinstance(data["concept_focus"], dict):
        errors.append(f"{relative_path}: concept_focus must be a mapping.")
    if "stage_rules" in data and not isinstance(data["stage_rules"], list):
        errors.append(f"{relative_path}: stage_rules must be a list.")

    selected_cards = data.get("selected_cards", [])
    if "selected_cards" in data and not isinstance(selected_cards, list):
        errors.append(f"{relative_path}: selected_cards must be a list.")
        selected_cards = []

    known_card_ids = {card.get("id") for card in load_craft_cards()}
    for index, entry in enumerate(selected_cards):
        if not isinstance(entry, dict):
            errors.append(f"{relative_path}: selected_cards[{index}] must be a mapping.")
            continue
        card_id = entry.get("id")
        if not isinstance(card_id, str) or not card_id.strip():
            errors.append(f"{relative_path}: selected_cards[{index}].id is required.")
        elif card_id not in known_card_ids:
            errors.append(
                f"{relative_path}: selected_cards[{index}].id references unknown craft card {card_id}."
            )
        mode = entry.get("mode")
        if mode not in CARD_MODES:
            errors.append(
                f"{relative_path}: selected_cards[{index}].mode must be hard_rule, soft_heuristic, or diagnostic."
            )
    return errors


def load_contract_cards(book_id: str, applies_to: str | list[str] | None = None) -> list[dict[str, Any]]:
    root = _maybe_book_root(book_id)
    if root is None:
        return []
    path = root / "craft" / "craft_contract.yaml"
    if not path.exists():
        return []
    contract = read_yaml(path)
    selected = contract.get("selected_cards", [])
    if not isinstance(selected, list):
        return []

    card_by_id = {card.get("id"): card for card in load_craft_cards(applies_to)}
    cards: list[dict[str, Any]] = []
    for entry in selected:
        if not isinstance(entry, dict):
            continue
        card = card_by_id.get(entry.get("id"))
        if not card:
            continue
        contract_card = dict(card)
        contract_card["contract_mode"] = entry.get("mode", _mode_for_card(card))
        contract_card["contract_required_when"] = entry.get("required_when", "")
        contract_card["contract_notes"] = entry.get("notes", "")
        cards.append(contract_card)
    return cards


def render_book_craft_contract(book_id: str, applies_to: str | list[str] | None = None) -> list[str]:
    root = _maybe_book_root(book_id)
    if root is None:
        return []
    path = root / "craft" / "craft_contract.yaml"
    if not path.exists():
        return []

    cards = load_contract_cards(book_id, applies_to)
    data = read_yaml(path)
    lines = ["## Book Craft Contract", ""]
    approval = data.get("approval", {})
    if isinstance(approval, dict):
        lines.append(f"- Approval: {approval.get('status', 'draft')}")
    focus = data.get("concept_focus", {})
    if isinstance(focus, dict):
        for key in (
            "genre",
            "tone",
            "golden_finger",
            "protagonist_appeal",
            "repeatable_engine",
            "first_three_chapter_promise",
        ):
            value = focus.get(key)
            if value:
                lines.append(f"- {key}: {value}")
    if not cards:
        lines.append("- No selected craft cards apply to this stage.")
        lines.append("")
        return lines

    lines.append("")
    for card in cards:
        lines.append(f"- {card.get('id')}: {card.get('principle', '')}")
        lines.append(f"  - Mode: {card.get('contract_mode', _mode_for_card(card))}")
        if card.get("use_when"):
            lines.append(f"  - Use when: {card['use_when']}")
        for check in _as_list(card.get("checks")):
            lines.append(f"  - Check: {check}")
        for failure in _as_list(card.get("failure_modes")):
            lines.append(f"  - Failure mode: {failure}")
    lines.append("")
    return lines


def craft_alignment_section(book_id: str, applies_to: str = "brief") -> list[str]:
    cards = load_contract_cards(book_id, applies_to)
    if not cards:
        return []
    lines = ["## Craft Alignment", ""]
    for card in cards:
        lines.append(f"- {card.get('id')}")
        for check in _as_list(card.get("checks")):
            lines.append(f"  - [ ] {check}")
    lines.append("")
    return lines


def has_craft_contract(book_id: str) -> bool:
    root = _maybe_book_root(book_id)
    if root is None:
        return False
    return (root / "craft" / "craft_contract.yaml").exists()


def generate_concept_review(book_id: str, output_path: Path | None = None) -> Path:
    _book_root(book_id)
    output = output_path or (BOOKS_DIR / book_id / "reports" / "concept_review.md")
    lines = [
        "# Concept Review",
        "",
        f"- Book: {book_id}",
        "- Status: draft review scaffold; human approval is still required before book concept lock.",
        "",
    ]
    lines.extend(render_book_craft_contract(book_id, ["context", "brief", "review", "drift", "outline"]))
    lines.extend(
        [
            "## Concept Gate Questions",
            "",
            "- Golden finger necessity: what pressure cannot be faced without the system or advantage?",
            "- Golden finger uniqueness: why this protagonist and not anyone else?",
            "- Protagonist appeal: what early action makes the reader root for them?",
            "- Repeatable engine: what loop can produce chapters without becoming bookkeeping?",
            "- Tone engine: where does light humor arise from scene pressure instead of detached jokes?",
            "- First three chapter promise: what concrete payoff appears by chapter 3?",
            "- Failure risk: what would make this concept collapse into a same-button solution or slice-of-life drift?",
            "",
            "## Decision",
            "",
            "- Approve as book concept: no",
            "- Required revisions:",
            "  - ",
            "- Notes:",
            "  - ",
            "",
        ]
    )
    write_text(output, "\n".join(lines))
    write_text(output.with_suffix(".html"), markdown_to_html_page("Concept Review", "\n".join(lines)))
    return output


def _book_root(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    return root


def _maybe_book_root(book_id: str) -> Path | None:
    root = BOOKS_DIR / book_id
    if not root.exists():
        return None
    return root


def _default_cards() -> list[dict[str, Any]]:
    return load_craft_cards(["context", "brief", "review", "drift", "outline"])


def _contract_entry(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": card.get("id", ""),
        "mode": _mode_for_card(card),
        "applies_to": card.get("applies_to", []),
        "required_when": card.get("use_when", ""),
        "review_questions": card.get("checks", []),
        "notes": "",
    }


def _mode_for_card(card: dict[str, Any]) -> str:
    severity = card.get("severity")
    if severity == "hard":
        return "hard_rule"
    if severity == "genre-specific":
        return "diagnostic"
    return "soft_heuristic"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _relative_path(path: Path, root: Path | None) -> str:
    if root is None:
        return path.as_posix()
    return path.relative_to(root).as_posix()
