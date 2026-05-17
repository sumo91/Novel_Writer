from engine import book_factory, validators
from engine.hardening import validate_acceptance_packet
from engine.io_utils import write_json, write_yaml


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


def test_validate_book_requires_v3_files(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "canon" / "payoff_ledger.yaml").unlink()

    errors = validators.validate_book("demo")

    assert "Missing required file: canon/payoff_ledger.yaml" in errors


def test_validate_acceptance_packet_requires_v3_state_updates():
    errors = validate_acceptance_packet(
        {
            "chapter": 1,
            "title": "First",
            "source_draft": "drafts/ch_0001_revised.md",
            "accepted_chapter_path": "chapters/ch_0001.md",
            "summary": "Summary.",
            "current_state": {
                "current_chapter": 1,
                "current_arc": "arc_001",
                "latest_location": "",
                "active_characters": [],
                "active_conflicts": [],
                "pending_approvals": [],
            },
            "state_changes": [],
            "open_threads_touched": [],
            "timeline_event": {"id": "t001", "when": "Chapter 1", "summary": "Summary."},
            "open_thread_updates": [],
            "change_log": {"summary": "Accepted.", "canon_updates": [], "pending_approvals": []},
        },
        chapter_number=1,
    )

    assert "Acceptance packet is missing fields: v3_state_updates." in errors


def test_validate_acceptance_packet_rejects_falsey_non_mapping_v3_timeline():
    errors = validate_acceptance_packet(
        _valid_acceptance_packet(
            {
                "timeline": [],
                "character_states": [],
                "resource_changes": [],
                "open_thread_updates": [],
                "payoff_updates": [
                    {
                        "frustration_level": "controlled",
                        "promises_made": ["Promise."],
                        "payoffs_delivered": [],
                    }
                ],
                "conflict_updates": {"active": []},
                "next_hook": {},
                "pending_approvals": [],
            }
        ),
        chapter_number=1,
    )

    assert "v3_state_updates.timeline must be a mapping." in errors


def test_validate_acceptance_packet_rejects_non_mapping_conflict_updates():
    errors = validate_acceptance_packet(
        _valid_acceptance_packet(
            {
                "timeline": {},
                "character_states": [],
                "resource_changes": [],
                "open_thread_updates": [],
                "payoff_updates": [
                    {
                        "frustration_level": "controlled",
                        "promises_made": ["Promise."],
                        "payoffs_delivered": [],
                    }
                ],
                "conflict_updates": [],
                "next_hook": {},
                "pending_approvals": [],
            }
        ),
        chapter_number=1,
    )

    assert "v3_state_updates.conflict_updates must be a mapping." in errors


def test_validate_acceptance_packet_rejects_non_list_active_conflict_updates():
    errors = validate_acceptance_packet(
        _valid_acceptance_packet(
            {
                "timeline": {},
                "character_states": [],
                "resource_changes": [],
                "open_thread_updates": [],
                "payoff_updates": [
                    {
                        "frustration_level": "controlled",
                        "promises_made": ["Promise."],
                        "payoffs_delivered": [],
                    }
                ],
                "conflict_updates": {"active": "bad"},
                "next_hook": {},
                "pending_approvals": [],
            }
        ),
        chapter_number=1,
    )

    assert "v3_state_updates.conflict_updates.active must be a list." in errors


def test_validate_book_rejects_invalid_open_thread_status(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_0001_01",
                    "promise": "Promise.",
                    "source_chapter": 1,
                    "status": "maybe",
                    "last_touched": 1,
                    "next_obligation": "Answer soon.",
                    "payoff_deadline": 3,
                    "risk_if_ignored": "Reader forgets.",
                }
            ]
        },
    )

    errors = validators.validate_book("demo")

    assert any("open_threads.yaml" in error and "status" in error for error in errors)


def test_validate_book_rejects_invalid_payoff_and_resource_ledgers(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "canon" / "payoff_ledger.yaml",
        {"entries": [{"chapter": 1, "frustration_level": "wild"}]},
    )
    write_yaml(
        book / "canon" / "resource_ledger.yaml",
        {
            "resources": [
                {
                    "id": "res_001",
                    "owner": "protagonist",
                    "name": "Shop cash",
                    "category": "vibes",
                    "last_updated_chapter": 1,
                }
            ]
        },
    )

    errors = validators.validate_book("demo")

    assert any("payoff_ledger.yaml" in error and "frustration_level" in error for error in errors)
    assert any("resource_ledger.yaml" in error and "category" in error for error in errors)


def test_validate_book_rejects_invalid_hook_and_memory_indexes(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(book / "state" / "hook_index.json", {"hooks": [{"status": "maybe"}]})
    write_json(book / "state" / "memory_index.json", {"by_character": {}})

    errors = validators.validate_book("demo")

    assert any("hook_index.json" in error and "status" in error for error in errors)
    assert any("memory_index.json" in error and "by_thread" in error for error in errors)


def test_validate_book_reports_malformed_v3_ledger_and_index_roots(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(book / "canon" / "payoff_ledger.yaml", [])
    write_json(book / "state" / "hook_index.json", [])

    errors = validators.validate_book("demo")

    assert "canon/payoff_ledger.yaml: root must be a mapping." in errors
    assert "state/hook_index.json: root must be a mapping." in errors


def test_validate_score_accepts_only_zero_to_one_hundred():
    assert validators.validate_score(0)
    assert validators.validate_score(100)
    assert not validators.validate_score(-1)
    assert not validators.validate_score(101)


def _valid_acceptance_packet(v3_state_updates):
    return {
        "chapter": 1,
        "title": "First",
        "source_draft": "drafts/ch_0001_revised.md",
        "accepted_chapter_path": "chapters/ch_0001.md",
        "summary": "Summary.",
        "current_state": {
            "current_chapter": 1,
            "current_arc": "arc_001",
            "latest_location": "",
            "active_characters": [],
            "active_conflicts": [],
            "pending_approvals": [],
        },
        "state_changes": [],
        "open_threads_touched": [],
        "timeline_event": {"id": "t001", "when": "Chapter 1", "summary": "Summary."},
        "open_thread_updates": [],
        "change_log": {"summary": "Accepted.", "canon_updates": [], "pending_approvals": []},
        "v3_state_updates": v3_state_updates,
    }
