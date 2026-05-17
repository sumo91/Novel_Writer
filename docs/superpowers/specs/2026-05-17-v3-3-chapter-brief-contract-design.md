# V3.3 Chapter Brief Contract Design

## Goal

V3.3 turns the approved V3.1/V3.2 outline chain into a concrete chapter-brief contract. The system should not only say whether a brief may be written; it should scaffold the brief with the required long-form obligations and mechanically check whether a hand-written brief contains the required sections.

## Scope

In scope:

- Generate a chapter brief scaffold for a target chapter.
- Check an existing chapter brief against required V3.3 sections.
- Add CLI commands for scaffold/check.
- Add brief-check visibility to `prepare-chapter` output.
- Document the workflow and update the project-local showrunner skill.

Out of scope:

- Generating final prose.
- Automatically accepting a scaffold as a human-approved brief.
- Inferring missing outline content from accepted chapters.
- Reader simulation, market scoring, dashboards, or RAG retrieval.

## Brief Contract

A V3.3 brief should include:

- `## V3.3 Outline Contract`
- `master -> volume -> arc -> unit -> chapter brief`
- `## Chapter Goal`
- `## Opening Hook`
- `## Required Beats`
- `## Character Movement`
- `## Payoff Design`
- `## State Update Expectations`
- `## Economy And Faction Constraints`
- `## Ending Pull`
- `## Continuity Notes`

The scaffold should prefill contract material from:

- active volume, arc, and unit files;
- the unit chapter function for the target chapter;
- open threads;
- payoff ledger;
- hook index;
- current state;
- economy and faction files.

## Architecture

Create `engine/brief_contract.py`.

Core functions:

- `build_chapter_brief_scaffold(book_id, chapter_number) -> str`
- `check_chapter_brief(book_id, chapter_number) -> dict`

The module should use existing YAML/JSON helpers and the V3.2 gate rules. CLI commands should be thin wrappers:

- `chapter-brief-scaffold <book_id> <chapter> [--output <path>] [--force]`
- `chapter-brief-check <book_id> <chapter>`

## Prepare Integration

`prepare-chapter` should not create a brief automatically in V3.3. It should surface whether the brief gate is allowed and whether an existing brief passes the contract. This preserves human/editorial control while making the next required action explicit.

## Testing

Use TDD. Add tests for:

- scaffold contains the V3.3 contract, outline chain, unit chapter function, threads, payoffs, hooks, economy, and factions;
- brief check reports missing file;
- brief check rejects missing required sections;
- brief check passes a scaffold;
- CLI writes scaffold and refuses overwrite without `--force`;
- `prepare-chapter` output includes brief gate/check status.
