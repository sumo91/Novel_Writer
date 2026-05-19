import json

import pytest

from engine import acceptance_packet, book_factory, context_builder, craft_knowledge, pipeline
from engine.io_utils import read_yaml, write_json, write_yaml


def test_pipeline_paths_for_chapter(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")

    paths = pipeline.pipeline_paths("demo", 1)

    assert paths.root == tmp_path / "books" / "demo"
    assert paths.pipeline_dir == tmp_path / "books" / "demo" / "pipeline" / "ch_0001"
    assert paths.context_path == paths.pipeline_dir / "context.md"
    assert paths.manifest_path == paths.pipeline_dir / "manifest.json"
    assert paths.handoff_dir == paths.pipeline_dir / "handoffs"


def test_prepare_chapter_creates_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")

    result = pipeline.prepare_chapter("demo", 1)

    assert result.pipeline_dir == tmp_path / "books" / "demo" / "pipeline" / "ch_0001"
    assert result.context_path.exists()
    assert result.manifest_path.exists()
    assert (result.handoff_dir / "01_plot_planner.md").exists()
    assert (result.handoff_dir / "02_chapter_writer.md").exists()
    assert (result.handoff_dir / "03_continuity_editor.md").exists()
    assert (result.handoff_dir / "04_tomato_pacing_editor.md").exists()
    assert (result.handoff_dir / "05_reviser.md").exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["book_id"] == "demo"
    assert manifest["chapter"] == 1
    assert manifest["status"] == "prepared"
    assert manifest["artifacts"]["context"] == "pipeline/ch_0001/context.md"
    assert manifest["artifacts"]["brief"] == "outlines/chapter_briefs/ch_0001_brief.md"


def test_prepare_chapter_handoffs_include_v3_expectations(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")

    result = pipeline.prepare_chapter("demo", 1)

    continuity = (result.handoff_dir / "03_continuity_editor.md").read_text(
        encoding="utf-8"
    )
    pacing = (result.handoff_dir / "04_tomato_pacing_editor.md").read_text(
        encoding="utf-8"
    )
    assert "V3 state updates" in continuity
    assert "payoff ledger" in pacing


def test_prepare_chapter_handoffs_include_v3_1_outline_obligations(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")

    result = pipeline.prepare_chapter("demo", 1)

    plot_planner = (result.handoff_dir / "01_plot_planner.md").read_text(
        encoding="utf-8"
    )
    continuity = (result.handoff_dir / "03_continuity_editor.md").read_text(
        encoding="utf-8"
    )
    assert "V3.1 outline obligations" in plot_planner
    assert "master -> volume -> arc -> unit -> chapter brief" in plot_planner
    assert "served the active unit and arc function" in continuity


def test_prepare_chapter_review_handoffs_include_craft_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr(craft_knowledge, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    card_dir = tmp_path / "knowledge" / "craft_cards"
    card_dir.mkdir(parents=True)
    (card_dir / "review.yaml").write_text(
        "\n".join(
            [
                "id: craft_review_passive_protagonist",
                "applies_to: [review]",
                "principle: Flag chapters where the protagonist does not drive the scene.",
                "checks:",
                "  - Identify the protagonist's decisive action.",
                "failure_modes:",
                "  - Passive protagonist",
                "",
            ]
        ),
        encoding="utf-8",
    )
    book_factory.create_book("demo", title="Demo Book")

    result = pipeline.prepare_chapter("demo", 1)

    continuity = (result.handoff_dir / "03_continuity_editor.md").read_text(
        encoding="utf-8"
    )
    pacing = (result.handoff_dir / "04_tomato_pacing_editor.md").read_text(
        encoding="utf-8"
    )
    assert "## Craft Knowledge Cards" in continuity
    assert "craft_review_passive_protagonist" in continuity
    assert "Identify the protagonist's decisive action." in pacing


def test_prepare_chapter_refuses_existing_workspace_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)

    with pytest.raises(FileExistsError):
        pipeline.prepare_chapter("demo", 1)


def test_prepare_chapter_force_replaces_existing_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")
    result = pipeline.prepare_chapter("demo", 1)
    stale_file = result.pipeline_dir / "stale.txt"
    stale_file.write_text("remove me", encoding="utf-8")

    pipeline.prepare_chapter("demo", 1, force=True)

    assert not stale_file.exists()


def test_pipeline_status_reports_missing_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)

    status = pipeline.pipeline_status("demo", 1)

    assert status["book_id"] == "demo"
    assert status["chapter"] == 1
    assert status["status"] == "needs_brief"
    assert status["artifacts"]["context"]["present"] is True
    assert status["artifacts"]["style_bible"]["present"] is True
    assert status["artifacts"]["brief"]["present"] is False
    assert status["next_action"] == "Create chapter brief."


def test_pipeline_status_advances_when_files_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)
    (book / "outlines" / "chapter_briefs").mkdir()
    (book / "outlines" / "chapter_briefs" / "ch_0001_brief.md").write_text(
        "brief", encoding="utf-8"
    )
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_draft.md").write_text("draft", encoding="utf-8")

    status = pipeline.pipeline_status("demo", 1)

    assert status["status"] == "needs_reviews"
    assert status["artifacts"]["brief"]["present"] is True
    assert status["artifacts"]["draft"]["present"] is True
    assert status["artifacts"]["continuity_review"]["present"] is False


def test_pipeline_status_requires_author_direction_after_revised_draft(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)
    (book / "outlines" / "chapter_briefs").mkdir()
    (book / "outlines" / "chapter_briefs" / "ch_0001_brief.md").write_text(
        "brief", encoding="utf-8"
    )
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_draft.md").write_text("draft", encoding="utf-8")
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")
    write_json(book / "reviews" / "ch_0001" / "continuity_review.json", {})
    write_json(book / "reviews" / "ch_0001" / "pacing_review.json", {"score": 90})

    status = pipeline.pipeline_status("demo", 1)

    assert status["status"] == "needs_author_direction"
    assert status["artifacts"]["author_direction"]["present"] is False
    assert status["next_action"] == "Create or approve author direction notes."


def test_pipeline_status_merges_v4_1_artifacts_into_old_manifest(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    paths = pipeline.prepare_chapter("demo", 1)
    manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"].pop("author_direction")
    manifest["artifacts"].pop("prose_quality_review")
    manifest["artifacts"].pop("final_candidate")
    paths.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _write_complete_revised_inputs(book)

    status = pipeline.pipeline_status("demo", 1)

    assert status["status"] == "needs_author_direction"
    assert status["artifacts"]["author_direction"]["path"] == (
        "authoring/ch_0001_author_direction.yaml"
    )


def test_pipeline_status_requires_prose_quality_review_after_author_direction(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)
    _write_complete_revised_inputs(book)
    write_yaml(
        book / "authoring" / "ch_0001_author_direction.yaml",
        {
            "chapter": 1,
            "author_intent": ["Keep the protagonist in control."],
            "approved_for_final_candidate": True,
        },
    )

    status = pipeline.pipeline_status("demo", 1)

    assert status["status"] == "needs_prose_quality_review"
    assert status["artifacts"]["prose_quality_review"]["present"] is False
    assert status["next_action"] == "Create prose quality review."


def test_pipeline_status_requires_final_candidate_after_quality_review(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    pipeline.prepare_chapter("demo", 1)
    _write_complete_revised_inputs(book)
    write_yaml(
        book / "authoring" / "ch_0001_author_direction.yaml",
        {
            "chapter": 1,
            "author_intent": ["Keep the protagonist in control."],
            "approved_for_final_candidate": True,
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        _passing_prose_quality_review(),
    )

    status = pipeline.pipeline_status("demo", 1)

    assert status["status"] == "needs_final_candidate"
    assert status["artifacts"]["final_candidate"]["present"] is False
    assert status["next_action"] == "Create AI-assisted final candidate draft."


def test_pipeline_draft_acceptance_uses_final_candidate_by_default(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    _write_complete_revised_inputs(book)
    (book / "drafts" / "ch_0001_final_candidate.md").write_text(
        "final candidate", encoding="utf-8"
    )
    write_yaml(
        book / "authoring" / "ch_0001_author_direction.yaml",
        {
            "chapter": 1,
            "author_intent": ["Keep the protagonist in control."],
            "approved_for_final_candidate": True,
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        _passing_prose_quality_review(),
    )

    output = pipeline.pipeline_draft_acceptance(
        "demo",
        1,
        title="First Signal",
        summary="Summary.",
    )

    packet = read_yaml(output)
    assert packet["source_draft"] == "drafts/ch_0001_final_candidate.md"


def test_pipeline_prose_quality_gate_passes_high_quality_review(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "reviews" / "ch_0001" / "prose_quality_review.json",
        _passing_prose_quality_review(),
    )

    result = pipeline.pipeline_prose_quality_gate("demo", 1)

    assert result["passed"] is True
    assert result["status"] == "passed"
    assert result["score"] == 88
    assert result["rewrite_required"] is False


def test_pipeline_prose_quality_gate_requires_rewrite_below_threshold(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    review = _passing_prose_quality_review()
    review["score"] = 82
    write_json(book / "reviews" / "ch_0001" / "prose_quality_review.json", review)

    result = pipeline.pipeline_prose_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "needs_rewrite"
    assert result["rewrite_required"] is True
    assert "Prose quality score 82 is below 85." in result["reasons"]


def test_pipeline_prose_quality_gate_blocks_low_dimension_score(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    review = _passing_prose_quality_review()
    review["dimension_scores"]["dialogue_tension"] = 5
    write_json(book / "reviews" / "ch_0001" / "prose_quality_review.json", review)

    result = pipeline.pipeline_prose_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "needs_rewrite"
    assert "dialogue_tension is below 7." in result["reasons"]


def test_pipeline_prose_quality_gate_requires_style_alignment(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    review = _passing_prose_quality_review()
    review["style_alignment"] = {
        "passed": False,
        "score": 76,
        "violations": ["Dialogue sounds like generic霸总 voice."],
    }
    write_json(book / "reviews" / "ch_0001" / "prose_quality_review.json", review)

    result = pipeline.pipeline_prose_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "needs_rewrite"
    assert "Style alignment score 76 is below 85." in result["reasons"]
    assert "Dialogue sounds like generic霸总 voice." in result["reasons"]


def test_author_direction_scaffold_writes_human_lightweight_controls(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")

    output = pipeline.write_author_direction_scaffold("demo", 1)

    data = read_yaml(output)
    assert output == book / "authoring" / "ch_0001_author_direction.yaml"
    assert data["chapter"] == 1
    assert data["approved_for_final_candidate"] is False
    assert "author_intent" in data
    assert output.with_suffix(".html").exists()


def test_pipeline_draft_acceptance_requires_revised_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    with pytest.raises(FileNotFoundError, match="revised draft"):
        pipeline.pipeline_draft_acceptance(
            "demo",
            1,
            title="First Signal",
            summary="Summary.",
        )


def test_pipeline_draft_acceptance_requires_reviews_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="review"):
        pipeline.pipeline_draft_acceptance(
            "demo",
            1,
            title="First Signal",
            summary="Summary.",
        )


def test_pipeline_draft_acceptance_creates_packet(tmp_path, monkeypatch):
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
        _passing_prose_quality_review(),
    )
    (book / "drafts" / "ch_0001_final_candidate.md").write_text(
        "final candidate", encoding="utf-8"
    )

    output = pipeline.pipeline_draft_acceptance(
        "demo",
        1,
        title="First Signal",
        summary="Summary.",
    )

    assert output == book / "state_updates" / "ch_0001_acceptance.yaml"
    assert output.exists()


def test_pipeline_accept_requires_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    with pytest.raises(PermissionError, match="approval"):
        pipeline.pipeline_accept("demo", 1, approved=False)


def test_pipeline_accept_requires_acceptance_packet(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    with pytest.raises(FileNotFoundError, match="acceptance packet"):
        pipeline.pipeline_accept("demo", 1, approved=True)


def test_pipeline_accept_applies_packet(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    import engine.chapter_acceptance as chapter_acceptance

    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="Summary.",
    )

    result = pipeline.pipeline_accept("demo", 1, approved=True)

    assert result == book / "chapters" / "ch_0001.md"
    assert result.read_text(encoding="utf-8") == "accepted"


def test_pipeline_accept_rejects_stale_acceptance_contract_snapshot(tmp_path, monkeypatch):
    books_root = tmp_path / "books"
    books_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(book_factory, "BOOKS_DIR", books_root)
    monkeypatch.setattr(pipeline, "BOOKS_DIR", books_root)
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", books_root)
    import engine.chapter_acceptance as chapter_acceptance

    monkeypatch.setattr(chapter_acceptance, "BOOKS_DIR", books_root)
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="Summary.",
    )
    packet = read_yaml(output)
    packet["acceptance_contract"]["quality_gate_summary"]["pacing_score"] = 42
    output.write_text(
        __import__("yaml").safe_dump(packet, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="acceptance_contract"):
        pipeline.pipeline_accept("demo", 1, approved=True)


def test_validate_book_ignores_acceptance_contract_snapshot_freshness(tmp_path, monkeypatch):
    books_root = tmp_path / "books"
    books_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(book_factory, "BOOKS_DIR", books_root)
    monkeypatch.setattr(pipeline, "BOOKS_DIR", books_root)
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", books_root)
    import engine.validators as validators

    monkeypatch.setattr(validators, "BOOKS_DIR", books_root)
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="Summary.",
    )
    packet = read_yaml(output)
    packet["acceptance_contract"]["quality_gate_summary"]["pacing_score"] = 42
    output.write_text(
        __import__("yaml").safe_dump(packet, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    assert validators.validate_book("demo") == []


def test_pipeline_accept_rejects_stale_acceptance_packet_text(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("accepted", encoding="utf-8")
    packet_path = book / "state_updates" / "ch_0001_acceptance.yaml"
    packet_path.parent.mkdir(exist_ok=True)
    packet_path.write_text(
        "\n".join(
            [
                "chapter: 1",
                "title: First Signal",
                "source_draft: drafts/ch_0001_revised.md",
                "accepted_chapter_path: chapters/ch_0001.md",
                "summary: Summary.",
                "current_state:",
                "  current_chapter: 1",
                "  current_arc: arc_001",
                "  latest_location: Backstage",
                "  active_characters: []",
                "  active_conflicts: []",
                "  pending_approvals: []",
                "state_changes: []",
                "open_threads_touched: []",
                "timeline_event:",
                "  id: t001",
                "  when: Chapter 1",
                "  summary: Summary.",
                "open_thread_updates: []",
                "change_log:",
                "  summary: pending human acceptance",
                "  canon_updates: []",
                "  pending_approvals: []",
                "acceptance_contract:",
                "  quality_gate_summary:",
                "    continuity_review_present: true",
                "    continuity_blockers: []",
                "    pacing_review_present: true",
                "    pacing_score: 86",
                "    revised_pacing_score: 86",
                "    revision_required: false",
                "    waiver_required: false",
                "  outline_alignment:",
                "    reference_chain: master -> volume -> arc -> unit -> chapter brief",
                "    volume_id: volume_001",
                "    arc_id: arc_001",
                "    unit_id: unit_0001",
                "    required_unit_obligations: []",
                "    claimed_fulfilled_unit_obligations: []",
                "    pending_unit_obligations: []",
                "  state_updates:",
                "    timeline_event:",
                "      id: t001",
                "      when: Chapter 1",
                "      summary: Summary.",
                "    character_state_changes: []",
                "    resource_changes: []",
                "    open_thread_updates: []",
                "    payoff_updates: []",
                "    next_hook: {}",
                "    pending_approvals: []",
                "    economy_changes: []",
                "    faction_changes: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stale text"):
        pipeline.pipeline_accept("demo", 1, approved=True)


def test_pipeline_quality_gate_passes_clean_reviews(tmp_path, monkeypatch):
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

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is True
    assert result["status"] == "passed"
    assert result["revision_required"] is False
    assert result["waiver_required"] is False
    assert result["initial_pacing_score"] == 86


def test_pipeline_quality_gate_rejects_invalid_total_score(tmp_path, monkeypatch):
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
            "score": 101,
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

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "invalid_review"
    assert "Pacing score must be an integer from 0 to 100." in result["reasons"]


def test_pipeline_quality_gate_rejects_invalid_dimension_score(tmp_path, monkeypatch):
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
            "score": 88,
            "dimension_scores": {
                "hook_strength": 9,
                "conflict_clarity": 8,
                "protagonist_agency": 9,
                "emotional_payoff": 12,
                "pacing": 8,
                "character_consistency": 9,
                "continuity_safety": 9,
                "chapter_end_pull": 8,
                "mainline_relevance": 9,
                "fresh_information_or_expectation": 8,
            },
        },
    )

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "invalid_review"
    assert "Pacing review has invalid dimension scores: emotional_payoff." in result[
        "reasons"
    ]


def test_pipeline_quality_gate_requires_revision_for_low_pacing_score(
    tmp_path, monkeypatch
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
            "score": 72,
            "dimension_scores": {
                "hook_strength": 7,
                "conflict_clarity": 7,
                "protagonist_agency": 7,
                "emotional_payoff": 7,
                "pacing": 7,
                "character_consistency": 8,
                "continuity_safety": 8,
                "chapter_end_pull": 7,
                "mainline_relevance": 7,
                "fresh_information_or_expectation": 7,
            },
        },
    )

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "needs_revision"
    assert result["revision_required"] is True
    assert "Pacing score 72 is below 80." in result["reasons"]


def test_pipeline_quality_gate_requires_waiver_after_low_revised_score(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {"passed": True, "issues": [], "required_fixes": []},
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 72,
            "revised_score": 78,
            "dimension_scores": {
                "hook_strength": 7,
                "conflict_clarity": 8,
                "protagonist_agency": 8,
                "emotional_payoff": 7,
                "pacing": 8,
                "character_consistency": 8,
                "continuity_safety": 8,
                "chapter_end_pull": 8,
                "mainline_relevance": 8,
                "fresh_information_or_expectation": 8,
            },
        },
    )

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "needs_waiver"
    assert result["revision_required"] is True
    assert result["waiver_required"] is True
    assert "Revised pacing score 78 is still below 80." in result["reasons"]


def test_pipeline_quality_gate_fails_continuity_blockers(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {
            "passed": False,
            "issues": [{"severity": "high", "evidence": "Wrong location."}],
            "required_fixes": ["Move scene back to the archive."],
        },
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 88,
            "dimension_scores": {
                "hook_strength": 9,
                "conflict_clarity": 9,
                "protagonist_agency": 9,
                "emotional_payoff": 8,
                "pacing": 9,
                "character_consistency": 8,
                "continuity_safety": 8,
                "chapter_end_pull": 9,
                "mainline_relevance": 9,
                "fresh_information_or_expectation": 9,
            },
        },
    )

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is False
    assert result["status"] == "blocked"
    assert result["continuity_blockers"] == [
        "Move scene back to the archive.",
        "Wrong location.",
    ]


def test_pipeline_quality_gate_accepts_quality_gate_waiver(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")
    write_json(
        book / "reviews" / "ch_0001" / "continuity_review.json",
        {"passed": True, "issues": [], "required_fixes": []},
    )
    write_json(
        book / "reviews" / "ch_0001" / "pacing_review.json",
        {
            "score": 72,
            "revised_score": 78,
            "dimension_scores": {
                "hook_strength": 7,
                "conflict_clarity": 8,
                "protagonist_agency": 8,
                "emotional_payoff": 7,
                "pacing": 8,
                "character_consistency": 8,
                "continuity_safety": 8,
                "chapter_end_pull": 8,
                "mainline_relevance": 8,
                "fresh_information_or_expectation": 8,
            },
        },
    )
    packet_path = book / "state_updates" / "ch_0001_acceptance.yaml"
    packet_path.write_text(
        "\n".join(
            [
                "quality_gate:",
                "  waiver:",
                "    required: true",
                "    type: pacing",
                "    reason: Strategic slow-burn setup.",
                "    approved_by: human",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = pipeline.pipeline_quality_gate("demo", 1)

    assert result["passed"] is True
    assert result["status"] == "passed_with_waiver"
    assert result["waiver_required"] is True


def _write_complete_revised_inputs(book):
    (book / "outlines" / "chapter_briefs").mkdir()
    (book / "outlines" / "chapter_briefs" / "ch_0001_brief.md").write_text(
        "brief", encoding="utf-8"
    )
    (book / "drafts").mkdir()
    (book / "drafts" / "ch_0001_draft.md").write_text("draft", encoding="utf-8")
    (book / "drafts" / "ch_0001_revised.md").write_text("revised", encoding="utf-8")
    write_json(book / "reviews" / "ch_0001" / "continuity_review.json", {})
    write_json(book / "reviews" / "ch_0001" / "pacing_review.json", {"score": 90})


def _passing_prose_quality_review():
    return {
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
    }
