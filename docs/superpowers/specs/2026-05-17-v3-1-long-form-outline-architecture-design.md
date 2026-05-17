# V3.1 Long-Form Outline Architecture Design

## Purpose

V3 made accepted chapters durable by recording character states, resources, open threads, payoffs, hooks, and memory indexes. V3.1 adds the missing upstream control layer: long-form outline architecture. The system should know the book's opening, ending direction, three-act spine, volume goals, arc goals, unit goals, economy rules, and faction pressures before it asks an agent to write a chapter.

The goal is not to overbuild lore. The goal is to stop long-form drift by making every chapter serve an approved outline layer.

## Current State

Implemented:

- V2/V2.6 chapter pipeline: prepare, brief, draft, review, revise, acceptance packet, human approval, accept.
- V3 state machine: character state, resource ledger, payoff ledger, open threads, hook index, memory index, drift warnings.
- `xiuxian_shop_pilot` has accepted chapters 1-4 and a working V3 state update for chapter 4.

Weaknesses:

- `master_outline.yaml` is useful for premise validation but too thin for a long novel.
- Volume planning is embedded inside `master_outline.yaml`; there is no independent volume file.
- `arc_001.yaml` and `unit_0001.yaml` exist but are empty templates.
- There is no explicit economy model for fragments, goods, prices, margins, or reality/cultivation-world conversion.
- There is no faction map for pill shops, patrols, loose cultivators, shops, black markets, or future powers.
- Chapter briefs are not required to cite their master/volume/arc/unit obligations.
- Drift reports mostly inspect accepted state; they do not yet compare chapters against the long-form outline plan.

## Design Principles

1. **Bottom locked, top open**
   Lock the opening, ending direction, three-act structure, core rules, protagonist end-state, and major mystery answer direction. Leave chapter-level execution, minor characters, local reversals, and specific goods flexible.

2. **Outline before prose**
   New chapters should be prepared against approved outline layers. The agent should know which volume, arc, unit, open thread, and next hook it is serving.

3. **Files remain book-local**
   Story truth stays under `books/<book_id>/`. Reusable craft patterns stay in `knowledge/`. Repository rules stay in `AGENTS.md`.

4. **Approval gates apply above chapters**
   Master, volume, arc, unit, economy, and faction changes can be drafted, but they should not silently become writing constraints without human approval.

5. **No intelligent backfill**
   V3.1 may migrate older books by creating missing files and empty schemas. It must not parse old prose or infer a long-form outline from accepted chapters.

## New Outline Hierarchy

```text
canon/novel_bible.yaml
  -> outlines/master_outline.yaml
  -> outlines/volumes/volume_001.yaml
  -> outlines/arc_001.yaml
  -> outlines/units/unit_0001.yaml
  -> outlines/chapter_briefs/ch_0005_brief.md
  -> drafts/reviews/acceptance_packet
  -> V3 state machine ledgers
```

### `outlines/master_outline.yaml`

Purpose: full-book control.

Required fields:

```yaml
logline: ""
story_promise: ""
opening_state:
  protagonist: ""
  world: ""
  first_pressure: ""
  first_hook: ""
ending_state:
  protagonist: ""
  shop: ""
  two_world_order: ""
  final_emotional_image: ""
three_act_structure:
  act_1:
    chapter_range: ""
    function: ""
    major_turning_points: []
    act_climax: ""
  act_2:
    chapter_range: ""
    function: ""
    major_turning_points: []
    midpoint: ""
    act_climax: ""
  act_3:
    chapter_range: ""
    function: ""
    major_turning_points: []
    final_climax: ""
    ending: ""
protagonist_growth_curve:
  start: ""
  act_1_end: ""
  midpoint: ""
  act_2_end: ""
  end: ""
core_mystery:
  question: ""
  answer_direction: ""
  reveal_stages: []
core_rules_locked: []
volume_plan: []
major_turning_points: []
ending_direction: ""
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

Backward compatibility:

- Existing fields `logline`, `full_book_arc`, `volume_plan`, `major_turning_points`, and `ending_direction` remain valid.
- V3.1 validators should warn or error on missing new required fields only after migration has added the schema.

### `outlines/volumes/volume_001.yaml`

Purpose: a 30-80 chapter commercial-web-fiction stage.

Required fields:

```yaml
volume_id: volume_001
title: ""
chapter_range:
  start: 1
  end: 50
volume_goal: ""
reader_promise: ""
main_pressure:
  antagonist_or_force: ""
  pressure_type: ""
  escalation_path: []
protagonist_progress:
  start_state: ""
  end_state: ""
core_payoffs: []
major_reveal: ""
volume_climax: ""
ending_hook: ""
required_threads: []
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

### `outlines/arc_001.yaml`

Purpose: a 10-25 chapter plot arc.

Upgrade current schema to:

```yaml
arc_id: arc_001
title: ""
chapter_range:
  start: 1
  end: 20
parent_volume: volume_001
arc_goal: ""
main_conflict: ""
stage_enemy_or_pressure: ""
protagonist_move: ""
required_payoffs: []
required_threads: []
major_reveal_or_reversal: ""
exit_state: ""
chapters: []
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

### `outlines/units/unit_0001.yaml`

Purpose: 10-chapter tactical rhythm map.

Upgrade current schema to:

```yaml
unit: 1
chapter_range:
  start: 1
  end: 10
parent_arc: arc_001
unit_goal: ""
stage_enemy: ""
stage_payoffs: []
stage_end_hook: ""
required_threads: []
chapters:
  - chapter: 1
    function: ""
    opening_hook: ""
    main_payoff: ""
    next_hook: ""
    state_obligation: []
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

## New Canon Support Files

### `canon/economy.yaml`

Purpose: keep price, currency, value, margin, and conversion logic out of prose.

Required fields:

```yaml
currencies:
  - id: spirit_fragment
    name: 碎灵
    world: qingshifang
    tier: low
    purchasing_power_notes: []
real_world_money:
  currency: CNY
  pressure_points: []
price_index:
  - item: ""
    world: ""
    price: ""
    source_chapter: null
    confidence: draft
trade_rules:
  - rule: ""
    source: ""
locked_constraints: []
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

For `xiuxian_shop_pilot`, this should capture facts such as:

- one small yellow sprout grass sample produced CNY 3000;
- one low-end止血散 costs about two fragments;
- chapter 4 traded basic medical goods for 13 fragments;
- large-scale real-world monetization remains dangerous.

### `canon/factions.yaml`

Purpose: define social pressure and escalation routes.

Required fields:

```yaml
factions:
  - id: ""
    name: ""
    world: ""
    public_role: ""
    private_interest: ""
    current_pressure: ""
    escalation_path: []
    relationship_to_protagonist: ""
    source_chapter: null
approval:
  status: draft
  approved_by: ""
  approved_at: ""
  notes: []
```

For `xiuxian_shop_pilot`, initial factions include:

- 回春丹铺
- 青石坊巡卫
- 底层散修
- 现实亲戚/刘素芬
- 现实老街房东与街坊

## Approval Model

V3.1 does not need a separate approval engine for outline files in the first implementation. Use the existing pending approval system and file-level `approval` blocks.

Rules:

- `approval.status: draft` means the file exists but should not be treated as hard canon.
- `approval.status: approved` means context builder and drift report may treat the file as a writing constraint.
- Major changes to approved master/volume/arc/unit/economy/factions files should create pending approvals.
- Chapter briefs may reference draft outline layers, but must label them as draft assumptions.

## Context Builder Changes

Context packs should include:

- Story Bible
- Master Outline
- Current Volume
- Current Arc
- Current Unit
- Economy
- Factions
- Character States
- Open Threads
- Resource Ledger
- Payoff Ledger
- Hook Index
- Memory Index

Current volume/arc/unit selection can be simple:

- choose the first volume/arc/unit whose chapter range contains the requested chapter;
- fall back to existing `volume_001`, `arc_001`, `unit_0001` when range selection is unavailable.

## Validator Changes

Add outline validation that checks:

- required files exist;
- YAML roots are mappings;
- required fields are present;
- approval blocks have valid status: `draft`, `approved`, `rejected`, or `superseded`;
- chapter ranges contain start/end integers;
- unit chapters fit inside the unit range;
- arc parent volume exists when `outlines/volumes/` exists;
- chapter briefs after V3.1 include references to current arc/unit obligations.

Validation should be strict for schema shape but modest about story content. For example, it should catch missing `ending_state`, but it should not judge whether the ending is creatively strong.

## Drift Report Changes

Add a long-form outline section:

```text
## Outline Alignment
```

Warnings:

- current chapter is outside all approved unit ranges;
- active unit has empty `chapters`;
- chapter accepted without serving any required thread;
- next hook does not match unit or arc obligation;
- open thread deadline exceeds its planned arc/unit without status change;
- resource growth exceeds known economy constraints without a pending approval;
- repeated payoff type appears too often inside the same unit.

## Migration

Add a lightweight `migrate-v3-1` command or extend `migrate-v3` with V3.1 creation behavior.

Migration should:

- create `outlines/volumes/volume_001.yaml`;
- upgrade `master_outline.yaml` with new empty fields while preserving existing values;
- upgrade `arc_001.yaml` and `unit_0001.yaml` with new fields;
- create `canon/economy.yaml`;
- create `canon/factions.yaml`;
- mark all new outline/canon support files as `approval.status: draft`;
- never infer story facts from prose.

## `xiuxian_shop_pilot` Application

After V3.1 code and templates are in place, apply the architecture to `xiuxian_shop_pilot`:

1. Upgrade the master outline:
   - opening state;
   - ending state;
   - three-act structure;
   - protagonist growth curve;
   - core mystery answer direction.
2. Create first volume:
   - chapters 1-50;
   - goal: secure small shop, establish stable two-world trade, survive first faction pressure;
   - climax: Chen An defeats or neutralizes the first local trade lock-in attempt without becoming a pill-shop subordinate.
3. Fill `arc_001`:
   - chapters 1-20;
   - main conflict: first trading foothold versus pill shop/patrol pressure;
   - required payoffs: stable price index, first repeat customers, first real-world shop improvement, first clear clue about Grandpa Chen.
4. Fill `unit_0001`:
   - chapters 1-10;
   - every chapter gets a function, payoff, and hook.
5. Fill `economy.yaml` and `factions.yaml` with only facts confirmed through chapters 1-4 plus draft assumptions for chapter 5.
6. Run validation and drift report.
7. Only then write chapter 5 brief.

## Out Of Scope

- No UI.
- No RAG.
- No reader simulator.
- No market-data agent.
- No intelligent old-chapter backfill.
- No full power-system encyclopedia.
- No 100-chapter detailed map in this iteration.

## Success Criteria

V3.1 is successful when:

- new books contain master, volume, arc, unit, economy, and faction scaffolds;
- existing books can be migrated without inferred canon;
- `xiuxian_shop_pilot` validates with filled first long-form outline layers;
- chapter 5 context includes the approved outline hierarchy;
- drift report can warn about outline misalignment;
- the system can explain what chapter 5 must accomplish before any prose is drafted.
