from engine import book_factory, validators


def test_freshly_initialized_book_validates(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    assert validators.validate_book("demo") == []


def test_validate_book_reports_missing_required_file(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    created = book_factory.create_book("demo", title="Demo Book")
    (created / "canon" / "novel_bible.yaml").unlink()

    errors = validators.validate_book("demo")

    assert "Missing required file: canon/novel_bible.yaml" in errors


def test_validate_score_accepts_only_zero_to_one_hundred():
    assert validators.validate_score(0)
    assert validators.validate_score(100)
    assert not validators.validate_score(-1)
    assert not validators.validate_score(101)
