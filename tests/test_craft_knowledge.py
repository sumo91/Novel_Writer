from engine import craft_knowledge


def test_load_craft_cards_reads_structured_yaml_cards(tmp_path, monkeypatch):
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "agency.yaml").write_text(
        "\n".join(
            [
                "id: craft_agency_001",
                "scope: craft",
                "applies_to:",
                "  - brief",
                "  - review",
                "use_when: Protagonist choice is at risk.",
                "principle: Every chapter should force a visible protagonist choice.",
                "checks:",
                "  - Does the protagonist choose under pressure?",
                "failure_modes:",
                "  - Passive protagonist",
                "severity: hard",
                "",
            ]
        ),
        encoding="utf-8",
    )

    cards = craft_knowledge.load_craft_cards("brief")

    assert len(cards) == 1
    assert cards[0]["id"] == "craft_agency_001"
    assert cards[0]["principle"] == "Every chapter should force a visible protagonist choice."
    assert cards[0]["checks"] == ["Does the protagonist choose under pressure?"]


def test_load_craft_cards_filters_by_application(tmp_path, monkeypatch):
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "brief.yaml").write_text(
        "id: craft_brief\napplies_to: [brief]\nprinciple: Brief only.\n",
        encoding="utf-8",
    )
    (card_dir / "drift.yaml").write_text(
        "id: craft_drift\napplies_to: [drift]\nprinciple: Drift only.\n",
        encoding="utf-8",
    )

    cards = craft_knowledge.load_craft_cards("drift")

    assert [card["id"] for card in cards] == ["craft_drift"]


def test_validate_craft_cards_reports_schema_errors(tmp_path, monkeypatch):
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "broken.yaml").write_text(
        "\n".join(
            [
                "id: craft_broken",
                "scope: craft",
                "applies_to: brief",
                "principle: ''",
                "checks: none",
                "failure_modes: []",
                "severity: extreme",
                "",
            ]
        ),
        encoding="utf-8",
    )

    errors = craft_knowledge.validate_craft_cards()

    assert "craft_cards/broken.yaml: applies_to must be a list." in errors
    assert "craft_cards/broken.yaml: principle is required." in errors
    assert "craft_cards/broken.yaml: checks must be a list." in errors
    assert (
        "craft_cards/broken.yaml: severity must be hard, soft, or genre-specific."
        in errors
    )
