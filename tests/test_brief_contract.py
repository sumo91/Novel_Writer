from engine import book_factory, brief_contract, craft_knowledge, outline_gate
from engine.io_utils import write_json, write_yaml


def test_build_chapter_brief_scaffold_includes_outline_and_state_contract(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_contract_fixture(book)

    scaffold = brief_contract.build_chapter_brief_scaffold("demo", 5)

    assert "# Chapter 5 Brief Scaffold" in scaffold
    assert "## V3.3 Outline Contract" in scaffold
    assert "master -> volume -> arc -> unit -> chapter brief" in scaffold
    assert "volume_001: Keep the shop alive." in scaffold
    assert "arc_001: Establish first trade rules." in scaffold
    assert "unit_0001: Turn pressure into rules." in scaffold
    assert "Chapter 5 function:赵掌柜 tests the price rules." in scaffold
    assert "thread_0004_pill_shop_exclusive_pressure" in scaffold
    assert "Pay off negotiation pressure." in scaffold
    assert "Last hook: Zhao comes in person." in scaffold
    assert "spirit_fragment" in scaffold
    assert "huichun_pill_shop" in scaffold
    assert "## State Update Expectations" in scaffold


def test_build_chapter_brief_scaffold_includes_applicable_craft_cards(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_contract_fixture(book)
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "agency.yaml").write_text(
        "\n".join(
            [
                "id: craft_agency_001",
                "applies_to: [brief]",
                "principle: Force a visible protagonist choice.",
                "checks:",
                "  - Name the choice and pressure.",
                "failure_modes:",
                "  - Passive protagonist",
                "",
            ]
        ),
        encoding="utf-8",
    )

    scaffold = brief_contract.build_chapter_brief_scaffold("demo", 5)

    assert "## Craft Knowledge Cards" in scaffold
    assert "craft_agency_001" in scaffold
    assert "Force a visible protagonist choice." in scaffold
    assert "Name the choice and pressure." in scaffold


def test_build_chapter_brief_scaffold_shows_craft_card_metadata(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_contract_fixture(book)
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "brief.yaml").write_text(
        "\n".join(
            [
                "id: craft_brief_passive",
                "scope: craft",
                "applies_to: [brief]",
                "use_when: A chapter risks becoming reactive.",
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

    scaffold = brief_contract.build_chapter_brief_scaffold("demo", 5)

    assert "  - Scope: craft" in scaffold
    assert "  - Severity: hard" in scaffold


def test_check_chapter_brief_reports_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = brief_contract.check_chapter_brief("demo", 5)

    assert result["passed"] is False
    assert result["status"] == "missing"
    assert "Missing chapter brief" in result["errors"][0]


def test_check_chapter_brief_rejects_missing_contract_sections(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    brief = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text("# Chapter 5\n\nToo thin.\n", encoding="utf-8")

    result = brief_contract.check_chapter_brief("demo", 5)

    assert result["passed"] is False
    assert "Missing required section: ## V3.3 Outline Contract" in result["errors"]
    assert "Missing required section: ## State Update Expectations" in result["errors"]


def test_check_chapter_brief_accepts_generated_scaffold(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_contract_fixture(book)
    brief = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(
        brief_contract.build_chapter_brief_scaffold("demo", 5),
        encoding="utf-8",
    )

    result = brief_contract.check_chapter_brief("demo", 5)

    assert result["passed"] is True
    assert result["errors"] == []


def _write_contract_fixture(book):
    write_yaml(
        book / "outlines" / "volumes" / "volume_001.yaml",
        {
            "volume_id": "volume_001",
            "chapter_range": {"start": 1, "end": 50},
            "volume_goal": "Keep the shop alive.",
            "approval": {"status": "approved"},
        },
    )
    write_yaml(
        book / "outlines" / "arc_001.yaml",
        {
            "arc_id": "arc_001",
            "chapter_range": {"start": 1, "end": 20},
            "arc_goal": "Establish first trade rules.",
            "required_threads": ["thread_0004_pill_shop_exclusive_pressure"],
            "approval": {"status": "approved"},
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {
            "unit": 1,
            "chapter_range": {"start": 1, "end": 10},
            "unit_goal": "Turn pressure into rules.",
            "chapters": [
                {
                    "chapter": 5,
                    "function": "赵掌柜 tests the price rules.",
                    "opening_hook": "Zhao comes in person.",
                    "main_payoff": "Chen sets terms.",
                    "next_hook": "Ledger clue deepens.",
                    "state_obligation": ["Update pill-shop pressure."],
                }
            ],
            "approval": {"status": "approved"},
        },
    )
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_0004_pill_shop_exclusive_pressure",
                    "promise": "Pill shop wants exclusive supply.",
                    "status": "open",
                    "source_chapter": 4,
                    "last_touched": 4,
                }
            ]
        },
    )
    write_yaml(
        book / "canon" / "payoff_ledger.yaml",
        {"entries": [{"chapter": 5, "promises_made": ["Pay off negotiation pressure."]}]},
    )
    write_json(
        book / "state" / "hook_index.json",
        {"hooks": [{"chapter": 4, "text": "Last hook: Zhao comes in person.", "status": "open"}]},
    )
    write_yaml(
        book / "canon" / "economy.yaml",
        {"currencies": [{"id": "spirit_fragment"}], "approval": {"status": "approved"}},
    )
    write_yaml(
        book / "canon" / "factions.yaml",
        {"factions": [{"id": "huichun_pill_shop"}], "approval": {"status": "approved"}},
    )
