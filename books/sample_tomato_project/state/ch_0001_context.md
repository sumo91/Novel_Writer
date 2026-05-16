# Chapter 0001 Context Pack

## Book Metadata

- Book ID: sample_tomato_project
- Title: 逆光重启
- Chapter: 1

## Story Bible

Source: `canon/novel_bible.yaml`

```yaml
premise: "被合伙人背刺的年轻产品经理林照，在公司发布会前夜得到一套只能验证商业谎言的黑箱系统。他要用一场公开演示夺回项目、揭开资本局中局。"
platform_style: "tomato"
target_reader: "喜欢都市逆袭、职场博弈、系统爽点和公开打脸的男频读者"
story_promise: "主角用专业能力和系统验证谎言，一步步反杀职场、资本和行业黑幕。"
protagonist_fantasy: "低谷中的聪明人不靠蛮力，而靠证据、判断和当众翻盘夺回尊严。"
tone: "快节奏、压迫感强、克制但有锋芒，爽点来自公开验证与智斗反转。"
main_conflict: "林照的项目被合伙人夺走，幕后投资方试图把他包装成失败替罪羊。"
long_term_goal: "建立一家真正透明的智能商业公司，同时查清父亲当年破产背后的资本骗局。"
ending_direction: "林照公开击穿行业最大的虚假估值联盟，完成事业与家庭名誉的双重翻盘。"
hard_constraints:
- "系统只能验证商业场景中的谎言、合同漏洞、数据造假和利益关系，不能直接预测未来。"
- "主角每次翻盘必须付出信息、时间、资源或信任成本。"
- "避免无脑降智反派，反派可以傲慢，但必须有现实利益逻辑。"
human_notes:
- "第一章只验证 V1 流水线，不追求长篇完整设计。"
```

## Characters

Source: `canon/characters.yaml`

```yaml
characters:
- id: lin_zhao
  name: "林照"
  role: "protagonist"
  age: 27
  public_identity: "星阈科技前产品负责人"
  current_state: "被合伙人架空，背负发布会失败责任，即将被迫签离职协议"
  desire: "夺回产品署名权，证明项目数据被篡改"
  pressure_point: "父亲当年因商业欺诈背债，林照极度厌恶虚假数据"
  voice: "冷静、短句、先观察再出手，情绪爆发时更克制"
- id: qin_muyu
  name: "秦暮雨"
  role: "ally"
  age: 29
  public_identity: "风控律师"
  current_state: "受林照父亲旧案牵连，暗中调查星阈科技投资方"
  desire: "找到资本造假链条的证据"
  pressure_point: "不轻易信任创业者"
  voice: "锋利、专业、会直接指出风险"
- id: zhou_yan
  name: "周衍"
  role: "rival"
  age: 31
  public_identity: "星阈科技联合创始人兼临时 CEO"
  current_state: "准备在发布会上夺走林照的产品成果"
  desire: "拿到下一轮融资，彻底清理林照"
  pressure_point: "害怕真实演示暴露数据造假"
  voice: "体面、傲慢、喜欢用规则压人"
- id: he_sheng
  name: "何盛"
  role: "hidden_antagonist"
  age: 45
  public_identity: "曜石资本合伙人"
  current_state: "幕后操盘星阈科技融资"
  desire: "把虚假增长包装成高估值退出"
  pressure_point: "与林照父亲旧案存在未公开关联"
  voice: "温和、缓慢、从不亲自威胁"
```

## Timeline

Source: `canon/timeline.yaml`

```yaml
events:
- id: t001
  when: "三年前"
  summary: "林照父亲因一场供应链融资欺诈破产，留下巨额债务。"
- id: t002
  when: "一年前"
  summary: "林照与周衍共同创办星阈科技，林照负责核心产品。"
- id: t003
  when: "一个月前"
  summary: "曜石资本提出 B 轮融资意向，但要求发布会数据必须足够亮眼。"
- id: t004
  when: "第一章前夜"
  summary: "林照发现演示数据被篡改，却被周衍反咬为项目负责人失职。"
```

## Open Threads

Source: `canon/open_threads.yaml`

```yaml
threads:
- id: thread_001
  type: "betrayal"
  status: "open"
  promise: "周衍如何篡改数据、为何急着赶走林照"
  first_expected_payoff: "第 1-3 章"
- id: thread_002
  type: "system"
  status: "open"
  promise: "逆光系统的触发条件和代价"
  first_expected_payoff: "第 1 章"
- id: thread_003
  type: "long_arc"
  status: "open"
  promise: "曜石资本与林照父亲旧案的关系"
  first_expected_payoff: "第 8-15 章"
```

## Relevant Outline

Source: `outlines/arc_001.yaml`

```yaml
arc_id: "arc_001"
title: "发布会前夜"
chapters:
- chapter: 1
  goal: "林照被逼签离职协议，逆光系统首次触发，发现发布会话术中隐藏的致命谎言。"
- chapter: 2
  goal: "林照借秦暮雨的律师身份拿到后台数据权限，准备公开验证。"
- chapter: 3
  goal: "林照在发布会上用真实客户日志反杀周衍。"
arc_goal: "让主角从背锅者变成掌握关键证据的人。"
main_conflict: "周衍和曜石资本要把数据造假的锅扣给林照，林照必须在发布会开始前找到反击证据。"
required_payoffs:
- "第一章末让主角看见反杀路径。"
- "前三章完成一次公开打脸。"
required_threads:
- "thread_001"
- "thread_002"
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
