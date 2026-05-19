from engine import (
    acceptance_packet,
    book_factory,
    brief_contract,
    cli,
    outline_gate,
    pipeline,
    style_knowledge,
    v3_migration,
)
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


def test_pipeline_quality_gate_cli_writes_html_review_summary(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {"passed": True, "issues": [], "required_fixes": []},
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 86,
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

    result = cli.main(["pipeline-quality-gate", "demo", "1"])

    captured = capsys.readouterr()
    output = book / "reviews" / "ch_0001" / "quality_gate.html"
    assert result == 0
    assert f"HTML review copy: {output.as_posix()}" in captured.out
    assert output.exists()
    assert "Quality Gate" in output.read_text(encoding="utf-8")


def test_author_direction_scaffold_cli_writes_yaml_and_html(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["author-direction-scaffold", "demo", "1"])

    captured = capsys.readouterr()
    output = book / "authoring" / "ch_0001_author_direction.yaml"
    assert result == 0
    assert output.exists()
    assert output.with_suffix(".html").exists()
    assert f"Wrote author direction scaffold: {output.as_posix()}" in captured.out
    assert f"HTML review copy: {output.with_suffix('.html').as_posix()}" in captured.out


def test_pipeline_prose_quality_gate_cli_reports_review_result(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        {
            "score": 82,
            "dimension_scores": {
                "opening_hook": 8,
                "conflict_pressure": 8,
                "protagonist_agency": 8,
                "payoff_execution": 11,
                "dialogue_tension": 8,
                "scene_specificity": 8,
                "voice_distinction": 8,
                "rhythm_variation": 8,
                "ending_pull": 8,
                "style_slop_control": 4,
            },
            "blocking_issues": [],
            "rewrite_required": False,
        },
    )

    result = cli.main(["pipeline-prose-quality-gate", "demo", "1"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Prose quality gate: needs_rewrite" in captured.out
    assert "- score: 82" in captured.out
    assert "- reason: Prose quality score 82 is below 85." in captured.out


def test_style_bible_scaffold_cli_writes_yaml_and_html(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["style-bible-scaffold", "demo", "--force"])

    captured = capsys.readouterr()
    output = book / "style" / "style_bible.yaml"
    assert result == 0
    assert output.exists()
    assert output.with_suffix(".html").exists()
    assert f"Wrote style bible scaffold: {output.as_posix()}" in captured.out
    assert f"HTML review copy: {output.with_suffix('.html').as_posix()}" in captured.out


def test_style_bible_check_cli_reports_errors(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(style_knowledge, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "style" / "style_bible.yaml").write_text("book_id: demo\n", encoding="utf-8")

    result = cli.main(["style-bible-check", "demo"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Style bible check: failed" in captured.out
    assert "missing required field narration" in captured.out


def test_prepare_chapter_cli_reports_brief_gate_and_check_status(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    import engine.context_builder as context_builder

    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["prepare-chapter", "demo", "5"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Prepared chapter pipeline:" in captured.out
    assert "Chapter brief gate:" in captured.out
    assert "Chapter brief check:" in captured.out


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
    assert f"HTML review copy: {output.with_suffix('.html').as_posix()}" in captured.out
    assert output.with_suffix(".html").exists()
    content = output.read_text(encoding="utf-8")
    assert "# Chapter 1-1 Drift Review" in content
    assert "| 1 | 88 |  | False |" in content


def test_pipeline_draft_acceptance_cli_writes_html_sidecar(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {"proposed_state_updates": ["State changed."]},
    )
    write_json(book / "reviews" / "ch_0001" / "pacing_review.json", {})
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        {
            "score": 88,
            "dimension_scores": {
                "opening_hook": 9,
                "conflict_pressure": 9,
                "protagonist_agency": 9,
                "payoff_execution": 13,
                "dialogue_tension": 9,
                "scene_specificity": 9,
                "voice_distinction": 8,
                "rhythm_variation": 8,
                "ending_pull": 9,
                "style_slop_control": 5,
            },
            "blocking_issues": [],
            "rewrite_required": False,
        },
    )
    (book / "drafts" / "ch_0001_final_candidate.md").write_text(
        "final candidate", encoding="utf-8"
    )

    result = cli.main(
        [
            "pipeline-draft-acceptance",
            "demo",
            "1",
            "--title",
            "First Signal",
            "--summary",
            "Summary.",
        ]
    )

    captured = capsys.readouterr()
    output = book / "state_updates" / "ch_0001_acceptance.yaml"
    assert result == 0
    assert f"Drafted pipeline acceptance packet: {output.as_posix()}" in captured.out
    assert f"HTML review copy: {output.with_suffix('.html').as_posix()}" in captured.out
    assert output.with_suffix(".html").exists()


def test_accept_chapter_cli_requires_explicit_approval(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.chapter_acceptance as chapter_acceptance
    import engine.pipeline as pipeline

    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    packet = book / "state_updates" / "ch_0001_acceptance.yaml"
    packet.write_text(
        "\n".join(
            [
                "chapter: 1",
                "title: First Signal",
                "source_draft: drafts/ch_0001_revised.md",
                "summary: Summary.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli.main(["accept-chapter", "demo", "--update-file", packet.as_posix()])

    captured = capsys.readouterr()
    assert result == 1
    assert "Human approval is required" in captured.out
    assert not (book / "chapters" / "ch_0001.md").exists()


def test_accept_chapter_cli_validates_supplied_update_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.chapter_acceptance as chapter_acceptance
    import engine.pipeline as pipeline

    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    packet = book / "state_updates" / "manual_packet.yaml"
    packet.write_text(
        "\n".join(
            [
                "chapter: 1",
                "title: First Signal",
                "source_draft: drafts/ch_0001_revised.md",
                "summary: Summary.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli.main(
        ["accept-chapter", "demo", "--update-file", packet.as_posix(), "--approved"]
    )

    captured = capsys.readouterr()
    assert result == 1
    assert "Acceptance packet is missing fields" in captured.out
    assert not (book / "chapters" / "ch_0001.md").exists()


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


def test_migrate_v3_cli_creates_missing_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    missing_path = book / "state" / "hook_index.json"
    missing_path.unlink()

    result = cli.main(["migrate-v3", "demo"])

    captured = capsys.readouterr()
    assert result == 0
    assert missing_path.exists()
    assert "Migrated book to V3: demo" in captured.out
    assert "- created: state/hook_index.json" in captured.out


def test_migrate_v3_1_cli_creates_missing_outline_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    missing_path = book / "outlines" / "volumes" / "volume_001.yaml"
    missing_path.unlink()

    result = cli.main(["migrate-v3-1", "demo"])

    captured = capsys.readouterr()
    assert result == 0
    assert missing_path.exists()
    assert "Migrated book to V3.1: demo" in captured.out
    assert "- created: outlines/volumes/volume_001.yaml" in captured.out


def test_outline_status_cli_lists_approval_layers(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["outline-status", "demo"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Outline status: demo" in captured.out
    assert "- master: draft (outlines/master_outline.yaml)" in captured.out
    assert "- factions: draft (canon/factions.yaml)" in captured.out


def test_outline_approval_update_cli_updates_layer(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(
        [
            "outline-approval-update",
            "demo",
            "unit",
            "--status",
            "approved",
            "--note",
            "Ready for next brief.",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert "Updated outline approval: unit -> approved" in captured.out


def test_chapter_brief_gate_cli_blocks_strict_draft_layers(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["chapter-brief-gate", "demo", "5", "--strict"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Chapter brief gate: blocked" in captured.out
    assert "master (outlines/master_outline.yaml) is draft, not approved." in captured.out


def test_chapter_brief_scaffold_cli_writes_brief(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    result = cli.main(["chapter-brief-scaffold", "demo", "5"])

    captured = capsys.readouterr()
    output = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    assert result == 0
    assert output.exists()
    assert f"Wrote chapter brief scaffold: {output.as_posix()}" in captured.out
    assert f"HTML review copy: {output.with_suffix('.html').as_posix()}" in captured.out
    assert output.with_suffix(".html").exists()
    assert "## V3.3 Outline Contract" in output.read_text(encoding="utf-8")


def test_chapter_brief_scaffold_cli_refuses_overwrite_without_force(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    output = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("Existing brief.", encoding="utf-8")

    result = cli.main(["chapter-brief-scaffold", "demo", "5"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Error: Chapter brief already exists" in captured.out
    assert output.read_text(encoding="utf-8") == "Existing brief."


def test_chapter_brief_check_cli_reports_passed_scaffold(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(brief_contract, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(outline_gate, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    output = book / "outlines" / "chapter_briefs" / "ch_0005_brief.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        brief_contract.build_chapter_brief_scaffold("demo", 5),
        encoding="utf-8",
    )

    result = cli.main(["chapter-brief-check", "demo", "5"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Chapter brief check: passed" in captured.out
