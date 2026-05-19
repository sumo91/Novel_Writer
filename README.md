# Novel Writer

Novel Writer is a file-based CLI writers' room for long-form AI-assisted web fiction. The first target is Tomato-style Chinese web fiction: strong hooks, clear emotional payoff, stable canon, and chapter-by-chapter continuity.

The system keeps reusable engine files separate from book projects. Shared prompts, templates, validators, and craft knowledge live in the engine and knowledge folders. Each novel lives under `books/<book_id>/` with its own canon, outlines, chapters, reviews, state, and exports.

The long-term direction is described in [AI Novel Writer Ultimate Roadmap](docs/vision/ultimate-novel-writer-roadmap.md).

## Quickstart

Install the package in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

Create a book project:

```powershell
python -m engine.cli init-book demo --title "Demo Book"
```

Validate the book structure:

```powershell
python -m engine.cli validate-book demo
```

Build a chapter context pack:

```powershell
python -m engine.cli build-context demo 1 --output books/demo/state/ch_0001_context.md
```

Apply an approved chapter acceptance packet:

```powershell
python -m engine.cli accept-chapter demo --update-file books/demo/state_updates/ch_0001_acceptance.yaml --approved
```

Draft an acceptance packet from a final draft and review files:

```powershell
python -m engine.cli draft-acceptance-packet demo 1 --title "Chapter Title" --source-draft drafts/ch_0001_revised.md --summary "What changed in this chapter."
```

Prepare and inspect a V2 chapter pipeline workspace:

```powershell
python -m engine.cli prepare-chapter demo 1
python -m engine.cli pipeline-status demo 1
python -m engine.cli pipeline-quality-gate demo 1
```

Use the V2 wrappers after the human-approved artifacts exist:

```powershell
python -m engine.cli pipeline-draft-acceptance demo 1 --title "Chapter Title" --summary "What changed in this chapter."
python -m engine.cli pipeline-accept demo 1 --approved
```

## V1 Manual Workflow

The first writing loop is manual and human-approved:

1. Build a chapter context pack.
2. Use `engine/prompts/agents/plot_planner.md` to create a chapter brief.
3. Use `engine/prompts/agents/chapter_writer.md` to draft the chapter.
4. Use `engine/prompts/agents/continuity_editor.md` and `engine/prompts/agents/tomato_pacing_editor.md` to review it.
5. Use `engine/prompts/agents/reviser.md` to revise from approved notes.
6. Draft an acceptance packet with `draft-acceptance-packet`.
7. Human reviews and edits the YAML packet.
8. Run `accept-chapter --approved` to copy the accepted chapter and update state/canon files.

See [Manual Single-Chapter Pipeline](docs/workflows/manual-single-chapter-pipeline.md) and [Human Approval Checkpoints](docs/workflows/human-approval-checkpoints.md).

For the command-assisted V2 loop, see [V2 Single-Chapter Pipeline](docs/workflows/v2-single-chapter-pipeline.md).

## Philosophy

Novel Writer is not a one-prompt novel generator. It is a structured workflow for a human-led digital writers' room:

- Humans approve story direction, major canon changes, and final chapters.
- Agents draft, review, revise, and maintain memory through explicit files.
- YAML stores durable canon and project state.
- Markdown stores prompts, theory, workflows, and readable context packs.
- JSON stores structured reviews and machine-facing state.

The first useful milestone is simple: write 10 chapters without losing the story.
