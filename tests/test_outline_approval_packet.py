from engine import book_factory, outline_approval_packet
from engine.io_utils import write_yaml


def test_master_outline_approval_packet_expands_human_review_sections(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_approval_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_master_fixture(book)

    output = outline_approval_packet.generate_outline_approval_packet(
        "demo",
        layer="master",
    )

    content = output.read_text(encoding="utf-8")
    assert output == book / "reports" / "master_outline_approval_packet.md"
    assert output.with_suffix(".html").exists()
    assert "# Master Outline Approval Packet" in content
    assert "This is a human review packet, not a mechanical minimum-map report." in content
    assert "## Full Book Direction" in content
    assert "Reach the mother-hive highway." in content
    assert "## Core Mystery" in content
    assert "The RV protocol waits for the next driver." in content
    assert "## Volume Plan" in content
    assert "First Rule" in content
    assert "## Approval Questions" in content


def test_outline_approval_packet_rejects_unknown_layer(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_approval_packet, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    try:
        outline_approval_packet.generate_outline_approval_packet("demo", layer="mystery")
    except ValueError as exc:
        assert "Unknown outline approval packet layer" in str(exc)
    else:
        raise AssertionError("Expected unknown layer to be rejected")


def _write_master_fixture(book):
    write_yaml(
        book / "outlines" / "master_outline.yaml",
        {
            "logline": "A rescue captain drives an upgradeable RV into the fog.",
            "story_promise": "Road pressure, RV upgrades, and hard rescue choices.",
            "full_book_arc": "Reach the mother-hive highway.",
            "opening_state": {
                "protagonist": "A retired rescue captain.",
                "world": "Fog covers the roads.",
                "first_pressure": "A service area collapses.",
                "first_hook": "The RV system wakes.",
            },
            "ending_state": {
                "protagonist": "A driver who can carry the final choice.",
                "shop": "The RV becomes a mobile anchor.",
                "two_world_order": "Fog, roads, and protocol are understood.",
                "final_emotional_image": "Headlights reach the source fog.",
            },
            "three_act_structure": {
                "act_1": {
                    "chapter_range": "1-80",
                    "function": "Open the road survival loop.",
                    "major_turning_points": ["The first filter works."],
                    "act_climax": "The RV reaches a higher-pollution road.",
                },
                "act_2": {
                    "chapter_range": "81-500",
                    "function": "Escalate road ecology and father clues.",
                    "major_turning_points": ["The old route appears."],
                    "midpoint": "The route is a training path.",
                    "act_climax": "The RV enters the hive network.",
                },
                "act_3": {
                    "chapter_range": "501+",
                    "function": "Resolve the fog-heart choice.",
                    "major_turning_points": ["The fog-heart speaks."],
                    "final_climax": "The driver chooses what rescue means.",
                    "ending": "The choice returns to the human world.",
                },
            },
            "protagonist_growth_curve": {
                "start": "Refuses to save everyone.",
                "act_1_end": "Protects the people inside his rules.",
                "midpoint": "Understands the route is a test.",
                "act_2_end": "Stops treating every altered person as a monster.",
                "end": "Can carry the final consequence.",
            },
            "core_mystery": {
                "question": "Why did the RV choose him?",
                "answer_direction": "The RV protocol waits for the next driver.",
                "reveal_stages": ["It looks like a survival system.", "It is his father's protocol."],
            },
            "core_rules_locked": ["The fog follows roads.", "The RV upgrades through tasks."],
            "locked_story_promises": ["opening_state", "ending_direction"],
            "open_story_spaces": ["local reversals"],
            "volume_plan": [
                {
                    "volume": 1,
                    "title": "First Rule",
                    "chapter_range": "1-50",
                    "function": "Build the RV rules.",
                    "endpoint": "Father's first clue appears.",
                }
            ],
            "major_turning_points": ["The RV wakes.", "The fog-heart is revealed."],
            "ending_direction": "Carry the fog-heart choice back.",
            "approval": {"status": "draft"},
        },
    )
