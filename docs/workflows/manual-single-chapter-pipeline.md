# Manual Single-Chapter Pipeline

This workflow is the V1 writers' room loop. It keeps humans in charge while giving agents clear handoff material.

For the command-assisted V2 version, use `docs/workflows/v2-single-chapter-pipeline.md`.

## Steps

1. Initialize or validate the book.

```powershell
python -m engine.cli init-book demo --title "Demo Book"
python -m engine.cli validate-book demo
```

2. Build the chapter context pack.

```powershell
python -m engine.cli build-context demo 1 --output books/demo/state/ch_0001_context.md
```

3. Give the context pack to the Plot Planner prompt.

Use `engine/prompts/agents/plot_planner.md` and ask for a chapter brief.

4. Give the approved brief and context pack to the Chapter Writer prompt.

Use `engine/prompts/agents/chapter_writer.md` and ask for a draft.

5. Run continuity review.

Use `engine/prompts/agents/continuity_editor.md`. Save the JSON review under:

```text
books/demo/reviews/ch_0001/continuity_review.json
```

6. Run Tomato pacing review.

Use `engine/prompts/agents/tomato_pacing_editor.md`. Save the JSON review under:

```text
books/demo/reviews/ch_0001/pacing_review.json
```

7. Revise the chapter.

Give the draft and approved review notes to `engine/prompts/agents/reviser.md`.

8. Human approves the final draft and asks the CLI to draft a state update packet.

```powershell
python -m engine.cli draft-acceptance-packet demo 1 --title "Chapter Title" --source-draft drafts/ch_0001_revised.md --summary "What happened and what changed."
```

This creates:

```text
books/demo/state_updates/ch_0001_acceptance.yaml
```

The generated packet is a draft. Review and edit it before acceptance, especially:

- `current_state`
- `state_changes`
- `open_threads_touched`
- `timeline_event`
- `open_thread_updates`
- `change_log.pending_approvals`

Packet shape:

```yaml
chapter: 1
title: "Chapter Title"
source_draft: "drafts/ch_0001_revised.md"
accepted_chapter_path: "chapters/ch_0001.md"
summary: "What happened and what changed."
current_state:
  current_arc: "arc_001"
  latest_location: ""
  active_characters: []
  active_conflicts: []
  pending_approvals: []
state_changes: []
open_threads_touched: []
timeline_event:
  id: "t001"
  when: "Chapter 1"
  summary: ""
open_thread_updates:
- id: "thread_001"
  status: "advanced"
  latest_note: ""
change_log:
  summary: "Accepted chapter 1."
  canon_updates: []
  pending_approvals: []
```

9. Apply the approved acceptance packet.

```powershell
python -m engine.cli accept-chapter demo --update-file books/demo/state_updates/ch_0001_acceptance.yaml --approved
```

This copies the accepted draft into `chapters/`, updates `chapter_index.json`, updates `current_state.json`, appends or replaces the timeline event, updates open threads, and writes `change_log.jsonl`.

Use `--force` only when intentionally re-applying an already accepted chapter.

## Rule

No generated chapter becomes authoritative until the human approves both the chapter text and the acceptance packet.
