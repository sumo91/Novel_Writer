import pytest

from engine import book_factory, reader_panel
from engine.io_utils import read_json


def test_reader_panel_scaffold_writes_json_and_html(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(reader_panel, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    output = reader_panel.write_reader_panel_review_scaffold("demo", 1)

    assert output == book / "reviews" / "ch_0001" / "reader_panel_review.json"
    assert output.exists()
    assert output.with_suffix(".html").exists()
    data = read_json(output)
    assert data["book_id"] == "demo"
    assert data["chapter"] == 1
    assert data["canon_status"] == "non_canon_feedback"
    assert data["blocks_acceptance"] is False
    assert [persona["id"] for persona in data["simulated_personas"]] == [
        "payoff_reader",
        "binge_reader",
        "setting_logic_reader",
        "emotional_reader",
        "dropoff_risk_reader",
    ]
    assert data["aggregate_findings"]["recommended_revision_priority"] == []


def test_reader_panel_scaffold_refuses_existing_file_without_force(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(reader_panel, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")
    reader_panel.write_reader_panel_review_scaffold("demo", 1)

    with pytest.raises(FileExistsError):
        reader_panel.write_reader_panel_review_scaffold("demo", 1)


def test_reader_panel_scaffold_requires_book(tmp_path, monkeypatch):
    monkeypatch.setattr(reader_panel, "BOOKS_DIR", tmp_path / "books")

    with pytest.raises(FileNotFoundError):
        reader_panel.write_reader_panel_review_scaffold("missing", 1)
