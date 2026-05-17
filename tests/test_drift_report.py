from engine import book_factory, drift_report
from engine.io_utils import write_json, write_yaml


def test_drift_report_includes_v3_warnings_for_stale_thread_and_overdue_hook(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(book / "state" / "current_state.json", {"current_chapter": 6})
    write_json(book / "state" / "chapter_index.json", {"chapters": []})
    write_yaml(book / "canon" / "timeline.yaml", {"events": []})
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_old_vendor",
                    "promise": "丹铺迟早会上门压价",
                    "status": "open",
                    "payoff_deadline": 3,
                }
            ]
        },
    )
    write_json(
        book / "state" / "hook_index.json",
        {
            "hooks": [
                {
                    "hook": "回春丹铺带价来谈",
                    "status": "open",
                    "target_chapter": 3,
                }
            ]
        },
    )

    output = drift_report.generate_drift_report("demo", 1, 6)

    content = output.read_text(encoding="utf-8")
    assert "## V3 State Machine Warnings" in content
    assert "| Type | Item | Evidence | Recommended Action |" in content
    assert "stale_thread" in content
    assert "thread_old_vendor" in content
    assert "overdue_hook" in content
    assert "回春丹铺带价来谈" in content


def test_drift_report_includes_no_v3_warning_row_for_empty_template_ledgers(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    output = drift_report.generate_drift_report("demo", 1, 6)

    content = output.read_text(encoding="utf-8")
    assert "## V3 State Machine Warnings" in content
    assert "| None | - | No mechanical V3 warning found. | Continue. |" in content


def test_drift_report_includes_v3_1_outline_alignment_warnings(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(book / "state" / "current_state.json", {"current_chapter": 6})
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {
                    "chapter": 6,
                    "summary": "A chapter beyond the approved unit.",
                    "open_threads_touched": [],
                }
            ]
        },
    )
    write_yaml(
        book / "outlines" / "units" / "unit_0001.yaml",
        {
            "unit": 1,
            "chapter_range": {"start": 1, "end": 4},
            "required_threads": ["thread_required"],
            "chapters": [],
            "approval": {"status": "approved"},
        },
    )

    output = drift_report.generate_drift_report("demo", 1, 6)

    content = output.read_text(encoding="utf-8")
    assert "## Outline Alignment" in content
    assert "chapter_outside_approved_unit" in content
    assert "empty_unit_chapters" in content
    assert "missing_required_thread" in content


def test_drift_report_includes_unit_review_warnings(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {
            "current_chapter": 5,
            "active_characters": ["chen_an"],
            "active_conflicts": [],
        },
    )
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {"chapter": 1, "summary": "Trade pressure.", "state_changes": ["Trade.", "Win."]},
                {"chapter": 2, "summary": "Trade pressure.", "state_changes": ["Trade.", "Win."]},
                {"chapter": 3, "summary": "Trade pressure.", "state_changes": ["Trade.", "Win."]},
                {"chapter": 4, "summary": "Trade pressure.", "state_changes": ["Trade.", "Win."]},
                {"chapter": 5, "summary": "Trade pressure.", "state_changes": ["Trade.", "Win."]},
            ]
        },
    )
    write_yaml(book / "canon" / "timeline.yaml", {"events": []})
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_shop_pressure",
                    "promise": "The pill shop will escalate.",
                    "status": "open",
                    "source_chapter": 1,
                    "last_touched": 1,
                    "payoff_deadline": 5,
                    "next_obligation": "Escalate the shop pressure.",
                }
            ]
        },
    )
    write_yaml(
        book / "canon" / "payoff_ledger.yaml",
        {
            "entries": [
                {
                    "chapter": chapter,
                    "payoff_types": ["trade"],
                    "promises_made": [],
                    "payoffs_delivered": [f"Trade win {chapter}."],
                    "frustration_level": "controlled",
                }
                for chapter in range(1, 6)
            ]
        },
    )
    write_yaml(
        book / "canon" / "resource_ledger.yaml",
        {
            "resources": [
                {
                    "id": "res_chen_an_spirit_fragments",
                    "owner": "chen_an",
                    "name": "spirit fragments",
                    "category": "money",
                    "unit": "pieces",
                    "current_amount": 100,
                    "history": [
                        {"chapter": chapter, "delta": 10, "reason": "trade income"}
                        for chapter in range(1, 6)
                    ],
                }
            ]
        },
    )
    write_yaml(
        book / "canon" / "character_states.yaml",
        {
            "characters": {
                "chen_an": {
                    "display_name": "Chen An",
                    "current_goal": "keep trading",
                    "last_updated_chapter": 0,
                    "history": [
                        {
                            "chapter": 0,
                            "emotional_state": "wary",
                            "current_goal": "keep trading",
                        }
                    ],
                }
            }
        },
    )
    for chapter in range(1, 6):
        write_json(
            book / "reviews" / f"ch_{chapter:04d}" / "pacing_review.json",
            {"score": 78 if chapter == 3 else 86, "revised_score": None},
        )
        write_yaml(
            book / "state_updates" / f"ch_{chapter:04d}_acceptance.yaml",
            {"quality_gate": {"waiver": {"required": False}}},
        )

    output = drift_report.generate_drift_report("demo", 1, 5)

    content = output.read_text(encoding="utf-8")
    assert "## Unit Review" in content
    assert "pacing_risk" in content
    assert "repeated_payoff_type" in content
    assert "stalled_foreshadowing" in content
    assert "resource_inflation" in content
    assert "protagonist_growth_gap" in content
