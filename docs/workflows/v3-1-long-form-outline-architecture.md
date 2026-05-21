# V3.1 Long-Form Outline Architecture Workflow

V3.1 adds the upstream long-form control layer above the V2.6 chapter pipeline and V3 state machine. The goal is to make each chapter serve an approved full-book, volume, arc, and unit plan before prose is drafted.

## Outline Hierarchy

```text
canon/novel_bible.yaml
  -> outlines/master_outline.yaml
  -> outlines/volumes/volume_001.yaml
  -> outlines/arc_001.yaml
  -> outlines/units/unit_0001.yaml
  -> outlines/chapter_briefs/ch_XXXX_brief.md
  -> draft/review/revision/acceptance
  -> V3 state ledgers
```

## V3.1 Files

- `outlines/master_outline.yaml`
- `outlines/volumes/volume_001.yaml`
- `outlines/arc_001.yaml`
- `outlines/units/unit_0001.yaml`
- `canon/economy.yaml`
- `canon/factions.yaml`
- strengthened `canon/open_threads.yaml` as the current mystery and foreshadowing ledger

Do not add a separate `canon/mystery_ledger.yaml` in V3.1 unless `open_threads.yaml` becomes insufficient.

## Approval Gates

Master, volume, arc, unit, economy, and faction files each use an `approval` block.

- `draft`: usable as a labeled assumption only.
- `approved`: usable as a hard writing constraint.
- `rejected`: not usable.
- `superseded`: replaced by a newer plan.

Major changes to approved outline or canon-support files require human approval.

## Locked And Open Layers

Locked planning layer:

- opening state;
- ending direction;
- three-act spine;
- core rules;
- protagonist end-state;
- major mystery answer direction.

Open planning layer:

- local chapter details;
- minor characters;
- exact goods and trades;
- tactical scene reversals;
- chapter-level execution.

## Chapter Context

`prepare-chapter` builds a context pack that includes:

- master outline;
- active volume;
- active arc;
- active unit;
- economy;
- factions;
- open threads, hooks, payoff ledger, resources, and memory indexes.

The handoff reference chain is:

```text
master -> volume -> arc -> unit -> chapter brief
```

Chapter briefs after V3.1 should state which master, volume, arc, and unit obligations they serve.

## Outline Map Review

Use:

```powershell
python -m engine.cli outline-map-review <book_id>
```

The command writes `reports/outline_map_review.md` plus an HTML sidecar. It summarizes the book, volume, arc, and unit as a minimum writing map: core conflict, turning point, payoff or climax, stage ending, and protagonist change. This is a human-readable review artifact, not canon.

## Migration

Use:

```powershell
python -m engine.cli migrate-v3-1 <book_id>
```

Migration creates missing V3.1 files and upgrades empty schema keys while preserving existing values. It must not parse old prose, convert free-text notes, or infer canon.

## Drift Review

`drift-report` includes `## Outline Alignment`.

The section warns when:

- accepted chapters fall outside approved unit ranges;
- an approved unit has no chapter function map;
- required unit threads were not touched;
- hooks, open threads, payoffs, or resources drift away from outline/economy constraints.

These are mechanical warnings. Human editorial judgment still decides whether to revise, approve, defer, or update the outline.
