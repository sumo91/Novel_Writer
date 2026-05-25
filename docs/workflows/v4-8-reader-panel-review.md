# V4.8 Reader Panel Review

V4.8 adds an optional simulated reader feedback layer to the chapter pipeline. It is a reader-reaction aid, not market data, canon, or a hard quality gate.

## Purpose

Use reader panel review after a revised draft or final-candidate pass when you want to test likely reader reactions before acceptance.

The panel focuses on:

- whether the chapter payoff is visible;
- whether the next-chapter pull is strong;
- whether setting, resource, economy, or faction logic feels legible;
- whether emotional movement lands;
- where a reader may drop off.

## Command

```powershell
python -m engine.cli reader-panel-review <book_id> <chapter>
```

The command writes:

```text
books/<book_id>/reviews/ch_XXXX/reader_panel_review.json
books/<book_id>/reviews/ch_XXXX/reader_panel_review.html
```

Use `--force` only when intentionally replacing an existing review scaffold.

## Status In The Pipeline

`pipeline-status` lists `reader_panel_review` as an artifact, but missing reader panel feedback does not block the normal chapter lifecycle.

Reader panel notes may inform:

- author direction;
- prose quality review;
- final candidate revisions;
- future craft knowledge cards.

They must not directly update canon, pending approvals, state ledgers, chapter acceptance packets, or accepted chapters.

## Default Personas

The scaffold includes:

- `payoff_reader`: checks visible gain, trade advantage, and protagonist initiative.
- `binge_reader`: checks chapter-end pull and next action.
- `setting_logic_reader`: checks rule, resource, economy, and faction logic.
- `emotional_reader`: checks character pressure and emotional payoff.
- `dropoff_risk_reader`: checks slow openings, exposition, and unclear reward.

## Human Control

The human showrunner decides which reader-panel suggestions matter. A simulated reader complaint is not automatically a required fix.
