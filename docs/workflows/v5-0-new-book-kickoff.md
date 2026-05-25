# V5.0 New Book Kickoff

Use this workflow when starting a new long-form web novel from a raw idea.

This runbook is the detailed source of truth for new-book kickoff. `AGENTS.md` owns hard rules; the showrunner skill routes to this file; this file owns the step-by-step discussion and artifact sequence.

The goal is not to produce prose immediately. The goal is to turn a promising idea into an approved concept engine, then into an approved outline package.

## 1. Brainstorming Gate

Before creating files, run a staged conversation. Ask one question at a time and prefer 2-3 concrete choices when the human has not already decided.

Do not dump the full checklist into one message. Move through phases, summarize decisions, and ask for approval before implementation.

### Phase A: Reader Promise

Collect or infer:

- genre and subgenre;
- target reader;
- desired emotional payoff;
- first-page promise.

Clarify whether the reader mainly comes for leisure, humor, business growth, system upgrades, relationship warmth, exploration, face-saving, or another promise.

### Phase B: Protagonist Appeal

Collect or infer:

- protagonist fantasy;
- protagonist early appeal hook;
- core hook;
- opening likability risk.

Check for oiliness, cowardice without courage, greed without warmth, passivity, cruelty, entitlement, or emotional flatness before any redeeming value.

### Phase C: Golden Finger

Collect or infer:

- golden finger or system mechanism;
- necessity;
- uniqueness;
- what it grants;
- limits, costs, uncertainty, safety net, and upgrade path.

Make sure the mechanism does not become a same-button solution.

### Phase D: Repeatable Engine

Collect or infer:

- repeatable promise-payoff engine;
- first visible pressure;
- first payoff;
- what each gain costs or exposes.

For business or management stories, clarify goods, customers, supply, pricing, inventory, competition, risk, reputation, and how gains create new pressure.

### Phase E: First Three Chapters

Collect or infer:

- chapter 1 hook;
- chapter 2 proof that the mechanism works;
- chapter 3 payoff or escalation;
- visible payoff by chapter 3.

### Phase F: Humor And Tone

Collect or infer:

- tone mechanism;
- humor source;
- how lightness avoids erasing pressure.

Humor may come from contrast, transaction mismatch, system behavior, customer trouble, protagonist voice, relationship banter, operational accidents, or world-view collision.

### Phase G: Stage, Relationships, Long Direction, Taste

Collect or infer:

- first stage and which rules can be delayed;
- first supporting characters who challenge, misunderstand, recognize, depend on, or pressure the protagonist;
- first-volume problem;
- protagonist end-state direction;
- long mystery, antagonist pressure, business scale, or system evolution;
- narration weight, dialogue density, joke frequency, warmth, payoff intensity, and disliked patterns.

Offer 2-3 premise approaches and recommend one. Do not create files until the human confirms the direction.

The approval summary should include:

- reader promise;
- protagonist fantasy and appeal hook;
- golden finger design;
- repeatable engine;
- first pressure and first payoff;
- first-three-chapter promise;
- humor/tone source;
- first stage and first relationship pressures;
- long direction;
- open risks.

## 2. Book Project

After confirmation:

```powershell
python -m engine.cli init-book <book_id> --title "<title>"
```

Fill only minimum necessary book facts at this stage. Do not build a heavy lore bible before the concept engine is reviewed.

## 3. Craft Contract

Create and check the book-local craft contract:

```powershell
python -m engine.cli craft-contract-scaffold <book_id> --force
python -m engine.cli craft-contract-check <book_id>
```

Edit `books/<book_id>/craft/craft_contract.yaml` so it selects only the craft cards this book should actively obey.

The contract should answer:

- why this golden finger is necessary;
- why this protagonist uniquely fits it;
- how the protagonist becomes likable early;
- what repeatable engine can sustain chapters;
- how humor or lightness emerges from scene pressure;
- what payoff appears by chapter 3.

Keep the contract in `draft` until the human approves it.

## 4. Concept Review

Generate the review scaffold:

```powershell
python -m engine.cli concept-review <book_id>
```

Read first:

- `books/<book_id>/reports/concept_review.html`

Machine contract:

- `books/<book_id>/reports/concept_review.md`

Stop for human review. Do not proceed to long-form outline if the golden finger, protagonist appeal, repeatable engine, or first-three-chapter promise is still vague.

## 5. V3.1 Outline Package

After concept approval, draft:

- `outlines/master_outline.yaml`
- `outlines/volumes/volume_001.yaml`
- `outlines/arc_001.yaml`
- `outlines/units/unit_0001.yaml`

The active unit must include a complete chapter map for its full `chapter_range`. Each chapter needs:

- `chapter`
- `function`
- `opening_hook`
- `main_payoff`
- `next_hook`

Generate the human-readable approval packet:

```powershell
python -m engine.cli outline-approval-packet <book_id> --layer master
```

Use `outline-map-review` only as a mechanical diagnostic, not as approval.

## 6. Style Layer

After the concept engine is stable, draft or tune:

```powershell
python -m engine.cli style-bible-scaffold <book_id> --force
python -m engine.cli style-calibration-scaffold <book_id> --force
```

Or seed from a reusable profile:

```powershell
python -m engine.cli style-profile-list
python -m engine.cli style-bible-from-profile <book_id> <profile_id> --force
```

Keep style rules abstract, book-specific, and human-reviewable.

## 7. First Chapter Gate

Only after concept and outline approval:

```powershell
python -m engine.cli chapter-brief-gate <book_id> 1
python -m engine.cli prepare-chapter <book_id> 1
python -m engine.cli chapter-brief-scaffold <book_id> 1
python -m engine.cli chapter-brief-check <book_id> 1
```

If `craft/craft_contract.yaml` exists, the brief must contain `## Craft Alignment`.

## Stop Conditions

Stop and ask for human decision when:

- concept review has unresolved premise risks;
- craft contract would turn global theory into hard book rules without approval;
- outline layers are draft but the user wants strict canon;
- the unit chapter map is incomplete;
- the user asks for prose before the concept engine and outline package are ready.
