# V2 Single-Chapter Pipeline

V2 organizes the V1 manual workflow into a repeatable local pipeline. It still does not call LLM APIs or generate chapters by itself. Humans or Codex create the brief, draft, reviews, revised chapter, author direction, prose quality review, and final candidate, then the CLI tracks what exists and applies approved state updates.

## What V2 Automates

- Creates a per-chapter workspace under `books/<book_id>/pipeline/ch_XXXX/`.
- Builds a chapter context pack.
- Creates agent handoff files for planning, writing, reviewing, and revision.
- Writes a manifest of expected chapter artifacts.
- Reports which artifacts are present or missing.
- Drafts an acceptance packet from the final candidate and review files.
- Applies the approved acceptance packet.

## What Humans Still Approve

- Chapter brief.
- Lightweight author direction notes.
- Final candidate chapter text.
- Review notes to act on.
- Acceptance packet contents.
- Any canon, timeline, thread, or state change.

## Commands

Prepare a chapter:

```powershell
python -m engine.cli prepare-chapter sample_tomato_project 3 --force
```

Check status:

```powershell
python -m engine.cli pipeline-status sample_tomato_project 3
```

After the revised draft and reviews exist, draft the acceptance packet:

```powershell
python -m engine.cli pipeline-quality-gate sample_tomato_project 3
```

Only proceed when the quality gate passes or the human has recorded an explicit waiver in the acceptance packet.

Add the V4.1 author-direction and prose-quality layer:

```powershell
python -m engine.cli author-direction-scaffold sample_tomato_project 3
python -m engine.cli pipeline-prose-quality-gate sample_tomato_project 3
```

Create `drafts/ch_0003_final_candidate.md` from the revised draft, prose quality review, and human direction. The human does not need to rewrite the whole chapter, but must approve the direction that the AI integrates.

```powershell
python -m engine.cli pipeline-draft-acceptance sample_tomato_project 3 --title "Chapter Title" --summary "What changed in this chapter."
```

After human review, accept the chapter:

```powershell
python -m engine.cli pipeline-accept sample_tomato_project 3 --approved
```

## Artifact Lifecycle

Expected files:

```text
pipeline/ch_XXXX/context.md
pipeline/ch_XXXX/manifest.json
pipeline/ch_XXXX/handoffs/*.md
outlines/chapter_briefs/ch_XXXX_brief.md
drafts/ch_XXXX_draft.md
reviews/ch_XXXX/continuity_review.json
reviews/ch_XXXX/pacing_review.json
drafts/ch_XXXX_revised.md
authoring/ch_XXXX_author_direction.yaml
reviews/ch_XXXX/prose_quality_review.json
drafts/ch_XXXX_final_candidate.md
state_updates/ch_XXXX_acceptance.yaml
chapters/ch_XXXX.md
```

## Force Flags

Use `--force` only when intentionally regenerating or reapplying an artifact:

- `prepare-chapter --force` replaces the pipeline workspace.
- `pipeline-draft-acceptance --force` replaces the acceptance packet draft.
- `pipeline-accept --force` replaces an already accepted chapter and updates the acceptance log entry.

## Approval Gate

`pipeline-accept` requires `--approved` because accepting a chapter writes to canon-facing project state. The flag is a deliberate friction point: review the chapter and acceptance packet before running it.
