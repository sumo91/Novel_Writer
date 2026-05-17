import pytest

from engine import book_factory, context_builder


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


def test_build_context_surfaces_missing_book_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")

    with pytest.raises(FileNotFoundError, match="Missing book project: missing"):
        context_builder.build_context("missing", 1)
