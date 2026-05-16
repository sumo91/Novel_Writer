from engine import book_factory, v3_migration
from engine.io_utils import read_json, read_yaml, write_json, write_yaml


V3_PATHS = [
    "canon/character_states.yaml",
    "canon/resource_ledger.yaml",
    "canon/payoff_ledger.yaml",
    "outlines/units/unit_0001.yaml",
    "state/hook_index.json",
    "state/memory_index.json",
]


def test_migrate_book_to_v3_creates_missing_files_without_inference(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    for relative_path in V3_PATHS:
        (book / relative_path).unlink()
    preserved_path = book / "canon" / "resource_ledger.yaml"
    preserved_path.parent.mkdir(parents=True, exist_ok=True)
    preserved_path.write_text("resources:\n- id: existing\n", encoding="utf-8")
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {
                    "chapter": 1,
                    "state_changes": ["Do not infer this into V3 canon."],
                }
            ]
        },
    )

    result = v3_migration.migrate_book_to_v3("demo")

    assert result.book_id == "demo"
    assert result.created == [
        "canon/character_states.yaml",
        "canon/payoff_ledger.yaml",
        "outlines/units/unit_0001.yaml",
        "state/hook_index.json",
        "state/memory_index.json",
    ]
    assert result.updated == []
    assert preserved_path.read_text(encoding="utf-8") == "resources:\n- id: existing\n"
    assert read_json(book / "state" / "hook_index.json") == {"hooks": []}
    created_text = "\n".join(
        (book / relative_path).read_text(encoding="utf-8")
        for relative_path in result.created
    )
    assert "Do not infer this into V3 canon." not in created_text


def test_migrate_book_to_v3_preserves_existing_open_threads(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_001",
                    "text": "Grandfather's debt is unresolved.",
                    "status": "active",
                    "custom_field": "keep me",
                }
            ]
        },
    )

    result = v3_migration.migrate_book_to_v3("demo")

    threads = read_yaml(book / "canon" / "open_threads.yaml")["threads"]
    assert result.created == []
    assert result.updated == ["canon/open_threads.yaml"]
    assert threads == [
        {
            "id": "thread_001",
            "text": "Grandfather's debt is unresolved.",
            "status": "active",
            "custom_field": "keep me",
            "promise": "",
            "source_chapter": "",
            "last_touched": "",
            "next_obligation": "",
            "payoff_deadline": "",
            "risk_if_ignored": "",
            "related_characters": [],
            "related_locations": [],
            "payoff_chapter": "",
            "notes": [],
        }
    ]
