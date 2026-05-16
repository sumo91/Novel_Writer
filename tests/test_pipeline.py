import json

import pytest

from engine import acceptance_packet, book_factory, context_builder, pipeline
from engine.io_utils import write_json


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

    output = pipeline.pipeline_draft_acceptance(
        "demo",
        1,
        title="First Signal",
        summary="Summary.",
    )

    assert output == book / "state_updates" / "ch_0001_acceptance.yaml"
    assert output.exists()
