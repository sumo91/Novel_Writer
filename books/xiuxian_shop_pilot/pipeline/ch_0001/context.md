# Chapter 0001 Context Pack

## Book Metadata

- Book ID: xiuxian_shop_pilot
- Title: 我家小卖部通修仙界
- Chapter: 1

## Story Bible

Source: `canon/novel_bible.yaml`

```yaml
premise: "陈安继承爷爷留下的破旧小卖部，本以为只剩债务和逼卖铺子的亲戚，没想到午夜仓库后门会通向修仙界坊市。他用现代小商品和修仙界低阶资源做交易，一边盘活现实小店，一边揭开爷爷当年留下这扇门的原因。"
platform_style: "tomato"
target_reader: "喜欢轻松修仙、两界倒卖、经营升级、低门槛爽点和小人物翻身的男频读者"
story_promise: "一个快倒闭的小卖部，靠每天一小时通往修仙界的后门，从一包盐、一只打火机开始，慢慢变成两界都离不开的神秘铺子。"
protagonist_fantasy: "主角不靠天生灵根，而靠现代常识、货源信息差和稳健交易，把小店一步步经营成现实与修仙界之间的安全据点。"
tone: "轻松、接地气、爽点清楚，危险存在但不压抑。"
main_conflict: "现实中小卖部面临债务、租金和亲戚逼卖；修仙界中主角没有灵力身份，必须在坊市规矩和修士贪念之间保住交易通道。"
long_term_goal: "守住小卖部，弄清爷爷留下后门和旧账本的秘密，把两界生意做成真正的立身之本。"
ending_direction: "陈安成为两界公认的店主，既不完全归属现实商业，也不完全依附修仙宗门，而是掌握自己的铺子和规则。"
hard_constraints:
  - "爽点要直给，交易价值必须容易理解。"
  - "小卖部后门每天午夜只开一个时辰。"
  - "第一阶段不要铺太多宗门和境界名。"
  - "主角可以谨慎，但必须主动做选择。"
human_notes:
  - "本项目是目标题材3-5章小样本，优先验证题材、爽点和V2.6流程。"
```

## Characters

Source: `canon/characters.yaml`

```yaml
characters:
  - id: chen_an
    name: "陈安"
    role: "主角，小卖部继承人"
    public_status: "刚接手爷爷留下的老旧小卖部，现实里被债务和亲戚逼到墙角"
    private_goal: "守住小卖部，弄清爷爷为什么留下这间店"
    strengths:
      - "谨慎"
      - "会算账"
      - "熟悉小商品进货和街坊人情"
    flaws:
      - "一开始缺乏底气"
      - "容易把风险先往坏处想"
    current_state: "尚未知道仓库后门通向修仙界"
  - id: grandpa_chen
    name: "陈守业"
    role: "陈安爷爷，已故店主"
    public_status: "街坊眼里守了一辈子小卖部的老人"
    private_goal: "未知"
    strengths:
      - "留下小卖部和一本旧账本"
    flaws: []
    current_state: "已去世，只通过账本、旧货架和后门规则影响剧情"
  - id: liu_sufen
    name: "刘素芬"
    role: "陈安大姑"
    public_status: "主张把小卖部低价卖掉还债"
    private_goal: "尽快把铺子变现，分掉陈守业留下的最后资产"
    strengths:
      - "会用亲情和现实压力逼人"
    flaws:
      - "短视"
    current_state: "正在逼陈安签转让协议"
  - id: xu_qing
    name: "许青"
    role: "修仙界第一位交易对象，炼气二层散修"
    public_status: "青石坊底层散修，靠跑腿和采药维持修炼"
    private_goal: "用最少灵石买到能救同伴或换钱的实用品"
    strengths:
      - "识货"
      - "警觉"
    flaws:
      - "不敢得罪坊市巡卫和丹铺"
    current_state: "尚未登场"
```

## Timeline

Source: `canon/timeline.yaml`

```yaml
events: []
```

## Open Threads

Source: `canon/open_threads.yaml`

```yaml
threads: []
```

## Relevant Outline

Source: `outlines/arc_001.yaml`

```yaml
arc_id: "arc_001"
title: ""
chapters: []
arc_goal: ""
main_conflict: ""
required_payoffs: []
required_threads: []
```

## Current State

Source: `state/current_state.json`

```json
{
  "current_chapter": 0,
  "current_arc": "arc_001",
  "latest_location": "",
  "active_characters": [],
  "active_conflicts": [],
  "pending_approvals": []
}
```

## Chapter Index

Source: `state/chapter_index.json`

```json
{
  "chapters": []
}
```

## Shared Knowledge References

- `craft/common-failure-modes.md`
- `craft/narrative-basics.md`
- `readers/tomato-reader-personas.md`
- `risk/content-and-quality-risks.md`
- `tomato/chapter-scoring.md`
- `tomato/opening-hooks.md`
- `tomato/style-rules.md`

## Agent Handoff Instructions

- Treat book-local canon as truth.
- Use shared knowledge as guidance, not as overriding canon.
- List assumptions and proposed canon changes separately.
- Major canon or state changes require human approval.
- Plan and draft only the requested chapter.
