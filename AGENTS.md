# Novel Writer Agent Guide

This repository is a file-based long-form web-novel engineering system. Treat it as a reusable writers' room, not a one-prompt story generator.

AGENTS.md is the constitution layer. It defines non-negotiable repository rules, authority boundaries, and canonical workflow entry points. Detailed steps belong in `docs/workflows/`; routing behavior belongs in `.agents/skills/novel-writing-showrunner/SKILL.md`; executable checks belong in `engine/` and tests.

## Use The Showrunner Skill

Use `$novel-writing-showrunner` whenever the user asks to:

- develop or evaluate a novel idea;
- choose a genre, premise, protagonist, hook, or selling point;
- create or continue a book project;
- decide the next writing workflow step;
- write chapter briefs, drafts, reviews, revised drafts, final candidates, or acceptance packets;
- review drift, pending approvals, canon, style, craft contracts, or long-form architecture;
- turn writing theory, courses, videos, or examples into reusable knowledge;
- discuss how the Novel_Writer system should evolve.

Prefer the repository-local skill at `.agents/skills/novel-writing-showrunner/SKILL.md`. Use the user-level skill only as a fallback when the repository-local file is missing or unreadable.

## Project Goal

Novel_Writer supports million-word commercial web fiction with explicit memory, controlled drift, reusable craft knowledge, and human editorial authority.

Current priority:

1. Keep the V2.6/V4.1 chapter pipeline stable.
2. Keep V3 state and V3.1 outline architecture stable.
3. Make V4.9 craft contracts and concept review the default new-book gate.
4. Only then expand market intelligence, reader simulation, dashboards, or data feedback.

Current project facts live in `docs/project_status.md`, not in this rulebook.

## Human Authority

- The human is the final showrunner and canon owner.
- Do not accept a chapter into `chapters/` without explicit human confirmation.
- Do not treat generated drafts, reviews, state updates, concept reviews, craft contracts, style files, outline layers, or pending approvals as canon until accepted or approved.
- Major premise, canon, power-system, golden-finger, relationship, style-contract, and long-arc changes require human approval.
- Do not ask for approval vaguely. State exactly what would become canon, which files would be accepted, and what remains unresolved.

## Workflow Authority

Use the runbook layer as the detailed source of truth:

- New book kickoff: `docs/workflows/v5-0-new-book-kickoff.md`
- Craft contract and concept review: `docs/workflows/v4-9-craft-contract-and-concept-review.md`
- Single chapter pipeline: `docs/workflows/v2-single-chapter-pipeline.md`
- Long-form outline architecture: `docs/workflows/v3-1-long-form-outline-architecture.md`
- Outline approval gate: `docs/workflows/v3-2-outline-approval-gate.md`
- Chapter brief contract: `docs/workflows/v3-3-chapter-brief-contract.md`

When AGENTS, skill, and runbook seem to overlap, follow this hierarchy:

1. AGENTS defines what must never be violated.
2. The showrunner skill decides which workflow applies.
3. The relevant runbook provides detailed steps.
4. Engine validators and tests decide mechanical pass/fail.

## Hard Gates

New books:

- Do not create files, outline, or draft prose from a raw idea until the human approves a concept direction.
- The concept direction must cover reader promise, protagonist appeal, golden-finger necessity and limits, repeatable engine, first-three-chapter promise, humor/tone source, first stage, first relationship pressures, long direction, style taste, and open risks.
- After approval, use `init-book`, then `craft-contract-scaffold`, `craft-contract-check`, and `concept-review`.
- Do not proceed to long-form outline until the concept review and craft contract have been reviewed by the human.

Outlines:

- Approved outline layers are hard constraints. Draft outline layers are labeled assumptions.
- Before chapter brief work, the active unit must map every chapter in its `chapter_range` with `chapter`, `function`, `opening_hook`, `main_payoff`, and `next_hook`.
- Use `outline-map-review` only as a mechanical diagnostic. Use `outline-approval-packet` for human-readable approval.

Chapters:

- Do not skip chapter brief, draft, continuity review, pacing review, revision, author direction, prose quality review, final candidate, acceptance packet, and human acceptance.
- Chapter briefs must include an anti-infodump opening plan.
- If `craft/craft_contract.yaml` exists, chapter briefs must include `## Craft Alignment`.
- Continuity blockers, pacing below 80, prose quality below 85, style violations, rejected style patterns, or exposition-density failures require revision or explicit human waiver.
- Acceptance packets must not contain stale placeholder text such as `TODO`, `draft_note`, `ready_for_acceptance`, or `pending human acceptance`.

State:

- Chapter acceptance updates durable state through acceptance packets, not ad hoc memory.
- New facts belong in state updates, canon files, or pending approvals as appropriate.
- Use batch pending-approval updates for multi-item triage.

## Book-Local Contracts

Book-local truth and contracts stay under `books/<book_id>/`:

- canon and state: `canon/`, `state/`
- outline layers: `outlines/`
- craft contract: `craft/craft_contract.yaml`
- style bible: `style/style_bible.yaml`
- style calibration: `style/calibration/style_calibration.yaml`

Reusable knowledge stays under `knowledge/`:

- craft cards: `knowledge/craft_cards/`
- style cards and profiles: `knowledge/style_cards/`, `knowledge/style_profiles/`
- system execution cards: `knowledge/system_cards/`

Book-local contracts are draft until the human approves them. Shared theory guides judgment but never overrides confirmed book canon.

## Knowledge Hygiene

Do not dump raw writing books, course transcripts, video notes, or long theory texts directly into `knowledge/`.

When the user provides theory material:

1. Confirm reliable source text first: user notes, public subtitles, downloaded subtitles, or local transcription.
2. Do not sediment knowledge from title, metadata, comments, recommendations, danmaku, or guesswork.
3. Keep raw subtitles, transcripts, and temporary downloads in `.tmp/` or reports, not directly in `knowledge/`.
4. Extract practical principles.
5. Convert them into concise knowledge cards with `id`, `scope`, `applies_to`, `use_when`, `principle`, `checks`, `failure_modes`, and `severity`.
6. Use cards during concept design, craft contracts, chapter briefs, reviews, and drift reports.

## Execution Discipline

Use `knowledge/system_cards/goal-driven-creative-execution.yaml` for creative and architecture work.

- State important assumptions and ambiguities before creating files, canon, outlines, or prose.
- Offer 2-3 reasonable approaches when intent is broad or underspecified.
- Prefer the simplest concept, system, outline, or contract that can prove the reader promise.
- Convert vague goals into observable success criteria before executing.
- Make targeted changes to canon, outline, style, and craft contracts; do not opportunistically rewrite unrelated story truth.
- Stop for human approval when a change would alter premise, canon, relationship direction, golden-finger rules, style contract, or long-arc obligations.

## Repository Practices

- Use `rg` / `rg --files` for search.
- Use `apply_patch` for manual edits.
- Do not revert user or other-agent changes unless explicitly asked.
- The worktree may be dirty; preserve unrelated changes.
- `.obsidian/` is ignored and should stay ignored.
- Keep book-specific facts inside `books/<book_id>/`.
- Keep reusable workflows, prompts, validators, and tests inside `engine/`, `docs/`, and `tests/`.

## What Not To Do

- Do not skip directly from idea to long-form drafting.
- Do not use a sample-chapter goal as the pre-outline reward for a new book.
- Do not accept chapters based only on prose quality.
- Do not let market theory override confirmed canon.
- Do not imitate a living author's distinctive style.
- Do not overbuild UI, data feedback, market agents, or workflow engines before current writing workflows have been exercised.
- Do not use `sample_tomato_project` as proof of target-genre quality.
