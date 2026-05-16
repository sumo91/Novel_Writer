from pathlib import Path

import pytest

from engine import book_factory
from engine.io_utils import read_yaml


def test_create_book_copies_templates_and_sets_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")

    created = book_factory.create_book("demo", title="Demo Book")

    assert created == tmp_path / "books" / "demo"
    assert (created / "canon" / "novel_bible.yaml").exists()
    assert (created / "state" / "current_state.json").exists()
    metadata = read_yaml(created / "book.yaml")
    assert metadata["book_id"] == "demo"
    assert metadata["title"] == "Demo Book"
    assert metadata["created_at"]


def test_create_book_includes_v3_state_machine_files(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")

    book = book_factory.create_book("demo", title="Demo Book")

    expected = [
        "canon/character_states.yaml",
        "canon/resource_ledger.yaml",
        "canon/payoff_ledger.yaml",
        "outlines/units/unit_0001.yaml",
        "state/hook_index.json",
        "state/memory_index.json",
    ]
    for relative_path in expected:
        assert (book / relative_path).exists()


def test_create_book_refuses_existing_project(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    with pytest.raises(FileExistsError):
        book_factory.create_book("demo", title="Other")


def test_create_book_force_replaces_existing_project(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    created = book_factory.create_book("demo", title="Demo Book")
    extra_file = created / "extra.txt"
    extra_file.write_text("remove me", encoding="utf-8")

    book_factory.create_book("demo", title="Replacement", force=True)

    assert not extra_file.exists()
    assert read_yaml(created / "book.yaml")["title"] == "Replacement"


def test_create_book_rejects_path_like_book_id(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")

    with pytest.raises(ValueError):
        book_factory.create_book(str(Path("bad") / "id"), title="Bad")
