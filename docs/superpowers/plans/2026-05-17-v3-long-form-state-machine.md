# V3 Long-Form State Machine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the V3 file-based long-form state machine so accepted chapters update explicit memory ledgers for characters, resources, open threads, payoffs, hooks, conflicts, and 10-chapter unit planning.

**Architecture:** Keep V2.6's chapter pipeline intact and extend the acceptance packet as the only durable state-update contract. Add focused V3 helper modules for ledger application and migration, then wire validators, context packs, and drift reports to the new files. Storage remains YAML/JSON/JSONL with conservative lightweight migration and no intelligent prose backfill.

**Tech Stack:** Python standard library, PyYAML through existing `engine.io_utils`, pytest, file-based book templates under `engine/templates/book/`.

---

## Source Spec

Implement from:

- `docs/superpowers/specs/2026-05-17-v3-long-form-state-machine-design.md`

## Current Baseline

Relevant existing files:

- `engine/acceptance_packet.py` drafts V2 acceptance YAML from revised draft, current state, and reviews.
- `engine/chapter_acceptance.py` copies the accepted chapter and updates `chapter_index.json`, `current_state.json`, `timeline.yaml`, `open_threads.yaml`, and `change_log.jsonl`.
- `engine/context_builder.py` builds a Markdown context pack by dumping selected canon and state files.
- `engine/drift_report.py` generates the current drift report from chapter index, current state, timeline, open threads, reviews, and pending approvals.
- `engine/hardening.py` validates reviews, acceptance packets, and pending approval registries.
- `engine/validators.py` validates required book files and existing pipeline artifacts.
- `engine/book_factory.py` creates a new book by copying `engine/templates/book`.
- `engine/cli.py` wires commands.

## File Structure

Create:

- `engine/v3_state.py`: pure helpers for applying V3 acceptance packet updates to ledgers and indexes.
- `engine/v3_migration.py`: conservative migration helper for adding missing V3 files and mechanical backfill.
- `engine/templates/book/canon/character_states.yaml`: dynamic per-character state ledger template.
- `engine/templates/book/canon/resource_ledger.yaml`: money/item/power/debt ledger template.
- `engine/templates/book/canon/payoff_ledger.yaml`: chapter-level promise and payoff ledger template.
- `engine/templates/book/outlines/units/unit_0001.yaml`: first 10-chapter unit planning template.
- `engine/templates/book/state/hook_index.json`: next-hook tracking template.
- `engine/templates/book/state/memory_index.json`: deterministic memory lookup index template.
- `tests/test_v3_state.py`: unit tests for applying V3 packet updates.
- `tests/test_v3_migration.py`: tests for lightweight migration.
- `docs/workflows/v3-long-form-state-machine.md`: operator-facing workflow notes.

Modify:

- `engine/templates/book/canon/open_threads.yaml`: upgrade template schema.
- `engine/templates/book/state/current_state.json`: include V3-friendly current fields while preserving existing required fields.
- `engine/acceptance_packet.py`: draft a valid empty/minimal `v3_state_updates` section.
- `engine/chapter_acceptance.py`: call V3 ledger application after existing V2 state updates.
- `engine/hardening.py`: validate V3 acceptance packet sections and V3 ledger files.
- `engine/validators.py`: require V3 files and call V3 ledger validation.
- `engine/context_builder.py`: include concise V3 memory sections.
- `engine/drift_report.py`: add V3 warning sections.
- `engine/cli.py`: add `migrate-v3` command.
- `tests/test_acceptance_packet.py`: assert packet includes V3 state update scaffold.
- `tests/test_chapter_acceptance.py`: assert V3 ledgers are updated during acceptance.
- `tests/test_context_builder.py`: assert V3 memory appears in context.
- `tests/test_cli.py`: assert migration command works and drift report includes V3 sections.
- `tests/test_validators.py`: assert V3 validation catches malformed ledgers.
- `AGENTS.md`: mention V3 files and migration command if workflow changes.

## Data Contracts

Use these constants in `engine/v3_state.py` or `engine/hardening.py`:

```python
OPEN_THREAD_STATUSES = {"open", "advanced", "paid_off", "deferred", "dropped"}
HOOK_STATUSES = {"open", "answered", "deferred", "dropped"}
FRUSTRATION_LEVELS = {"low", "controlled", "high", "overdue"}
RESOURCE_CATEGORIES = {
    "money",
    "item",
    "trade_good",
    "power",
    "debt",
    "relationship_asset",
    "knowledge",
}
DEFAULT_PAYOFF_TYPES = {
    "赚钱",
    "打脸",
    "护短",
    "升级",
    "揭谜",
    "交易",
    "压价",
    "身份",
    "报仇",
    "救人",
    "经营",
}
```

Book-specific payoff types may be allowed later, but V3 first pass should only warn on unknown types instead of blocking acceptance.

---

### Task 1: Add V3 Book Templates

**Files:**

- Create: `engine/templates/book/canon/character_states.yaml`
- Create: `engine/templates/book/canon/resource_ledger.yaml`
- Create: `engine/templates/book/canon/payoff_ledger.yaml`
- Create: `engine/templates/book/outlines/units/unit_0001.yaml`
- Create: `engine/templates/book/state/hook_index.json`
- Create: `engine/templates/book/state/memory_index.json`
- Modify: `engine/templates/book/canon/open_threads.yaml`
- Modify: `engine/templates/book/state/current_state.json`
- Test: `tests/test_book_factory.py`

- [ ] **Step 1: Write failing template copy test**

Add this test to `tests/test_book_factory.py`:

```python
def test_create_book_includes_v3_state_machine_files(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")

    book = book_factory.create_book("demo", title="Demo Book")

    expected = [
        "canon/character_states.yaml",
        "canon/resource_ledger.yaml",
        "canon/payoff_ledger.yaml",
        "outlines/units/unit_0001.yaml",
        "state/hook_index.json",
        "state/memory_index.json",
    ]
    for relative_path in expected:
        assert (book / relative_path).exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_book_factory.py::test_create_book_includes_v3_state_machine_files -q
```

Expected: FAIL because the new template files do not exist yet.

- [ ] **Step 3: Add template files**

Create `engine/templates/book/canon/character_states.yaml`:

```yaml
characters: {}
```

Create `engine/templates/book/canon/resource_ledger.yaml`:

```yaml
resources: []
```

Create `engine/templates/book/canon/payoff_ledger.yaml`:

```yaml
entries: []
```

Create `engine/templates/book/outlines/units/unit_0001.yaml`:

```yaml
unit: 1
chapter_range:
  start: 1
  end: 10
unit_goal: ""
stage_enemy: ""
stage_payoffs: []
stage_end_hook: ""
chapters: []
```

Create `engine/templates/book/state/hook_index.json`:

```json
{
  "hooks": []
}
```

Create `engine/templates/book/state/memory_index.json`:

```json
{
  "by_character": {},
  "by_thread": {},
  "by_location": {},
  "by_resource": {}
}
```

Replace `engine/templates/book/canon/open_threads.yaml` with:

```yaml
threads: []
```

Keep the file empty in data terms, but validators will now expect every future thread item to use the V3 schema.

Update `engine/templates/book/state/current_state.json` to preserve existing keys and add optional V3-friendly keys:

```json
{
  "current_chapter": 0,
  "current_arc": "arc_001",
  "latest_location": "",
  "active_characters": [],
  "active_conflicts": [],
  "current_timeline": "",
  "pending_approvals": []
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_book_factory.py::test_create_book_includes_v3_state_machine_files -q
```

Expected: PASS.

- [ ] **Step 5: Run existing book factory tests**

Run:

```powershell
python -m pytest tests/test_book_factory.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/templates/book tests/test_book_factory.py
git commit -m "feat: add v3 book memory templates"
```

---

### Task 2: Validate V3 Ledgers And Acceptance Sections

**Files:**

- Modify: `engine/hardening.py`
- Modify: `engine/validators.py`
- Test: `tests/test_validators.py`

- [ ] **Step 1: Write failing validation tests**

Add tests to `tests/test_validators.py`:

```python
from engine import book_factory
from engine.io_utils import read_yaml, write_yaml
from engine.validators import validate_book
from engine.hardening import validate_acceptance_packet


def test_validate_book_requires_v3_files(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.validators as validators

    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "canon" / "payoff_ledger.yaml").unlink()

    errors = validate_book("demo")

    assert "Missing required file: canon/payoff_ledger.yaml" in errors


def test_validate_acceptance_packet_requires_v3_state_updates():
    errors = validate_acceptance_packet(
        {
            "chapter": 1,
            "title": "First",
            "source_draft": "drafts/ch_0001_revised.md",
            "accepted_chapter_path": "chapters/ch_0001.md",
            "summary": "Summary.",
            "current_state": {
                "current_chapter": 1,
                "current_arc": "arc_001",
                "latest_location": "",
                "active_characters": [],
                "active_conflicts": [],
                "pending_approvals": [],
            },
            "state_changes": [],
            "open_threads_touched": [],
            "timeline_event": {"id": "t001", "when": "第 1 章", "summary": "Summary."},
            "open_thread_updates": [],
            "change_log": {"summary": "Accepted.", "canon_updates": [], "pending_approvals": []},
        },
        chapter_number=1,
    )

    assert "Acceptance packet is missing fields: v3_state_updates." in errors


def test_validate_book_rejects_invalid_open_thread_status(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.validators as validators

    monkeypatch.setattr(validators, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_0001_01",
                    "promise": "Promise.",
                    "source_chapter": 1,
                    "status": "maybe",
                    "last_touched": 1,
                    "next_obligation": "Answer soon.",
                    "payoff_deadline": 3,
                    "risk_if_ignored": "Reader forgets.",
                }
            ]
        },
    )

    errors = validate_book("demo")

    assert any("open_threads.yaml" in error and "status" in error for error in errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_validators.py -q
```

Expected: FAIL because V3 required files and schemas are not validated yet.

- [ ] **Step 3: Add V3 constants and acceptance validation**

In `engine/hardening.py`, add:

```python
OPEN_THREAD_STATUSES = {"open", "advanced", "paid_off", "deferred", "dropped"}
HOOK_STATUSES = {"open", "answered", "deferred", "dropped"}
FRUSTRATION_LEVELS = {"low", "controlled", "high", "overdue"}
RESOURCE_CATEGORIES = {
    "money",
    "item",
    "trade_good",
    "power",
    "debt",
    "relationship_asset",
    "knowledge",
}

REQUIRED_V3_STATE_UPDATE_FIELDS = {
    "timeline",
    "character_states",
    "resource_changes",
    "open_thread_updates",
    "payoff_updates",
    "conflict_updates",
    "next_hook",
    "pending_approvals",
}
```

Add `"v3_state_updates"` to `REQUIRED_ACCEPTANCE_FIELDS`.

Extend `validate_acceptance_packet()`:

```python
    v3_updates = packet.get("v3_state_updates")
    if isinstance(v3_updates, dict):
        missing_v3 = sorted(
            field for field in REQUIRED_V3_STATE_UPDATE_FIELDS if field not in v3_updates
        )
        if missing_v3:
            errors.append(
                "Acceptance packet v3_state_updates is missing fields: "
                + ", ".join(missing_v3)
                + "."
            )
        errors.extend(validate_v3_state_updates(v3_updates))
    elif "v3_state_updates" in packet:
        errors.append("Acceptance packet v3_state_updates must be a mapping.")
```

Add:

```python
def validate_v3_state_updates(updates: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for list_field in (
        "character_states",
        "resource_changes",
        "open_thread_updates",
        "payoff_updates",
        "pending_approvals",
    ):
        if list_field in updates and not isinstance(updates[list_field], list):
            errors.append(f"v3_state_updates.{list_field} must be a list.")

    timeline = updates.get("timeline", {})
    if timeline and not isinstance(timeline, dict):
        errors.append("v3_state_updates.timeline must be a mapping.")
    elif isinstance(timeline, dict) and not isinstance(timeline.get("occurred_events", []), list):
        errors.append("v3_state_updates.timeline.occurred_events must be a list.")

    for thread in updates.get("open_thread_updates", []):
        if not isinstance(thread, dict):
            errors.append("v3_state_updates.open_thread_updates items must be mappings.")
            continue
        if thread.get("status") not in OPEN_THREAD_STATUSES:
            errors.append("v3_state_updates.open_thread_updates.status is invalid.")
        for field in ("id", "promise", "source_chapter", "last_touched"):
            if field not in thread or thread[field] in (None, ""):
                errors.append(f"v3_state_updates.open_thread_updates.{field} is required.")

    for payoff in updates.get("payoff_updates", []):
        if not isinstance(payoff, dict):
            errors.append("v3_state_updates.payoff_updates items must be mappings.")
            continue
        if payoff.get("frustration_level") not in FRUSTRATION_LEVELS:
            errors.append("v3_state_updates.payoff_updates.frustration_level is invalid.")
        if not payoff.get("promises_made") and not payoff.get("payoffs_delivered"):
            errors.append("v3_state_updates.payoff_updates needs a promise or payoff.")

    next_hook = updates.get("next_hook")
    if next_hook not in ({}, None) and not isinstance(next_hook, dict):
        errors.append("v3_state_updates.next_hook must be a mapping.")

    return errors
```

- [ ] **Step 4: Add V3 ledger validators**

Add to `engine/hardening.py`:

```python
def validate_v3_ledgers(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_open_threads_ledger(root))
    errors.extend(validate_payoff_ledger(root))
    errors.extend(validate_character_states_ledger(root))
    errors.extend(validate_resource_ledger(root))
    errors.extend(validate_hook_index(root))
    errors.extend(validate_memory_index(root))
    return errors
```

Implement focused validators:

```python
def validate_open_threads_ledger(root: Path) -> list[str]:
    path = root / "canon" / "open_threads.yaml"
    if not path.exists():
        return []
    data = read_yaml(path)
    threads = data.get("threads")
    if not isinstance(threads, list):
        return ["canon/open_threads.yaml: threads must be a list."]
    errors = []
    for index, thread in enumerate(threads, start=1):
        prefix = f"canon/open_threads.yaml: threads[{index}]"
        if not isinstance(thread, dict):
            errors.append(f"{prefix} must be a mapping.")
            continue
        for field in ("id", "promise", "source_chapter", "status", "last_touched"):
            if field not in thread or thread[field] in (None, ""):
                errors.append(f"{prefix}.{field} is required.")
        if thread.get("status") not in OPEN_THREAD_STATUSES:
            errors.append(f"{prefix}.status must be one of {sorted(OPEN_THREAD_STATUSES)}.")
    return errors
```

For `payoff_ledger.yaml`, require `entries` list, valid `frustration_level` when present, and at least one promise or payoff per entry.

For `character_states.yaml`, require `characters` mapping; each populated character must have `last_updated_chapter`.

For `resource_ledger.yaml`, require `resources` list; each item must have `id`, `owner`, `name`, `category`, `last_updated_chapter`, and valid category.

For `hook_index.json`, require `hooks` list and valid status when present.

For `memory_index.json`, require mappings for `by_character`, `by_thread`, `by_location`, and `by_resource`.

- [ ] **Step 5: Wire validators**

In `engine/validators.py`, add V3 files to `REQUIRED_BOOK_FILES`:

```python
"canon/character_states.yaml",
"canon/resource_ledger.yaml",
"canon/payoff_ledger.yaml",
"outlines/units/unit_0001.yaml",
"state/hook_index.json",
"state/memory_index.json",
```

Import and call `validate_v3_ledgers(root)` inside `validate_book()`.

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m pytest tests/test_validators.py -q
```

Expected: PASS.

- [ ] **Step 7: Run related hardening tests**

Run:

```powershell
python -m pytest tests/test_acceptance_packet.py tests/test_pipeline.py tests/test_cli.py -q
```

Expected: FAIL may occur because existing generated acceptance packets do not yet include `v3_state_updates`. Fix in Task 3.

- [ ] **Step 8: Commit**

```powershell
git add engine/hardening.py engine/validators.py tests/test_validators.py
git commit -m "feat: validate v3 state machine ledgers"
```

---

### Task 3: Draft V3 Acceptance Packet Scaffold

**Files:**

- Modify: `engine/acceptance_packet.py`
- Test: `tests/test_acceptance_packet.py`

- [ ] **Step 1: Write failing packet scaffold test**

Add to `tests/test_acceptance_packet.py`:

```python
def test_draft_acceptance_packet_includes_v3_state_updates(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(acceptance_packet, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    draft = book / "drafts" / "ch_0001_revised.md"
    draft.parent.mkdir()
    draft.write_text("accepted draft", encoding="utf-8")

    output = acceptance_packet.draft_acceptance_packet(
        "demo",
        1,
        title="First Signal",
        source_draft="drafts/ch_0001_revised.md",
        summary="The first contradiction appears.",
    )

    packet = read_yaml(output)
    updates = packet["v3_state_updates"]
    assert updates["timeline"]["occurred_events"][0]["source_chapter"] == 1
    assert updates["timeline"]["occurred_events"][0]["summary"] == "The first contradiction appears."
    assert updates["character_states"] == []
    assert updates["resource_changes"] == []
    assert updates["open_thread_updates"] == []
    assert updates["payoff_updates"][0]["chapter"] == 1
    assert updates["conflict_updates"]["active"] == []
    assert updates["next_hook"] == {}
    assert updates["pending_approvals"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_acceptance_packet.py::test_draft_acceptance_packet_includes_v3_state_updates -q
```

Expected: FAIL because `v3_state_updates` is missing.

- [ ] **Step 3: Add scaffold builder**

In `engine/acceptance_packet.py`, add:

```python
def _draft_v3_state_updates(
    chapter_number: int,
    summary: str,
    pending_approvals: list[str],
) -> dict[str, Any]:
    return {
        "timeline": {
            "occurred_events": [
                {
                    "id": f"ev_{chapter_number:04d}_01",
                    "summary": summary,
                    "location": "",
                    "involved_characters": [],
                    "source_chapter": chapter_number,
                }
            ]
        },
        "character_states": [],
        "resource_changes": [],
        "open_thread_updates": [],
        "payoff_updates": [
            {
                "chapter": chapter_number,
                "promises_made": [],
                "payoffs_delivered": [],
                "frustration_level": "controlled",
                "payoff_types": [],
                "delayed_payoffs": [],
                "risks": [],
            }
        ],
        "conflict_updates": {"active": []},
        "next_hook": {},
        "pending_approvals": list(pending_approvals),
    }
```

Add to the packet dictionary:

```python
"v3_state_updates": _draft_v3_state_updates(
    chapter_number,
    summary,
    pending_approvals,
),
```

- [ ] **Step 4: Run acceptance packet tests**

Run:

```powershell
python -m pytest tests/test_acceptance_packet.py -q
```

Expected: PASS.

- [ ] **Step 5: Run pipeline quality tests**

Run:

```powershell
python -m pytest tests/test_pipeline.py tests/test_cli.py -q
```

Expected: PASS or fail only where hand-authored test packets need V3 scaffolds added.

- [ ] **Step 6: Update hand-authored test packets**

If tests fail because test packets omit `v3_state_updates`, add:

```python
"v3_state_updates": {
    "timeline": {"occurred_events": []},
    "character_states": [],
    "resource_changes": [],
    "open_thread_updates": [],
    "payoff_updates": [],
    "conflict_updates": {"active": []},
    "next_hook": {},
    "pending_approvals": [],
},
```

Only update test fixtures that pass through hardening validation. Do not weaken V3 validation.

- [ ] **Step 7: Commit**

```powershell
git add engine/acceptance_packet.py tests/test_acceptance_packet.py tests/test_pipeline.py tests/test_cli.py
git commit -m "feat: scaffold v3 acceptance updates"
```

---

### Task 4: Apply V3 State Updates On Chapter Acceptance

**Files:**

- Create: `engine/v3_state.py`
- Modify: `engine/chapter_acceptance.py`
- Test: `tests/test_v3_state.py`
- Test: `tests/test_chapter_acceptance.py`

- [ ] **Step 1: Write failing V3 apply tests**

Create `tests/test_v3_state.py`:

```python
from engine import book_factory
from engine.io_utils import read_json, read_yaml
from engine.v3_state import apply_v3_state_updates


def test_apply_v3_state_updates_writes_ledgers_and_indexes(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    packet = {
        "chapter": 3,
        "v3_state_updates": {
            "timeline": {
                "occurred_events": [
                    {
                        "id": "ev_0003_01",
                        "summary": "A shop pressure arrives.",
                        "location": "Shop",
                        "involved_characters": ["chen_an"],
                        "source_chapter": 3,
                    }
                ]
            },
            "character_states": [
                {
                    "character_id": "chen_an",
                    "display_name": "陈安",
                    "physical_state": "正常",
                    "social_state": "被丹铺注意",
                    "emotional_state": "警惕",
                    "current_goal": "保住小卖部",
                    "known_secrets": ["后门规则"],
                    "public_knowledge": [],
                    "relationship_changes": [],
                    "voice_notes": ["谈价不露底"],
                }
            ],
            "resource_changes": [
                {
                    "owner": "chen_an",
                    "item": "现金",
                    "delta": 3000,
                    "unit": "元",
                    "category": "money",
                    "reason": "黄芽草变现",
                    "source_chapter": 3,
                }
            ],
            "open_thread_updates": [
                {
                    "id": "thread_0003_01",
                    "promise": "回春丹铺盯上夜间货源",
                    "source_chapter": 3,
                    "status": "open",
                    "last_touched": 3,
                    "next_obligation": "第4章回应报价",
                    "payoff_deadline": 5,
                    "risk_if_ignored": "商业压力落空",
                }
            ],
            "payoff_updates": [
                {
                    "chapter": 3,
                    "promises_made": ["丹铺会上门"],
                    "payoffs_delivered": ["黄芽草变现"],
                    "frustration_level": "controlled",
                    "payoff_types": ["赚钱", "交易"],
                    "delayed_payoffs": ["丹铺报价"],
                    "risks": [],
                }
            ],
            "conflict_updates": {
                "active": [
                    {
                        "id": "conflict_0003_01",
                        "summary": "丹铺压价风险",
                        "pressure_type": "商业压迫",
                        "source_chapter": 3,
                    }
                ]
            },
            "next_hook": {
                "hook": "丹铺明晚带价来谈",
                "obligation": "第4章回应报价",
                "target_chapter": 4,
            },
            "pending_approvals": ["确认丹铺为阶段敌人"],
        },
    }

    apply_v3_state_updates(book, packet)

    threads = read_yaml(book / "canon" / "open_threads.yaml")
    assert threads["threads"][0]["id"] == "thread_0003_01"
    character_states = read_yaml(book / "canon" / "character_states.yaml")
    assert character_states["characters"]["chen_an"]["last_updated_chapter"] == 3
    resources = read_yaml(book / "canon" / "resource_ledger.yaml")
    assert resources["resources"][0]["current_amount"] == 3000
    payoffs = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoffs["entries"][0]["payoff_types"] == ["赚钱", "交易"]
    hooks = read_json(book / "state" / "hook_index.json")
    assert hooks["hooks"][0]["status"] == "open"
    memory = read_json(book / "state" / "memory_index.json")
    assert memory["by_character"]["chen_an"] == [3]
    assert memory["by_thread"]["thread_0003_01"] == [3]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_v3_state.py -q
```

Expected: FAIL because `engine.v3_state` does not exist.

- [ ] **Step 3: Implement `engine/v3_state.py`**

Create helpers with this public function:

```python
from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_json, write_yaml


def apply_v3_state_updates(root: Path, packet: dict[str, Any]) -> None:
    updates = packet.get("v3_state_updates")
    if not isinstance(updates, dict):
        return
    chapter_number = int(packet.get("chapter", 0))
    _append_events_to_memory_index(root, chapter_number, updates)
    _update_character_states(root, chapter_number, updates.get("character_states", []))
    _update_resource_ledger(root, chapter_number, updates.get("resource_changes", []))
    _update_open_threads(root, updates.get("open_thread_updates", []))
    _append_payoff_entries(root, updates.get("payoff_updates", []))
    _append_next_hook(root, chapter_number, updates.get("next_hook", {}))
```

Implementation rules:

- Use existing `read_yaml`, `write_yaml`, `read_json`, `write_json`.
- Deduplicate open threads by `id`; update existing thread in place.
- Deduplicate payoff entries by `chapter`; replace the chapter's existing entries on force reaccept.
- For resources, derive stable id as `res_{owner}_{item}` when no `id` is given. Normalize with lowercase and underscores for ASCII owner/item, or use a short deterministic fallback if needed.
- For resources with numeric `delta`, update `current_amount`. If current amount is missing, start from 0.
- Append resource `history` entries with `chapter`, `delta`, and `reason`.
- For hook index, append a hook only when `hook` is non-empty. Default status is `open`.
- For memory index, add the accepted chapter number to:
  - `by_character` for involved event characters and `character_states.character_id`.
  - `by_thread` for open thread ids.
  - `by_location` for event locations.
  - `by_resource` for resource item names.
- Always sort and dedupe chapter lists.

- [ ] **Step 4: Wire chapter acceptance**

In `engine/chapter_acceptance.py`, import:

```python
from engine.v3_state import apply_v3_state_updates
```

After `_update_open_threads(...)` and before `_append_change_log(...)`, call:

```python
    apply_v3_state_updates(root, packet)
```

Note: This duplicates open thread update handling for V2 and V3 until V2 fields are retired. Keep it deliberate. V3 updates should be richer, while V2 `open_thread_updates` remains backward compatible.

- [ ] **Step 5: Add chapter acceptance integration test**

In `tests/test_chapter_acceptance.py`, extend `test_accept_chapter_applies_update_packet` packet with a valid `v3_state_updates` section and assert:

```python
    payoff_ledger = read_yaml(book / "canon" / "payoff_ledger.yaml")
    assert payoff_ledger["entries"][0]["chapter"] == 1
    hook_index = json.loads((book / "state" / "hook_index.json").read_text(encoding="utf-8"))
    assert hook_index["hooks"][0]["chapter"] == 1
```

- [ ] **Step 6: Run V3 state and acceptance tests**

Run:

```powershell
python -m pytest tests/test_v3_state.py tests/test_chapter_acceptance.py -q
```

Expected: PASS.

- [ ] **Step 7: Run acceptance pipeline tests**

Run:

```powershell
python -m pytest tests/test_acceptance_packet.py tests/test_pipeline.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```powershell
git add engine/v3_state.py engine/chapter_acceptance.py tests/test_v3_state.py tests/test_chapter_acceptance.py
git commit -m "feat: apply v3 state updates on acceptance"
```

---

### Task 5: Add Lightweight V3 Migration

**Files:**

- Create: `engine/v3_migration.py`
- Modify: `engine/cli.py`
- Test: `tests/test_v3_migration.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing migration tests**

Create `tests/test_v3_migration.py`:

```python
from engine import book_factory
from engine.io_utils import read_json, read_yaml, write_json, write_yaml
from engine.v3_migration import migrate_book_to_v3


def test_migrate_book_to_v3_creates_missing_files_without_inference(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "canon" / "payoff_ledger.yaml").unlink()
    (book / "state" / "hook_index.json").unlink()
    write_json(
        book / "state" / "chapter_index.json",
        {
            "chapters": [
                {
                    "chapter": 1,
                    "title": "First",
                    "summary": "Something happened.",
                    "state_changes": ["Free-text change."],
                    "open_threads_touched": [],
                }
            ]
        },
    )

    result = migrate_book_to_v3("demo")

    assert (book / "canon" / "payoff_ledger.yaml").exists()
    assert (book / "state" / "hook_index.json").exists()
    assert result.created
    assert read_yaml(book / "canon" / "payoff_ledger.yaml")["entries"] == []
    assert read_json(book / "state" / "hook_index.json")["hooks"] == []


def test_migrate_book_to_v3_preserves_existing_open_threads(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {"threads": [{"id": "thread_001", "status": "open", "promise": "Old promise"}]},
    )

    migrate_book_to_v3("demo")

    threads = read_yaml(book / "canon" / "open_threads.yaml")["threads"]
    assert threads[0]["id"] == "thread_001"
    assert threads[0]["promise"] == "Old promise"
    assert "source_chapter" in threads[0]
    assert "payoff_deadline" in threads[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_v3_migration.py -q
```

Expected: FAIL because `engine.v3_migration` does not exist.

- [ ] **Step 3: Implement migration helper**

Create `engine/v3_migration.py`:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.io_utils import read_json, read_yaml, write_json, write_yaml
from engine.paths import books_dir, project_root

BOOKS_DIR = books_dir()
TEMPLATE_DIR = project_root() / "engine" / "templates" / "book"


@dataclass
class V3MigrationResult:
    book_id: str
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)


def migrate_book_to_v3(book_id: str) -> V3MigrationResult:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    result = V3MigrationResult(book_id=book_id)
    _ensure_template_file(root, "canon/character_states.yaml", result)
    _ensure_template_file(root, "canon/resource_ledger.yaml", result)
    _ensure_template_file(root, "canon/payoff_ledger.yaml", result)
    _ensure_template_file(root, "outlines/units/unit_0001.yaml", result)
    _ensure_template_file(root, "state/hook_index.json", result)
    _ensure_template_file(root, "state/memory_index.json", result)
    _upgrade_open_threads(root, result)
    return result
```

Implementation details:

- `_ensure_template_file()` copies the matching template file only if missing.
- `_upgrade_open_threads()` reads `canon/open_threads.yaml`, preserves existing thread fields, and adds missing V3 keys with conservative blanks:

```python
defaults = {
    "promise": "",
    "source_chapter": "",
    "status": "open",
    "last_touched": "",
    "next_obligation": "",
    "payoff_deadline": "",
    "risk_if_ignored": "",
    "related_characters": [],
    "related_locations": [],
    "payoff_chapter": "",
    "notes": [],
}
```

- Do not convert `state_changes` strings into structured ledgers.
- Do not parse chapter prose.

- [ ] **Step 4: Wire CLI command**

In `engine/cli.py`, import:

```python
from engine.v3_migration import migrate_book_to_v3
```

Add parser:

```python
    migrate_v3_cmd = subparsers.add_parser(
        "migrate-v3",
        help="Create missing V3 state-machine files for an existing book.",
    )
    migrate_v3_cmd.add_argument("book_id")
```

Add handler:

```python
    if args.command == "migrate-v3":
        try:
            result = migrate_book_to_v3(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Migrated book to V3: {args.book_id}")
        for path in result.created:
            print(f"- created: {path}")
        for path in result.updated:
            print(f"- updated: {path}")
        return 0
```

- [ ] **Step 5: Add CLI test**

Add to `tests/test_cli.py`:

```python
def test_migrate_v3_cli_creates_missing_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    import engine.v3_migration as v3_migration

    monkeypatch.setattr(v3_migration, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "state" / "hook_index.json").unlink()

    result = cli.main(["migrate-v3", "demo"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Migrated book to V3: demo" in captured.out
    assert (book / "state" / "hook_index.json").exists()
```

- [ ] **Step 6: Run migration tests**

Run:

```powershell
python -m pytest tests/test_v3_migration.py tests/test_cli.py::test_migrate_v3_cli_creates_missing_files -q
```

Expected: PASS.

- [ ] **Step 7: Run validation against existing pilot after migration**

Run:

```powershell
python -m engine.cli migrate-v3 xiuxian_shop_pilot
python -m engine.cli validate-book xiuxian_shop_pilot
```

Expected:

- `migrate-v3` prints created or updated V3 files.
- `validate-book` exits 0 or only reports pre-existing unrelated validation problems. If unrelated dirty sample issues appear, document them and do not hide them.

- [ ] **Step 8: Commit**

```powershell
git add engine/v3_migration.py engine/cli.py tests/test_v3_migration.py tests/test_cli.py
git commit -m "feat: add lightweight v3 migration"
```

---

### Task 6: Include V3 Memory In Context Packs

**Files:**

- Modify: `engine/context_builder.py`
- Test: `tests/test_context_builder.py`

- [ ] **Step 1: Write failing context test**

Add to `tests/test_context_builder.py`:

```python
def test_build_context_includes_v3_memory_ledgers(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(context_builder, "KNOWLEDGE_DIR", tmp_path / "knowledge")
    book = book_factory.create_book("demo", title="Demo Book")
    (book / "canon" / "payoff_ledger.yaml").write_text(
        "entries:\n- chapter: 1\n  promises_made:\n  - 丹铺会上门\n  payoffs_delivered: []\n  frustration_level: controlled\n",
        encoding="utf-8",
    )
    (book / "state" / "hook_index.json").write_text(
        '{"hooks":[{"chapter":1,"hook":"丹铺上门","target_chapter":2,"status":"open"}]}',
        encoding="utf-8",
    )

    context = context_builder.build_context("demo", 2)

    assert "## Payoff Ledger" in context
    assert "丹铺会上门" in context
    assert "## Hook Index" in context
    assert "丹铺上门" in context
    assert "## Unit Plan" in context
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_context_builder.py::test_build_context_includes_v3_memory_ledgers -q
```

Expected: FAIL because context builder does not include new V3 ledgers yet.

- [ ] **Step 3: Add V3 files to context sections**

In `engine/context_builder.py`, extend `YAML_FILES`:

```python
    ("Character States", "canon/character_states.yaml"),
    ("Resource Ledger", "canon/resource_ledger.yaml"),
    ("Payoff Ledger", "canon/payoff_ledger.yaml"),
    ("Unit Plan", "outlines/units/unit_0001.yaml"),
```

Extend `JSON_FILES`:

```python
    ("Hook Index", "state/hook_index.json"),
    ("Memory Index", "state/memory_index.json"),
```

This first implementation can include full V3 files. Add a comment above the lists:

```python
# V3 ledgers are still small. Later versions can slice these sections by relevance.
```

- [ ] **Step 4: Run context tests**

Run:

```powershell
python -m pytest tests/test_context_builder.py -q
```

Expected: PASS.

- [ ] **Step 5: Run prepare-chapter smoke test**

Run:

```powershell
python -m engine.cli prepare-chapter xiuxian_shop_pilot 4 --force
```

Expected: writes `books/xiuxian_shop_pilot/pipeline/ch_0004/context.md` and context includes V3 sections. If `xiuxian_shop_pilot` has not been migrated in this worktree, run `python -m engine.cli migrate-v3 xiuxian_shop_pilot` first.

- [ ] **Step 6: Commit**

```powershell
git add engine/context_builder.py tests/test_context_builder.py books/xiuxian_shop_pilot
git commit -m "feat: include v3 memory in chapter context"
```

Note: Only stage `books/xiuxian_shop_pilot` if this task intentionally migrated or refreshed its pipeline context. Do not stage unrelated sample-project dirt.

---

### Task 7: Upgrade V3 Drift Report

**Files:**

- Modify: `engine/drift_report.py`
- Test: `tests/test_cli.py` or create `tests/test_drift_report.py`

- [ ] **Step 1: Prefer a dedicated drift test file**

Create `tests/test_drift_report.py` if drift-specific tests grow beyond the existing CLI smoke test. Use direct calls to `generate_drift_report()` for precise assertions, and keep CLI tests for command wiring only.

- [ ] **Step 2: Write failing drift warning test**

Create `tests/test_drift_report.py`:

```python
from engine import book_factory, drift_report
from engine.io_utils import write_json, write_yaml


def test_v3_drift_report_flags_stale_threads_and_overdue_hooks(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(drift_report, "BOOKS_DIR", tmp_path / "books")
    book = book_factory.create_book("demo", title="Demo Book")
    write_json(book / "state" / "current_state.json", {"current_chapter": 6, "active_characters": [], "active_conflicts": []})
    write_json(book / "state" / "chapter_index.json", {"chapters": []})
    write_yaml(
        book / "canon" / "open_threads.yaml",
        {
            "threads": [
                {
                    "id": "thread_0001_01",
                    "promise": "丹铺会上门",
                    "source_chapter": 1,
                    "status": "open",
                    "last_touched": 1,
                    "next_obligation": "第3章回应",
                    "payoff_deadline": 3,
                    "risk_if_ignored": "压力落空",
                }
            ]
        },
    )
    write_json(
        book / "state" / "hook_index.json",
        {
            "hooks": [
                {
                    "chapter": 2,
                    "hook": "丹铺明晚带价来谈",
                    "obligation": "第3章回应",
                    "target_chapter": 3,
                    "status": "open",
                    "answered_by_chapter": None,
                }
            ]
        },
    )

    output = drift_report.generate_drift_report("demo", 1, 6)

    content = output.read_text(encoding="utf-8")
    assert "## V3 State Machine Warnings" in content
    assert "thread_0001_01" in content
    assert "丹铺明晚带价来谈" in content
```

- [ ] **Step 3: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_drift_report.py -q
```

Expected: FAIL because V3 warnings are not rendered.

- [ ] **Step 4: Implement V3 report sections**

In `engine/drift_report.py`, read:

```python
hook_index = read_json(root / "state" / "hook_index.json")
payoff_ledger = read_yaml(root / "canon" / "payoff_ledger.yaml")
resource_ledger = read_yaml(root / "canon" / "resource_ledger.yaml")
character_states = read_yaml(root / "canon" / "character_states.yaml")
```

Add after current sections:

```python
lines.extend(_v3_state_machine_warnings(current_state, open_threads, hook_index, payoff_ledger, resource_ledger, character_states))
```

Implement `_v3_state_machine_warnings()` with a Markdown table:

```python
def _v3_state_machine_warnings(
    current_state: dict[str, Any],
    open_threads: dict[str, Any],
    hook_index: dict[str, Any],
    payoff_ledger: dict[str, Any],
    resource_ledger: dict[str, Any],
    character_states: dict[str, Any],
) -> list[str]:
    current_chapter = int(current_state.get("current_chapter", 0) or 0)
    lines = [
        "## V3 State Machine Warnings",
        "",
        "| Type | Item | Evidence | Recommended Action |",
        "| --- | --- | --- | --- |",
    ]
    # append warnings here
    if len(lines) == 3:
        lines.append("| None | - | No mechanical V3 warning found. | Continue. |")
    lines.append("")
    return lines
```

Warnings to implement in first pass:

- `stale_thread`: thread status `open` or `advanced` and `payoff_deadline` is an int less than `current_chapter`.
- `overdue_hook`: hook status `open` and `target_chapter` is an int less than `current_chapter`.
- `high_frustration`: two or more consecutive payoff entries with `frustration_level` in `{"high", "overdue"}`.
- `stale_character_state`: active character in `current_state.active_characters` has no character state entry.
- `resource_missing_history`: resource item has empty or missing `history`.

- [ ] **Step 5: Run drift tests**

Run:

```powershell
python -m pytest tests/test_drift_report.py tests/test_cli.py::test_drift_report_cli_generates_report -q
```

Expected: PASS.

- [ ] **Step 6: Generate pilot drift smoke report**

Run:

```powershell
python -m engine.cli drift-report xiuxian_shop_pilot --start 1 --end 3
```

Expected: report regenerates and includes `## V3 State Machine Warnings`.

- [ ] **Step 7: Commit**

```powershell
git add engine/drift_report.py tests/test_drift_report.py tests/test_cli.py books/xiuxian_shop_pilot/reports
git commit -m "feat: add v3 drift warnings"
```

Note: Only stage regenerated pilot reports if they are intentionally part of this task.

---

### Task 8: Improve Pipeline Handoffs For V3 Updates

**Files:**

- Modify: `engine/pipeline.py`
- Modify: `engine/prompts/agents/continuity_editor.md`
- Modify: `engine/prompts/agents/tomato_pacing_editor.md`
- Modify: `engine/prompts/agents/reviser.md`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Inspect prompt files**

Run:

```powershell
rg -n "state|canon|approval|pacing|payoff|thread|hook" engine/prompts/agents
```

Expected: identify where V3 output expectations should be added.

- [ ] **Step 2: Write failing handoff test**

Add to `tests/test_pipeline.py`:

```python
def test_prepare_chapter_handoffs_mention_v3_state_updates(tmp_path, monkeypatch):
    monkeypatch.setattr(book_factory, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(pipeline, "BOOKS_DIR", tmp_path / "books")
    book_factory.create_book("demo", title="Demo Book")

    paths = pipeline.prepare_chapter("demo", 1)

    continuity = (paths.handoff_dir / "03_continuity_editor.md").read_text(encoding="utf-8")
    pacing = (paths.handoff_dir / "04_tomato_pacing_editor.md").read_text(encoding="utf-8")
    assert "V3 state updates" in continuity
    assert "payoff ledger" in pacing
```

- [ ] **Step 3: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_pipeline.py::test_prepare_chapter_handoffs_mention_v3_state_updates -q
```

Expected: FAIL because handoffs do not mention V3.

- [ ] **Step 4: Update agent prompts**

In `engine/prompts/agents/continuity_editor.md`, add a compact V3 review expectation:

```markdown
## V3 State Update Notes

When reviewing, list proposed V3 state updates separately from canon facts:

- character state changes
- resource, wealth, power, or item changes
- open thread additions or updates
- current conflicts
- next-hook obligations
- human approvals needed
```

In `engine/prompts/agents/tomato_pacing_editor.md`, add:

```markdown
## Payoff Ledger Notes

Record what this chapter promises, what it pays off, whether frustration is low/controlled/high/overdue, and the payoff types used such as 赚钱, 打脸, 护短, 升级, 揭谜, 交易, 压价.
```

In `engine/prompts/agents/reviser.md`, add:

```markdown
Preserve approved V3 state facts while revising. If a revision changes a payoff, hook, resource, or character state, call that out for the acceptance packet.
```

- [ ] **Step 5: Add generated handoff note if needed**

If prompt edits alone do not satisfy the exact phrase, update `_write_handoffs()` in `engine/pipeline.py` to include:

```python
"V3 state updates must remain proposed until the acceptance packet is approved.",
```

- [ ] **Step 6: Run pipeline tests**

Run:

```powershell
python -m pytest tests/test_pipeline.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add engine/pipeline.py engine/prompts/agents tests/test_pipeline.py
git commit -m "feat: add v3 expectations to chapter handoffs"
```

---

### Task 9: Document V3 Workflow And Agent Rules

**Files:**

- Create: `docs/workflows/v3-long-form-state-machine.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add workflow document**

Create `docs/workflows/v3-long-form-state-machine.md`:

```markdown
# V3 Long-Form State Machine Workflow

V3 keeps the V2 chapter pipeline and adds explicit long-form memory ledgers.

## New Files

- `canon/character_states.yaml`
- `canon/resource_ledger.yaml`
- `canon/payoff_ledger.yaml`
- upgraded `canon/open_threads.yaml`
- `outlines/units/unit_0001.yaml`
- `state/hook_index.json`
- `state/memory_index.json`

## Normal Chapter Flow

1. Prepare the chapter workspace.
2. Write brief, draft, reviews, and revision as before.
3. Draft the acceptance packet.
4. Fill `v3_state_updates`.
5. Human reviews the packet.
6. Run `pipeline-accept` only after explicit approval.
7. Run `validate-book`.
8. Use `drift-report` after a sample or unit.

## Migration

Use:

```powershell
python -m engine.cli migrate-v3 <book_id>
```

Migration creates missing V3 files and upgrades empty schemas. It does not parse old prose or infer canon.
```

- [ ] **Step 2: Update `AGENTS.md`**

Add under State Machine Expectations:

```markdown
V3 adds explicit ledgers:

- `canon/character_states.yaml`
- `canon/resource_ledger.yaml`
- `canon/payoff_ledger.yaml`
- upgraded `canon/open_threads.yaml`
- `outlines/units/unit_0001.yaml`
- `state/hook_index.json`
- `state/memory_index.json`

Use `python -m engine.cli migrate-v3 <book_id>` before applying V3 checks to an older book. Migration is lightweight and must not infer canon from old prose.
```

- [ ] **Step 3: Run doc sanity search**

Run:

```powershell
rg -n "migrate-v3|v3_state_updates|payoff_ledger|character_states|resource_ledger|hook_index" AGENTS.md docs/workflows/v3-long-form-state-machine.md
```

Expected: all key terms appear.

- [ ] **Step 4: Commit**

```powershell
git add AGENTS.md docs/workflows/v3-long-form-state-machine.md
git commit -m "docs: document v3 state machine workflow"
```

---

### Task 10: Full Verification And Pilot Migration

**Files:**

- Possibly modify generated files under `books/xiuxian_shop_pilot/` only if deliberately migrated.

- [ ] **Step 1: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Validate a fresh generated book**

Run:

```powershell
python -m engine.cli init-book v3_smoke_book --title "V3 Smoke Book" --force
python -m engine.cli validate-book v3_smoke_book
```

Expected:

- New book is created.
- Validation exits 0.

Clean up the smoke book only if it was not meant to remain in the repo. Use PowerShell safely:

```powershell
$target = Resolve-Path .\books\v3_smoke_book
if ($target.Path -like "$(Resolve-Path .\books)\*") {
  Remove-Item -LiteralPath $target.Path -Recurse -Force
}
```

- [ ] **Step 3: Migrate and validate pilot**

Run:

```powershell
python -m engine.cli migrate-v3 xiuxian_shop_pilot
python -m engine.cli validate-book xiuxian_shop_pilot
```

Expected: exits 0 unless pre-existing project dirt has unrelated validation issues. If unrelated issues appear, document them in the final handoff instead of silently changing story files.

- [ ] **Step 4: Regenerate pilot context**

Run:

```powershell
python -m engine.cli prepare-chapter xiuxian_shop_pilot 4 --force
```

Expected: `books/xiuxian_shop_pilot/pipeline/ch_0004/context.md` includes V3 memory sections.

- [ ] **Step 5: Generate pilot drift report**

Run:

```powershell
python -m engine.cli drift-report xiuxian_shop_pilot --start 1 --end 3
```

Expected: report includes V3 warning section and does not crash on empty ledgers.

- [ ] **Step 6: Run final validation**

Run:

```powershell
python -m pytest -q
python -m engine.cli validate-book xiuxian_shop_pilot
```

Expected: PASS / valid.

- [ ] **Step 7: Inspect git diff**

Run:

```powershell
git status --short
git diff --stat
```

Expected: changes match V3 implementation. There may be pre-existing unrelated dirty files; do not revert them.

- [ ] **Step 8: Commit final pilot migration only if intentional**

If pilot migration files should be kept:

```powershell
git add books/xiuxian_shop_pilot
git commit -m "chore: migrate xiuxian pilot to v3 memory"
```

If the repository is intentionally left uncommitted in this session, record exact changed paths in the handoff.

---

## Implementation Notes

- Keep V2 fields backward compatible until at least one V3 sample chapter has been accepted successfully.
- Do not weaken the human approval gate.
- Do not parse old chapter prose for migration.
- Do not infer character emotions, resource meaning, or plot intent from free-text `state_changes`.
- Prefer adding warnings over blocking validation when a rule is editorial rather than structural.
- Keep V3 ledgers book-local. Shared writing theory remains under `knowledge/`.

## Suggested Execution Order

1. Task 1: templates.
2. Task 2: validators.
3. Task 3: acceptance packet scaffold.
4. Task 4: V3 acceptance application.
5. Task 5: migration.
6. Task 6: context builder.
7. Task 7: drift report.
8. Task 8: handoffs.
9. Task 9: docs.
10. Task 10: full verification.

This order keeps every task testable and avoids modifying accepted story files before the new structure exists.
