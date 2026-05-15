# V0+V1 CLI Writers' Room Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the V0+V1 starting version of Novel Writer: a Python CLI writers' room with YAML/Markdown knowledge, reusable templates, isolated book projects, and a manual single-chapter workflow.

**Architecture:** Use a reusable `engine/` for CLI, templates, prompt contracts, validation, and context building. Store shared craft knowledge in `knowledge/`, while each novel lives under `books/<book_id>/` with its own canon, outlines, chapters, reviews, and state. Keep the first version file-based and human-approved; do not add a web UI, vector database, or fully automated multi-agent runner yet.

**Tech Stack:** Python 3.14, standard library first, PyYAML for YAML parsing, pytest for tests, Markdown/YAML/JSON/JSONL for project data.

---

## File Structure

Create or modify these files:

- Create: `.gitignore` - ignores Python caches, virtual envs, generated exports, and local secrets.
- Create: `pyproject.toml` - package metadata, console script, pytest settings.
- Create: `README.md` - quickstart and project philosophy.
- Create: `engine/__init__.py` - package marker.
- Create: `engine/cli.py` - command-line entrypoint.
- Create: `engine/book_factory.py` - creates a new book from templates.
- Create: `engine/context_builder.py` - builds a chapter context pack from canon, state, outline, and knowledge.
- Create: `engine/paths.py` - central path helpers.
- Create: `engine/io_utils.py` - safe YAML/JSON/Markdown read-write helpers.
- Create: `engine/validators.py` - validates expected book files and review scores.
- Create: `engine/templates/book/*` - reusable book project templates.
- Create: `engine/prompts/agents/*.md` - core agent role prompts.
- Create: `engine/prompts/shared/output-contracts.md` - shared structured-output rules.
- Create: `knowledge/tomato/*.md` - Tomato-style writing guidance.
- Create: `knowledge/craft/*.md` - general narrative craft guidance.
- Create: `knowledge/readers/*.md` - reader persona guidance.
- Create: `knowledge/risk/*.md` - content and quality risk notes.
- Create: `tests/test_book_factory.py` - tests book initialization.
- Create: `tests/test_context_builder.py` - tests chapter context generation.
- Create: `tests/test_validators.py` - tests project validation.
- Modify: `docs/vision/ultimate-novel-writer-roadmap.md` only if implementation reveals a needed decision update.

Do not create a database, web app, automated market scraper, or full LLM API orchestration in this version.

---

## Task 1: Initialize Project Basics

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `engine/__init__.py`

- [ ] **Step 1: Initialize git if needed**

Run:

```powershell
git status
```

Expected now: FAIL with "not a git repository".

Then run:

```powershell
git init
```

Expected: repository initialized.

- [ ] **Step 2: Create `.gitignore`**

Use:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
.env
.env.*
dist/
build/
*.egg-info/
books/*/exports/
books/*/tmp/
```

- [ ] **Step 3: Create `pyproject.toml`**

Use:

```toml
[project]
name = "novel-writer"
version = "0.1.0"
description = "A CLI writers' room for long-form AI-assisted web fiction."
requires-python = ">=3.12"
dependencies = [
  "PyYAML>=6.0.2",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0",
]

[project.scripts]
novel-writer = "engine.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 4: Create `README.md`**

Include:

- What the project is.
- Why it is file-based.
- The difference between reusable engine and isolated book projects.
- Quickstart commands for `init-book`, `validate-book`, and `build-context`.
- Link to `docs/vision/ultimate-novel-writer-roadmap.md`.

- [ ] **Step 5: Create package marker**

Create empty `engine/__init__.py`.

- [ ] **Step 6: Install dependencies**

Run:

```powershell
python -m pip install -e ".[dev]"
```

Expected: package installed with PyYAML and pytest.

- [ ] **Step 7: Commit**

Run:

```powershell
git add .gitignore pyproject.toml README.md engine/__init__.py
git commit -m "chore: initialize novel writer project"
```

Expected: commit succeeds.

---

## Task 2: Add Path And IO Utilities

**Files:**
- Create: `engine/paths.py`
- Create: `engine/io_utils.py`
- Test: `tests/test_io_utils.py`

- [ ] **Step 1: Write failing tests**

Create tests for:

- `project_root()` returns the repository root.
- `book_path("demo")` returns `books/demo`.
- `read_yaml()` returns `{}` for an empty YAML file.
- `write_json()` creates parent directories.

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
pytest tests/test_io_utils.py -v
```

Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement `engine/paths.py`**

Functions:

```python
from pathlib import Path

def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def books_dir() -> Path:
    return project_root() / "books"

def book_path(book_id: str) -> Path:
    return books_dir() / book_id

def knowledge_dir() -> Path:
    return project_root() / "knowledge"
```

- [ ] **Step 4: Implement `engine/io_utils.py`**

Functions:

- `read_text(path: Path) -> str`
- `write_text(path: Path, content: str) -> None`
- `read_yaml(path: Path) -> dict`
- `write_yaml(path: Path, data: dict) -> None`
- `read_json(path: Path) -> dict`
- `write_json(path: Path, data: dict) -> None`

Use UTF-8 and create parent directories before writing.

- [ ] **Step 5: Run tests**

Run:

```powershell
pytest tests/test_io_utils.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/paths.py engine/io_utils.py tests/test_io_utils.py
git commit -m "feat: add path and io utilities"
```

---

## Task 3: Add Book Templates

**Files:**
- Create: `engine/templates/book/book.yaml`
- Create: `engine/templates/book/canon/novel_bible.yaml`
- Create: `engine/templates/book/canon/characters.yaml`
- Create: `engine/templates/book/canon/relationships.yaml`
- Create: `engine/templates/book/canon/world_rules.yaml`
- Create: `engine/templates/book/canon/timeline.yaml`
- Create: `engine/templates/book/canon/open_threads.yaml`
- Create: `engine/templates/book/canon/forbidden_rules.yaml`
- Create: `engine/templates/book/outlines/master_outline.yaml`
- Create: `engine/templates/book/outlines/arc_001.yaml`
- Create: `engine/templates/book/chapters/.gitkeep`
- Create: `engine/templates/book/reviews/.gitkeep`
- Create: `engine/templates/book/state/current_state.json`
- Create: `engine/templates/book/state/chapter_index.json`
- Create: `engine/templates/book/state/change_log.jsonl`
- Create: `engine/templates/book/exports/.gitkeep`

- [ ] **Step 1: Create durable canon templates**

Use YAML fields that are human-readable and sparse. Example `novel_bible.yaml`:

```yaml
premise: ""
platform_style: "tomato"
target_reader: ""
story_promise: ""
protagonist_fantasy: ""
tone: ""
main_conflict: ""
long_term_goal: ""
ending_direction: ""
hard_constraints: []
human_notes: []
```

- [ ] **Step 2: Create state templates**

`current_state.json`:

```json
{
  "current_chapter": 0,
  "current_arc": "arc_001",
  "latest_location": "",
  "active_characters": [],
  "active_conflicts": [],
  "pending_approvals": []
}
```

`chapter_index.json`:

```json
{
  "chapters": []
}
```

- [ ] **Step 3: Create empty directory placeholders**

Use `.gitkeep` files in empty directories that need to be preserved.

- [ ] **Step 4: Commit**

```powershell
git add engine/templates/book
git commit -m "feat: add reusable book templates"
```

---

## Task 4: Implement Book Initialization

**Files:**
- Create: `engine/book_factory.py`
- Modify: `engine/cli.py`
- Test: `tests/test_book_factory.py`

- [ ] **Step 1: Write failing tests**

Test:

- `create_book("demo", title="Demo Book")` creates `books/demo/book.yaml`.
- Template directories are copied.
- Existing book creation fails unless `force=True`.
- `book.yaml` receives the provided title and book id.

- [ ] **Step 2: Run tests to verify failure**

```powershell
pytest tests/test_book_factory.py -v
```

Expected: FAIL because `book_factory.py` does not exist.

- [ ] **Step 3: Implement `create_book`**

Signature:

```python
def create_book(book_id: str, title: str, force: bool = False) -> Path:
    ...
```

Behavior:

- Copy `engine/templates/book` into `books/<book_id>`.
- Refuse to overwrite existing books unless `force=True`.
- Update `book.yaml` with `book_id`, `title`, and created timestamp.

- [ ] **Step 4: Implement CLI command**

Command:

```powershell
python -m engine.cli init-book demo --title "Demo Book"
```

Expected output:

```text
Created book project: books/demo
```

- [ ] **Step 5: Run tests**

```powershell
pytest tests/test_book_factory.py -v
```

Expected: PASS.

- [ ] **Step 6: Manual smoke test**

```powershell
python -m engine.cli init-book demo --title "Demo Book"
```

Expected: creates `books/demo`.

- [ ] **Step 7: Commit**

```powershell
git add engine/book_factory.py engine/cli.py tests/test_book_factory.py books/demo
git commit -m "feat: initialize book projects"
```

If `books/demo` is only test output and not wanted as a sample project, delete it before committing and commit only code plus tests.

---

## Task 5: Add Shared Knowledge Base

**Files:**
- Create: `knowledge/tomato/style-rules.md`
- Create: `knowledge/tomato/chapter-scoring.md`
- Create: `knowledge/tomato/opening-hooks.md`
- Create: `knowledge/craft/narrative-basics.md`
- Create: `knowledge/craft/common-failure-modes.md`
- Create: `knowledge/readers/tomato-reader-personas.md`
- Create: `knowledge/risk/content-and-quality-risks.md`

- [ ] **Step 1: Write Tomato style rules**

Include:

- Strong opening situation.
- Clear protagonist agency.
- Fast conflict setup.
- Frequent emotional payoff.
- Chapter-end pull.
- Avoid treating patterns as mandatory formulas.

- [ ] **Step 2: Write chapter scoring rubric**

Use a 100-point human-readable rubric:

```text
Hook strength: 10
Conflict clarity: 10
Protagonist agency: 10
Emotional payoff: 15
Pacing: 10
Character consistency: 10
Continuity safety: 10
Chapter-end pull: 10
Mainline relevance: 10
Fresh information or expectation: 5
```

- [ ] **Step 3: Add craft and risk notes**

Keep notes concise and usable by agents. Include warnings about formulaic writing, outdated trends, canon pollution, and generic reviewer approval.

- [ ] **Step 4: Commit**

```powershell
git add knowledge
git commit -m "feat: add initial writing knowledge base"
```

---

## Task 6: Add Core Agent Prompts

**Files:**
- Create: `engine/prompts/shared/output-contracts.md`
- Create: `engine/prompts/agents/showrunner.md`
- Create: `engine/prompts/agents/plot_planner.md`
- Create: `engine/prompts/agents/chapter_writer.md`
- Create: `engine/prompts/agents/continuity_editor.md`
- Create: `engine/prompts/agents/tomato_pacing_editor.md`
- Create: `engine/prompts/agents/reviser.md`

- [ ] **Step 1: Create shared output contracts**

Define:

- Agents must state assumptions.
- Agents must preserve book canon.
- Review agents must provide evidence, severity, and suggested fixes.
- Canon changes must be listed separately.
- No major canon change is authoritative until human approval.

- [ ] **Step 2: Create Showrunner prompt**

Responsibilities:

- Protect story promise.
- Reject plot turns that break protagonist fantasy.
- Keep target reader and tone visible.

Output sections:

- Direction check.
- Approved priorities.
- Risks.
- Human approval needed.

- [ ] **Step 3: Create Plot Planner prompt**

Responsibilities:

- Convert arc goals into chapter briefs.
- Maintain chapter-level conflict and payoff.

Output sections:

- Chapter goal.
- Required beats.
- Required emotional payoff.
- Required canon references.
- End hook.

- [ ] **Step 4: Create Chapter Writer prompt**

Responsibilities:

- Draft only from the brief and context.
- Avoid inventing unsupported canon.
- End with a clear next-chapter pull.

Output sections:

- Chapter draft.
- New facts introduced.
- State changes.
- Open threads touched.

- [ ] **Step 5: Create review prompts**

Continuity Editor output JSON:

```json
{
  "passed": false,
  "score": 0,
  "issues": [
    {
      "type": "timeline_conflict",
      "severity": "high",
      "evidence": "",
      "suggested_fix": ""
    }
  ],
  "required_fixes": []
}
```

Tomato Pacing Editor output JSON:

```json
{
  "score": 0,
  "strengths": [],
  "issues": [],
  "revision_priorities": []
}
```

- [ ] **Step 6: Create Reviser prompt**

Responsibilities:

- Apply approved review notes.
- Preserve working parts of the draft.
- Report what changed.

- [ ] **Step 7: Commit**

```powershell
git add engine/prompts
git commit -m "feat: add core writers room agent prompts"
```

---

## Task 7: Implement Book Validation

**Files:**
- Create: `engine/validators.py`
- Modify: `engine/cli.py`
- Test: `tests/test_validators.py`

- [ ] **Step 1: Write failing tests**

Test:

- A freshly initialized book validates.
- Removing `canon/novel_bible.yaml` returns a missing-file error.
- Review score validation rejects scores below 0 or above 100.

- [ ] **Step 2: Run tests to verify failure**

```powershell
pytest tests/test_validators.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement validation**

Functions:

```python
def validate_book(book_id: str) -> list[str]:
    ...

def validate_score(score: int) -> bool:
    ...
```

Return a list of human-readable errors. Empty list means valid.

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli validate-book demo
```

Expected valid output:

```text
Book project is valid: demo
```

- [ ] **Step 5: Run tests**

```powershell
pytest tests/test_validators.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add engine/validators.py engine/cli.py tests/test_validators.py
git commit -m "feat: validate book project structure"
```

---

## Task 8: Implement Chapter Context Builder

**Files:**
- Create: `engine/context_builder.py`
- Modify: `engine/cli.py`
- Test: `tests/test_context_builder.py`

- [ ] **Step 1: Write failing tests**

Test:

- `build_context("demo", 1)` includes novel bible, characters, current state, arc outline, chapter index, and relevant knowledge file names.
- The context output is Markdown.
- Missing book validation errors are surfaced clearly.

- [ ] **Step 2: Run tests to verify failure**

```powershell
pytest tests/test_context_builder.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement context builder**

Function:

```python
def build_context(book_id: str, chapter_number: int) -> str:
    ...
```

Markdown output sections:

- Book metadata.
- Story bible.
- Characters.
- Current state.
- Timeline.
- Open threads.
- Relevant outline.
- Recent chapter summaries.
- Shared knowledge references.
- Agent handoff instructions.

- [ ] **Step 4: Add CLI command**

Command:

```powershell
python -m engine.cli build-context demo 1 --output books/demo/state/ch_0001_context.md
```

Expected: writes a context pack Markdown file.

- [ ] **Step 5: Run tests**

```powershell
pytest tests/test_context_builder.py -v
```

Expected: PASS.

- [ ] **Step 6: Manual smoke test**

```powershell
python -m engine.cli init-book demo --title "Demo Book" --force
python -m engine.cli build-context demo 1 --output books/demo/state/ch_0001_context.md
```

Expected: context file exists and is readable.

- [ ] **Step 7: Commit**

```powershell
git add engine/context_builder.py engine/cli.py tests/test_context_builder.py
git commit -m "feat: build chapter context packs"
```

---

## Task 9: Add Manual Single-Chapter Workflow Documentation

**Files:**
- Create: `docs/workflows/manual-single-chapter-pipeline.md`
- Create: `docs/workflows/human-approval-checkpoints.md`
- Modify: `README.md`

- [ ] **Step 1: Create workflow directory**

```powershell
New-Item -ItemType Directory -Force -Path docs\workflows
```

- [ ] **Step 2: Document single-chapter loop**

Include:

```text
1. Initialize or validate book.
2. Build chapter context.
3. Give context to Plot Planner prompt.
4. Give brief and context to Chapter Writer prompt.
5. Run Continuity Editor prompt.
6. Run Tomato Pacing Editor prompt.
7. Give review notes to Reviser prompt.
8. Human approves final draft.
9. Human or Codex updates canon/state from listed changes.
```

- [ ] **Step 3: Document approval checkpoints**

Required human approval:

- Book bible.
- Major protagonist changes.
- Major canon changes.
- New long-running threads.
- Chapter acceptance.
- State update acceptance.

- [ ] **Step 4: Link docs from README**

Add a "V1 manual workflow" section.

- [ ] **Step 5: Commit**

```powershell
git add docs/workflows README.md
git commit -m "docs: document manual chapter workflow"
```

---

## Task 10: Final Verification

**Files:**
- Modify as needed based on verification findings.

- [ ] **Step 1: Run all tests**

```powershell
pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Run CLI smoke test**

```powershell
python -m engine.cli init-book smoke_test --title "Smoke Test" --force
python -m engine.cli validate-book smoke_test
python -m engine.cli build-context smoke_test 1 --output books/smoke_test/state/ch_0001_context.md
```

Expected:

- Book is created.
- Validation passes.
- Context file is created.

- [ ] **Step 3: Inspect generated context**

Run:

```powershell
Get-Content books\smoke_test\state\ch_0001_context.md -TotalCount 80
```

Expected: context includes bible, state, outline, open threads, and handoff instructions.

- [ ] **Step 4: Remove or keep smoke project intentionally**

If keeping as sample, rename it to `books/sample_tomato_project` and mention it in README.

If not keeping:

```powershell
Remove-Item -Recurse -Force books\smoke_test
```

- [ ] **Step 5: Check git status**

```powershell
git status --short
```

Expected: only intentional files are changed.

- [ ] **Step 6: Final commit**

```powershell
git add .
git commit -m "feat: complete v0 v1 writers room starter"
```

Only run this commit if there are final documentation or cleanup changes after previous task commits.

---

## Acceptance Criteria

The V0+V1 starter is complete when:

- `python -m engine.cli init-book <book_id> --title "<title>"` creates an isolated book project.
- `python -m engine.cli validate-book <book_id>` verifies required files.
- `python -m engine.cli build-context <book_id> <chapter>` writes a usable Markdown context pack.
- Core prompt files exist for Showrunner, Plot Planner, Chapter Writer, Continuity Editor, Tomato Pacing Editor, and Reviser.
- Shared knowledge files exist for Tomato style, craft basics, reader personas, and risks.
- Tests cover book initialization, validation, IO helpers, and context building.
- README explains how to run the manual single-chapter pipeline.
- The system remains file-based and does not exceed the V0+V1 scope.

## Review Note

The original writing-plans workflow recommends a plan-document-reviewer subagent. In this workspace, do not dispatch a subagent unless the user explicitly requests parallel agent review. If the user asks for review, send this plan file to a reviewer before implementation.
