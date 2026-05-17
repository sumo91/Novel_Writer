from engine import book_factory, craft_knowledge, validators
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


def test_validate_book_requires_v3_1_outline_files(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "outlines" / "volumes" / "volume_001.yaml").unlink()
    (book / "canon" / "economy.yaml").unlink()
    (book / "canon" / "factions.yaml").unlink()

    errors = validators.validate_book("demo")

    assert "Missing required file: outlines/volumes/volume_001.yaml" in errors
    assert "Missing required file: canon/economy.yaml" in errors
    assert "Missing required file: canon/factions.yaml" in errors


def test_validate_book_rejects_invalid_v3_1_outline_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "outlines" / "master_outline.yaml",
        {
            "logline": "Missing most V3.1 fields.",
            "approval": {"status": "maybe"},
        },
    )
    write_yaml(
        book / "outlines" / "volumes" / "volume_001.yaml",
        {
            "volume_id": "volume_001",
            "chapter_range": {"start": "one", "end": 50},
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "arc_001.yaml",
        {
            "arc_id": "arc_001",
            "chapter_range": {"start": 1, "end": 20},
            "parent_volume": "volume_missing",
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {
            "unit": 1,
            "chapter_range": {"start": 1, "end": 10},
            "parent_arc": "arc_001",
            "chapters": [{"chapter": 11}],
            "approval": {"status": "draft"},
        },
    )
    write_yaml(book / "canon" / "economy.yaml", [])
    write_yaml(book / "canon" / "factions.yaml", {"factions": {}, "approval": {"status": "draft"}})

    errors = validators.validate_book("demo")

    assert "outlines/master_outline.yaml: missing required field opening_state." in errors
    assert "outlines/master_outline.yaml: approval.status must be draft, approved, rejected, or superseded." in errors
    assert "outlines/volumes/volume_001.yaml: chapter_range.start must be an integer." in errors
    assert "outlines/arc_001.yaml: parent_volume volume_missing does not exist." in errors
    assert "outlines/units/unit_0001.yaml: chapters[1].chapter must fit inside chapter_range." in errors
    assert "canon/economy.yaml: root must be a mapping." in errors
    assert "canon/factions.yaml: factions must be a list." in errors


def test_validate_book_reports_invalid_craft_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "broken.yaml").write_text(
        "\n".join(
            [
                "id: craft_broken",
                "scope: craft",
                "applies_to: []",
                "use_when: Test.",
                "principle: Test.",
                "checks: []",
                "failure_modes: []",
                "severity: extreme",
                "",
            ]
        ),
        encoding="utf-8",
    )

    errors = validators.validate_book("demo")

    assert (
        "knowledge/craft_cards/broken.yaml: severity must be hard, soft, or genre-specific."
        in errors
    )


def test_validate_book_rejects_chapter_brief_missing_v3_1_reference_chain(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    brief = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(
        "# Chapter 5 Brief\n\nThis chapter has a hook but no long-form reference chain.\n",
        encoding="utf-8",
    )

    errors = validators.validate_book("demo")

    assert (
        "outlines/chapter_briefs/ch_0005_brief.md: Chapter brief must cite "
        "`master -> volume -> arc -> unit`."
    ) in errors
    assert (
        "outlines/chapter_briefs/ch_0005_brief.md: Chapter brief must describe "
        "outline obligations."
    ) in errors


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
            "acceptance_contract": {
                "quality_gate_summary": {
                    "continuity_review_present": True,
                    "continuity_blockers": [],
                    "pacing_review_present": True,
                    "pacing_score": 86,
                    "revised_pacing_score": 86,
                    "revision_required": False,
                    "waiver_required": False,
                },
                "outline_alignment": {
                    "reference_chain": "master -> volume -> arc -> unit -> chapter brief",
                    "volume_id": "volume_001",
                    "arc_id": "arc_001",
                    "unit_id": "unit_0001",
                    "required_unit_obligations": [],
                    "claimed_fulfilled_unit_obligations": [],
                    "pending_unit_obligations": [],
                },
                "state_updates": {
                    "timeline_event": {
                        "id": "t001",
                        "when": "Chapter 1",
                        "summary": "Summary.",
                    },
                    "character_state_changes": [],
                    "resource_changes": [],
                    "open_thread_updates": [],
                    "payoff_updates": [],
                    "next_hook": {},
                    "pending_approvals": [],
                    "economy_changes": [],
                    "faction_changes": [],
                },
            },
        },
        chapter_number=1,
    )

    assert "Acceptance packet is missing fields: v3_state_updates." in errors


def test_validate_acceptance_packet_requires_acceptance_contract():
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
                "conflict_updates": {"active": []},
                "next_hook": {},
                "pending_approvals": [],
            },
            include_acceptance_contract=False,
        ),
        chapter_number=1,
    )

    assert "Acceptance packet is missing fields: acceptance_contract." in errors


def test_validate_acceptance_packet_requires_acceptance_contract_sections():
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
            "v3_state_updates": {
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
                "conflict_updates": {"active": []},
                "next_hook": {},
                "pending_approvals": [],
            },
            "acceptance_contract": {},
        },
        chapter_number=1,
    )

    assert (
        "Acceptance packet acceptance_contract is missing fields: "
        "outline_alignment, quality_gate_summary, state_updates."
    ) in errors


def test_validate_acceptance_packet_requires_contract_state_updates_to_mirror_v3_updates():
    packet = _valid_acceptance_packet(
        {
            "timeline": {},
            "character_states": [
                {
                    "character_id": "chen_an",
                    "display_name": "Chen An",
                    "physical_state": "steady",
                    "social_state": "watched",
                    "emotional_state": "wary",
                    "current_goal": "keep trading",
                    "known_secrets": [],
                    "public_knowledge": [],
                    "relationship_changes": [],
                    "voice_notes": [],
                }
            ],
            "resource_changes": [
                {
                    "owner": "chen_an",
                    "item": "cash",
                    "delta": 5,
                    "unit": "yuan",
                    "category": "money",
                    "reason": "small sale",
                }
            ],
            "open_thread_updates": [
                {
                    "id": "thread_0001_01",
                    "promise": "A buyer will return.",
                    "source_chapter": 1,
                    "status": "open",
                    "last_touched": 1,
                }
            ],
            "payoff_updates": [
                {
                    "frustration_level": "controlled",
                    "promises_made": ["Promise."],
                    "payoffs_delivered": [],
                }
            ],
            "conflict_updates": {"active": []},
            "next_hook": {
                "hook": "The buyer returns.",
                "obligation": "Answer the trade pressure.",
                "target_chapter": 2,
            },
            "pending_approvals": ["Confirm buyer rule."],
        }
    )

    errors = validate_acceptance_packet(packet, chapter_number=1)

    assert (
        "acceptance_contract.state_updates.character_state_changes must mirror "
        "v3_state_updates.character_states."
    ) in errors
    assert (
        "acceptance_contract.state_updates.resource_changes must mirror "
        "v3_state_updates.resource_changes."
    ) in errors
    assert (
        "acceptance_contract.state_updates.open_thread_updates must mirror "
        "v3_state_updates.open_thread_updates."
    ) in errors
    assert (
        "acceptance_contract.state_updates.payoff_updates must mirror "
        "v3_state_updates.payoff_updates."
    ) in errors
    assert (
        "acceptance_contract.state_updates.next_hook must mirror "
        "v3_state_updates.next_hook."
    ) in errors
    assert (
        "acceptance_contract.state_updates.pending_approvals must mirror "
        "v3_state_updates.pending_approvals."
    ) in errors


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


def _valid_acceptance_packet(v3_state_updates, *, include_acceptance_contract=True):
    packet = {
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
    if include_acceptance_contract:
        packet["acceptance_contract"] = {
            "quality_gate_summary": {
                "continuity_review_present": True,
                "continuity_blockers": [],
                "pacing_review_present": True,
                "pacing_score": 86,
                "revised_pacing_score": None,
                "revision_required": False,
                "waiver_required": False,
            },
            "outline_alignment": {
                "reference_chain": "master -> volume -> arc -> unit -> chapter brief",
                "volume_id": "volume_001",
                "arc_id": "arc_001",
                "unit_id": "unit_0001",
                "required_unit_obligations": [],
                "claimed_fulfilled_unit_obligations": [],
                "pending_unit_obligations": [],
            },
            "state_updates": {
                "timeline_event": {"id": "t001", "when": "Chapter 1", "summary": "Summary."},
                "character_state_changes": [],
                "resource_changes": [],
                "open_thread_updates": [],
                "payoff_updates": [],
                "next_hook": {},
                "pending_approvals": [],
                "economy_changes": [],
                "faction_changes": [],
            },
        }
    return packet
