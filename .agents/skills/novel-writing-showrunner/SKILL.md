---
name: novel-writing-showrunner
description: Use when helping a user develop, evaluate, plan, write, review, or continue a long-form web novel project in the Novel_Writer system; especially for novel ideation, book setup, chapter workflow decisions, drift review, canon/state approval, craft knowledge, or system evolution.
---

# Novel Writing Showrunner

Showrunner skill is the routing layer. It decides the current writing state, chooses the correct runbook, protects human approval gates, and keeps the conversation moving one clear step at a time.

Use `AGENTS.md` for non-negotiable repository rules. Use `docs/workflows/` for detailed steps. Use engine commands and validators for mechanical pass/fail.

## Core Rules

- The human is final showrunner and canon owner.
- Do not create prose unless the required upstream gates are approved.
- Do not create a new book, outline, chapter brief, or prose from a raw idea until the human approves a concept direction.
- Do not treat drafts, reviews, outline layers, craft contracts, style files, state updates, or pending approvals as canon until accepted or approved.
- State assumptions, offer 2-3 approaches when useful, and convert vague goals into observable success criteria.
- Ask one necessary question at a time.
- When an artifact needs approval, state exactly what would become canon and which files are involved.

## Route By State

Use the first matching state.

1. **Raw Idea**
   - Use `docs/workflows/v5-0-new-book-kickoff.md`.
   - Run the brainstorming gate in conversation: one question at a time, 2-3 options when helpful, then a compact concept direction for approval.
   - Do not create files until the human approves the concept direction.

2. **Concept Approved, No Book Project**
   - Create the book with `init-book`.
   - Then follow the new-book kickoff runbook: craft contract, craft-contract check, concept review, human review, outline package, style layer.

3. **Book Exists, Pre-Outline Or Outline Draft**
   - Use V3/V3.1 migration only when required.
   - Use `outline-status`, `outline-map-review`, and `outline-approval-packet` as described in the outline runbooks.
   - Do not treat draft outline layers as hard canon.

4. **Book Exists, Next Chapter Not Prepared**
   - Check `chapter-brief-gate` before brief work.
   - Confirm the active unit has a complete chapter map for its full range.
   - Prepare the chapter workspace and scaffold/check the chapter brief.
   - If a craft contract exists, ensure the brief includes `## Craft Alignment`.

5. **Brief Exists, No Draft**
   - Draft only from the approved or explicitly assumed context chain.
   - Open with scene pressure before exposition.
   - Preserve protagonist agency and concrete payoff.

6. **Draft Exists, Reviews Missing**
   - Write continuity and pacing reviews.
   - Treat new canon/state facts as proposed until acceptance.

7. **Reviews Exist, Revised Draft Missing**
   - Revise only what the brief and reviews require.
   - Do not broaden local fixes into premise, canon, relationship, style, or golden-finger changes without approval.

8. **Revised Draft Exists, Author Direction Or Prose Review Missing**
   - Scaffold or use lightweight author direction.
   - Write prose quality review with style alignment when style files exist and exposition-density checks for openings or new units.
   - Run the prose quality gate before final candidate.

9. **Final Candidate Or Acceptance Packet Stage**
   - Draft the acceptance packet from the final candidate.
   - Stop for explicit human acceptance before running `pipeline-accept`.
   - After acceptance, verify pipeline status and book validity.

10. **Accepted Range Completed**
   - Use drift report and pending-approval sync.
   - Prefer 3 accepted chapters for first readability/drift review, 5 for stronger proof, 10 for drift testing.

11. **Knowledge Ingestion**
   - Confirm reliable source text first: user notes, subtitles, downloaded subtitles, or local transcription.
   - Do not create cards from title, metadata, comments, danmaku, recommendation context, or guesswork.
   - Convert only practical principles into concise cards.

12. **Architecture Or System Evolution**
   - Compare the request against implemented files and commands.
   - Prefer reducing drift and clarifying ownership before adding new agents or dashboards.
   - Keep AGENTS as constitution, this skill as router, runbooks as detailed procedures, and engine/tests as validators.

## Key Runbooks

- New book kickoff: `docs/workflows/v5-0-new-book-kickoff.md`
- Craft contract and concept review: `docs/workflows/v4-9-craft-contract-and-concept-review.md`
- Chapter pipeline: `docs/workflows/v2-single-chapter-pipeline.md`
- Long-form outline architecture: `docs/workflows/v3-1-long-form-outline-architecture.md`
- Outline approval gate: `docs/workflows/v3-2-outline-approval-gate.md`
- Chapter brief contract: `docs/workflows/v3-3-chapter-brief-contract.md`

## Common Commands

```powershell
python -m engine.cli init-book <book_id> --title "<title>"
python -m engine.cli craft-contract-scaffold <book_id> --force
python -m engine.cli craft-contract-check <book_id>
python -m engine.cli concept-review <book_id>
python -m engine.cli outline-status <book_id>
python -m engine.cli outline-map-review <book_id>
python -m engine.cli outline-approval-packet <book_id> --layer master
python -m engine.cli chapter-brief-gate <book_id> <chapter>
python -m engine.cli prepare-chapter <book_id> <chapter>
python -m engine.cli chapter-brief-scaffold <book_id> <chapter>
python -m engine.cli chapter-brief-check <book_id> <chapter>
python -m engine.cli pipeline-status <book_id> <chapter>
python -m engine.cli pipeline-quality-gate <book_id> <chapter>
python -m engine.cli pipeline-prose-quality-gate <book_id> <chapter>
python -m engine.cli pipeline-draft-acceptance <book_id> <chapter> --title "<title>" --summary "<summary>"
python -m engine.cli pipeline-accept <book_id> <chapter> --approved
python -m engine.cli drift-report <book_id> --start <n> --end <m>
python -m engine.cli sync-pending-approvals <book_id>
python -m engine.cli validate-book <book_id>
python -m pytest -q
```

## Response Style

- Say what stage the project is in and what the next gate is.
- Ask at most one necessary question at a time.
- Prefer concrete options over abstract theory.
- Give the human a short reading order for review artifacts.
- Label recommended paths and tradeoffs; do not pretend every option is equal.
