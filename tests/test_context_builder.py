import pytest

from engine import book_factory, context_builder, craft_contract, craft_knowledge
from engine.io_utils import write_yaml


def test_build_context_includes_core_book_material(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", knowledge_dir)
    (knowledge_dir / "tomato").mkdir(parents=True)
    (knowledge_dir / "tomato" / "style-rules.md").write_text("Hook fast.", encoding="utf-8")

    created = book_factory.create_book("demo", title="Demo Book")
    (created / "canon" / "novel_bible.yaml").write_text(
        'premise: "A sharp comeback story."\nstory_promise: "Win with wit."\n',
        encoding="utf-8",
    )
    (created / "canon" / "characters.yaml").write_text(
        "characters:\n  - name: Lin Qiao\n    role: protagonist\n",
        encoding="utf-8",
    )

    context = context_builder.build_context("demo", 1)

    assert "# Chapter 0001 Context Pack" in context
    assert "Demo Book" in context
    assert "A sharp comeback story." in context
    assert "Lin Qiao" in context
    assert "style-rules.md" in context
    assert "## Agent Handoff Instructions" in context


def test_build_context_includes_structured_craft_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", knowledge_dir)
    import engine.craft_knowledge as craft_knowledge

    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "agency.yaml").write_text(
        "\n".join(
            [
                "id: craft_agency",
                "scope: craft",
                "applies_to:",
                "  - context",
                "  - brief",
                "use_when: A chapter could become reactive.",
                "principle: Force a visible protagonist choice.",
                "checks:",
                "  - Name the choice.",
                "failure_modes:",
                "  - Passive protagonist",
                "severity: hard",
                "",
            ]
        ),
        encoding="utf-8",
    )
    book_factory.create_book("demo", title="Demo Book")

    context = context_builder.build_context("demo", 1)

    assert "## Craft Knowledge Cards" in context
    assert "craft_agency: Force a visible protagonist choice." in context
    assert "Check: Name the choice." in context


def test_build_context_includes_book_craft_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_contract, "BOOKS_DIR", tmp_path / "books")
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", knowledge_dir)
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "golden.yaml",
        {
            "id": "craft_golden",
            "scope": "craft",
            "applies_to": ["context", "brief"],
            "use_when": "A system creates leverage.",
            "principle": "Make advantage necessary.",
            "checks": ["Name the necessary pressure."],
            "failure_modes": ["Button solves all."],
            "severity": "hard",
        },
    )
    book_factory.create_book("demo", title="Demo Book")
    craft_contract.write_craft_contract_scaffold("demo", force=True)

    context = context_builder.build_context("demo", 1)

    assert "## Book Craft Contract" in context
    assert "craft_golden: Make advantage necessary." in context
    assert "Check: Name the necessary pressure." in context


def test_build_context_includes_existing_workflow_craft_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", knowledge_dir)
    import engine.craft_knowledge as craft_knowledge

    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    card_dir = knowledge_dir / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "brief.yaml").write_text(
        "\n".join(
            [
                "id: craft_brief_agency",
                "scope: craft",
                "applies_to:",
                "  - brief",
                "use_when: A chapter could become reactive.",
                "principle: Force a visible protagonist choice.",
                "checks:",
                "  - Name the choice.",
                "failure_modes:",
                "  - Passive protagonist",
                "severity: hard",
                "",
            ]
        ),
        encoding="utf-8",
    )
    book_factory.create_book("demo", title="Demo Book")

    context = context_builder.build_context("demo", 1)

    assert "### Hard Rules" in context
    assert "craft_brief_agency: Force a visible protagonist choice." in context


def test_build_context_includes_book_style_bible_and_style_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    knowledge_dir = tmp_path / "knowledge"
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", knowledge_dir)
    import engine.style_knowledge as style_knowledge

    monkeypatch.setattr(style_knowledge, "KNOWLEDGE_DIR", knowledge_dir)
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "style" / "style_bible.yaml",
        {
            "book_id": "demo",
            "style_id": "grounded_trade",
            "approval": {"status": "approved"},
            "narration": {"pace": "fast but grounded"},
            "dialogue": {"density": "medium-high"},
            "protagonist_voice": {"chen_an": "shopkeeper, not overlord"},
            "payoff_style": {"pattern": "small gain creates larger risk"},
            "banned_patterns": ["generic inner monologue"],
            "style_cards": ["style_grounded_trade"],
        },
    )
    card_dir = knowledge_dir / "style_cards"
    card_dir.mkdir(parents=True)
    write_yaml(
        card_dir / "grounded_trade.yaml",
        {
            "id": "style_grounded_trade",
            "scope": "style",
            "applies_to": ["context", "draft"],
            "use_when": "Trading scenes carry pressure.",
            "principle": "Use concrete goods and prices to carry tension.",
            "checks": ["Name the trade pressure."],
            "failure_modes": ["Abstract negotiation"],
            "severity": "soft",
        },
    )

    context = context_builder.build_context("demo", 1)

    assert "## Style Bible" in context
    assert "fast but grounded" in context
    assert "generic inner monologue" in context
    assert "## Style Cards" in context
    assert "style_grounded_trade: Use concrete goods and prices to carry tension." in context


def test_build_context_returns_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")

    context = context_builder.build_context("demo", 1)

    assert context.startswith("# ")
    assert "```yaml" in context
    assert "```json" in context


def test_build_context_includes_v3_memory_ledgers(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")

    created = book_factory.create_book("demo", title="Demo Book")
    (created / "canon" / "payoff_ledger.yaml").write_text(
        "promises:\n  - promise: The midnight bell must be answered.\n",
        encoding="utf-8",
    )
    (created / "outlines" / "units").mkdir(parents=True, exist_ok=True)
    (created / "outlines" / "units" / "unit_0001.yaml").write_text(
        "unit_goal: Keep the shop alive through the first ten chapters.\n",
        encoding="utf-8",
    )
    (created / "state" / "hook_index.json").write_text(
        '{\n  "hooks": ["The back door glows before midnight."]\n}\n',
        encoding="utf-8",
    )

    context = context_builder.build_context("demo", 2)

    assert "## Payoff Ledger" in context
    assert "The midnight bell must be answered." in context
    assert "## Hook Index" in context
    assert "The back door glows before midnight." in context
    assert "## Unit Plan" in context
    assert "Keep the shop alive through the first ten chapters." in context


def test_build_context_includes_v3_1_outline_layers_and_reference_chain(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")

    created = book_factory.create_book("demo", title="Demo Book")
    (created / "outlines" / "master_outline.yaml").write_text(
        "logline: Master promise.\napproval:\n  status: approved\n",
        encoding="utf-8",
    )
    (created / "outlines" / "volumes" / "volume_001.yaml").write_text(
        "\n".join(
            [
                "volume_id: volume_001",
                "chapter_range:",
                "  start: 1",
                "  end: 50",
                "volume_goal: First volume goal.",
                "approval:",
                "  status: draft",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (created / "outlines" / "arc_001.yaml").write_text(
        "arc_id: arc_001\nchapter_range:\n  start: 1\n  end: 20\narc_goal: First arc goal.\n",
        encoding="utf-8",
    )
    (created / "outlines" / "units" / "unit_0001.yaml").write_text(
        "unit: 1\nchapter_range:\n  start: 1\n  end: 10\nunit_goal: First unit goal.\n",
        encoding="utf-8",
    )
    (created / "canon" / "economy.yaml").write_text(
        "currencies:\n  - id: spirit_fragment\n    name: 碎灵\n",
        encoding="utf-8",
    )
    (created / "canon" / "factions.yaml").write_text(
        "factions:\n  - id: pill_shop\n    name: 回春丹铺\n",
        encoding="utf-8",
    )

    context = context_builder.build_context("demo", 5)

    assert "## Outline Reference Chain" in context
    assert "master -> volume_001 -> arc_001 -> unit_0001 -> chapter_0005" in context
    assert "## Master Outline" in context
    assert "Master promise." in context
    assert "## Current Volume" in context
    assert "First volume goal." in context
    assert "draft assumption" in context
    assert "## Current Arc" in context
    assert "First arc goal." in context
    assert "## Current Unit" in context
    assert "First unit goal." in context
    assert "## Economy" in context
    assert "spirit_fragment" in context
    assert "## Factions" in context
    assert "回春丹铺" in context


def test_build_context_surfaces_missing_book_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")

    with pytest.raises(FileNotFoundError, match="Missing book project: missing"):
        context_builder.build_context("missing", 1)
