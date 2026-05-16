import json

import pytest
import yaml

from engine import book_factory, chapter_acceptance
from engine.io_utils import read_yaml


def test_accept_chapter_applies_update_packet(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("# Chapter One\n\nAccepted text.", encoding="utf-8")
    update_file = book / "state_updates" / "ch_0001_acceptance.yaml"
    update_file.parent.mkdir(exist_ok=True)
    update_file.write_text(
        yaml.safe_dump(
            {
                "chapter": 1,
                "title": "First Signal",
                "source_draft": "drafts/ch_0001_revised.md",
                "summary": "The protagonist finds the first contradiction.",
                "current_state": {
                    "current_arc": "arc_001",
                    "latest_location": "Backstage",
                    "active_characters": ["Lin Zhao"],
                    "active_conflicts": ["Verify the contradiction"],
                    "pending_approvals": ["Define system cost"],
                },
                "state_changes": ["System triggered."],
                "open_threads_touched": ["thread_001"],
                "timeline_event": {
                    "id": "t001",
                    "when": "Chapter 1",
                    "summary": "System triggered backstage.",
                },
                "open_thread_updates": [
                    {
                        "id": "thread_001",
                        "status": "advanced",
                        "latest_note": "The first contradiction appears.",
                    }
                ],
                "change_log": {
                    "summary": "Accepted chapter 1.",
                    "canon_updates": ["timeline:t001"],
                    "pending_approvals": ["Define system cost"],
                },
                "v3_state_updates": {
                    "timeline": {"occurred_events": []},
                    "character_states": [],
                    "resource_changes": [],
                    "open_thread_updates": [],
                    "payoff_updates": [
                        {
                            "chapter": 1,
                            "promises_made": ["The contradiction has a cost."],
                            "payoffs_delivered": ["The system triggered."],
                            "frustration_level": "controlled",
                        }
                    ],
                    "conflict_updates": {"active": []},
                    "next_hook": {
                        "hook": "A stranger recognizes the system trace.",
                        "obligation": "Reveal the stranger's motive.",
                        "target_chapter": 2,
                    },
                    "pending_approvals": [],
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    result = chapter_acceptance.accept_chapter("demo", update_file)

    assert result.chapter_path == book / "chapters" / "ch_0001.md"
    assert result.chapter_path.read_text(encoding="utf-8") == "# Chapter One\n\nAccepted text."
    chapter_index = json.loads((book / "state" / "chapter_index.json").read_text(encoding="utf-8"))
    assert chapter_index["chapters"][0]["title"] == "First Signal"
    current_state = json.loads((book / "state" / "current_state.json").read_text(encoding="utf-8"))
    assert current_state["current_chapter"] == 1
    assert current_state["latest_location"] == "Backstage"
    timeline = read_yaml(book / "canon" / "timeline.yaml")
    assert timeline["events"][0]["id"] == "t001"
    open_threads = read_yaml(book / "canon" / "open_threads.yaml")
    assert open_threads["threads"][0]["status"] == "advanced"
    payoff_ledger = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoff_ledger["entries"][0]["chapter"] == 1
    hook_index = json.loads((book / "state" / "hook_index.json").read_text(encoding="utf-8"))
    assert hook_index["hooks"][0]["chapter"] == 1
    assert "Accepted chapter 1." in (book / "state" / "change_log.jsonl").read_text(encoding="utf-8")


def test_accept_chapter_refuses_to_overwrite_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("new", encoding="utf-8")
    chapter_path = book / "chapters" / "ch_0001.md"
    chapter_path.write_text("existing", encoding="utf-8")
    update_file = book / "state_updates" / "ch_0001_acceptance.yaml"
    update_file.parent.mkdir(exist_ok=True)
    update_file.write_text(
        yaml.safe_dump(
            {
                "chapter": 1,
                "title": "First Signal",
                "source_draft": "drafts/ch_0001_revised.md",
                "summary": "Summary.",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileExistsError):
        chapter_acceptance.accept_chapter("demo", update_file)


def test_accept_chapter_force_replaces_existing_change_log_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted", encoding="utf-8")
    update_file = book / "state_updates" / "ch_0001_acceptance.yaml"
    update_file.parent.mkdir(exist_ok=True)
    update_file.write_text(
        yaml.safe_dump(
            {
                "chapter": 1,
                "title": "First Signal",
                "source_draft": "drafts/ch_0001_revised.md",
                "summary": "Summary.",
                "change_log": {"summary": "Accepted chapter 1."},
            }
        ),
        encoding="utf-8",
    )

    chapter_acceptance.accept_chapter("demo", update_file)
    chapter_acceptance.accept_chapter("demo", update_file, force=True)

    entries = [
        json.loads(line)
        for line in (book / "state" / "change_log.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert entries == [
        {
            "chapter": 1,
            "type": "chapter_acceptance",
            "summary": "Accepted chapter 1.",
            "canon_updates": [],
            "pending_approvals": [],
        }
    ]


def test_accept_chapter_requires_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("draft", encoding="utf-8")
    update_file = book / "state_updates" / "ch_0001_acceptance.yaml"
    update_file.parent.mkdir(exist_ok=True)
    update_file.write_text(
        yaml.safe_dump(
            {
                "chapter": 1,
                "title": "First Signal",
                "source_draft": "drafts/ch_0001_revised.md",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="summary"):
        chapter_acceptance.accept_chapter("demo", update_file)
