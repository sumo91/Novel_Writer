from engine import book_factory, v3_migration, validators
from engine.io_utils import read_json, read_yaml, write_json, write_yaml


V3_PATHS = [
    "canon/character_states.yaml",
    "canon/resource_ledger.yaml",
    "canon/payoff_ledger.yaml",
    "outlines/units/unit_0001.yaml",
    "state/hook_index.json",
    "state/memory_index.json",
]

V3_1_PATHS = [
    "outlines/volumes/volume_001.yaml",
    "canon/economy.yaml",
    "canon/factions.yaml",
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
            "status": "open",
            "custom_field": "keep me",
            "promise": "Grandfather's debt is unresolved.",
            "source_chapter": 0,
            "last_touched": 0,
            "next_obligation": "Legacy migration needs human review.",
            "payoff_deadline": "",
            "risk_if_ignored": "Legacy migration needs human review.",
            "related_characters": [],
            "related_locations": [],
            "payoff_chapter": "",
            "notes": [],
        }
    ]


def test_migrate_book_to_v3_upgrades_old_acceptance_packet_scaffold(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    packet_path = book / "state_updates" / "ch_0001_acceptance.yaml"
    write_yaml(
        packet_path,
        {
            "chapter": 1,
            "title": "Old Chapter",
            "source_draft": "drafts/ch_0001_revised.md",
            "accepted_chapter_path": "chapters/ch_0001.md",
            "summary": "The old packet summary stays intact.",
            "current_state": {
                "current_arc": "arc_001",
                "latest_location": "Shop",
                "active_characters": [],
                "active_conflicts": [],
                "pending_approvals": [],
            },
            "state_changes": [],
            "open_threads_touched": [],
            "timeline_event": {
                "id": "t001",
                "when": "Chapter 1",
                "summary": "The old packet summary stays intact.",
            },
            "open_thread_updates": [],
            "change_log": {
                "summary": "Accepted old chapter.",
                "canon_updates": [],
                "pending_approvals": [],
            },
            "acceptance_contract": {
                "quality_gate_summary": {
                    "continuity_review_present": False,
                    "continuity_blockers": [],
                    "pacing_review_present": False,
                    "pacing_score": None,
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
                    "timeline_event": {
                        "id": "t001",
                        "when": "第 1 章",
                        "summary": "The old packet summary stays intact.",
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
    )

    result = v3_migration.migrate_book_to_v3("demo")

    packet = read_yaml(packet_path)
    assert "state_updates/ch_0001_acceptance.yaml" in result.updated
    assert packet["title"] == "Old Chapter"
    assert packet["summary"] == "The old packet summary stays intact."
    assert packet["source_draft"] == "drafts/ch_0001_revised.md"
    assert packet["current_state"]["current_chapter"] == 1
    assert packet["acceptance_contract"]["outline_alignment"]["reference_chain"] == "master -> volume -> arc -> unit -> chapter brief"
    assert packet["v3_state_updates"] == {
        "timeline": {
            "occurred_events": [
                {
                    "id": "ev_0001_01",
                    "summary": "The old packet summary stays intact.",
                    "location": "",
                    "involved_characters": [],
                    "source_chapter": 1,
                }
            ],
        },
        "character_states": [],
        "resource_changes": [],
        "open_thread_updates": [],
        "payoff_updates": [
            {
                "chapter": 1,
                "promises_made": [],
                "payoffs_delivered": ["The old packet summary stays intact."],
                "frustration_level": "controlled",
                "payoff_types": [],
                "delayed_payoffs": [],
                "risks": [],
            }
        ],
        "conflict_updates": {"active": []},
        "next_hook": {},
        "pending_approvals": [],
    }


def test_migrate_book_to_v3_makes_old_structural_book_validate(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
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
    write_yaml(
        book / "state_updates" / "ch_0001_acceptance.yaml",
        {
            "chapter": 1,
            "title": "Old Chapter",
            "source_draft": "drafts/ch_0001_revised.md",
            "accepted_chapter_path": "chapters/ch_0001.md",
            "summary": "The old packet summary stays intact.",
            "current_state": {
                "current_arc": "arc_001",
                "latest_location": "Shop",
                "active_characters": [],
                "active_conflicts": [],
                "pending_approvals": [],
            },
            "state_changes": [],
            "open_threads_touched": [],
            "timeline_event": {
                "id": "t001",
                "when": "Chapter 1",
                "summary": "The old packet summary stays intact.",
            },
            "open_thread_updates": [],
            "change_log": {
                "summary": "Accepted old chapter.",
                "canon_updates": [],
                "pending_approvals": [],
            },
            "acceptance_contract": {
                "quality_gate_summary": {
                    "continuity_review_present": False,
                    "continuity_blockers": [],
                    "pacing_review_present": False,
                    "pacing_score": None,
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
                    "timeline_event": {
                        "id": "t001",
                        "when": "第 1 章",
                        "summary": "The old packet summary stays intact.",
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
    )

    v3_migration.migrate_book_to_v3("demo")

    assert validators.validate_book("demo") == []


def test_migrate_book_to_v3_1_creates_outline_files_without_inference(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    for relative_path in V3_1_PATHS:
        (book / relative_path).unlink()
    write_yaml(
        book / "outlines" / "master_outline.yaml",
        {
            "logline": "Keep this premise.",
            "volume_plan": [{"volume": 1, "goal": "Keep this plan."}],
            "major_turning_points": ["Keep this turn."],
            "ending_direction": "Keep this ending.",
        },
    )
    write_yaml(
        book / "outlines" / "arc_001.yaml",
        {
            "arc_id": "arc_001",
            "title": "Keep this arc title.",
            "arc_goal": "Keep this arc goal.",
            "main_conflict": "Keep this conflict.",
            "required_payoffs": [],
            "required_threads": [],
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {
            "unit": 1,
            "chapter_range": {"start": 1, "end": 10},
            "unit_goal": "Keep this unit goal.",
            "chapters": [],
        },
    )
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {
                    "chapter": 1,
                    "summary": "Do not infer this into V3.1 outlines.",
                }
            ]
        },
    )

    result = v3_migration.migrate_book_to_v3_1("demo")

    assert result.book_id == "demo"
    assert result.created == V3_1_PATHS
    assert "outlines/master_outline.yaml" in result.updated
    assert "outlines/arc_001.yaml" in result.updated
    assert "outlines/units/unit_0001.yaml" in result.updated
    master_outline = read_yaml(book / "outlines" / "master_outline.yaml")
    assert master_outline["logline"] == "Keep this premise."
    assert master_outline["volume_plan"] == [{"volume": 1, "goal": "Keep this plan."}]
    assert master_outline["major_turning_points"] == ["Keep this turn."]
    assert master_outline["ending_direction"] == "Keep this ending."
    assert master_outline["approval"]["status"] == "draft"
    created_text = "\n".join(
        (book / relative_path).read_text(encoding="utf-8")
        for relative_path in result.created
    )
    assert "Do not infer this into V3.1 outlines." not in created_text
