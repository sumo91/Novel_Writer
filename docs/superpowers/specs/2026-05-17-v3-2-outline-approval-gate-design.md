# V3.2 Outline Approval Gate Design

## Goal

V3.2 turns the V3.1 long-form outline layer into a pre-writing gate. Before a chapter brief is written, the system should show which outline/canon-support layers exist, whether they are draft or approved, and whether the next chapter can proceed under normal or strict rules.

## Scope

In scope:

- Report approval status for `master`, `volume`, `arc`, `unit`, `economy`, and `factions`.
- Update one outline-layer approval status from the CLI.
- Gate chapter brief preparation by checking V3.1 files, active outline chain, draft/approved status, and existing brief reference text.
- Validate chapter briefs for the V3.1 reference chain and obligation language.
- Document the V3.2 workflow and add the new commands to the project-local showrunner skill.

Out of scope:

- UI/dashboard work.
- Reader simulators, market agents, or data feedback.
- Batch outline approval updates.
- Automatic canon inference or automatic promotion from draft to approved.
- Rewriting existing briefs automatically.

## Architecture

Create `engine/outline_gate.py` as the single home for V3.2 business logic. CLI commands call this module and render human-readable output. Validators call a small validation helper from the same module so the gate rules are consistent between command-line checks and `validate-book`.

The active V3.1 layers are intentionally simple in this version:

- `master`: `outlines/master_outline.yaml`
- `volume`: `outlines/volumes/volume_001.yaml`
- `arc`: `outlines/arc_001.yaml`
- `unit`: `outlines/units/unit_0001.yaml`
- `economy`: `canon/economy.yaml`
- `factions`: `canon/factions.yaml`

## Command Behavior

`outline-status <book_id>` prints each layer path and approval status. Missing files are reported as missing. Draft layers are explicitly labeled as assumptions.

`outline-approval-update <book_id> <layer> --status <status> [--note "..."]` updates the file-level `approval.status`. Allowed statuses are `draft`, `approved`, `rejected`, and `superseded`. The command preserves existing YAML values and only edits the approval block.

`chapter-brief-gate <book_id> <chapter> [--strict]` reports whether the chapter brief can proceed. In default mode, draft outline layers warn but do not block. In strict mode, any non-approved active layer blocks the gate. Missing V3.1 files always block. If a brief already exists, it must include the literal reference chain `master -> volume -> arc -> unit` and mention outline obligations.

## Validation

`validate-book` should check existing chapter brief files. Briefs created after V3.1 should include:

- `master -> volume -> arc -> unit`
- `outline obligation` or `outline obligations`
- `unit`
- `arc`
- `volume`

This is intentionally mechanical. The check proves the handoff has the long-form control language; it does not judge whether the outline work is artistically good.

## Testing

Use TDD. Add focused tests for:

- status reporting on a fresh book;
- approval status update and invalid layer/status errors;
- gate warnings in default mode for draft outlines;
- strict gate blocking draft outlines;
- missing V3.1 file blocking the gate;
- validator errors for a chapter brief missing V3.1 reference language.

Full completion requires `python -m pytest -q` and `python -m engine.cli validate-book xiuxian_shop_pilot`.
