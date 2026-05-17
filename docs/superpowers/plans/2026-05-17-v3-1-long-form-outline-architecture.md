# V3.1 Long-Form Outline Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the V3.1 long-form outline control layer so chapters are planned against full-book, volume, arc, unit, economy, and faction constraints before entering the existing chapter pipeline.

**Architecture:** Keep V2.6 chapter workflow and V3 state machine intact. Add book-local outline/canon support files, lightweight migration, structural validators, context-pack inclusion, and drift-report outline-alignment warnings. V3.1 remains file-based YAML/JSON and does not infer old canon from prose.

**Tech Stack:** Python standard library, existing `engine.io_utils` YAML/JSON helpers, pytest, file templates under `engine/templates/book/`.

---

## Source Spec

- `docs/superpowers/specs/2026-05-17-v3-1-long-form-outline-architecture-design.md`

## Scope

In scope:

- Stronger `outlines/master_outline.yaml`
- New `outlines/volumes/volume_001.yaml`
- Upgraded `outlines/arc_001.yaml`
- Upgraded `outlines/units/unit_0001.yaml`
- New `canon/economy.yaml`
- New `canon/factions.yaml`
- Stronger `canon/open_threads.yaml` usage as the first mystery/foreshadowing ledger. Do not add `canon/mystery_ledger.yaml` in V3.1 unless implementation shows `open_threads.yaml` is insufficient.
- File-level approval gates for master, volume, arc, unit, economy, and factions.
- Explicit reference chain from chapter brief back to master -> volume -> arc -> unit.
- Locked/open distinction for long-form planning:
  - locked: opening state, ending direction, three-act spine, core rules, protagonist end-state, major mystery answer direction;
  - open: local chapter details, minor characters, exact goods, scene reversals, tactical execution.
- V3.1 migration, validation, context-pack integration, drift alignment checks
- Apply V3.1 to `books/xiuxian_shop_pilot` after code support

Out of scope:

- UI, RAG, market agent, reader simulator, data feedback
- Intelligent old-chapter backfill
- Full 100-chapter detailed map
- Replacing the existing approval system

## Execution Style

This is the compact master plan. Do not expand every implementation detail here. When starting a task, create a short task card in the session with:

- exact tests to add;
- exact files to edit;
- verification command;
- commit message.

This prevents the plan itself from becoming too long while keeping implementation controlled.

---

### Task 0: Preflight Checkpoint

**Files:**

- No planned edits.

- [ ] Confirm current fiction/state work is already checkpointed before architecture work starts.
- [ ] Run `git status --short`.
- [ ] Expected at this point: only this V3.1 plan may be uncommitted. If chapter files, V3 ledgers, or pending approval files are dirty, commit or deliberately exclude them before Task 1.
- [ ] Commit this plan if desired: `docs: plan v3.1 long-form outline architecture`.

### Task 1: Add V3.1 Templates

**Files:**

- Modify: `engine/templates/book/outlines/master_outline.yaml`
- Create: `engine/templates/book/outlines/volumes/volume_001.yaml`
- Modify: `engine/templates/book/outlines/arc_001.yaml`
- Modify: `engine/templates/book/outlines/units/unit_0001.yaml`
- Create: `engine/templates/book/canon/economy.yaml`
- Create: `engine/templates/book/canon/factions.yaml`
- Test: `tests/test_book_factory.py`

- [ ] Add a failing book-factory test that new books contain all V3.1 outline/canon files.
- [ ] Add template schemas from the V3.1 spec with `approval.status: draft`.
- [ ] Add locked/open fields or notes to `master_outline.yaml` so executors can tell which story promises are fixed and which remain flexible.
- [ ] Run `python -m pytest tests/test_book_factory.py -q`.
- [ ] Commit: `feat: add v3.1 outline templates`.

### Task 2: Add Lightweight V3.1 Migration

**Files:**

- Modify: `engine/v3_migration.py`
- Modify: `engine/cli.py`
- Test: `tests/test_v3_migration.py`
- Test: `tests/test_cli.py`

- [ ] Add tests proving migration creates missing V3.1 files without parsing prose.
- [ ] Upgrade `master_outline.yaml`, `arc_001.yaml`, and `unit_0001.yaml` by adding missing keys while preserving existing values.
- [ ] Create missing `outlines/volumes/volume_001.yaml`, `canon/economy.yaml`, and `canon/factions.yaml`.
- [ ] Add CLI command `migrate-v3-1 <book_id>` or extend `migrate-v3` with V3.1 behavior. Prefer explicit `migrate-v3-1` if command output would be clearer.
- [ ] Run `python -m pytest tests/test_v3_migration.py tests/test_cli.py -q`.
- [ ] Commit: `feat: add v3.1 migration`.

### Task 3: Validate V3.1 Outline Shape

**Files:**

- Modify: `engine/hardening.py`
- Modify: `engine/validators.py`
- Test: `tests/test_validators.py`

- [ ] Add tests for required V3.1 files, YAML root mappings, approval status values, and chapter ranges.
- [ ] Validate `master_outline.yaml` required fields from the spec.
- [ ] Validate file-level approval status values: `draft`, `approved`, `rejected`, `superseded`.
- [ ] Validate that approved outline layers are allowed as hard constraints, while draft layers must be treated as assumptions by downstream context.
- [ ] Validate volume/arc/unit hierarchy shape:
  - volume chapter range has integer start/end;
  - arc parent volume exists when volumes exist;
  - unit parent arc exists;
  - unit chapter entries stay inside unit range.
- [ ] Validate that `unit_0001.yaml` can require explicit chapter functions for chapters 1-10 once the unit is approved.
- [ ] Validate chapter briefs after V3.1 include references to current master, volume, arc, and unit obligations.
- [ ] Validate `canon/economy.yaml` and `canon/factions.yaml` structural fields.
- [ ] Keep validation structural, not creative.
- [ ] Run `python -m pytest tests/test_validators.py -q`.
- [ ] Commit: `feat: validate v3.1 outline architecture`.

### Task 4: Include Active Outline Layers In Context Packs

**Files:**

- Modify: `engine/context_builder.py`
- Test: `tests/test_context_builder.py`

- [ ] Add tests proving chapter context includes master outline, active volume, active arc, active unit, economy, and factions.
- [ ] Select active volume/arc/unit by chapter range; fall back to `volume_001`, `arc_001`, `unit_0001`.
- [ ] Label draft outline assumptions clearly when `approval.status` is not `approved`.
- [ ] Render the active reference chain in the context pack: master -> volume -> arc -> unit -> chapter.
- [ ] Include open threads as the active mystery/foreshadowing ledger alongside next-hook and payoff ledgers.
- [ ] Run `python -m pytest tests/test_context_builder.py -q`.
- [ ] Commit: `feat: add v3.1 outline context`.

### Task 5: Add Outline Alignment To Drift Reports

**Files:**

- Modify: `engine/drift_report.py`
- Test: `tests/test_drift_report.py`

- [ ] Add a failing test for a `## Outline Alignment` section.
- [ ] Warn when the current chapter is outside approved unit ranges.
- [ ] Warn when active unit has empty chapter obligations.
- [ ] Warn when accepted chapters do not serve required unit/arc threads.
- [ ] Warn when hooks, open-thread deadlines, payoff repetition, or resource growth conflict with known outline/economy constraints.
- [ ] Warn when chapter brief reference-chain data is missing after V3.1.
- [ ] Warn when new setting/canon claims appear in chapter acceptance without pending approval or durable canon/state placement.
- [ ] Keep warnings advisory unless they are schema errors.
- [ ] Run `python -m pytest tests/test_drift_report.py -q`.
- [ ] Commit: `feat: add v3.1 outline drift checks`.

### Task 6: Update Chapter Pipeline Guidance

**Files:**

- Modify: `engine/prompts/agents/plot_planner.md`
- Modify: `engine/prompts/agents/showrunner.md`
- Modify: `engine/prompts/agents/continuity_editor.md`
- Modify: `engine/prompts/agents/tomato_pacing_editor.md`
- Possibly modify: `engine/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] Add tests that prepared handoffs mention master/volume/arc/unit obligations.
- [ ] Ensure chapter brief guidance asks for current outline obligations before prose.
- [ ] Ensure chapter brief guidance records the reference chain: master -> volume -> arc -> unit.
- [ ] Ensure review guidance checks whether the chapter served the planned unit/arc function.
- [ ] Run `python -m pytest tests/test_pipeline.py -q`.
- [ ] Commit: `feat: align chapter handoffs with v3.1 outlines`.

### Task 7: Document V3.1 Workflow

**Files:**

- Create: `docs/workflows/v3-1-long-form-outline-architecture.md`
- Modify: `AGENTS.md`
- Possibly modify: `README.md`

- [ ] Document V3.1 hierarchy and migration command.
- [ ] Document approval expectations for master, volume, arc, unit, economy, and factions.
- [ ] Document locked/open planning layers.
- [ ] Document that `open_threads.yaml` remains the V3.1 mystery/foreshadowing ledger unless a later version splits out `mystery_ledger.yaml`.
- [ ] Document that V3.1 does not infer canon from old prose.
- [ ] Run `rg -n "V3.1|migrate-v3-1|Outline Alignment|economy.yaml|factions.yaml" AGENTS.md docs README.md`.
- [ ] Commit: `docs: document v3.1 outline workflow`.

### Task 8: Apply V3.1 To `xiuxian_shop_pilot`

**Files:**

- Modify: `books/xiuxian_shop_pilot/outlines/master_outline.yaml`
- Create/modify: `books/xiuxian_shop_pilot/outlines/volumes/volume_001.yaml`
- Modify: `books/xiuxian_shop_pilot/outlines/arc_001.yaml`
- Modify: `books/xiuxian_shop_pilot/outlines/units/unit_0001.yaml`
- Create/modify: `books/xiuxian_shop_pilot/canon/economy.yaml`
- Create/modify: `books/xiuxian_shop_pilot/canon/factions.yaml`
- Possibly create: `books/xiuxian_shop_pilot/reports/ch_0001_0004_drift_review_v3_1.md`

- [ ] Run V3.1 migration on `xiuxian_shop_pilot`.
- [ ] Fill long-form outline with only approved facts plus clearly marked draft assumptions.
- [ ] Capture first volume goal: secure the small shop, stabilize two-world trade, and survive first faction pressure.
- [ ] Capture arc 001 goal: foothold versus pill-shop/patrol pressure.
- [ ] Capture unit 0001 chapter functions for chapters 1-10, with chapters 1-4 anchored to accepted facts and chapters 5-10 as draft plan.
- [ ] Fill economy and factions using accepted chapters 1-4 facts.
- [ ] Strengthen the active open-thread ledger for: Grandpa Chen's old ledger, qingdeng grass, the back-door rule, and pill-shop pressure.
- [ ] Mark draft assumptions separately from approved facts.
- [ ] Run `python -m engine.cli validate-book xiuxian_shop_pilot`.
- [ ] Run `python -m engine.cli drift-report xiuxian_shop_pilot --start 1 --end 4 --output books/xiuxian_shop_pilot/reports/ch_0001_0004_drift_review_v3_1.md`.
- [ ] Commit: `chore: apply v3.1 outline architecture to xiuxian pilot`.

### Task 9: Final Verification

**Files:**

- No expected code changes unless verification exposes issues.

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m engine.cli validate-book xiuxian_shop_pilot`.
- [ ] Run `python -m engine.cli pipeline-status xiuxian_shop_pilot 4`.
- [ ] Inspect `git status --short`.
- [ ] If clean and all checks pass, report that V3.1 implementation is ready for chapter 5 brief planning.

---

## Success Criteria

V3.1 is complete when:

- new books include V3.1 outline/canon scaffolds;
- existing books can be migrated without inferred canon;
- validators catch malformed outline/economy/faction files;
- chapter context includes current master, volume, arc, unit, economy, and faction layers;
- drift reports include `## Outline Alignment`;
- `xiuxian_shop_pilot` has a usable first long-form outline layer for chapters 1-10;
- before chapter 5 drafting, the system can state what chapter 5 must accomplish in the volume/arc/unit plan.

## Notes For Executors

- Keep V2.6 and V3 behavior backward compatible.
- Do not accept outline changes as hard canon without human approval.
- Do not convert old prose into canon automatically.
- Prefer warnings over hard blockers for editorial-quality judgments.
- Keep story facts under `books/<book_id>/`; keep reusable craft knowledge under `knowledge/`.
