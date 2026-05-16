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
