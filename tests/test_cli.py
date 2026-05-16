from engine import book_factory, cli, pipeline
from engine.io_utils import read_yaml, write_json


def test_pipeline_quality_gate_cli_reports_missing_reviews_without_traceback(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["pipeline-quality-gate", "demo", "1"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Error: Missing continuity review:" in captured.out


def test_validate_book_reports_existing_review_errors(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.validators as validators

    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 88,
            "dimension_scores": {
                "hook_strength": 9,
                "conflict_clarity": 8,
                "protagonist_agency": 9,
                "emotional_payoff": 13,
                "pacing": 8,
                "character_consistency": 9,
                "continuity_safety": 9,
                "chapter_end_pull": 8,
                "mainline_relevance": 9,
                "fresh_information_or_expectation": 8,
            },
        },
    )

    result = cli.main(["validate-book", "demo"])

    captured = capsys.readouterr()
    assert result == 1
    assert "reviews/ch_0001/pacing_review.json" in captured.out
    assert "invalid dimension scores: emotional_payoff" in captured.out


def test_validate_book_reports_pending_registry_errors(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.validators as validators

    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    registry = book / "state" / "pending_approvals.yaml"
    registry.write_text(
        "\n".join(
            [
                "approvals:",
                "- id: broken",
                "  status: maybe",
                "  text: ''",
                "  source_chapters: nope",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli.main(["validate-book", "demo"])

    captured = capsys.readouterr()
    assert result == 1
    assert "state/pending_approvals.yaml" in captured.out
    assert "status must be open" in captured.out


def test_drift_report_cli_generates_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.validators as validators
    import engine.drift_report as drift_report

    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {
                    "chapter": 1,
                    "title": "First",
                    "path": "chapters/ch_0001.md",
                    "summary": "First event.",
                    "state_changes": ["Hook.", "Payoff."],
                    "open_threads_touched": ["thread_001"],
                }
            ]
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 88,
            "dimension_scores": {
                "hook_strength": 9,
                "conflict_clarity": 8,
                "protagonist_agency": 9,
                "emotional_payoff": 8,
                "pacing": 8,
                "character_consistency": 9,
                "continuity_safety": 9,
                "chapter_end_pull": 8,
                "mainline_relevance": 9,
                "fresh_information_or_expectation": 8,
            },
        },
    )
    packet = book / "state_updates" / "ch_0001_acceptance.yaml"
    packet.write_text(
        "\n".join(
            [
                "quality_gate:",
                "  waiver:",
                "    required: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli.main(["drift-report", "demo", "--start", "1", "--end", "1"])

    captured = capsys.readouterr()
    output = book / "reports" / "ch_0001_0001_drift_review.md"
    assert result == 0
    assert f"Generated drift report: {output.as_posix()}" in captured.out
    content = output.read_text(encoding="utf-8")
    assert "# Chapter 1-1 Drift Review" in content
    assert "| 1 | 88 |  | False |" in content


def test_pending_approvals_cli_lists_deduped_sources(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.pending_approvals as pending_approvals

    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 2, "pending_approvals": ["Define system cost."]},
    )
    (book / "state" / "change_log.jsonl").write_text(
        '{"chapter": 1, "pending_approvals": ["Define system cost."]}\n',
        encoding="utf-8",
    )

    result = cli.main(["pending-approvals", "demo"])

    captured = capsys.readouterr()
    assert result == 0
    assert "# Pending Approvals" in captured.out
    assert "逆光系统代价方向" in captured.out
    assert "Define system cost." in captured.out
    assert "1, 2" in captured.out


def test_sync_pending_approvals_cli_writes_registry(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.pending_approvals as pending_approvals

    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 1, "pending_approvals": ["Define system cost."]},
    )

    result = cli.main(["sync-pending-approvals", "demo"])

    captured = capsys.readouterr()
    output = book / "state" / "pending_approvals.yaml"
    assert result == 0
    assert f"Synced pending approvals: {output.as_posix()}" in captured.out
    assert output.exists()


def test_pending_approval_update_cli_updates_registry(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.pending_approvals as pending_approvals

    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 1, "pending_approvals": ["Define system cost."]},
    )
    pending_approvals.sync_pending_approvals("demo")
    registry_path = book / "state" / "pending_approvals.yaml"
    approval_id = read_yaml(registry_path)["approvals"][0]["id"]

    result = cli.main(
        [
            "pending-approval-update",
            "demo",
            approval_id,
            "--status",
            "approved",
            "--note",
            "Confirmed cost direction.",
        ]
    )

    captured = capsys.readouterr()
    registry = read_yaml(registry_path)
    assert result == 0
    assert f"Updated pending approval: {approval_id} -> approved" in captured.out
    assert registry["approvals"][0]["status"] == "approved"
    assert registry["approvals"][0]["note"] == "Confirmed cost direction."


def test_pending_approval_update_cli_reports_unknown_id(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.pending_approvals as pending_approvals

    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(
        ["pending-approval-update", "demo", "pa_missing", "--status", "approved"]
    )

    captured = capsys.readouterr()
    assert result == 1
    assert "Error: Pending approval not found: pa_missing" in captured.out


def test_pending_approval_batch_update_cli_updates_registry_from_file(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.pending_approvals as pending_approvals

    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {
            "current_chapter": 1,
            "pending_approvals": ["Define system cost.", "Track QY-17."],
        },
    )
    pending_approvals.sync_pending_approvals("demo")
    registry_path = book / "state" / "pending_approvals.yaml"
    approvals = read_yaml(registry_path)["approvals"]
    updates_path = tmp_path / "updates.yaml"
    updates_path.write_text(
        "\n".join(
            [
                "updates:",
                f"- id: {approvals[0]['id']}",
                "  status: approved",
                "  note: Resolved in sample.",
                f"- id: {approvals[1]['id']}",
                "  status: deferred",
                "  note: Carry forward.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli.main(
        ["pending-approval-batch-update", "demo", "--updates-file", str(updates_path)]
    )

    captured = capsys.readouterr()
    registry = read_yaml(registry_path)
    by_id = {approval["id"]: approval for approval in registry["approvals"]}
    assert result == 0
    assert "Batch updated pending approvals: 2" in captured.out
    assert by_id[approvals[0]["id"]]["status"] == "approved"
    assert by_id[approvals[1]["id"]]["status"] == "deferred"
