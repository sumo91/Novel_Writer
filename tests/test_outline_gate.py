import pytest

from engine import book_factory, outline_gate
from engine.io_utils import read_yaml


def test_get_outline_status_reports_v3_1_layers(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    status = outline_gate.get_outline_status("demo")

    assert [layer["layer"] for layer in status["layers"]] == [
        "master",
        "volume",
        "arc",
        "unit",
        "economy",
        "factions",
    ]
    assert {layer["approval_status"] for layer in status["layers"]} == {"draft"}
    assert all(layer["exists"] for layer in status["layers"])


def test_update_outline_approval_updates_only_target_layer(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    updated = outline_gate.update_outline_approval(
        "demo",
        "unit",
        status="approved",
        note="Approved for chapter 5 planning.",
    )

    unit = read_yaml(book / "outlines" / "units" / "unit_0001.yaml")
    master = read_yaml(book / "outlines" / "master_outline.yaml")
    assert updated["layer"] == "unit"
    assert unit["approval"]["status"] == "approved"
    assert unit["approval"]["note"] == "Approved for chapter 5 planning."
    assert master["approval"]["status"] == "draft"


def test_update_outline_approval_preserves_non_approval_text_format(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    path = book / "outlines" / "master_outline.yaml"
    before = path.read_text(encoding="utf-8")
    before_prefix = before.split("approval:", maxsplit=1)[0]

    outline_gate.update_outline_approval(
        "demo",
        "master",
        status="approved",
        note="Format should stay quiet.",
    )

    after = path.read_text(encoding="utf-8")
    after_prefix = after.split("approval:", maxsplit=1)[0]
    assert after_prefix == before_prefix
    assert "  status: approved" in after
    assert "  note: Format should stay quiet." in after


def test_update_outline_approval_rejects_invalid_layer_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    with pytest.raises(ValueError, match="Unknown outline layer"):
        outline_gate.update_outline_approval("demo", "mystery", status="approved")

    with pytest.raises(ValueError, match="Invalid approval status"):
        outline_gate.update_outline_approval("demo", "unit", status="maybe")


def test_chapter_brief_gate_warns_for_drafts_in_default_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = outline_gate.chapter_brief_gate("demo", 5)

    assert result["allowed"] is True
    assert result["blocking_errors"] == []
    assert any("draft assumption" in warning for warning in result["warnings"])


def test_chapter_brief_gate_blocks_drafts_in_strict_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = outline_gate.chapter_brief_gate("demo", 5, strict=True)

    assert result["allowed"] is False
    assert any("is draft, not approved" in error for error in result["blocking_errors"])


def test_chapter_brief_gate_blocks_missing_v3_1_file(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "canon" / "economy.yaml").unlink()

    result = outline_gate.chapter_brief_gate("demo", 5)

    assert result["allowed"] is False
    assert "Missing V3.1 layer file: canon/economy.yaml" in result["blocking_errors"]
