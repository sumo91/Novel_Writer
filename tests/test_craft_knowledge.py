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


def test_validate_craft_cards_reports_quality_errors(tmp_path, monkeypatch):
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "bloated.yaml").write_text(
        "\n".join(
            [
                "id: craft_bloated",
                "scope: craft",
                "applies_to:",
                "  - brief",
                "use_when: A card is too vague to guide action.",
                "principle: " + "This card keeps explaining background theory instead of giving one compact operating principle. " * 5,
                "checks: []",
                "failure_modes: []",
                "severity: hard",
                "",
            ]
        ),
        encoding="utf-8",
    )

    errors = craft_knowledge.validate_craft_cards()

    assert "craft_cards/bloated.yaml: principle must be concise." in errors
    assert "craft_cards/bloated.yaml: checks must contain at least one item." in errors
    assert (
        "craft_cards/bloated.yaml: failure_modes must contain at least one item."
        in errors
    )


def test_validate_craft_card_quality_rejects_raw_source_dump():
    source_text = (
        "金手指不是奖励按钮，而是主角进入牌桌的入场券。"
        "它必须制造新的选择压力，并持续暴露限制、代价和误判空间。"
    )
    card = {
        "id": "craft_source_dump",
        "scope": "craft",
        "applies_to": ["brief"],
        "use_when": "Designing golden-finger pressure.",
        "principle": source_text,
        "checks": ["Does the ability create a pressured choice?"],
        "failure_modes": ["The card repeats transcript wording instead of abstraction."],
        "severity": "hard",
    }

    errors = craft_knowledge.validate_craft_card_quality(
        card,
        "craft_cards/source_dump.yaml",
        source_text=source_text,
    )

    assert (
        "craft_cards/source_dump.yaml: principle appears to copy a long source excerpt."
        in errors
    )


def test_render_craft_cards_includes_scope_and_severity():
    lines = craft_knowledge.render_craft_cards(
        [
            {
                "id": "craft_agency_001",
                "scope": "craft",
                "severity": "hard",
                "use_when": "A chapter could go passive.",
                "principle": "Force a visible protagonist choice.",
                "checks": ["Name the choice."],
                "failure_modes": ["Passive protagonist"],
            }
        ]
    )

    assert "- craft_agency_001: Force a visible protagonist choice." in lines
    assert "  - Scope: craft" in lines
    assert "  - Severity: hard" in lines


def test_render_craft_cards_groups_by_severity():
    lines = craft_knowledge.render_craft_cards(
        [
            {
                "id": "soft_card",
                "scope": "craft",
                "severity": "soft",
                "principle": "Soft idea.",
                "checks": [],
                "failure_modes": [],
            },
            {
                "id": "hard_card",
                "scope": "craft",
                "severity": "hard",
                "principle": "Hard idea.",
                "checks": [],
                "failure_modes": [],
            },
            {
                "id": "genre_card",
                "scope": "craft",
                "severity": "genre-specific",
                "principle": "Genre idea.",
                "checks": [],
                "failure_modes": [],
            },
        ]
    )

    assert lines.index("### Hard Rules") < lines.index("- hard_card: Hard idea.")
    assert lines.index("### Soft Heuristics") < lines.index("- soft_card: Soft idea.")
    assert (
        lines.index("### Genre-Specific Patterns")
        < lines.index("- genre_card: Genre idea.")
    )


def test_builtin_golden_finger_engine_card_is_available():
    card_by_id = {card["id"]: card for card in craft_knowledge.load_craft_cards("brief")}

    card = card_by_id["craft_golden_finger_engine"]
    assert card["severity"] == "hard"
    assert "necessity and uniqueness" in card["principle"]
    assert any("seat at the table" in check for check in card["checks"])
    assert any("Answer necessity" in check for check in card["checks"])
    assert any("cognitive" in check for check in card["checks"])
    assert any("predictable result range" in check for check in card["checks"])
    assert any("controlled uncertainty" in check for check in card["checks"])
    assert any("story's theme" in check for check in card["checks"])
    assert any("same button" in failure.lower() for failure in card["failure_modes"])
    assert any("fully predictable or fully random" in failure for failure in card["failure_modes"])


def test_builtin_character_appeal_engine_card_is_available():
    card_by_id = {card["id"]: card for card in craft_knowledge.load_craft_cards("brief")}

    card = card_by_id["craft_character_appeal_engine"]
    assert card["severity"] == "hard"
    assert "early empathy hooks" in card["principle"]
    assert any("kindness" in check for check in card["checks"])
    assert any("controlled contrast" in card["principle"] for _ in [card])
    assert any("foregrounds cowardice" in failure for failure in card["failure_modes"])
