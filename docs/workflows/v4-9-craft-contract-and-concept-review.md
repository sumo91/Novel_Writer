# V4.9 Craft Contract And Concept Review

V4.9 turns reusable craft cards into a book-local craft contract before prose work starts.

Use this when opening or re-anchoring a book:

```powershell
python -m engine.cli craft-contract-scaffold <book_id> --force
python -m engine.cli craft-contract-check <book_id>
python -m engine.cli concept-review <book_id>
```

## Contract Role

`books/<book_id>/craft/craft_contract.yaml` selects which shared craft cards matter for this book.

The contract records:

- approval status;
- concept focus, including genre, tone, golden finger, protagonist appeal, repeatable engine, and first-three-chapter promise;
- selected craft cards and whether each one is a hard rule, soft heuristic, or diagnostic;
- stage rules for concept review, chapter briefs, and reviews.

The YAML is the machine contract. The generated HTML sidecar is only a readable review copy.

## Workflow Use

`concept-review` uses the book craft contract to produce a pre-outline review scaffold. It asks for golden finger necessity, protagonist appeal, repeatable engine, tone engine, and first-three-chapter promise before the book concept is treated as ready.

`chapter-brief-scaffold` includes the book craft contract and a `## Craft Alignment` checklist when the contract has cards that apply to briefs.

`chapter-brief-check` requires `## Craft Alignment` whenever a book craft contract exists.

Chapter context packs and pipeline handoffs also include the book craft contract, so planning and review agents see the same book-local rules instead of relying only on global knowledge cards.

## Human Approval

The craft contract begins as `draft`. Do not treat it as a hard book constraint until the human approves its selected cards and concept focus.
