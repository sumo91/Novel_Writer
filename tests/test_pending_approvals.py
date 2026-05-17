from engine import book_factory, pending_approvals
from engine.io_utils import read_yaml, write_json


def test_collect_pending_approvals_dedupes_and_tracks_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {
            "current_chapter": 2,
            "pending_approvals": ["Define system cost.", "Track QY-17."],
        },
    )
    (book / "state" / "change_log.jsonl").write_text(
        "\n".join(
            [
                '{"chapter": 1, "pending_approvals": ["Define system cost."]}',
                '{"chapter": 2, "pending_approvals": ["Define system cost.", "Track QY-17."]}',
                "",
            ]
        ),
        encoding="utf-8",
    )

    approvals = pending_approvals.collect_pending_approvals("demo")

    by_text = {approval.text: approval for approval in approvals}
    assert set(by_text) == {
        "逆光系统代价方向：信任资源消耗、授权人风险、反制窗口缩短。",
        "Track QY-17.",
    }
    system_cost = by_text["逆光系统代价方向：信任资源消耗、授权人风险、反制窗口缩短。"]
    assert system_cost.id.startswith("pa_")
    assert system_cost.source_chapters == (1, 2)
    assert "Define system cost." in system_cost.variants
    assert "state/current_state.json" in system_cost.sources
    assert "state/change_log.jsonl:chapter_1" in system_cost.sources


def test_sync_pending_approvals_writes_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 1, "pending_approvals": ["Define system cost."]},
    )

    output = pending_approvals.sync_pending_approvals("demo")

    registry = read_yaml(output)
    assert output == book / "state" / "pending_approvals.yaml"
    assert registry["approvals"][0]["id"].startswith("pa_")
    assert registry["approvals"][0]["status"] == "open"
    assert registry["approvals"][0]["source_chapters"] == [1]
    assert "Define system cost." in registry["approvals"][0]["variants"]


def test_sync_pending_approvals_preserves_existing_status_and_note(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 1, "pending_approvals": ["Define system cost."]},
    )
    pending_approvals.sync_pending_approvals("demo")
    registry_path = book / "state" / "pending_approvals.yaml"
    registry = read_yaml(registry_path)
    registry["approvals"][0]["status"] = "approved"
    registry["approvals"][0]["note"] = "Use trust-resource cost direction."
    pending_approvals.write_yaml(registry_path, registry)

    pending_approvals.sync_pending_approvals("demo")

    updated = read_yaml(registry_path)
    assert updated["approvals"][0]["status"] == "approved"
    assert updated["approvals"][0]["note"] == "Use trust-resource cost direction."


def test_update_pending_approval_status_updates_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pending_approvals, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(
        book / "state" / "current_state.json",
        {"current_chapter": 1, "pending_approvals": ["Define system cost."]},
    )
    pending_approvals.sync_pending_approvals("demo")
    approval_id = read_yaml(book / "state" / "pending_approvals.yaml")["approvals"][0][
        "id"
    ]

    pending_approvals.update_pending_approval(
        "demo",
        approval_id,
        status="deferred",
        note="Wait for target-genre pilot.",
    )

    registry = read_yaml(book / "state" / "pending_approvals.yaml")
    assert registry["approvals"][0]["status"] == "deferred"
    assert registry["approvals"][0]["note"] == "Wait for target-genre pilot."


def test_batch_update_pending_approvals_writes_multiple_changes_once(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
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
    first_id = approvals[0]["id"]
    second_id = approvals[1]["id"]

    updated_path = pending_approvals.batch_update_pending_approvals(
        "demo",
        [
            {"id": first_id, "status": "approved", "note": "Resolved in sample."},
            {"id": second_id, "status": "deferred", "note": "Carry forward."},
        ],
    )

    registry = read_yaml(updated_path)
    by_id = {approval["id"]: approval for approval in registry["approvals"]}
    assert updated_path == registry_path
    assert by_id[first_id]["status"] == "approved"
    assert by_id[first_id]["note"] == "Resolved in sample."
    assert by_id[second_id]["status"] == "deferred"
    assert by_id[second_id]["note"] == "Carry forward."
