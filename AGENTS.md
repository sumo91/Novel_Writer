# Novel Writer Agent Guide

This repository is a file-based long-form web-novel engineering system. Treat it as a reusable writers' room, not a one-prompt story generator.

## Use The Showrunner Skill

Use `$novel-writing-showrunner` whenever the user asks to:

- develop or evaluate a novel idea;
- choose a genre, premise, protagonist, hook, or selling point;
- create or continue a book project;
- decide what the next writing workflow step should be;
- write chapter briefs, drafts, reviews, revised drafts, or acceptance packets;
- run a 3-chapter, 5-chapter, or 10-chapter sample test;
- review drift, pending approvals, canon, or long-form architecture;
- turn writing theory, courses, videos, or examples into reusable knowledge;
- discuss how the Novel_Writer system should evolve.

The skill is the workflow driver. This file is the repository rulebook.

## Project Goal

Novel_Writer aims to support million-word commercial web fiction with explicit memory, controlled drift, reusable craft knowledge, and human editorial authority.

Current strategic priority:

1. Keep the V2.6 chapter pipeline stable.
2. Build V3 long-form state machine and memory.
3. Build V3.1 long-form outline architecture.
4. Only then expand into market intelligence, reader simulators, dashboards, or data feedback.

## Human Editorial Control

- The human is the final showrunner and canon owner.
- Do not accept a chapter into `chapters/` without explicit human confirmation.
- Do not treat generated drafts, reviews, state updates, or pending approvals as canon until accepted.
- Major premise, canon, power-system, relationship, and long-arc changes require human approval.

## Standard Chapter Workflow

For a normal chapter, follow this lifecycle:

1. Prepare chapter workspace:
   `python -m engine.cli prepare-chapter <book_id> <chapter>`
2. Write chapter brief:
   `books/<book_id>/outlines/chapter_briefs/ch_XXXX_brief.md`
3. Write draft:
   `books/<book_id>/drafts/ch_XXXX_draft.md`
4. Write continuity review:
   `books/<book_id>/reviews/ch_XXXX/continuity_review.json`
5. Write pacing review:
   `books/<book_id>/reviews/ch_XXXX/pacing_review.json`
6. Write revised draft:
   `books/<book_id>/drafts/ch_XXXX_revised.md`
7. Draft acceptance packet:
   `python -m engine.cli pipeline-draft-acceptance <book_id> <chapter> --title "<title>" --summary "<summary>"`
8. Stop for human confirmation.
9. After explicit confirmation:
   `python -m engine.cli pipeline-accept <book_id> <chapter> --approved`
10. Verify status and project validity.

## Quality Gates

- Continuity blockers must be fixed or explicitly waived before acceptance.
- Pacing score below 80 requires revision or explicit waiver.
- Pacing review dimension scores must be valid 0-10 integers.
- Acceptance packets must not contain stale text such as `TODO`, `draft_note`, `ready_for_acceptance`, or `pending human acceptance`.
- Chapter acceptance should update durable state through the acceptance packet, not ad hoc memory.

Useful verification commands:

```powershell
python -m pytest -q
python -m engine.cli validate-book <book_id>
python -m engine.cli pipeline-status <book_id> <chapter>
python -m engine.cli pipeline-quality-gate <book_id> <chapter>
```

## State Machine Expectations

Each accepted chapter should maintain or prepare updates for:

- current timeline;
- character state;
- current location;
- active conflicts;
- occurred events;
- open threads and foreshadowing;
- next-chapter hook;
- protagonist progress;
- payoff records;
- pending approvals.

Current files involved:

- `state/current_state.json`
- `state/chapter_index.json`
- `state/change_log.jsonl`
- `state/pending_approvals.yaml`
- `canon/timeline.yaml`
- `canon/open_threads.yaml`
- `canon/characters.yaml`
- `canon/world_rules.yaml`

V3 adds explicit long-form memory ledgers and indexes:

- `canon/character_states.yaml`
- `canon/resource_ledger.yaml`
- `canon/payoff_ledger.yaml`
- upgraded `canon/open_threads.yaml`
- `outlines/units/unit_0001.yaml`
- `state/hook_index.json`
- `state/memory_index.json`

For V3 chapters, fill `v3_state_updates` in the acceptance packet before human review. These updates remain proposed until the packet is accepted. Use `python -m engine.cli migrate-v3 <book_id>` before applying V3 checks to an older book. Migration creates missing V3 files and upgrades empty schemas, but it must not parse old prose, convert free-text notes, or infer canon.

V3.1 adds the long-form outline control layer:

- `outlines/master_outline.yaml`
- `outlines/volumes/volume_001.yaml`
- upgraded `outlines/arc_001.yaml`
- upgraded `outlines/units/unit_0001.yaml`
- `canon/economy.yaml`
- `canon/factions.yaml`

Use `python -m engine.cli migrate-v3-1 <book_id>` before applying V3.1 checks to an older book. Migration creates missing V3.1 files and upgrades empty schema keys while preserving existing values, but it must not parse old prose, convert free-text notes, or infer canon.

Master, volume, arc, unit, economy, and faction files use file-level `approval` blocks. Draft outline layers may be used only as labeled assumptions. Approved outline layers may be treated as hard writing constraints.

V3.1 uses `canon/open_threads.yaml` as the active mystery and foreshadowing ledger. Do not add a separate `canon/mystery_ledger.yaml` unless a later architecture review decides `open_threads.yaml` is insufficient.

Chapter briefs after V3.1 should cite the active reference chain:

```text
master -> volume -> arc -> unit -> chapter brief
```

Keep the locked/open distinction clear:

- Locked: opening state, ending direction, three-act spine, core rules, protagonist end-state, major mystery answer direction.
- Open: local chapter details, minor characters, exact goods, local reversals, tactical execution.

## Pending Approvals

Use pending approvals to track human decisions that should not silently become canon.

Commands:

```powershell
python -m engine.cli sync-pending-approvals <book_id>
python -m engine.cli pending-approval-update <book_id> <approval_id> --status approved --note "..."
python -m engine.cli pending-approval-batch-update <book_id> --updates-file <path>
```

Do not run multiple single-item pending approval updates in parallel against the same registry file. Use batch update for multi-item triage.

## Knowledge Management

Do not dump raw writing books, course transcripts, video notes, or long theory texts directly into `knowledge/`.

When the user provides theory material:

1. Extract practical principles.
2. Convert them into concise knowledge cards.
3. Include fields such as `id`, `scope`, `applies_to`, `use_when`, `principle`, `checks`, and `failure_modes`.
4. Mark whether each item is a hard rule, soft heuristic, or genre-specific pattern.
5. Use these cards during concept design, chapter briefs, reviews, and drift reports.

Theory guides judgment. Book-local canon remains the source of story truth.

## Current Project Facts

- `sample_tomato_project` is an urban/business V2.5-V2.6 tool-validation sample. It is not the user's preferred genre.
- `xiuxian_shop_pilot` is the target-genre pilot sample.
- `xiuxian_shop_pilot` has accepted chapters 1-4.
- Its current premise is: a failing small shop inherited from the protagonist's grandfather opens to a cultivation-world market at midnight.
- The back door rule is approved: it opens every midnight for one Chinese `时辰`, about two hours.
- The 1-4 sample validated: opening hook, first trade, reality payoff, cultivation-world commercial pressure, and the first pill-shop negotiation pressure.
- The recommended story next step, if continuing fiction, is chapter 5: 赵掌柜亲自来谈.
- The recommended system next step is V3.1 long-form outline architecture.

## Repository Practices

- Use `rg` / `rg --files` for search.
- Use `apply_patch` for manual edits.
- Do not revert user or other-agent changes unless explicitly asked.
- The worktree may be dirty; preserve unrelated changes.
- `.obsidian/` is ignored and should stay ignored.
- Keep book-specific facts inside `books/<book_id>/`.
- Keep reusable workflows, prompts, and validators inside `engine/` and `docs/`.
- Keep reusable craft knowledge inside `knowledge/`.

## What Not To Do

- Do not skip directly from idea to long-form drafting.
- Do not skip chapter brief, review, or human acceptance.
- Do not accept chapters based only on prose quality.
- Do not let market theory override confirmed canon.
- Do not overbuild UI, data feedback, or market agents before V3 memory is stronger.
- Do not use the urban sample as proof of target-genre quality.
