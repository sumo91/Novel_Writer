# V3.3 Chapter Brief Contract Workflow

V3.3 converts approved outline layers into a concrete chapter brief scaffold. It sits after V3.2's outline gate and before chapter drafting.

## Commands

Write a scaffold to the default brief path:

```powershell
python -m engine.cli chapter-brief-scaffold <book_id> <chapter>
```

Write to a custom path:

```powershell
python -m engine.cli chapter-brief-scaffold <book_id> <chapter> --output <path>
```

Overwrite an existing scaffold:

```powershell
python -m engine.cli chapter-brief-scaffold <book_id> <chapter> --force
```

Check an existing brief:

```powershell
python -m engine.cli chapter-brief-check <book_id> <chapter>
```

## Required Brief Sections

V3.3 expects:

- `## V3.3 Outline Contract`
- `## Chapter Goal`
- `## Opening Hook`
- `## Required Beats`
- `## Character Movement`
- `## Payoff Design`
- `## Anti-Infodump Opening`
- `## State Update Expectations`
- `## Economy And Faction Constraints`
- `## Ending Pull`
- `## Continuity Notes`

The brief must include:

```text
master -> volume -> arc -> unit -> chapter brief
```

The anti-infodump opening section should name the first concrete scene pressure,
which explanations should be delayed, and what event triggers any necessary
setting, system, economy, faction, or backstory explanation.

## Recommended Flow

1. Run `outline-status`.
2. Run `chapter-brief-gate`.
3. Run `chapter-brief-scaffold`.
4. Edit the scaffold into a human-approved chapter brief.
5. Run `chapter-brief-check`.
6. Only then draft the chapter.

`prepare-chapter` now reports brief gate and brief check status, but it does not create or approve a brief by itself.
