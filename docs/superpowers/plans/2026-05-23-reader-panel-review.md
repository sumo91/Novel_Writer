# Reader Panel Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a non-canon reader persona review scaffold to the chapter pipeline.

**Architecture:** Create a focused `engine.reader_panel` module that writes `reviews/ch_XXXX/reader_panel_review.json` plus an HTML review copy. Wire a CLI command to that module and expose the artifact in pipeline status as optional feedback, not as an acceptance gate.

**Tech Stack:** Python, argparse CLI, JSON/YAML file helpers, pytest.

---

### Task 1: Reader Panel Scaffold

**Files:**
- Create: `engine/reader_panel.py`
- Test: `tests/test_reader_panel.py`

- [ ] Write failing tests for JSON and HTML scaffold generation.
- [ ] Verify the tests fail because `engine.reader_panel` is missing.
- [ ] Implement `write_reader_panel_review_scaffold`.
- [ ] Verify `python -m pytest tests/test_reader_panel.py -q` passes.

### Task 2: CLI Command

**Files:**
- Modify: `engine/cli.py`
- Test: `tests/test_cli.py`

- [ ] Write a failing CLI test for `reader-panel-review`.
- [ ] Verify the test fails because the command is missing.
- [ ] Add parser and command handling.
- [ ] Verify the targeted CLI test passes.

### Task 3: Optional Pipeline Artifact

**Files:**
- Modify: `engine/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] Write a failing test proving `pipeline_status` lists `reader_panel_review`.
- [ ] Verify the test fails.
- [ ] Add the artifact to the manifest and keep `_derive_status` unchanged.
- [ ] Verify pipeline tests pass.

### Task 4: Workflow Documentation

**Files:**
- Create: `docs/workflows/v4-8-reader-panel-review.md`

- [ ] Document that reader panel feedback is simulated, non-canon, and not a hard quality gate.
- [ ] Include the CLI command and expected file path.
- [ ] Run relevant tests and `validate-book` for the target pilot if practical.
