# V3.3 Chapter Brief Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a chapter brief scaffold/check layer so approved outlines become a concrete pre-draft brief contract.

**Architecture:** Add `engine/brief_contract.py` for scaffold/check logic. CLI commands render and write scaffolds. `prepare-chapter` surfaces gate/check status without auto-writing a brief.

**Tech Stack:** Python, pytest, Markdown, YAML/JSON helpers from `engine.io_utils`.

---

### Task 1: Core Brief Contract Module

**Files:**
- Create: `engine/brief_contract.py`
- Test: `tests/test_brief_contract.py`

- [ ] Write failing tests for scaffold content and brief checking.
- [ ] Run `python -m pytest tests/test_brief_contract.py -q` and verify failure.
- [ ] Implement minimal scaffold/check logic.
- [ ] Run `python -m pytest tests/test_brief_contract.py -q` and verify pass.

### Task 2: CLI Commands

**Files:**
- Modify: `engine/cli.py`
- Test: `tests/test_cli.py`

- [ ] Write failing tests for `chapter-brief-scaffold` and `chapter-brief-check`.
- [ ] Run targeted CLI tests and verify failure.
- [ ] Add CLI parsers and handlers.
- [ ] Run targeted CLI tests and verify pass.

### Task 3: Prepare-Chapter Visibility

**Files:**
- Modify: `engine/cli.py`
- Test: `tests/test_cli.py`

- [ ] Write failing test that `prepare-chapter` output includes brief gate/check status.
- [ ] Add status rendering after workspace creation.
- [ ] Run targeted test and verify pass.

### Task 4: Docs And Skill

**Files:**
- Create: `docs/workflows/v3-3-chapter-brief-contract.md`
- Modify: `.agents/skills/novel-writing-showrunner/SKILL.md`

- [ ] Document scaffold/check commands and expected brief sections.
- [ ] Add V3.3 commands to the showrunner skill.
- [ ] Run `git diff --check`.

### Task 5: Full Verification

**Files:**
- No new files.

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m engine.cli validate-book xiuxian_shop_pilot`.
- [ ] Run `python -m engine.cli chapter-brief-scaffold xiuxian_shop_pilot 5 --output <temp>`.
- [ ] Run `python -m engine.cli chapter-brief-check xiuxian_shop_pilot 5`.
- [ ] Commit and merge.
