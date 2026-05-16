# V2 Single-Chapter Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a V2 single-chapter pipeline command that organizes the existing V1 steps into a repeatable, inspectable workflow without removing human approval.

**Architecture:** Add a lightweight pipeline layer that creates a per-chapter workspace under `books/<book_id>/pipeline/ch_XXXX/`, writes a run manifest, builds the context pack, materializes prompt handoff files, detects required human inputs, drafts an acceptance packet when enough files exist, and optionally applies the approved packet. This remains file-based and local; it does not call LLM APIs or attempt full autonomous generation.

**Tech Stack:** Python 3.14, standard library, PyYAML, pytest, Markdown/YAML/JSON/JSONL.

---

## Scope

In scope:

- A pipeline manifest file for each chapter run.
- A `prepare-chapter` command that creates context and agent handoff files.
- A `pipeline-status` command that reports which artifacts are present or missing.
- A `pipeline-draft-acceptance` command that wraps `draft-acceptance-packet` after required files exist.
- A `pipeline-accept` command that wraps `accept-chapter` after human approval.
- Documentation for the V2 single-chapter workflow.
- Tests for status detection, manifest writing, and CLI behavior.

Out of scope:

- LLM API calls.
- Automatic chapter generation.
- Automatic review generation.
- Web UI.
- Vector database.
- Multi-agent concurrency.
- Real publishing integration.

## File Structure

Create or modify these files:

- Create: `engine/pipeline.py` - V2 pipeline orchestration helpers.
- Modify: `engine/cli.py` - add `prepare-chapter`, `pipeline-status`, `pipeline-draft-acceptance`, and `pipeline-accept`.
- Create: `tests/test_pipeline.py` - tests manifest, status, and wrapper behavior.
- Modify: `README.md` - add V2 command examples.
- Modify: `docs/workflows/manual-single-chapter-pipeline.md` - add V2 command-assisted workflow.
- Create: `docs/workflows/v2-single-chapter-pipeline.md` - dedicated workflow guide.
- Optionally create sample pipeline artifacts under `books/sample_tomato_project/pipeline/ch_0003/` if useful and clearly marked as workflow artifacts.

Do not modify `.obsidian/`.

---

## Task 1: Pipeline Manifest And Paths

**Files:**
- Create: `engine/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Add tests for:

```python
def test_pipeline_paths_for_chapter(tmp_path, monkeypatch):
    ...
```

Expected:

- `pipeline_dir` is `books/demo/pipeline/ch_0001`.
- `context_path` is `books/demo/pipeline/ch_0001/context.md`.
- `manifest_path` is `books/demo/pipeline/ch_0001/manifest.json`.
- `handoff_dir` is `books/demo/pipeline/ch_0001/handoffs`.

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_pipeline.py::test_pipeline_paths_for_chapter -v
```

Expected: FAIL because `engine.pipeline` does not exist.

- [ ] **Step 3: Implement path helpers**

Implement:

```python
@dataclass(frozen=True)
class PipelinePaths:
    root: Path
    pipeline_dir: Path
    context_path: Path
    manifest_path: Path
    handoff_dir: Path

def pipeline_paths(book_id: str, chapter_number: int) -> PipelinePaths:
    ...
```

- [ ] **Step 4: Run test**

```powershell
python -m pytest tests/test_pipeline.py::test_pipeline_paths_for_chapter -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add engine/pipeline.py tests/test_pipeline.py
git commit -m "feat: add chapter pipeline paths"
```

---

## Task 2: Prepare Chapter Pipeline Workspace

**Files:**
- Modify: `engine/pipeline.py`
- Modify: `engine/cli.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Test `prepare_chapter(book_id, chapter_number, force=False)`:

- Creates `pipeline/ch_0001/`.
- Writes `context.md` using existing context builder.
- Writes `manifest.json`.
- Writes handoff files:
  - `handoffs/01_plot_planner.md`
  - `handoffs/02_chapter_writer.md`
  - `handoffs/03_continuity_editor.md`
  - `handoffs/04_tomato_pacing_editor.md`
  - `handoffs/05_reviser.md`
- Refuses to overwrite an existing pipeline directory unless `force=True`.

- [ ] **Step 2: Run test to verify failure**

```powershell
python -m pytest tests/test_pipeline.py::test_prepare_chapter_creates_workspace -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `prepare_chapter`**

Behavior:

- Validate book directory exists.
- Create pipeline directory.
- Build context to pipeline `context.md`.
- Read relevant agent prompt files.
- Create handoff Markdown files that include:
  - Agent prompt path.
  - Context path.
  - Expected input artifact.
  - Expected output artifact.
  - Human approval note where relevant.
- Write `manifest.json` with:

```json
{
  "book_id": "demo",
  "chapter": 1,
  "status": "prepared",
  "artifacts": {
    "context": "pipeline/ch_0001/context.md",
    "brief": "outlines/chapter_briefs/ch_0001_brief.md",
    "draft": "drafts/ch_0001_draft.md",
    "revised": "drafts/ch_0001_revised.md",
    "continuity_review": "reviews/ch_0001/continuity_review.json",
    "pacing_review": "reviews/ch_0001/pacing_review.json",
    "acceptance_packet": "state_updates/ch_0001_acceptance.yaml",
    "accepted_chapter": "chapters/ch_0001.md"
  }
}
```

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli prepare-chapter demo 1
```

Options:

- `--force`

Expected output:

```text
Prepared chapter pipeline: books/demo/pipeline/ch_0001
```

- [ ] **Step 5: Run tests**

```powershell
python -m pytest tests/test_pipeline.py -v
```

Expected: PASS for current pipeline tests.

- [ ] **Step 6: Commit**

```powershell
git add engine/pipeline.py engine/cli.py tests/test_pipeline.py
git commit -m "feat: prepare chapter pipeline workspace"
```

---

## Task 3: Pipeline Status

**Files:**
- Modify: `engine/pipeline.py`
- Modify: `engine/cli.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Test:

- `pipeline_status(book_id, chapter_number)` reports all manifest artifacts.
- Existing files are marked `present`.
- Missing files are marked `missing`.
- Status includes `next_action`.

Suggested statuses:

- `needs_brief`
- `needs_draft`
- `needs_reviews`
- `needs_revised_draft`
- `needs_acceptance_packet`
- `ready_for_acceptance`
- `accepted`

- [ ] **Step 2: Run test to verify failure**

```powershell
python -m pytest tests/test_pipeline.py::test_pipeline_status_reports_missing_artifacts -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `pipeline_status`**

Return a dictionary:

```python
{
    "book_id": book_id,
    "chapter": chapter_number,
    "status": "needs_brief",
    "artifacts": {
        "brief": {"path": "...", "present": False},
        ...
    },
    "next_action": "Create chapter brief."
}
```

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli pipeline-status demo 1
```

Print readable status lines, not raw JSON by default.

- [ ] **Step 5: Run tests**

```powershell
python -m pytest tests/test_pipeline.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/pipeline.py engine/cli.py tests/test_pipeline.py
git commit -m "feat: report chapter pipeline status"
```

---

## Task 4: Pipeline Draft Acceptance Wrapper

**Files:**
- Modify: `engine/pipeline.py`
- Modify: `engine/cli.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Test:

- `pipeline_draft_acceptance(book_id, chapter_number, title, summary)` calls existing acceptance packet logic.
- It refuses when revised draft is missing.
- It refuses when required reviews are missing unless `allow_missing_reviews=True`.
- It returns the acceptance packet path.

- [ ] **Step 2: Run test to verify failure**

```powershell
python -m pytest tests/test_pipeline.py::test_pipeline_draft_acceptance_requires_revised_draft -v
```

Expected: FAIL.

- [ ] **Step 3: Implement wrapper**

Use existing `draft_acceptance_packet`.

Default source draft:

```text
drafts/ch_XXXX_revised.md
```

Default output:

```text
state_updates/ch_XXXX_acceptance.yaml
```

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli pipeline-draft-acceptance demo 1 --title "Title" --summary "Summary"
```

Options:

- `--force`
- `--allow-missing-reviews`

- [ ] **Step 5: Run tests**

```powershell
python -m pytest tests/test_pipeline.py tests/test_acceptance_packet.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/pipeline.py engine/cli.py tests/test_pipeline.py
git commit -m "feat: draft acceptance packets from pipeline"
```

---

## Task 5: Pipeline Accept Wrapper

**Files:**
- Modify: `engine/pipeline.py`
- Modify: `engine/cli.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Test:

- `pipeline_accept(book_id, chapter_number)` uses `state_updates/ch_XXXX_acceptance.yaml`.
- It refuses when packet is missing.
- It refuses unless `approved=True`.
- With approval, it calls `accept_chapter`.

- [ ] **Step 2: Run test to verify failure**

```powershell
python -m pytest tests/test_pipeline.py::test_pipeline_accept_requires_approval -v
```

Expected: FAIL.

- [ ] **Step 3: Implement wrapper**

Function:

```python
def pipeline_accept(book_id: str, chapter_number: int, approved: bool, force: bool = False) -> Path:
    ...
```

If `approved` is false, raise `PermissionError` with a clear message.

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli pipeline-accept demo 1 --approved
```

Options:

- `--approved`
- `--force`

- [ ] **Step 5: Run tests**

```powershell
python -m pytest tests/test_pipeline.py tests/test_chapter_acceptance.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/pipeline.py engine/cli.py tests/test_pipeline.py
git commit -m "feat: accept chapters from pipeline"
```

---

## Task 6: Sample Book Pipeline Smoke Test

**Files:**
- Create or modify: `books/sample_tomato_project/pipeline/ch_0003/*`
- Do not create a fake accepted chapter unless it is clearly marked as a non-story smoke artifact.

- [ ] **Step 1: Prepare chapter 3 pipeline**

Run:

```powershell
python -m engine.cli prepare-chapter sample_tomato_project 3 --force
```

Expected: creates `books/sample_tomato_project/pipeline/ch_0003`.

- [ ] **Step 2: Check status**

Run:

```powershell
python -m engine.cli pipeline-status sample_tomato_project 3
```

Expected: status indicates missing brief/draft/reviews.

- [ ] **Step 3: Decide whether to keep sample pipeline artifacts**

Keep if useful for documentation. If kept, make clear these are pipeline workspace artifacts, not a real chapter.

- [ ] **Step 4: Commit**

```powershell
git add books/sample_tomato_project/pipeline
git commit -m "docs: add sample chapter pipeline workspace"
```

Skip this commit if sample artifacts are not kept.

---

## Task 7: Documentation And Final Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/workflows/manual-single-chapter-pipeline.md`
- Create: `docs/workflows/v2-single-chapter-pipeline.md`

- [ ] **Step 1: Update README**

Add commands:

```powershell
python -m engine.cli prepare-chapter sample_tomato_project 3
python -m engine.cli pipeline-status sample_tomato_project 3
python -m engine.cli pipeline-draft-acceptance sample_tomato_project 3 --title "Title" --summary "Summary"
python -m engine.cli pipeline-accept sample_tomato_project 3 --approved
```

- [ ] **Step 2: Add dedicated V2 workflow doc**

Include:

- What V2 automates.
- What V2 still requires humans to do.
- Artifact lifecycle.
- When to use `--force`.
- Why `pipeline-accept` requires `--approved`.

- [ ] **Step 3: Run all tests**

```powershell
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 4: Validate sample book**

```powershell
python -m engine.cli validate-book sample_tomato_project
```

Expected:

```text
Book project is valid: sample_tomato_project
```

- [ ] **Step 5: Check git status**

```powershell
git status --short
```

Expected: only `.obsidian/` remains untracked, unless the user wants it committed.

- [ ] **Step 6: Commit final docs**

```powershell
git add README.md docs/workflows
git commit -m "docs: document v2 chapter pipeline"
```

---

## Acceptance Criteria

V2 is complete when:

- `prepare-chapter` creates a chapter pipeline workspace with context, handoffs, and manifest.
- `pipeline-status` reports present/missing artifacts and next action.
- `pipeline-draft-acceptance` creates an acceptance packet from the expected revised draft and reviews.
- `pipeline-accept --approved` applies the accepted packet.
- `pipeline-accept` refuses to run without explicit approval.
- All new behavior is covered by tests.
- The existing V1 commands still work.
- `sample_tomato_project` remains valid.
- The workflow documentation explains the V2 command-assisted loop.

## Review Note

The original writing-plans workflow recommends a plan-document-reviewer subagent. In this workspace, do not dispatch a subagent unless the user explicitly requests parallel agent review. If the user asks for review, send this plan file to a reviewer before implementation.
