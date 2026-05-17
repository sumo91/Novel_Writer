# V3.2 Outline Approval Gate Workflow

V3.2 makes the V3.1 outline layer operational before chapter planning. Its purpose is to stop draft outlines from silently becoming hard canon and to make every new chapter brief declare which long-form obligations it serves.

## Commands

Check outline approval state:

```powershell
python -m engine.cli outline-status <book_id>
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

## Chapter Brief Requirement

Every V3.2 chapter brief should include the reference chain:

```text
master -> volume -> arc -> unit -> chapter brief
```

It should also name the outline obligations it serves, including the active volume, arc, and unit. This is a mechanical handoff requirement, not a claim that the outline itself is perfect.

## Recommended Pre-Writing Flow

1. Run `outline-status`.
2. Decide whether draft layers are acceptable assumptions or whether strict approval is needed.
3. Run `chapter-brief-gate`.
4. If blocked, approve/update the relevant outline layer or revise the brief.
5. Prepare the chapter workspace only after the gate is clear.

## What V3.2 Does Not Do

- It does not judge market quality.
- It does not infer canon from prose.
- It does not auto-approve outline layers.
- It does not replace human showrunner approval.
