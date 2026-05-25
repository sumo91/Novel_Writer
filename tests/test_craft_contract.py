from engine import book_factory, craft_contract, craft_knowledge
from engine.io_utils import read_yaml, write_yaml


def test_write_craft_contract_scaffold_selects_existing_craft_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "golden.yaml",
        {
            "id": "craft_golden",
            "scope": "craft",
            "applies_to": ["context", "brief", "review"],
            "use_when": "A system creates leverage.",
            "principle": "Make the advantage necessary.",
            "checks": ["Name the pressure the system solves."],
            "failure_modes": ["Button solves all."],
            "severity": "hard",
        },
    )
    book = book_factory.create_book("demo", title="Demo Book")

    output = craft_contract.write_craft_contract_scaffold("demo", force=True)

    data = read_yaml(output)
    assert output == book / "craft" / "craft_contract.yaml"
    assert data["book_id"] == "demo"
    assert data["approval"]["status"] == "draft"
    assert data["selected_cards"][0]["id"] == "craft_golden"
    assert data["selected_cards"][0]["mode"] == "hard_rule"
    assert output.with_suffix(".html").exists()


def test_check_craft_contract_reports_unknown_card(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "craft" / "craft_contract.yaml",
        {
            "book_id": "demo",
            "approval": {"status": "draft"},
            "concept_focus": {},
            "selected_cards": [{"id": "missing_card", "mode": "hard_rule"}],
            "stage_rules": [],
        },
    )

    result = craft_contract.check_craft_contract("demo")

    assert result["passed"] is False
    assert "craft/craft_contract.yaml: selected_cards[0].id references unknown craft card missing_card." in result["errors"]


def test_generate_concept_review_uses_contract_and_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "appeal.yaml",
        {
            "id": "craft_appeal",
            "scope": "craft",
            "applies_to": ["brief", "review"],
            "use_when": "A protagonist needs reader affection.",
            "principle": "Give an early empathy hook.",
            "checks": ["Name the empathy hook."],
            "failure_modes": ["Unlikable opening."],
            "severity": "hard",
        },
    )
    book_factory.create_book("demo", title="Demo Book")
    craft_contract.write_craft_contract_scaffold("demo", force=True)

    output = craft_contract.generate_concept_review("demo")

    content = output.read_text(encoding="utf-8")
    assert "# Concept Review" in content
    assert "craft_appeal" in content
    assert "Name the empathy hook." in content
    assert "## Concept Gate Questions" in content
    assert output.with_suffix(".html").exists()
