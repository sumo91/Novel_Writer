# V3.2 Outline Approval Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a command-line and validation gate that prevents chapter planning from silently bypassing V3.1 outline approval status.

**Architecture:** Add `engine/outline_gate.py` for status/update/gate logic. Keep `engine/cli.py` as a renderer. Reuse the same outline-gate helper inside `engine/hardening.py`/`engine/validators.py` for chapter brief validation.

**Tech Stack:** Python, pytest, YAML files through `engine.io_utils`.

---

### Task 1: Outline Gate Core

**Files:**
- Create: `engine/outline_gate.py`
- Test: `tests/test_outline_gate.py`

- [ ] Write failing tests for `get_outline_status`, `update_outline_approval`, and `chapter_brief_gate`.
- [ ] Run `python -m pytest tests/test_outline_gate.py -q` and verify failures.
- [ ] Implement minimal status/update/gate logic in `engine/outline_gate.py`.
- [ ] Run `python -m pytest tests/test_outline_gate.py -q` and verify pass.

### Task 2: CLI Commands

**Files:**
- Modify: `engine/cli.py`
- Test: `tests/test_cli.py`

- [ ] Write failing CLI tests for `outline-status`, `outline-approval-update`, and `chapter-brief-gate --strict`.
- [ ] Run targeted CLI tests and verify failures.
- [ ] Add CLI parsers and command handlers.
- [ ] Run targeted CLI tests and verify pass.

### Task 3: Brief Validation

**Files:**
- Modify: `engine/hardening.py`
- Modify: `engine/validators.py`
- Test: `tests/test_validators.py`

- [ ] Write failing validator test for a chapter brief missing V3.1 reference language.
- [ ] Run the targeted validator test and verify failure.
- [ ] Implement chapter brief validation helper using `outline_gate`.
- [ ] Run targeted validator tests and verify pass.

### Task 4: Docs And Skill

**Files:**
- Create: `docs/workflows/v3-2-outline-approval-gate.md`
- Modify: `.agents/skills/novel-writing-showrunner/SKILL.md`

- [ ] Document the V3.2 workflow and commands.
- [ ] Add V3.2 commands to the project-local showrunner skill.
- [ ] Run `git diff --check`.

### Task 5: Full Verification

**Files:**
- No new files.

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m engine.cli validate-book xiuxian_shop_pilot`.
- [ ] Run `python -m engine.cli outline-status xiuxian_shop_pilot`.
- [ ] Run `python -m engine.cli chapter-brief-gate xiuxian_shop_pilot 5`.
- [ ] Commit the V3.2 changes.
