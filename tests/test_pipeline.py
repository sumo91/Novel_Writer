from engine import pipeline


def test_pipeline_paths_for_chapter(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")

    paths = pipeline.pipeline_paths("demo", 1)

    assert paths.root == tmp_path / "books" / "demo"
    assert paths.pipeline_dir == tmp_path / "books" / "demo" / "pipeline" / "ch_0001"
    assert paths.context_path == paths.pipeline_dir / "context.md"
    assert paths.manifest_path == paths.pipeline_dir / "manifest.json"
    assert paths.handoff_dir == paths.pipeline_dir / "handoffs"
