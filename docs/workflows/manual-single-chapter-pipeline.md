# Manual Single-Chapter Pipeline

This workflow is the V1 writers' room loop. It keeps humans in charge while giving agents clear handoff material.

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

8. Human approves the final draft.

Save the accepted chapter as:

```text
books/demo/chapters/ch_0001.md
```

9. Update canon and state.

Only accepted facts should enter canon, timeline, open threads, chapter index, and current state.

## Rule

No generated chapter becomes authoritative until the human approves both the chapter text and the resulting state updates.
