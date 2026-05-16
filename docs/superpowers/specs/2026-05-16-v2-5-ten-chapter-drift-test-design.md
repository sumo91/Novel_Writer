# V2.5 Ten-Chapter Drift Test Design

## Purpose

V2.5 proves that Novel Writer can carry one sample novel from chapter 3 through chapter 10 without losing continuity, state, or commercial pacing discipline.

This is a production-line pressure test, not a platform expansion. The test uses `books/sample_tomato_project` because the project already has accepted chapters 1 and 2, a prepared chapter 3 pipeline workspace, structured canon, review examples, and passing tests.

Execution details live in [V2.5 Ten-Chapter Drift Test Runbook](../../workflows/v2-5-ten-chapter-drift-test-runbook.md). The design explains what V2.5 proves; the runbook defines the per-chapter checklist, review-file requirements, quality gate, waiver format, and chapter-10 drift report template.

## Success Criteria

The drift test is successful when chapters 3 through 10 are accepted into the sample project and each accepted chapter has:

- An approved chapter brief.
- A chapter draft.
- A continuity review.
- A Tomato pacing review with dimension scores.
- A revised draft when required by the quality gate.
- A human-reviewed acceptance packet.
- An accepted chapter file under `chapters/`.
- Updated `state/current_state.json`.
- Updated `state/chapter_index.json`.
- Updated `canon/timeline.yaml`.
- Updated `canon/open_threads.yaml` when threads change.
- A `state/change_log.jsonl` entry.

After chapter 10, the system must support a drift review that can answer:

- Where is the protagonist physically, socially, and emotionally?
- What active conflicts are still open?
- Which foreshadowing threads were introduced, advanced, paid off, deferred, or dropped?
- Which chapter-level payoffs were delivered?
- Which pending approvals or unresolved canon questions remain?
- What should the next 10-chapter unit do?

## Scope

In scope:

- Run chapters 3 through 10 through the existing file-based pipeline.
- Strengthen the handoff and acceptance discipline around the current pipeline.
- Treat the Tomato pacing score as a real quality gate.
- Record explicit waivers when a weak chapter is accepted for strategic reasons.
- Keep all durable story truth in book-local files.
- Use the sample project to discover friction before building broader automation.

Out of scope:

- Web UI.
- Vector database or RAG.
- Market scraping.
- Real reader metric import.
- Full autonomous LLM orchestration.
- Multi-book dashboard.
- Replacing human approval.

## Quality Gate

Each chapter must receive a Tomato pacing review with a total score from 0 to 100.

Rules:

- Score 80 or higher: the chapter may proceed to acceptance if continuity passes and the human approves it.
- Score below 80: the chapter must be revised at least once before acceptance.
- Revised score still below 80: the chapter may only be accepted with an explicit human waiver recorded in the acceptance packet and change log.
- Continuity blocker: the chapter must be fixed before acceptance unless the human explicitly changes canon to make the chapter valid.
- Major canon change: must be listed in `human_approval_needed` before entering durable canon.

The gate is designed to prevent "good enough prose" from slipping into the canon when the chapter lacks hook, conflict, payoff, or next-chapter pull.

## Chapter Loop

For each chapter from 3 through 10:

1. Prepare or refresh the pipeline workspace with `prepare-chapter`.
2. Build or inspect the chapter context pack.
3. Create `outlines/chapter_briefs/ch_XXXX_brief.md`.
4. Draft `drafts/ch_XXXX_draft.md`.
5. Create `reviews/ch_XXXX/continuity_review.json`.
6. Create `reviews/ch_XXXX/pacing_review.json`.
7. Revise into `drafts/ch_XXXX_revised.md` when required by reviews or the quality gate.
8. Draft `state_updates/ch_XXXX_acceptance.yaml`.
9. Human reviews and edits the acceptance packet.
10. Run `pipeline-accept` with explicit approval.
11. Prepare the next chapter context.

The loop should stop after each accepted chapter long enough to inspect the updated state before drafting the next one.

## State Machine Fields To Watch

The current implementation already updates chapter index, current state, timeline, open threads, and change log. During the drift test, every acceptance packet should pay special attention to:

- `current_chapter`
- `current_arc`
- `latest_location`
- `active_characters`
- `active_conflicts`
- `pending_approvals`
- `state_changes`
- `open_threads_touched`
- `timeline_event`
- `open_thread_updates`
- `change_log.canon_updates`
- `change_log.pending_approvals`

If the sample reveals repeated omissions, those fields should become stricter templates or validators in a later implementation plan.

## Agent Responsibilities

The V2.5 test uses the existing prompt contracts rather than adding new agents first.

- Plot Planner: turns the current arc and state into a concrete chapter brief.
- Chapter Writer: writes only from the approved brief and context.
- Continuity Editor: checks canon, timeline, character state, and unsupported changes.
- Tomato Pacing Editor: scores commercial readability and identifies weak payoff or weak pull.
- Reviser: fixes approved review issues while preserving the chapter's useful intent.
- Human Showrunner: approves briefs, revised chapters, waivers, and canon updates.

The existing Showrunner prompt may be used manually when a chapter direction threatens the story promise, but it is not required in the default loop.

## Drift Review After Chapter 10

After chapter 10 is accepted, create a drift review report. The report should summarize:

- Chapter 1-10 event timeline.
- Character state table.
- Open thread table.
- Payoff and hook ledger.
- Pending approval list.
- Continuity risks.
- Pacing score trend.
- Recommended chapter 11-20 direction.

This report is the decision point for V3 long-form memory work. If the report is hard to produce from existing files, that is evidence that memory and indexing should be improved next.

## Testing

Before and after changes to the tooling, run:

```powershell
python -m pytest
```

During chapter production, use:

```powershell
python -m engine.cli validate-book sample_tomato_project
python -m engine.cli pipeline-status sample_tomato_project <chapter_number>
```

The test suite should remain green throughout the drift test.

## Implementation Notes For Later

This design does not require immediate code changes, but it suggests likely follow-up work:

- Add a pipeline command that validates pacing score thresholds.
- Add acceptance-packet fields for waiver reason and revised score.
- Add a drift-review report generator after chapter 10.
- Add stricter validators for review JSON and acceptance YAML.
- Add a richer current-state schema once repeated omissions are visible.

Those changes should be planned after the first manual V2.5 run exposes the real friction.
