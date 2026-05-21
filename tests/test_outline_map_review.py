from engine import book_factory, outline_map_review
from engine.io_utils import write_yaml


def test_outline_map_review_generates_html_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_map_review, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_outline_fixture(book)

    output = outline_map_review.generate_outline_map_review("demo")

    content = output.read_text(encoding="utf-8")
    assert output.with_suffix(".html").exists()
    assert "## Outline Minimum Map" in content
    assert "## Book Overview" in content
    assert "## Volume Map" in content
    assert "## Arc Map" in content
    assert "## Unit Map" in content
    assert "## Outline Map Warnings" in content


def test_outline_map_review_reports_missing_map_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_map_review, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "outlines" / "master_outline.yaml",
        {
            "logline": "",
            "story_promise": "",
            "opening_state": {"protagonist": "", "world": "", "first_pressure": "", "first_hook": ""},
            "ending_state": {"protagonist": "", "shop": "", "two_world_order": "", "final_emotional_image": ""},
            "three_act_structure": {"act_1": {}, "act_2": {}, "act_3": {}},
            "protagonist_growth_curve": {},
            "core_mystery": {"question": "", "answer_direction": "", "reveal_stages": []},
            "core_rules_locked": [],
            "locked_story_promises": [],
            "open_story_spaces": [],
            "volume_plan": [],
            "major_turning_points": [],
            "ending_direction": "",
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "volumes" / "volume_001.yaml",
        {"volume_id": "volume_001", "chapter_range": {"start": 1, "end": 50}, "approval": {"status": "draft"}},
    )
    write_yaml(
        book / "outlines" / "arc_001.yaml",
        {"arc_id": "arc_001", "chapter_range": {"start": 1, "end": 20}, "parent_volume": "volume_001", "approval": {"status": "draft"}},
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {"unit": 1, "chapter_range": {"start": 1, "end": 10}, "parent_arc": "arc_001", "approval": {"status": "draft"}},
    )

    result = outline_map_review.generate_outline_map_review("demo")

    content = result.read_text(encoding="utf-8")
    assert "missing_core" in content
    assert "missing_stage_map" in content
    assert "missing_unit_flow" in content
    assert "missing_story_promise" in content


def test_outline_map_review_reports_unmapped_threads_and_payoffs(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_map_review, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_outline_fixture(book)
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_unmapped_vendor",
                    "promise": "A vendor will test the shop later.",
                    "status": "open",
                }
            ]
        },
    )
    write_yaml(
        book / "canon" / "payoff_ledger.yaml",
        {
            "entries": [
                {
                    "chapter": 3,
                    "promises_made": ["A hidden tax must be paid."],
                    "payoffs_delivered": [],
                }
            ]
        },
    )

    output = outline_map_review.generate_outline_map_review("demo")

    content = output.read_text(encoding="utf-8")
    assert "unmapped_open_thread" in content
    assert "thread_unmapped_vendor" in content
    assert "unmapped_payoff_promise" in content
    assert "A hidden tax must be paid." in content


def _write_outline_fixture(book):
    write_yaml(
        book / "outlines" / "master_outline.yaml",
        {
            "logline": "A small shop opens to a cultivation market.",
            "story_promise": "Two-world trade, escalating pressure, controlled growth.",
            "full_book_arc": "Turn the inherited shop into a stable bridge.",
            "opening_state": {
                "protagonist": "A broke shop owner with no leverage.",
                "world": "A failing old shop in the real world.",
                "first_pressure": "The back door opens at midnight.",
                "first_hook": "A stranger buys something impossible.",
            },
            "ending_state": {
                "protagonist": "A capable shopkeeper with firm terms.",
                "shop": "A profitable regulated two-world shop.",
                "two_world_order": "A stable exchange protocol exists.",
                "final_emotional_image": "The shop lights stay on through midnight.",
            },
            "three_act_structure": {
                "act_1": {"chapter_range": "1-10", "function": "Open the two-world premise.", "major_turning_points": [], "act_climax": "First trade works."},
                "act_2": {"chapter_range": "11-30", "function": "Expand pressure.", "major_turning_points": [], "midpoint": "The market notices.", "act_climax": "Trade rules break."},
                "act_3": {"chapter_range": "31-50", "function": "Lock in a new order.", "major_turning_points": [], "final_climax": "A final negotiation settles the shop.", "ending": "The shop survives and changes."},
            },
            "protagonist_growth_curve": {
                "start": "Confused and reactive.",
                "act_1_end": "Sees the opportunity.",
                "midpoint": "Starts setting rules.",
                "act_2_end": "Can negotiate from strength.",
                "end": "Owns the bridge between worlds.",
            },
            "core_mystery": {
                "question": "Why does the back door open?",
                "answer_direction": "The shop inherits a hidden trade function.",
                "reveal_stages": [],
            },
            "core_rules_locked": ["The back door opens at midnight."],
            "locked_story_promises": ["opening_state", "ending_direction"],
            "open_story_spaces": ["chapter-level scene execution"],
            "volume_plan": [],
            "major_turning_points": [],
            "ending_direction": "The protagonist keeps the shop and the bridge.",
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "volumes" / "volume_001.yaml",
        {
            "volume_id": "volume_001",
            "title": "First Trade",
            "chapter_range": {"start": 1, "end": 50},
            "volume_goal": "Keep the shop alive.",
            "reader_promise": "Grounded trading and pressure.",
            "main_pressure": {"antagonist_or_force": "A pill shop", "pressure_type": "price pressure", "escalation_path": []},
            "protagonist_progress": {"start_state": "Reactive", "end_state": "Strategic"},
            "core_payoffs": ["First trade"],
            "major_reveal": "The shop bridges two worlds.",
            "volume_climax": "The shop resists an exclusive lock-in.",
            "ending_hook": "A stronger negotiator arrives.",
            "required_threads": ["thread_0004_pill_shop_exclusive_pressure"],
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "arc_001.yaml",
        {
            "arc_id": "arc_001",
            "title": "Opening Trade Arc",
            "chapter_range": {"start": 1, "end": 20},
            "parent_volume": "volume_001",
            "arc_goal": "Establish the first trade system.",
            "main_conflict": "Can the shop stay independent?",
            "stage_enemy_or_pressure": "A pill shop seeks leverage.",
            "protagonist_move": "Define terms instead of conceding.",
            "required_payoffs": ["Pay off the first negotiation pressure."],
            "required_threads": ["thread_0004_pill_shop_exclusive_pressure"],
            "major_reveal_or_reversal": "The market sees the shop as a bridge.",
            "exit_state": "The protagonist has leverage.",
            "chapters": [],
            "approval": {"status": "draft"},
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {
            "unit": 1,
            "chapter_range": {"start": 1, "end": 10},
            "parent_arc": "arc_001",
            "unit_goal": "Turn pressure into rules.",
            "stage_enemy": "A shop competitor.",
            "stage_payoffs": ["A repeatable trade rule is established."],
            "stage_end_hook": "A bigger buyer appears.",
            "required_threads": ["thread_0004_pill_shop_exclusive_pressure"],
            "chapters": [
                {
                    "chapter": 5,
                    "function": "Zhao pressure tests the price rules.",
                    "opening_hook": "Zhao comes in person.",
                    "main_payoff": "Chen sets terms.",
                    "next_hook": "Ledger clue deepens.",
                    "state_obligation": ["Update pill-shop pressure."],
                }
            ],
            "approval": {"status": "draft"},
        },
    )
