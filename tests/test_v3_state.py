from engine import book_factory
from engine.io_utils import read_json, read_yaml
from engine.v3_state import apply_v3_state_updates


def _create_book(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    return book_factory.create_book("demo", title="Demo Book")


def _v3_packet(chapter=3, payoff_chapter=3):
    return {
        "chapter": chapter,
        "v3_state_updates": {
            "timeline": {
                "occurred_events": [
                    {
                        "id": "ev_0003_01",
                        "summary": "A shop pressure arrives.",
                        "location": "Shop",
                        "involved_characters": ["chen_an"],
                        "source_chapter": 3,
                    }
                ]
            },
            "character_states": [
                {
                    "character_id": "chen_an",
                    "display_name": "Chen An",
                    "physical_state": "steady",
                    "social_state": "watched by the pill shop",
                    "emotional_state": "wary",
                    "current_goal": "keep the small shop open",
                    "known_secrets": ["back door rule"],
                    "public_knowledge": [],
                    "relationship_changes": [],
                    "voice_notes": ["negotiate without revealing the floor"],
                }
            ],
            "resource_changes": [
                {
                    "owner": "chen_an",
                    "item": "cash",
                    "delta": 3000,
                    "unit": "yuan",
                    "category": "money",
                    "reason": "sold yellow sprout grass",
                    "source_chapter": 3,
                }
            ],
            "open_thread_updates": [
                {
                    "id": "thread_0003_01",
                    "promise": "The pill shop notices the midnight supply.",
                    "source_chapter": 3,
                    "status": "open",
                    "last_touched": 3,
                    "next_obligation": "Answer the quote in chapter 4.",
                    "payoff_deadline": 5,
                    "risk_if_ignored": "Commercial pressure fizzles.",
                }
            ],
            "payoff_updates": [
                {
                    "chapter": payoff_chapter,
                    "promises_made": ["The pill shop will come calling."],
                    "payoffs_delivered": ["Yellow sprout grass becomes cash."],
                    "frustration_level": "controlled",
                    "payoff_types": ["money", "trade"],
                    "delayed_payoffs": ["pill shop quote"],
                    "risks": [],
                }
            ],
            "conflict_updates": {
                "active": [
                    {
                        "id": "conflict_0003_01",
                        "summary": "Risk of a lowball pill shop offer.",
                        "pressure_type": "commercial",
                        "source_chapter": 3,
                    }
                ]
            },
            "next_hook": {
                "hook": "The pill shop brings a price tomorrow night.",
                "obligation": "Answer the quote in chapter 4.",
                "target_chapter": 4,
            },
            "pending_approvals": ["Confirm the pill shop as stage opponent."],
        },
    }


def test_apply_v3_state_updates_writes_ledgers_and_indexes(tmp_path, monkeypatch):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()

    apply_v3_state_updates(book, packet)

    threads = read_yaml(book / "canon" / "open_threads.yaml")
    assert threads["threads"][0]["id"] == "thread_0003_01"
    character_states = read_yaml(book / "canon" / "character_states.yaml")
    assert character_states["characters"]["chen_an"]["last_updated_chapter"] == 3
    resources = read_yaml(book / "canon" / "resource_ledger.yaml")
    assert resources["resources"][0]["id"] == "res_chen_an_cash"
    assert resources["resources"][0]["current_amount"] == 3000
    assert resources["resources"][0]["history"] == [
        {
            "chapter": 3,
            "delta": 3000,
            "reason": "sold yellow sprout grass",
        }
    ]
    payoffs = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoffs["entries"][0]["payoff_types"] == ["money", "trade"]
    hooks = read_json(book / "state" / "hook_index.json")
    assert hooks["hooks"][0]["status"] == "open"
    memory = read_json(book / "state" / "memory_index.json")
    assert memory["by_character"]["chen_an"] == [3]
    assert memory["by_thread"]["thread_0003_01"] == [3]
    assert memory["by_location"]["Shop"] == [3]
    assert memory["by_resource"]["cash"] == [3]


def test_apply_v3_state_updates_is_idempotent_for_resources_and_hooks(tmp_path, monkeypatch):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()

    apply_v3_state_updates(book, packet)
    apply_v3_state_updates(book, packet)

    resources = read_yaml(book / "canon" / "resource_ledger.yaml")
    assert resources["resources"][0]["current_amount"] == 3000
    assert resources["resources"][0]["history"] == [
        {
            "chapter": 3,
            "delta": 3000,
            "reason": "sold yellow sprout grass",
        }
    ]
    hooks = read_json(book / "state" / "hook_index.json")
    assert [
        hook
        for hook in hooks["hooks"]
        if hook["chapter"] == 3
        and hook["hook"] == "The pill shop brings a price tomorrow night."
    ] == [
        {
            "chapter": 3,
            "hook": "The pill shop brings a price tomorrow night.",
            "obligation": "Answer the quote in chapter 4.",
            "target_chapter": 4,
            "status": "open",
        }
    ]


def test_apply_v3_state_updates_normalizes_payoff_chapter_to_packet_chapter(tmp_path, monkeypatch):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet(payoff_chapter=99)

    apply_v3_state_updates(book, packet)

    payoffs = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoffs["entries"][0]["chapter"] == 3


def test_apply_v3_state_updates_clears_chapter_payoffs_when_reaccepted_empty(
    tmp_path,
    monkeypatch,
):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()
    empty_payoff_packet = _v3_packet()
    empty_payoff_packet["v3_state_updates"]["payoff_updates"] = []

    apply_v3_state_updates(book, packet)
    apply_v3_state_updates(book, empty_payoff_packet)

    payoffs = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoffs["entries"] == []


def test_apply_v3_state_updates_preserves_multiple_same_resource_deltas(
    tmp_path,
    monkeypatch,
):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()
    packet["v3_state_updates"]["resource_changes"] = [
        {
            "owner": "chen_an",
            "item": "cash",
            "delta": 3000,
            "unit": "yuan",
            "category": "money",
            "reason": "sold yellow sprout grass",
        },
        {
            "owner": "chen_an",
            "item": "cash",
            "delta": -2500,
            "unit": "yuan",
            "category": "money",
            "reason": "paid stall debt",
        },
    ]

    apply_v3_state_updates(book, packet)

    resources = read_yaml(book / "canon" / "resource_ledger.yaml")
    assert resources["resources"][0]["current_amount"] == 500
    assert resources["resources"][0]["history"] == [
        {
            "chapter": 3,
            "delta": 3000,
            "reason": "sold yellow sprout grass",
        },
        {
            "chapter": 3,
            "delta": -2500,
            "reason": "paid stall debt",
        },
    ]


def test_apply_v3_state_updates_clears_hook_when_reaccepted_without_hook(
    tmp_path,
    monkeypatch,
):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()
    no_hook_packet = _v3_packet()
    no_hook_packet["v3_state_updates"]["next_hook"] = {}

    apply_v3_state_updates(book, packet)
    apply_v3_state_updates(book, no_hook_packet)

    hooks = read_json(book / "state" / "hook_index.json")
    assert hooks["hooks"] == []


def test_apply_v3_state_updates_clears_stale_memory_refs_on_reaccept(
    tmp_path,
    monkeypatch,
):
    book = _create_book(tmp_path, monkeypatch)
    packet = _v3_packet()
    no_refs_packet = _v3_packet()
    no_refs_packet["v3_state_updates"]["timeline"] = {"occurred_events": []}
    no_refs_packet["v3_state_updates"]["character_states"] = []
    no_refs_packet["v3_state_updates"]["resource_changes"] = []
    no_refs_packet["v3_state_updates"]["open_thread_updates"] = []

    apply_v3_state_updates(book, packet)
    apply_v3_state_updates(book, no_refs_packet)

    memory = read_json(book / "state" / "memory_index.json")
    assert memory == {
        "by_character": {},
        "by_thread": {},
        "by_location": {},
        "by_resource": {},
    }


def test_apply_v3_state_updates_ignores_missing_or_non_mapping_updates(tmp_path, monkeypatch):
    book = _create_book(tmp_path, monkeypatch)
    expected_resources = read_yaml(book / "canon" / "resource_ledger.yaml")
    expected_payoffs = read_yaml(book / "canon" / "payoff_ledger.yaml")
    expected_hooks = read_json(book / "state" / "hook_index.json")
    expected_memory = read_json(book / "state" / "memory_index.json")

    apply_v3_state_updates(book, {"chapter": 3})
    apply_v3_state_updates(book, {"chapter": 3, "v3_state_updates": []})

    assert read_yaml(book / "canon" / "resource_ledger.yaml") == expected_resources
    assert read_yaml(book / "canon" / "payoff_ledger.yaml") == expected_payoffs
    assert read_json(book / "state" / "hook_index.json") == expected_hooks
    assert read_json(book / "state" / "memory_index.json") == expected_memory
