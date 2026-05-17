# V3 Long-Form State Machine Design

## Purpose

V3 upgrades Novel Writer from a single-chapter pipeline into a file-based long-form state machine that can support 50 to 100 chapters without losing timeline, character state, resources, foreshadowing, payoff rhythm, or next-chapter obligations.

V2.6 already proves that chapters can move through brief, draft, review, revision, acceptance, and basic state updates. The remaining weakness is that much of the long-form memory still lives in free-text summaries and `state_changes` strings. V3 turns those implicit notes into explicit ledgers that validators, context packs, drift reports, and future agents can use.

## Success Criteria

V3 is successful when each accepted chapter must produce structured updates for:

- Current timeline and occurred events.
- Character state changes.
- Resource, wealth, power, and item changes.
- New or updated foreshadowing/open threads.
- Payoffs delivered in the chapter.
- Current conflicts.
- Next-chapter hook and obligation.
- Pending approvals.

After acceptance, the system must be able to answer these questions from files, without rereading the full manuscript:

- What changed in this chapter?
- Which characters changed state?
- Which resources, money, abilities, debts, or trade goods changed?
- Which promises or foreshadowing threads are open, stale, paid off, or risky?
- What did this chapter promise, and what did it pay off?
- Is the protagonist being held down too long without payoff?
- Which next-chapter hooks have not been answered?
- What should the next 10-chapter unit protect or resolve?

## Scope

In scope:

- File-based V3 ledgers using YAML, JSON, and JSONL.
- Stricter chapter acceptance packet schema.
- Template updates for new book projects.
- Lightweight migration for existing book projects.
- Validator updates for V3 fields.
- Context builder updates so future chapter packs include relevant V3 memory.
- Drift report updates to inspect foreshadowing, payoff, protagonist growth, hooks, and resource drift.
- A 10-chapter unit planning file layered above `arc_001.yaml`.

Out of scope:

- Web UI.
- Vector database or RAG.
- SQLite or external database storage.
- Market analysis agents.
- Reader simulator agents.
- Automated intelligent backfill from old chapter prose.
- Fully autonomous canon approval.

## Design Decisions

### 1. Keep V3 File-Based

V3 continues the current repository pattern:

- YAML for human-editable canon and planning ledgers.
- JSON for machine-facing current state and indexes.
- JSONL for append-only change logs.
- Markdown for reports and human-facing design documents.

This keeps each book portable and auditable. A later version can add RAG or a database once the file contracts are proven.

### 2. Acceptance Packets Are The State Update Contract

No chapter should update V3 memory through ad hoc writes. The acceptance packet remains the single reviewable contract between draft/review artifacts and durable story state.

The human showrunner can inspect, edit, approve, or reject the packet before it enters canon-facing files.

### 3. Migrate Lightly, Do Not Infer Canon

Existing projects should be migrated by creating missing V3 files and mechanically copying facts that already exist in accepted packets or indexes.

Migration must not parse old prose and invent structured canon. Ambiguous or inferred information should become a pending approval or a human TODO, not accepted truth.

## Book File Structure

V3 adds these book-local files:

```text
books/<book_id>/
  canon/
    open_threads.yaml
    character_states.yaml
    resource_ledger.yaml
    payoff_ledger.yaml
  outlines/
    units/
      unit_0001.yaml
  state/
    hook_index.json
    memory_index.json
```

Existing files remain in place:

```text
books/<book_id>/
  canon/
    timeline.yaml
    characters.yaml
    world_rules.yaml
  state/
    current_state.json
    chapter_index.json
    change_log.jsonl
    pending_approvals.yaml
  state_updates/
    ch_XXXX_acceptance.yaml
```

## V3 Acceptance Packet Schema

Each V3 acceptance packet should keep the existing V2 fields and add a required `v3_state_updates` mapping.

```yaml
chapter: 4
title: 回春丹铺带价来谈
source_draft: drafts/ch_0004_revised.md
accepted_chapter_path: chapters/ch_0004.md
summary: 本章摘要

current_state:
  current_chapter: 4
  current_arc: arc_001
  latest_location: 陈家小卖部
  active_characters:
    - 陈安
    - 许青
  active_conflicts:
    - 回春丹铺试图压价控制夜间小卖部货源
  pending_approvals: []

v3_state_updates:
  timeline:
    occurred_events:
      - id: ev_0004_01
        summary: 回春丹铺派人试探陈安的供货底线。
        location: 陈家小卖部后门
        involved_characters:
          - 陈安
          - 许青
        source_chapter: 4

  character_states:
    - character_id: chen_an
      physical_state: 正常
      social_state: 被回春丹铺注意，现实中仍有房租压力
      emotional_state: 警惕但更主动
      known_secrets:
        - 后门午夜开启一个时辰
      public_knowledge:
        - 许青知道陈安能提供细盐和夜明筒
      relationship_changes:
        - target: xu_qing
          change: 从单次交易转为可重复合作试探
      voice_notes: 不主动泄底，谈价时短句明确

  resource_changes:
    - owner: chen_an
      item: 现金
      delta: -300
      reason: 采购可交易货物
      source_chapter: 4
    - owner: chen_an
      item: 碎灵
      delta: 2
      reason: 回春丹铺试探交易
      source_chapter: 4

  open_thread_updates:
    - id: thread_0004_01
      promise: 回春丹铺想控制夜间货源
      source_chapter: 4
      status: open
      last_touched: 4
      next_obligation: 5章内必须展示对方施压或陈安反制
      payoff_deadline: 8
      risk_if_ignored: 第一阶段商业压力落空，异界线失去压迫感

  payoff_updates:
    - chapter: 4
      promises_made:
        - 回春丹铺会进一步出价或施压
      payoffs_delivered:
        - 陈安没有被丹铺一句话压住，反向要求对方带价
      frustration_level: controlled
      payoff_types:
        - 交易
        - 压价
        - 护住主动权
      delayed_payoffs:
        - 回春丹铺背后掌柜身份

  conflict_updates:
    active:
      - id: conflict_0004_01
        summary: 陈安需要在不暴露后门秘密的情况下与回春丹铺谈价
        pressure_type: 商业压迫
        source_chapter: 4

  next_hook:
    hook: 回春丹铺明晚是否带来真正筹码
    obligation: 下一章必须回应回春丹铺的报价或施压方式
    target_chapter: 5

  pending_approvals:
    - 是否确认回春丹铺成为1-10章阶段敌人。
```

## Open Threads Ledger

`canon/open_threads.yaml` should become a real foreshadowing and promise ledger, not just a list of loose notes.

Required fields per thread:

```yaml
threads:
  - id: thread_0001_01
    promise: 小卖部后门午夜通向青石坊
    source_chapter: 1
    status: open
    last_touched: 3
    next_obligation: 每隔数章展示规则限制或新风险
    payoff_deadline: 10
    risk_if_ignored: 核心卖点变成背景设定，失去持续期待
    related_characters:
      - chen_an
    related_locations:
      - 陈家小卖部
      - 青石坊
    payoff_chapter:
    notes: []
```

Allowed statuses:

- `open`
- `advanced`
- `paid_off`
- `deferred`
- `dropped`

V3 validators should flag stale open threads when `current_chapter` exceeds `payoff_deadline` and the status is still `open` or `advanced`.

## Payoff Ledger

`canon/payoff_ledger.yaml` tracks chapter-level reader promises and emotional delivery.

```yaml
entries:
  - chapter: 3
    promises_made:
      - 回春丹铺会找上门
    payoffs_delivered:
      - 黄芽草小额变现，现实房租压力得到短期缓解
    frustration_level: controlled
    payoff_types:
      - 赚钱
      - 交易
      - 揭谜
    delayed_payoffs:
      - 回春丹铺真实报价
    risks:
      - 回春丹铺压力如果迟迟不落地，会显得空喊
```

Allowed `frustration_level` values:

- `low`
- `controlled`
- `high`
- `overdue`

Validators should not decide literary quality, but they can flag mechanical risks:

- Multiple consecutive chapters with `high` or `overdue`.
- Repeated payoff types without variation.
- Promises made but never paid off or moved into open threads.

## Character State Ledger

`canon/character_states.yaml` records dynamic chapter-by-chapter character state, separate from `canon/characters.yaml`.

`characters.yaml` remains the stable profile: identity, role, motivation, long-term notes.

`character_states.yaml` records what changes:

```yaml
characters:
  chen_an:
    display_name: 陈安
    last_updated_chapter: 3
    physical_state: 正常
    social_state: 现实中被亲戚逼卖，异界中被回春丹铺注意
    emotional_state: 从被动守店转向主动谈价
    current_goal: 用两界交易保住小卖部并缓解债务
    known_secrets:
      - 后门午夜开启一个时辰
    public_knowledge:
      - 刘素芬知道陈安突然有钱补房租
      - 许青知道陈安能提供细盐和夜明筒
    relationship_changes:
      - chapter: 3
        target: xu_qing
        change: 建立可复购交易关系
    voice_notes:
      - 谈判时克制，不轻易露底
```

Validators should flag malformed entries, missing `last_updated_chapter`, and impossible chapter regressions. They should not attempt to infer emotional truth from prose.

## Resource Ledger

`canon/resource_ledger.yaml` tracks money, trade goods, power, debts, and important items.

```yaml
resources:
  - id: res_cash_chen_an
    owner: chen_an
    name: 现金
    category: money
    current_amount: 500
    unit: 元
    last_updated_chapter: 3
    history:
      - chapter: 3
        delta: 3000
        reason: 黄芽草叶尖小额变现
      - chapter: 3
        delta: -2500
        reason: 补交部分房租
```

Suggested categories:

- `money`
- `item`
- `trade_good`
- `power`
- `debt`
- `relationship_asset`
- `knowledge`

Drift reports should flag suspicious resource jumps, missing units, and repeated gains without corresponding cost or risk.

## Next Hook Index

`state/hook_index.json` tracks chapter-end hooks and whether later chapters answer them.

```json
{
  "hooks": [
    {
      "chapter": 3,
      "hook": "回春丹铺要求见夜里开门的陈掌柜。",
      "obligation": "第4章必须回应回春丹铺谈价或试探。",
      "target_chapter": 4,
      "status": "open",
      "answered_by_chapter": null
    }
  ]
}
```

Allowed statuses:

- `open`
- `answered`
- `deferred`
- `dropped`

## Memory Index

`state/memory_index.json` gives the context builder a cheap way to locate relevant older facts without loading the whole manuscript.

```json
{
  "by_character": {
    "chen_an": [1, 2, 3]
  },
  "by_thread": {
    "thread_0003_01": [3]
  },
  "by_location": {
    "陈家小卖部": [1, 2, 3],
    "青石坊": [1, 2]
  },
  "by_resource": {
    "碎灵": [2, 3],
    "黄芽草": [2, 3]
  }
}
```

This is not semantic retrieval. It is a deterministic index built from accepted state updates.

## 10-Chapter Unit Planning

V3 adds `outlines/units/unit_0001.yaml` above chapter briefs and below `arc_001.yaml`.

```yaml
unit: 1
chapter_range:
  start: 1
  end: 10
unit_goal: 陈安完成两界小卖部的第一轮交易闭环，并确立第一阶段商业敌人。
stage_enemy: 回春丹铺
stage_payoffs:
  - 现实债务得到短期缓解
  - 现代货物在修仙界的价值被验证
  - 陈安第一次守住谈判主动权
stage_end_hook: 回春丹铺背后更高层势力注意到小卖部
chapters:
  - chapter: 1
    function: 开局压力与后门奇遇
  - chapter: 2
    function: 第一笔交易与异界风险
  - chapter: 3
    function: 现实变现与丹铺压力引入
```

The unit file is a planning aid, not canon by itself. Accepted chapters still define durable truth.

## Context Builder Changes

V3 context packs should include:

- Current state.
- Chapter index summaries.
- Open threads due soon.
- Latest character states for active or relevant characters.
- Resource ledger entries touched recently or referenced by the chapter brief.
- Payoff ledger for the last 3 to 5 chapters.
- Open hooks whose target chapter is now due.
- Current 10-chapter unit plan.

The context builder should prefer concise relevant slices over dumping every ledger in full.

## Drift Report Changes

V3 drift reports should add checks for:

- Open threads past `payoff_deadline`.
- Hooks whose target chapter passed without answer.
- Consecutive chapters with high frustration and weak payoff.
- Repeated payoff types across a unit.
- Protagonist growth stalls.
- Character state contradictions or missing updates.
- Resource, wealth, power, or item inflation.
- Active conflicts that never advance.

The drift report should separate mechanical warnings from editorial judgment:

- Mechanical warning: a deadline, status, or amount is inconsistent.
- Editorial risk: the system sees a pattern that may weaken reader satisfaction.
- Human decision needed: the issue may be intentional and should be approved or deferred.

## Validation Rules

V3 validators should check:

- Required V3 acceptance packet sections exist.
- Thread statuses are valid.
- Thread deadlines are numeric or blank.
- Payoff entries have at least one promise or payoff.
- Payoff types come from an allowed list, with room for book-specific additions.
- Character state entries include `last_updated_chapter`.
- Resource entries include owner, category, current amount or descriptive state, and history.
- Hook statuses are valid.
- Memory index values reference accepted chapter numbers.
- Migrated books have all required V3 files.

Validation should be strict about structure and conservative about interpretation.

## Migration Strategy

Add a lightweight migration command for existing books.

Migration should:

- Create missing V3 ledger files from templates.
- Preserve existing `canon/open_threads.yaml` entries if present.
- Add missing fields to open threads with blank or conservative defaults.
- Create `outlines/units/unit_0001.yaml` if missing.
- Create empty `hook_index.json` and `memory_index.json` if missing.
- Mechanically backfill from accepted chapter indexes and acceptance packets where fields are explicit.
- Put uncertain inferred facts into pending approvals or TODO notes.

Migration should not:

- Parse old chapter prose to infer canon.
- Rewrite accepted chapters.
- Automatically decide character emotions, relationship meaning, or hidden plot intent.
- Convert every `state_changes` string into a structured fact unless the mapping is obvious.

## Human Approval Gates

V3 keeps the existing human approval model:

- Drafts are not canon.
- Reviews are not canon.
- V3 state updates are not canon until the acceptance packet is approved.
- Major premise, power-system, relationship, thread payoff, and resource escalation changes require human approval.
- Migration-generated uncertain facts must remain pending until approved.

## Implementation Targets

The implementation plan should modify or create these areas:

- Book templates under `engine/templates/book/`.
- Acceptance packet generation in `engine/acceptance_packet.py`.
- Chapter acceptance application in `engine/chapter_acceptance.py`.
- Validators in `engine/hardening.py` and `engine/validators.py`.
- Context pack construction in `engine/context_builder.py`.
- Drift report generation in `engine/drift_report.py`.
- CLI command wiring in `engine/cli.py`.
- New migration helper, likely `engine/v3_migration.py`.
- Tests for packet validation, acceptance application, context output, drift warnings, and migration.
- Documentation updates in `docs/workflows/` and `AGENTS.md` if command names or workflow gates change.

## Open Questions Resolved

- Storage: file-based, no database in V3.
- Retrieval: deterministic indexes, no vector RAG in V3.
- Migration: lightweight creation and mechanical backfill, no intelligent prose backfill.
- Scope: memory/state machine first, market and reader simulator later.
- Authority: human remains final showrunner and canon owner.
