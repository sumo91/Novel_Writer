# V3 Long-Form State Machine Workflow

V3 keeps the V2 chapter pipeline intact and adds explicit long-form memory ledgers. The brief, draft, continuity review, pacing review, revision, acceptance packet, and human approval gate still control chapter production. V3 makes the durable state changes more structured so future chapters can track character state, resources, hooks, open promises, and payoffs without relying on loose prose summaries.

## V3 Memory Files

V3 adds or upgrades these book-local files:

- `canon/character_states.yaml`
- `canon/resource_ledger.yaml`
- `canon/payoff_ledger.yaml`
- upgraded `canon/open_threads.yaml`
- `outlines/units/unit_0001.yaml`
- `state/hook_index.json`
- `state/memory_index.json`

These files are ledgers and indexes, not a replacement for human editorial judgment. Proposed updates become canon only after the acceptance packet is reviewed and accepted.

## Normal Chapter Flow

1. Prepare the chapter workspace.

```powershell
python -m engine.cli prepare-chapter <book_id> <chapter>
```

2. Write the normal V2 artifacts: chapter brief, draft, continuity review, pacing review, and revised draft.
3. Draft the acceptance packet.

```powershell
python -m engine.cli pipeline-draft-acceptance <book_id> <chapter> --title "<title>" --summary "<summary>"
```

4. Fill `v3_state_updates` in the acceptance packet. Record only facts created or changed by the chapter, including character-state changes, resource changes, open-thread updates, payoff updates, and the next hook.
5. Stop for human review. The revised chapter and acceptance packet remain proposed until the human approves them.
6. After explicit approval, accept the chapter.

```powershell
python -m engine.cli pipeline-accept <book_id> <chapter> --approved
```

7. Validate the book.

```powershell
python -m engine.cli validate-book <book_id>
```

8. After a sample or unit, run a drift report and review V3 warnings before continuing.

```powershell
python -m engine.cli drift-report <book_id> --start <start_chapter> --end <end_chapter>
```

## Migration

Run the V3 migration command for an older book before expecting V3 validators, context packs, or drift reports to use the new files:

```powershell
python -m engine.cli migrate-v3 <book_id>
```

Migration creates missing V3 files and upgrades empty schemas. It does not parse old prose, convert free-text `state_changes`, or infer canon. If old chapters imply useful character states, resources, hooks, or payoffs, record those as human-reviewed updates instead of letting migration invent them.

