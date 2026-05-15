# AI Novel Writer Ultimate Roadmap

> This document describes the long-term target for the Novel Writer system. It is not the MVP implementation plan. Use it as the north star when deciding what to build, defer, or reject in later versions.

## 1. Vision

Build an AI-assisted long-form commercial fiction studio that can support million-word web novels with stable canon, controlled pacing, reusable craft knowledge, and human editorial authority.

The system should behave less like a chatbot and more like a digital writers' room:

- Human creators define taste, market intent, red lines, and final approval.
- AI agents provide scalable drafting, planning, reviewing, memory maintenance, and option generation.
- Canon, project state, reviews, and writing theory live in files and databases, not only in conversation history.
- Each novel is isolated as a project, while the writing engine and craft knowledge are reusable across novels.

The first target genre style is Tomato-style Chinese web fiction: strong opening hooks, clear emotional payoff, high readability, frequent chapter-level tension, and long-form continuity.

## 2. Core Principles

1. Human editorial control stays above automation.
   The system can suggest, draft, score, and revise, but humans approve core direction, major plot turns, canon changes, and publishing decisions.

2. Memory must be explicit.
   Long-form fiction cannot rely on model context alone. Characters, events, foreshadowing, timeline, power rules, relationship states, and unresolved promises must be stored in structured project files.

3. Agents need contracts, not vague roles.
   Each agent should have a clear input schema, output schema, quality bar, and responsibility boundary.

4. Write one chapter at a time, plan many chapters ahead.
   The system may maintain 10-chapter arcs, 100-chapter maps, and full-book outlines, but canon updates should happen after each accepted chapter.

5. Theory guides judgment, not obedience.
   Craft theory, genre patterns, and market observations should help agents generate and evaluate options. They should not become rigid rules that flatten the story.

6. Quality is produced through loops.
   A strong chapter is drafted, reviewed, scored, revised, and checked against canon. The system should expect revision rather than assuming first-pass generation is publishable.

7. Every version must be useful.
   Avoid building a large platform before the writing loop works. Each milestone should produce a usable improvement in planning, drafting, reviewing, or memory.

## 3. Final System Shape

The mature system has five layers.

### 3.1 Human Editorial Layer

Humans act as:

- Producer: chooses business goal, target platform, target audience, and publishing strategy.
- Showrunner: defines the story promise, protagonist appeal, long-term arc, and emotional taste.
- Editor: approves outlines, rejects weak chapters, adjusts pacing, and interprets reader data.
- Rights and risk owner: decides what content is acceptable for publication.

The UI should make human intervention easy at the points that matter:

- Approve or reject book concepts.
- Compare multiple openings.
- Approve volume and arc outlines.
- Review chapter scores and reviewer objections.
- Lock canon changes.
- Add human notes that agents must respect.

### 3.2 Agent Studio Layer

Agents are specialized workers. The mature studio may include:

- Market Analyst Agent: studies platform trends, reader expectations, title patterns, and genre movement.
- Concept Designer Agent: creates book concepts, hooks, protagonists, and selling points.
- Showrunner Agent: protects the story promise, protagonist fantasy, tone, and long-term direction.
- Plot Planner Agent: builds full-book outlines, volume outlines, arc plans, and chapter briefs.
- Chapter Writer Agent: writes the chapter draft from a strict brief and canon context.
- Continuity Editor Agent: checks timeline, character state, power rules, locations, and previous events.
- Tomato Pacing Editor Agent: checks hook strength, conflict clarity, emotional payoff, chapter rhythm, and cliffhanger quality.
- Character Voice Editor Agent: checks dialogue, motivation, relationship dynamics, and role consistency.
- Foreshadowing Editor Agent: tracks promises, clues, reveals, callbacks, and unresolved threads.
- Risk Editor Agent: checks platform-sensitive content, repetition, unsafe claims, and avoidable publishing risks.
- Reader Simulator Agent: reviews chapters from several target-reader personas.
- Reviser Agent: rewrites based on approved review notes while preserving canon.
- Memory Curator Agent: updates canon, state, timelines, summaries, and indexes after approval.
- Data Feedback Agent: interprets real or simulated performance data and proposes controlled adjustments.

The MVP should not implement all of these. It should begin with Showrunner, Plot Planner, Chapter Writer, Continuity Editor, Tomato Pacing Editor, and Reviser.

### 3.3 Memory And Canon Layer

Each book has its own project memory:

- Novel bible: premise, promise, tone, target reader, protagonist fantasy, forbidden directions.
- Character files: identity, motivation, relationship map, secrets, current state, voice notes.
- Timeline: absolute and relative event order.
- World rules: setting, power system, economy, organizations, technology, social rules.
- Open threads: unresolved mysteries, foreshadowing, promises, debts, revenge targets, emotional setups.
- Chapter summaries: what happened, what changed, what was promised next.
- Current state: latest known position of characters, resources, injuries, relationships, public knowledge, private knowledge.
- Review history: editor notes, scores, recurring weaknesses, rejected choices.

The long-term version can borrow ideas from an LLM wiki:

- Atomic notes for durable facts.
- Cross-links between characters, events, locations, and threads.
- Update logs so canon changes are traceable.
- Indexes that help agents retrieve only relevant context.
- Summaries at multiple levels: chapter, arc, volume, full book.

### 3.4 Craft Knowledge Layer

Reusable knowledge is shared across books but never allowed to overwrite book-specific canon.

Recommended knowledge areas:

- Tomato-style rhythm rules.
- Opening hook patterns.
- Chapter-level emotional payoff patterns.
- Genre pattern library.
- Reader persona library.
- Narrative theory notes.
- Common failure modes.
- Platform and compliance risk notes.
- Market observations with dates and confidence levels.

Knowledge entries should carry metadata:

- Scope: universal craft, platform-specific, genre-specific, temporary market observation.
- Confidence: high, medium, low.
- Date observed, when relevant.
- Examples or counterexamples, preferably abstracted rather than copied.
- Usage rule: generate ideas, review chapters, warn about risk, or enforce a hard constraint.

This prevents outdated or overgeneralized theory from misleading the agents.

### 3.5 Orchestration And Tooling Layer

The mature system should provide repeatable commands:

- Create a new book project.
- Generate several concepts.
- Create a book bible.
- Plan full book, volume, arc, or next 10 chapters.
- Generate a chapter brief.
- Draft a chapter.
- Run review agents.
- Revise a chapter.
- Update canon and state.
- Produce a chapter report.
- Search canon and chapter history.
- Export manuscript.

The first implementation should be CLI-based. A web UI can be added after the single-chapter pipeline works reliably.

## 4. Recommended Project Structure

The long-term structure should separate reusable engine files from individual book projects.

```text
Novel_Writer/
  engine/
    prompts/
      agents/
      shared/
    orchestrator/
    validators/
    memory/
    exporters/
    templates/

  knowledge/
    craft/
    tomato/
    genres/
    readers/
    risk/
    market/

  books/
    book_001/
      book.yaml
      canon/
      outlines/
      chapters/
      reviews/
      state/
      exports/

  docs/
    vision/
    specs/
    plans/
    decisions/
```

Each book should be portable. It should contain all story-specific material needed to resume writing later.

## 5. Canon Data Model

The system should converge toward structured files before adopting a database.

Recommended early formats:

- YAML for durable structured canon.
- Markdown for human-readable notes and theory.
- JSON for machine-generated reviews and pipeline state.

Suggested book files:

```text
books/<book_id>/
  book.yaml
  canon/
    novel_bible.yaml
    characters.yaml
    relationships.yaml
    world_rules.yaml
    timeline.yaml
    open_threads.yaml
    forbidden_rules.yaml
  outlines/
    master_outline.yaml
    volume_001.yaml
    arc_001.yaml
  chapters/
    ch_0001.md
  reviews/
    ch_0001/
      continuity_review.json
      pacing_review.json
      revision_notes.json
  state/
    current_state.json
    chapter_index.json
    change_log.jsonl
```

Later versions may add SQLite or a vector index, but only after the file-based workflow proves useful.

## 6. Chapter Pipeline

The mature chapter pipeline should be:

1. Load project state and relevant canon.
2. Retrieve recent chapter summaries and relevant older facts.
3. Generate or load the current chapter brief.
4. Draft the chapter.
5. Run continuity review.
6. Run pacing and payoff review.
7. Run optional voice, foreshadowing, risk, and reader-simulation reviews.
8. Create a revision instruction pack.
9. Revise the chapter.
10. Re-score the chapter.
11. Ask for human approval when scores or risks cross thresholds.
12. Commit accepted chapter to the project.
13. Update canon, timeline, open threads, current state, and chapter index.
14. Generate next-chapter handoff notes.

The core rule: no chapter becomes authoritative until its state updates are accepted.

## 7. Quality Control

Quality should be measured from several angles, not by one global score.

Recommended scores:

- Hook strength.
- Conflict clarity.
- Protagonist agency.
- Emotional payoff.
- Tomato pacing.
- Cliffhanger or next-chapter pull.
- Character consistency.
- Continuity safety.
- Canon change safety.
- Repetition risk.
- Reader confusion risk.

Suggested gate for early versions:

- Continuity blockers must be fixed.
- Pacing score below threshold triggers revision.
- Major canon changes require human approval.
- New long-term threads must be recorded.
- Any unresolved contradiction must be explicitly waived or corrected.

The system should preserve rejected drafts and reviews. Bad attempts are useful evidence for future tuning.

## 8. Human-AI Collaboration Model

The ideal collaboration loop is:

```text
Human defines direction
  -> Agents generate options
  -> Human chooses or edits direction
  -> Agents plan structure
  -> Human approves key beats
  -> Agents draft and review
  -> Human approves or requests revision
  -> Agents update memory
  -> System prepares the next step
```

Human attention should be concentrated on high-leverage decisions:

- Book concept.
- First 10 chapters.
- Main character fantasy.
- Major plot turns.
- Love interest or core relationship direction.
- Villain ladder.
- Power and resource escalation.
- Volume endings.
- Reader-data-driven pivots.

Low-leverage work can be delegated:

- Formatting files.
- Creating chapter summaries.
- Checking timeline details.
- Listing changed facts.
- Generating alternative beats.
- First-pass drafting.
- Mechanical review.

## 9. Version Roadmap

### V0: Documentation And Templates

Goal: make the project shape explicit.

Deliverables:

- Vision roadmap.
- MVP implementation plan.
- Book project template.
- Agent role definitions.
- Basic knowledge files.

Success criterion: a new book can be initialized manually from templates.

### V1: Manual CLI Writers' Room

Goal: support one chapter at a time with file-based memory.

Deliverables:

- CLI command to initialize a book.
- CLI command to build chapter context.
- Prompt templates for core agents.
- Manual copy/paste or API-assisted generation workflow.
- Review output templates.
- Canon update templates.

Success criterion: produce 3 to 10 chapters while preserving character state, timeline, and open threads.

### V2: Automated Single-Chapter Pipeline

Goal: orchestrate drafting, review, revision, and state update.

Deliverables:

- `run_chapter` command.
- Structured agent outputs.
- Review score gates.
- State update generator.
- Human approval checkpoints.
- Basic tests for file parsing and state updates.

Success criterion: generate and revise a chapter through the full pipeline with traceable outputs.

### V3: Long-Form Memory

Goal: reduce drift across 100+ chapters.

Deliverables:

- Multi-level summaries.
- Cross-linked canon notes.
- Retrieval by character, thread, location, and event.
- Change log.
- Contradiction detector.

Success criterion: agents can retrieve relevant old facts without loading the full manuscript.

### V4: Craft And Market Intelligence

Goal: improve commercial quality, not just continuity.

Deliverables:

- Craft knowledge library with metadata.
- Genre pattern library.
- Tomato-specific scoring.
- Reader simulator personas.
- Market observation notes with dates and confidence.

Success criterion: review agents provide useful, non-generic revision advice tied to project goals.

### V5: Production Workflow

Goal: support sustained drafting of a full novel.

Deliverables:

- 10-chapter planning loop.
- Batch outline tools.
- Export tools.
- Draft comparison.
- Review dashboard or rich reports.
- Metrics over time: scores, recurring issues, unresolved threads.

Success criterion: maintain a stable 50 to 100 chapter project with controlled drift.

### V6: Studio Platform

Goal: manage multiple books and richer human review.

Deliverables:

- Web UI or desktop UI.
- Multi-book dashboard.
- Agent run history.
- Canon browser.
- Timeline visualization.
- Thread tracker.
- Draft approval workflow.

Success criterion: one reusable system can support multiple independent novels without canon leakage.

### V7: Data Feedback Loop

Goal: adapt future writing based on real reader response.

Deliverables:

- Import of platform metrics or manually entered reader data.
- Comment clustering.
- Drop-off analysis.
- Hypothesis generation.
- Controlled story adjustment proposals.

Success criterion: system can propose targeted changes without blindly chasing noisy data.

## 10. MVP Boundary

The first build should only target V0 and the beginning of V1.

In scope:

- File structure.
- Book template.
- Core agent prompts.
- Basic knowledge files.
- A manual or semi-automatic chapter pipeline.
- Simple validation and review schemas.

Out of scope:

- Web UI.
- Full vector database.
- Automated market scraping.
- Full multi-agent concurrency.
- Publishing integration.
- Guaranteed bestseller optimization.

This boundary matters. The first question is not "can the system write a million words?" The first question is "can it write 10 chapters without losing the story?"

## 11. Risk Register

### Risk: Formulaic Writing

Cause: agents overuse pattern libraries.

Mitigation: treat theory as suggestions and review criteria, not mandatory templates. Require project-specific voice and protagonist fantasy.

### Risk: Canon Pollution Between Books

Cause: shared context or shared memory mixes facts from different projects.

Mitigation: strict book-level isolation. Shared knowledge may guide style, but only book-local canon defines truth.

### Risk: Outdated Market Knowledge

Cause: market observations decay quickly.

Mitigation: timestamp all market notes. Separate stable craft principles from temporary trend observations.

### Risk: Drift Through Unapproved State Updates

Cause: generated facts enter canon automatically.

Mitigation: all major canon changes require review, and state updates should be traceable.

### Risk: Agents Agree Too Easily

Cause: reviewers produce polite, generic approval.

Mitigation: reviewers must output issues, evidence, severity, and concrete fixes. Score gates should force revision when needed.

### Risk: Tooling Becomes The Project

Cause: building platform features before validating the writing loop.

Mitigation: keep early versions CLI-first and chapter-pipeline-first.

## 12. Decision Log

Current strategic decisions:

- Use a reusable engine plus isolated book projects.
- Start with a Python or Node CLI rather than a web platform.
- Store early memory in YAML, Markdown, JSON, and JSONL.
- Use an LLM-wiki-inspired memory layer for long-term canon maintenance.
- Build around chapter-level loops.
- Keep humans in charge of direction, canon approval, and publishing judgment.
- Optimize first for 10 stable chapters, then 100, then a million words.

## 13. North Star Test

When evaluating future work, ask:

1. Does this make long-form continuity more reliable?
2. Does this improve chapter-level commercial readability?
3. Does this preserve human editorial control?
4. Does this make each book more portable and recoverable?
5. Does this help agents use memory instead of hallucinating?
6. Does this move us closer to a reusable studio rather than a one-off prompt collection?

If the answer is no, defer it.
