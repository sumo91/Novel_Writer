from engine import book_factory, style_knowledge
from engine.io_utils import read_yaml, write_yaml


def test_style_bible_scaffold_writes_book_local_style_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    output = style_knowledge.write_style_bible_scaffold("demo", force=True)

    data = read_yaml(output)
    assert output == book / "style" / "style_bible.yaml"
    assert data["book_id"] == "demo"
    assert data["approval"]["status"] == "draft"
    assert "narration" in data
    assert "banned_patterns" in data
    assert output.with_suffix(".html").exists()


def test_style_bible_check_reports_missing_required_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(book / "style" / "style_bible.yaml", {"book_id": "demo"})

    result = style_knowledge.check_style_bible("demo")

    assert result["passed"] is False
    assert "style/style_bible.yaml: missing required field narration." in result["errors"]
    assert "style/style_bible.yaml: approval must be a mapping." in result["errors"]


def test_style_calibration_scaffold_writes_book_local_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    output = style_knowledge.write_style_calibration_scaffold("demo", force=True)

    data = read_yaml(output)
    assert output == book / "style" / "calibration" / "style_calibration.yaml"
    assert data["book_id"] == "demo"
    assert data["approval"]["status"] == "draft"
    assert "base_profiles" in data
    assert "approved_patterns" in data
    assert "rejected_patterns" in data
    assert output.with_suffix(".html").exists()


def test_style_calibration_check_reports_missing_required_fields(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    path = book / "style" / "calibration" / "style_calibration.yaml"
    write_yaml(path, {"book_id": "demo"})

    result = style_knowledge.check_style_calibration("demo")

    assert result["passed"] is False
    assert (
        "style/calibration/style_calibration.yaml: missing required field base_profiles."
        in result["errors"]
    )
    assert (
        "style/calibration/style_calibration.yaml: approval must be a mapping."
        in result["errors"]
    )


def test_load_style_cards_filters_by_application(tmp_path, monkeypatch):
    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    card_dir = tmp_path / "knowledge" / "style_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "grounded_trade.yaml",
        {
            "id": "style_grounded_trade",
            "scope": "style",
            "applies_to": ["context", "draft"],
            "use_when": "Trading scenes need grounded details.",
            "principle": "Use prices, goods, and negotiation moves to carry tension.",
            "checks": ["Name the trade pressure."],
            "failure_modes": ["Abstract business talk"],
            "severity": "soft",
        },
    )
    write_yaml(
        card_dir / "drift_only.yaml",
        {
            "id": "style_drift_only",
            "scope": "style",
            "applies_to": ["drift"],
            "use_when": "Reviewing drift.",
            "principle": "Review long-term voice drift.",
            "checks": ["Compare chapters."],
            "failure_modes": ["Voice drift"],
            "severity": "soft",
        },
    )

    cards = style_knowledge.load_style_cards("context")

    assert [card["id"] for card in cards] == ["style_grounded_trade"]


def test_validate_style_cards_reports_schema_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    card_dir = tmp_path / "knowledge" / "style_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "broken.yaml",
        {
            "id": "",
            "applies_to": "context",
            "severity": "extreme",
        },
    )

    errors = style_knowledge.validate_style_cards()

    assert "style_cards/broken.yaml: id is required." in errors
    assert "style_cards/broken.yaml: applies_to must be a list." in errors
    assert (
        "style_cards/broken.yaml: severity must be hard, soft, or genre-specific."
        in errors
    )


def test_load_style_profiles_reads_abstract_profile_library(tmp_path, monkeypatch):
    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    profile_dir = tmp_path / "knowledge" / "style_profiles"
    profile_dir.mkdir(parents=True)
    write_yaml(
        profile_dir / "grounded_trade.yaml",
        {
            "id": "grounded_trade",
            "label": "Grounded Trade",
            "use_when": "A story uses concrete commerce and resource pressure.",
            "narration": {"pace": "fast but grounded"},
            "dialogue": {"density": "medium-high"},
            "protagonist_voice": {"default": "practical"},
            "payoff_style": {"pattern": "small gain creates larger pressure"},
            "banned_patterns": ["generic dominance voice"],
            "style_cards": ["style_grounded_trade"],
            "calibration_prompts": ["Write a 500-word negotiation sample."],
        },
    )

    profiles = style_knowledge.load_style_profiles()

    assert [profile["id"] for profile in profiles] == ["grounded_trade"]
    assert profiles[0]["source"] == "style_profiles/grounded_trade.yaml"


def test_write_style_bible_from_profile_writes_book_local_contract(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    profile_dir = tmp_path / "knowledge" / "style_profiles"
    profile_dir.mkdir(parents=True)
    write_yaml(
        profile_dir / "grounded_trade.yaml",
        {
            "id": "grounded_trade",
            "label": "Grounded Trade",
            "use_when": "A story uses concrete commerce and resource pressure.",
            "narration": {"pace": "fast but grounded", "texture": "specific objects"},
            "dialogue": {"density": "medium-high", "tension_source": "prices"},
            "protagonist_voice": {"default": "practical"},
            "payoff_style": {"pattern": "small gain creates larger pressure"},
            "banned_patterns": ["generic dominance voice"],
            "style_cards": ["style_grounded_trade"],
            "calibration_prompts": ["Write a 500-word negotiation sample."],
        },
    )

    output = style_knowledge.write_style_bible_from_profile(
        "demo", "grounded_trade", force=True
    )

    data = read_yaml(output)
    assert output == book / "style" / "style_bible.yaml"
    assert data["style_id"] == "demo_grounded_trade"
    assert data["profile_id"] == "grounded_trade"
    assert data["narration"]["pace"] == "fast but grounded"
    assert data["style_cards"] == ["style_grounded_trade"]
    assert output.with_suffix(".html").exists()


def test_validate_style_profiles_reports_schema_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    profile_dir = tmp_path / "knowledge" / "style_profiles"
    profile_dir.mkdir(parents=True)
    write_yaml(
        profile_dir / "broken.yaml",
        {
            "id": "",
            "narration": "fast",
            "style_cards": "style_grounded_trade",
        },
    )

    errors = style_knowledge.validate_style_profiles()

    assert "style_profiles/broken.yaml: id is required." in errors
    assert "style_profiles/broken.yaml: narration must be a mapping." in errors
    assert "style_profiles/broken.yaml: style_cards must be a list." in errors


def test_builtin_rule_survival_suspense_assets_are_available():
    profiles = style_knowledge.load_style_profiles()
    profile_by_id = {profile["id"]: profile for profile in profiles}

    profile = profile_by_id["rule_survival_suspense"]
    assert profile["label"] == "规则生存悬疑风"
    assert profile["english_label"] == "Rule Survival Suspense"
    assert profile["style_cards"] == [
        "style_question_chain",
        "style_rule_pressure",
        "style_dialogue_as_probe",
        "style_hook_with_consequence",
        "style_scene_specificity",
    ]

    card_ids = {card["id"] for card in style_knowledge.load_style_cards("review")}
    assert {
        "style_question_chain",
        "style_rule_pressure",
        "style_dialogue_as_probe",
        "style_hook_with_consequence",
    }.issubset(card_ids)


def test_builtin_expanded_style_profiles_are_available():
    profiles = style_knowledge.load_style_profiles()
    profile_by_id = {profile["id"]: profile for profile in profiles}

    expected_profiles = {
        "warm_daily_life": ("温暖日常风", "Warm Daily Life"),
        "sharp_face_slap": ("锋利打脸风", "Sharp Face Slap"),
        "mythic_xianxia": ("仙侠气象风", "Mythic Xianxia"),
        "comic_lightweight": ("轻喜剧风", "Comic Lightweight"),
        "folk_story_digest": ("故事会式民间短篇风", "Folk Story Digest"),
        "gentle_local_life": ("清淡市井风", "Gentle Local Life"),
        "slow_burn_occult_investigation": (
            "慢热诡秘调查风",
            "Slow-Burn Occult Investigation",
        ),
        "ritual_power_system": ("仪式化力量体系风", "Ritual Power System"),
    }

    for profile_id, (label, english_label) in expected_profiles.items():
        assert profile_by_id[profile_id]["label"] == label
        assert profile_by_id[profile_id]["english_label"] == english_label
        assert profile_by_id[profile_id]["style_cards"]
        assert profile_by_id[profile_id]["calibration_prompts"]

    card_ids = {card["id"] for card in style_knowledge.load_style_cards("review")}
    assert {
        "style_warm_specificity",
        "style_face_slap_escalation",
        "style_mythic_consequence",
        "style_comic_timing",
        "style_folk_reversal",
        "style_plain_life_observation",
        "style_layered_revelation",
        "style_daily_uncanny_contrast",
        "style_power_with_cost",
    }.issubset(card_ids)


def test_builtin_popular_reference_style_profiles_are_available():
    profiles = style_knowledge.load_style_profiles()
    profile_by_id = {profile["id"]: profile for profile in profiles}

    expected_profiles = {
        "cautious_two_world_resource": (
            "苟道资源经营风",
            "Cautious Two-World Resource",
        ),
        "civilization_building_ensemble": (
            "文明建设群像风",
            "Civilization Building Ensemble",
        ),
        "frontier_office_wasteland": (
            "职能权力废土风",
            "Frontier Office Wasteland",
        ),
        "lineage_clan_cultivation": (
            "家族谱系修仙风",
            "Lineage Clan Cultivation",
        ),
        "sharp_sword_action": ("锋利剑修动作风", "Sharp Sword Action"),
    }

    for profile_id, (label, english_label) in expected_profiles.items():
        assert profile_by_id[profile_id]["label"] == label
        assert profile_by_id[profile_id]["english_label"] == english_label
        assert profile_by_id[profile_id]["style_cards"]
        assert profile_by_id[profile_id]["calibration_prompts"]

    card_ids = {card["id"] for card in style_knowledge.load_style_cards("review")}
    assert {
        "style_risk_ledger_growth",
        "style_systemic_payoff",
        "style_official_power_pressure",
        "style_lineage_memory",
        "style_sword_action_pressure",
    }.issubset(card_ids)
