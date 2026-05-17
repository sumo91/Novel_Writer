# V2.5 Ten-Chapter Drift Test Runbook

This runbook turns the V2.5 drift-test design into a repeatable execution protocol. Use it for `books/sample_tomato_project` while carrying chapters 3 through 10 through the V2 file-based pipeline.

The goal is not speed. The goal is to prove that each accepted chapter can preserve continuity, pacing discipline, and human editorial control.

## Entry Conditions

Before starting a chapter, confirm:

```powershell
python -m pytest
python -m engine.cli validate-book sample_tomato_project
python -m engine.cli pipeline-status sample_tomato_project <chapter_number>
```

For chapter 3, the expected starting status is `needs_brief` with `pipeline/ch_0003/context.md` present. For later chapters, prepare the workspace after the previous chapter is accepted:

```powershell
python -m engine.cli prepare-chapter sample_tomato_project <chapter_number>
```

Use `--force` only when intentionally refreshing a pipeline workspace after inspecting what will be replaced.

## Per-Chapter Definition Of Done

Each chapter from 3 through 10 is done only when all items are true:

- `outlines/chapter_briefs/ch_XXXX_brief.md` exists and has human approval.
- `drafts/ch_XXXX_draft.md` exists.
- `reviews/ch_XXXX/continuity_review.json` exists and has no unresolved blocker.
- `reviews/ch_XXXX/pacing_review.json` exists, includes `score`, includes all `dimension_scores`, and has a valid gate outcome.
- `drafts/ch_XXXX_revised.md` exists when any required fix, pacing score below 80, or approved review note requires revision.
- `state_updates/ch_XXXX_acceptance.yaml` has been reviewed and edited by the human.
- Any low-score waiver or contradiction waiver is explicitly recorded in both the acceptance packet and `change_log`.
- `python -m engine.cli pipeline-accept sample_tomato_project <chapter_number> --approved` has completed.
- `python -m engine.cli validate-book sample_tomato_project` passes after acceptance.
- The next chapter context is prepared or the run stops for a chapter-10 drift review.

## Review File Requirements

Continuity reviews use `engine/prompts/agents/continuity_editor.md` and must stay valid JSON:

```json
{
  "passed": false,
  "score": 0,
  "issues": [
    {
      "type": "timeline_conflict",
      "severity": "high",
      "evidence": "",
      "suggested_fix": ""
    }
  ],
  "required_fixes": [],
  "proposed_state_updates": [],
  "human_approval_needed": []
}
```

For V2.5, treat any issue with `severity` of `high` or any entry in `required_fixes` as a blocker unless the human explicitly changes canon or records a contradiction waiver.

Tomato pacing reviews use `engine/prompts/agents/tomato_pacing_editor.md` and must stay valid JSON:

```json
{
  "score": 0,
  "dimension_scores": {
    "hook_strength": 0,
    "conflict_clarity": 0,
    "protagonist_agency": 0,
    "emotional_payoff": 0,
    "pacing": 0,
    "character_consistency": 0,
    "continuity_safety": 0,
    "chapter_end_pull": 0,
    "mainline_relevance": 0,
    "fresh_information_or_expectation": 0
  },
  "strengths": [],
  "issues": [],
  "revision_priorities": [],
  "human_approval_needed": []
}
```

All scores are integers from 0 to 100 for the total score and 0 to 10 for each dimension score.

## Quality Gate

Apply this gate before drafting the acceptance packet:

```powershell
python -m engine.cli pipeline-quality-gate sample_tomato_project <chapter_number>
```

The command exits with `0` only when the gate passes. A nonzero exit means the chapter needs revision, a waiver, or review-file repair before acceptance.

| Condition | Required Action |
| --- | --- |
| Continuity review has no blockers and pacing score is 80 or higher | Proceed to human acceptance review. |
| Continuity review has blockers | Revise before acceptance, unless the human records a canon change or contradiction waiver. |
| Pacing score is below 80 | Revise at least once before acceptance. |
| Revised pacing score is still below 80 | Accept only with an explicit strategic waiver. |
| Major canon change is introduced | Add it to `human_approval_needed` and acceptance packet state fields before acceptance. |

Do not treat `pipeline-status` alone as the quality gate. It reports whether files exist; this runbook decides whether the contents are acceptable.

## Acceptance Packet Additions

The existing acceptance command tolerates extra YAML fields, so V2.5 quality audit data can be stored in the packet before acceptance. Add this block when relevant:

```yaml
quality_gate:
  continuity_passed: true
  continuity_blockers: []
  initial_pacing_score: 86
  revised_pacing_score:
  revision_required: false
  waiver:
    required: false
    type:
    reason:
    approved_by: human
```

When a waiver is used, also record it in:

```yaml
change_log:
  canon_updates:
  - "quality_gate: pacing waiver approved for chapter XXXX because ..."
  pending_approvals: []
```

For contradiction waivers, use a concrete note:

```yaml
quality_gate:
  waiver:
    required: true
    type: "contradiction"
    reason: "Human changed canon so the apparent contradiction is now authoritative."
    approved_by: human
```

## Acceptance Packet Checklist

Before running `pipeline-accept`, inspect these fields:

- `chapter`, `title`, `source_draft`, and `accepted_chapter_path`.
- `summary`, with the durable chapter outcome rather than process notes.
- `current_state.current_chapter`, `current_arc`, `latest_location`, `active_characters`, `active_conflicts`, and `pending_approvals`.
- `state_changes`, including character, resource, relationship, public-knowledge, and emotional-state changes.
- `open_threads_touched`, including advanced, introduced, paid off, deferred, or dropped threads.
- `timeline_event.id`, `when`, and `summary`.
- `open_thread_updates`, especially `status` and `latest_note`.
- `change_log.summary`, `canon_updates`, and `pending_approvals`.
- `quality_gate`, when a revision, waiver, or score threshold affected acceptance.

## Chapter Loop

For each chapter:

1. Prepare or inspect the pipeline workspace.
2. Read the context pack and prior chapter index.
3. Create and approve the chapter brief.
4. Draft the chapter.
5. Run continuity and Tomato pacing reviews.
6. Apply the quality gate.
7. Revise when required.
8. Draft the acceptance packet:

```powershell
python -m engine.cli pipeline-draft-acceptance sample_tomato_project <chapter_number> --title "Chapter Title" --summary "What changed in this chapter."
```

9. Edit the acceptance packet using the checklist above.
10. Accept the chapter:

```powershell
python -m engine.cli pipeline-accept sample_tomato_project <chapter_number> --approved
```

11. Validate the book and inspect the next status.

Stop after each accepted chapter long enough to confirm the updated state matches the intended story truth.

## Drift Review Report

After chapter 10 is accepted, create:

```text
books/sample_tomato_project/reports/ch_0001_0010_drift_review.md
```

Use this structure:

```markdown
# Chapter 1-10 Drift Review

## Event Timeline

| Chapter | Event | Durable State Change |
| --- | --- | --- |

## Character State

| Character | Physical State | Social State | Emotional State | Open Questions |
| --- | --- | --- | --- | --- |

## Open Threads

| Thread | Status | Last Touched | Next Obligation |
| --- | --- | --- | --- |

## Payoff And Hook Ledger

| Chapter | Hook | Payoff | Next-Chapter Pull |
| --- | --- | --- | --- |

## Pending Approvals

| Approval | Source Chapter | Decision Needed |
| --- | --- | --- |

## Continuity Risks

| Risk | Evidence | Recommended Fix |
| --- | --- | --- |

## Pacing Score Trend

| Chapter | Initial Score | Revised Score | Waiver |
| --- | --- | --- | --- |

## Chapter 11-20 Recommendation
```

If the report is hard to fill from existing files, record that friction in the report. That friction is evidence for V3 memory and indexing work.

## Exit Conditions

V2.5 is complete when:

- Chapters 3 through 10 are accepted.
- Every accepted chapter satisfies the per-chapter definition of done.
- The chapter 1-10 drift review report exists.
- `python -m pytest` passes.
- `python -m engine.cli validate-book sample_tomato_project` passes.
- Any discovered friction is listed as follow-up work rather than silently worked around.
