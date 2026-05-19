import yaml

from engine import acceptance_packet, book_factory
from engine.io_utils import read_yaml, write_json, write_yaml


def test_draft_acceptance_packet_uses_reviews_and_current_state(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {
            "proposed_state_updates": ["System triggered."],
            "human_approval_needed": ["Define system cost."],
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "human_approval_needed": ["Keep payoff delayed."],
        },
    )

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
    )

    packet = read_yaml(output)
    assert output == book / "state_updates" / "ch_0001_acceptance.yaml"
    assert packet["chapter"] == 1
    assert packet["title"] == "First Signal"
    assert packet["source_draft"] == "drafts/ch_0001_revised.md"
    assert packet["accepted_chapter_path"] == "chapters/ch_0001.md"
    assert packet["summary"] == "The first contradiction appears."
    assert packet["state_changes"] == ["System triggered."]
    assert packet["timeline_event"]["id"] == "t001"
    assert packet["timeline_event"]["when"] == "第 1 章"
    assert packet["change_log"]["canon_updates"] == ["timeline:t001"]
    assert "Define system cost." in packet["current_state"]["pending_approvals"]
    assert "Keep payoff delayed." in packet["current_state"]["pending_approvals"]
    contract = packet["acceptance_contract"]
    assert contract["quality_gate_summary"]["continuity_review_present"] is True
    assert contract["outline_alignment"]["reference_chain"] == "master -> volume -> arc -> unit -> chapter brief"
    assert contract["state_updates"]["timeline_event"]["id"] == "t001"


def test_draft_acceptance_packet_includes_v3_state_updates(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
    )

    packet = read_yaml(output)
    updates = packet["v3_state_updates"]
    assert updates["timeline"]["occurred_events"][0]["source_chapter"] == 1
    assert (
        updates["timeline"]["occurred_events"][0]["summary"]
        == "The first contradiction appears."
    )
    assert updates["character_states"] == []
    assert updates["resource_changes"] == []
    assert updates["open_thread_updates"] == []
    assert updates["payoff_updates"][0]["chapter"] == 1
    assert updates["conflict_updates"]["active"] == []
    assert updates["next_hook"] == {}
    assert updates["pending_approvals"] == []

    contract = packet["acceptance_contract"]
    assert contract["quality_gate_summary"]["pacing_review_present"] is False
    assert contract["outline_alignment"]["reference_chain"] == "master -> volume -> arc -> unit -> chapter brief"
    assert contract["state_updates"]["economy_changes"] == []


def test_draft_acceptance_packet_uses_active_ranged_outline_alignment(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0011_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")
    _write_second_outline_layer_fixture(book)

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        11,
        title="New Buyer",
        source_draft="drafts/ch_0011_revised.md",
        summary="A new buyer tests supply.",
    )

    packet = read_yaml(output)
    alignment = packet["acceptance_contract"]["outline_alignment"]
    assert alignment["volume_id"] == "volume_002"
    assert alignment["arc_id"] == "arc_002"
    assert alignment["unit_id"] == "unit_0002"
    assert alignment["required_unit_obligations"] == ["Track supply limits."]


def test_draft_acceptance_packet_includes_publication_readiness(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_final_candidate.md"
    draft.parent.mkdir()
    draft.write_text("final candidate", encoding="utf-8")
    write_yaml(
        book / "authoring" / "ch_0001_author_direction.yaml",
        {
            "chapter": 1,
            "author_intent": ["Keep the protagonist in control."],
            "must_change": ["Make the opening faster."],
            "approved_for_final_candidate": True,
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        {
            "score": 88,
            "rewrite_required": False,
            "blocking_issues": [],
        },
    )

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_final_candidate.md",
        summary="The first contradiction appears.",
    )

    readiness = read_yaml(output)["acceptance_contract"]["publication_readiness"]
    assert readiness["final_candidate_path"] == "drafts/ch_0001_final_candidate.md"
    assert readiness["author_direction_present"] is True
    assert readiness["author_direction_approved"] is True
    assert readiness["prose_quality_review_present"] is True
    assert readiness["prose_quality_score"] == 88
    assert readiness["prose_rewrite_required"] is False


def test_draft_acceptance_packet_refuses_existing_file_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")
    output = book / "state_updates" / "ch_0001_acceptance.yaml"
    output.write_text("existing: true\n", encoding="utf-8")

    try:
        acceptance_packet.draft_acceptance_packet(
            "demo",
            1,
            title="First Signal",
            source_draft="drafts/ch_0001_revised.md",
            summary="The first contradiction appears.",
        )
    except FileExistsError as exc:
        assert "ch_0001_acceptance.yaml" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError")


def test_draft_acceptance_packet_can_force_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")
    output = book / "state_updates" / "ch_0001_acceptance.yaml"
    output.write_text("existing: true\n", encoding="utf-8")

    acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
        force=True,
    )

    packet = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert packet["title"] == "First Signal"


def test_draft_acceptance_packet_does_not_emit_yaml_aliases(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {"human_approval_needed": ["Define system cost."]},
    )

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
    )

    content = output.read_text(encoding="utf-8")
    assert "&id" not in content
    assert "*id" not in content


def test_draft_acceptance_packet_writes_html_sidecar(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
    )

    html_output = output.with_suffix(".html")
    content = html_output.read_text(encoding="utf-8")
    assert html_output.exists()
    assert "<h1>Acceptance Packet</h1>" in content
    assert "The first contradiction appears." in content


def _write_second_outline_layer_fixture(book):
    write_yaml = __import__("engine.io_utils", fromlist=["write_yaml"]).write_yaml
    write_yaml(
        book / "outlines" / "volumes" / "volume_002.yaml",
        {
            "volume_id": "volume_002",
            "chapter_range": {"start": 11, "end": 60},
            "volume_goal": "Scale the shop.",
            "approval": {"status": "approved"},
        },
    )
    write_yaml(
        book / "outlines" / "arc_002.yaml",
        {
            "arc_id": "arc_002",
            "chapter_range": {"start": 11, "end": 30},
            "arc_goal": "Pressure becomes supply chain.",
            "approval": {"status": "approved"},
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0002.yaml",
        {
            "unit": 2,
            "chapter_range": {"start": 11, "end": 20},
            "unit_goal": "Open the second trading pattern.",
            "chapters": [
                {
                    "chapter": 11,
                    "state_obligation": ["Track supply limits."],
                }
            ],
            "approval": {"status": "approved"},
        },
    )
