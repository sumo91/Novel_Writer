# V3.2 Outline Approval Gate Workflow

V3.2 makes the V3.1 outline layer operational before chapter planning. Its purpose is to stop draft outlines from silently becoming hard canon and to make every new chapter brief declare which long-form obligations it serves.

## Commands

Check outline approval state:

```powershell
python -m engine.cli outline-status <book_id>
```

Generate mechanical map diagnostics:

```powershell
python -m engine.cli outline-map-review <book_id>
```

Generate the human-readable master approval packet:

```powershell
python -m engine.cli outline-approval-packet <book_id> --layer master
```

Update one outline layer:

```powershell
python -m engine.cli outline-approval-update <book_id> <layer> --status approved --note "..."
```

Valid layers:

- `master`
- `volume`
- `arc`
- `unit`
- `economy`
- `factions`

Valid statuses:

- `draft`
- `approved`
- `rejected`
- `superseded`

Check whether a chapter brief can proceed:

```powershell
python -m engine.cli chapter-brief-gate <book_id> <chapter>
python -m engine.cli chapter-brief-gate <book_id> <chapter> --strict
```

Default mode allows draft outline layers as labeled assumptions. Strict mode blocks unless every active V3.1 layer is approved.

The gate also blocks when the active unit does not contain a complete chapter map for its full `chapter_range`. Each chapter in the active unit range must have a `chapters` entry with `chapter`, `function`, `opening_hook`, `main_payoff`, and `next_hook`. This prevents a thin concept sketch or partial sample plan from being treated as enough structure for chapter-brief generation. `outline-map-review` reports this problem as `incomplete_active_unit_chapter_map`, but only `chapter-brief-gate` blocks the brief workflow.

## Chapter Brief Requirement

Every V3.2 chapter brief should include the reference chain:

```text
master -> volume -> arc -> unit -> chapter brief
```

It should also name the outline obligations it serves, including the active volume, arc, and unit. This is a mechanical handoff requirement, not a claim that the outline itself is perfect.

## Recommended Pre-Writing Flow

1. Run `outline-status`.
2. Run `outline-map-review` for mechanical missing-map diagnostics.
3. Generate and review the relevant approval packet before marking outline layers approved.
4. Decide whether draft layers are acceptable assumptions or whether strict approval is needed.
5. Make sure the active unit has a complete chapter map for its full range.
6. Run `chapter-brief-gate`.
7. If blocked, approve/update the relevant outline layer, complete the active unit chapter map, or revise the brief.
8. Prepare the chapter workspace only after the gate is clear.

## What V3.2 Does Not Do

- It does not judge market quality.
- It does not infer canon from prose.
- It does not auto-approve outline layers.
- It does not replace human showrunner approval.
