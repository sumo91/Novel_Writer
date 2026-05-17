# Chapter 0006 Context Pack

## Book Metadata

- Book ID: sample_tomato_project
- Title: 逆光重启
- Chapter: 6

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
  when: 三年前
  summary: 林照父亲因一场供应链融资欺诈破产，留下巨额债务。
- id: t002
  when: 一年前
  summary: 林照与周衍共同创办星阈科技，林照负责核心产品。
- id: t003
  when: 一个月前
  summary: 曜石资本提出 B 轮融资意向，但要求发布会数据必须足够亮眼。
- id: t004
  when: 第一章前夜
  summary: 林照发现演示数据被篡改，却被周衍反咬为项目负责人失职。
- id: t005
  when: 第 1 章
  summary: 林照被逼签署责任说明时首次触发逆光系统，随后取得秦暮雨提供的十分钟只读后台权限，并发现东澜医药验收未完成。
- id: t006
  when: 第 2 章
  summary: 林照在十分钟只读权限内确认客户未验收、演示账号登录设备异常和缓存清理请求，并将证据提交到发布会提问审核通道。
- id: t007
  when: 第 3 章
  summary: 林照将三项后台矛盾包装成风控问题投上发布会大屏，迫使周衍暂停发布会；秦暮雨公开要求保全日志，何盛随后要求会后见林照。
- id: t008
  when: 第 4 章
  summary: 何盛用顾问身份和补偿谈判试图压回发布会风波；林照识破追溯确认条款并拒绝联合口径，秦暮雨随后展示父亲旧案合同摘要中的相同结构。
- id: t009
  when: 第 5 章
  summary: 发布会恢复后，林照拆穿东澜补充说明的时间矛盾，让东澜代表承认发布会前未签正式验收；秦暮雨随后收到疑似东澜真实项目负责人关于被迫改口的私信。
```

## Open Threads

Source: `canon/open_threads.yaml`

```yaml
threads:
- id: thread_001
  type: betrayal
  status: advanced
  promise: 周衍如何篡改数据、为何急着赶走林照
  first_expected_payoff: 第 1-3 章
  latest_note: 第 5 章周衍试图用东澜补充说明覆盖未验收事实，但林照用版本时间和正式验收问题拆穿改口。
- id: thread_002
  type: system
  status: advanced
  promise: 逆光系统的触发条件和代价
  first_expected_payoff: 第 1 章
  latest_note: 第 5 章逆光提示状态说明话术偏移、签署时间和版本记录矛盾；仍不生成证据。
- id: thread_003
  type: long_arc
  status: advanced
  promise: 曜石资本与林照父亲旧案的关系
  first_expected_payoff: 第 8-15 章
  latest_note: 第 5 章客户改口压力链露出，但东澜私信和 legal_temp_02 仍需后续验证，不能直接证明何盛或曜石资本主谋身份。
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
- chapter: 4
  goal: "何盛在暂停窗口内提出口径交易，林照识破追溯确认条款，并从父亲旧案摘要中看到相同责任结构。"
- chapter: 5
  goal: "发布会恢复后，东澜医药代表的验收状态说明被临时改口，林照和秦暮雨追查改口压力来源。"
- chapter: 6
  goal: "林照拿到问题审核链路与素材缓存保全清单，发现有人试图把缓存清理归责给临时运维账号。"
- chapter: 7
  goal: "周衍反击，指控林照利用律师权限违规接触后台；林照必须证明自己没有篡改证据。"
- chapter: 8
  goal: "秦暮雨解释她接触旧案材料的来源，并带林照找到三年前追溯确认条款的经办人线索。"
- chapter: 9
  goal: "林照用逆光验证一份曜石资本风控备忘录，确认当前融资局与旧案共享同一类责任转移模板。"
- chapter: 10
  goal: "林照在董事会临时听证中保住证据链和产品署名权，同时确认何盛不是唯一操盘者，为下一阶段资本局埋钩。"
arc_goal: "让主角从背锅者变成掌握关键证据的人。"
main_conflict: "周衍和曜石资本要把数据造假的锅扣给林照，林照必须在发布会开始前找到反击证据。"
required_payoffs:
- "第一章末让主角看见反杀路径。"
- "前三章完成一次公开打脸。"
- "第 4-6 章把公开打脸后果转化为证据保全和责任条款博弈。"
- "第 7-10 章完成第二次身份翻盘：林照从闹事前员工变成不可绕开的证据链持有人。"
required_threads:
- "thread_001"
- "thread_002"
- "thread_003"
v2_5_mini_outline:
  purpose: "为第 5-10 章提供短程方向，降低 V2.5 漂移风险；具体章节仍以逐章 brief 和人工审批为准。"
  guardrails:
  - "不要在第 5-10 章直接坐实何盛为父亲旧案主谋，只推进证据和利益关系风险。"
  - "逆光系统仍只能提示可验证商业矛盾、合同漏洞、数据造假和利益关系，不能预测未来或凭空生成证据。"
  - "每章必须有一个清晰的商业压力场：发布会、客户验收、证据保全、权限合规、董事会或旧案调查。"
  - "系统代价优先围绕信任、权限、时间窗口和资源消耗展开，正式规则继续保留为 pending approval。"
  chapter_sequence:
  - chapter: 5
    title_direction: "验收改口"
    public_pressure: "发布会恢复，东澜医药代表被要求补充状态说明。"
    protagonist_move: "林照不抢话筒，要求说明保留版本记录和签署时间。"
    payoff: "发现客户说明存在临时改口痕迹，证明压力链还在运作。"
    end_hook: "东澜医药真实负责人私下发来一句：不是我们想改。"
  - chapter: 6
    title_direction: "临时账号"
    public_pressure: "星阈试图把缓存清理责任推给 ops_temp_07 临时运维账号。"
    protagonist_move: "林照核验权限申请链，发现临时账号需要高层二次授权。"
    payoff: "ops_temp_07 不是替罪羊终点，而是连接发布会控制台和资本风控账号的中间层。"
    end_hook: "授权记录显示二次审批时间早于周衍公开话术。"
  - chapter: 7
    title_direction: "反咬"
    public_pressure: "周衍指控林照借秦暮雨权限违规接触后台，试图让证据失效。"
    protagonist_move: "林照用只读日志和秦暮雨录音证明自己没有修改任何后台记录。"
    payoff: "林照保住证据合法性，秦暮雨正式从临时观察者变成风险共同体。"
    end_hook: "秦暮雨提出要查三年前旧案里的同一类权限签收记录。"
  - chapter: 8
    title_direction: "旧案摘要"
    public_pressure: "旧案线从私人记忆进入可核验材料。"
    protagonist_move: "林照和秦暮雨找到旧案合同摘要来源，确认追溯确认条款不是孤例。"
    payoff: "父亲旧案第一次从情绪伤口变成可验证商业结构。"
    end_hook: "旧案经办人名字与曜石早期风控名单出现交集。"
  - chapter: 9
    title_direction: "风控备忘录"
    public_pressure: "曜石资本内部备忘录出现，但真实性需要验证。"
    protagonist_move: "林照用逆光定位备忘录中的可验证矛盾，避免被假材料带偏。"
    payoff: "确认当前融资局与旧案共享责任转移模板，但仍未锁定最终操盘者。"
    end_hook: "模板编号指向一个比何盛更早的资本项目库。"
  - chapter: 10
    title_direction: "临时听证"
    public_pressure: "董事会临时听证决定林照、周衍和发布会事故的责任归属。"
    protagonist_move: "林照提交完整证据链，要求保留产品署名权和独立审计入口。"
    payoff: "林照从背锅者变成证据链持有人，周衍失去完全控场权。"
    end_hook: "听证后，林照收到父亲旧案经办人留下的第一条主动消息。"
```

## Current State

Source: `state/current_state.json`

```json
{
  "current_chapter": 5,
  "current_arc": "arc_001",
  "latest_location": "云栖会展中心发布会侧门与法务席",
  "active_characters": [
    "林照",
    "秦暮雨",
    "周衍",
    "何盛"
  ],
  "active_conflicts": [
    "东澜医药补充说明被证明创建于发布会暂停后，不能证明发布会前已完成验收",
    "东澜代表公开承认发布会开始前尚未签署正式验收确认",
    "legal_temp_02 上传了东澜补充说明文件，需要与 ops_temp_07 缓存清理账号区分追踪",
    "秦暮雨收到疑似东澜真实项目负责人的私信，称“不是我们想改”，但发送者身份尚未验证"
  ],
  "pending_approvals": [
    "逆光系统代价尚未定义；第 3 章出现“信任资源消耗”提示，需人类确认是否作为早期代价方向",
    "曜石资本复核账号 obsidian_capital_he01 目前只能作为轻微线索，不能直接证明何盛或曜石资本为主谋",
    "秦暮雨能够展示林照父亲旧案合同摘要的来源路径，需要后续解释",
    "“追溯确认”已作为当前融资局与三年前旧案的第一条结构性相似线索，需人类确认",
    "legal_temp_02 是否作为客户说明上传账号线索继续追踪，需人类确认",
    "东澜真实项目负责人私信可作为第 6 章入口，但需先验证身份，不能直接当作证据"
  ]
}
```

## Chapter Index

Source: `state/chapter_index.json`

```json
{
  "chapters": [
    {
      "chapter": 1,
      "title": "逆光",
      "path": "chapters/ch_0001.md",
      "summary": "发布会前二十分钟，林照被周衍逼签离职和责任文件。逆光系统首次触发，提示责任转移话术、伪造确认链和发布会话术存在可验证谎言。秦暮雨给林照十分钟只读后台权限，林照看到东澜医药验收未完成，与周衍公开话术冲突。",
      "state_changes": [
        "林照首次触发逆光系统。",
        "秦暮雨与林照形成临时证据交易。",
        "周衍公开说出高风险谎言。",
        "东澜医药验收未完成成为下一章验证入口。"
      ],
      "open_threads_touched": [
        "thread_001",
        "thread_002"
      ]
    },
    {
      "chapter": 2,
      "title": "十分钟",
      "path": "chapters/ch_0002.md",
      "summary": "林照用秦暮雨给的十分钟只读权限继续验证数据。东澜医药未完成验收，演示账号最后登录设备显示为 Zhou-Yan-MacBook，后台正在排队清理缓存。林照没有冲上台，而是把证据投进发布会提问审核通道，并发现复核账号疑似关联曜石资本。",
      "state_changes": [
        "林照确认东澜医药验收状态为未完成。",
        "林照发现 demo_admin 最后登录设备为 Zhou-Yan-MacBook。",
        "林照发现发布会控制台正在排队清理演示缓存。",
        "林照将第一组证据提交进提问审核通道。",
        "曜石资本相关复核账号 obsidian_capital_he01 首次露出。"
      ],
      "open_threads_touched": [
        "thread_001",
        "thread_002",
        "thread_003"
      ]
    },
    {
      "chapter": 3,
      "title": "提问上墙",
      "path": "chapters/ch_0003.md",
      "summary": "林照将东澜医药未验收、demo_admin 登录设备和缓存清理请求包装成风控问题投上发布会大屏，迫使周衍暂停发布会；秦暮雨公开要求保全日志，何盛随后要求会后见林照。",
      "state_changes": [
        "林照将证据从后台提交推进到发布会公开场域",
        "周衍无法继续用“系统状态更新延迟”完全压过东澜医药未验收问题",
        "秦暮雨以风控律师身份要求保全问题审核链路、素材缓存链路和演示账号日志",
        "发布会暂停五分钟，周衍第一次在公开场合失去节奏",
        "何盛要求会后十分钟内见林照"
      ],
      "open_threads_touched": [
        "thread_001",
        "thread_002",
        "thread_003"
      ]
    },
    {
      "chapter": 4,
      "title": "十分钟会面",
      "path": "chapters/ch_0004.md",
      "summary": "何盛在发布会暂停窗口内提出恢复林照顾问身份和补偿谈判，要求将公开问题定性为口径误会；林照识破临时协议中的追溯确认条款，拒绝配合联合口径，并从秦暮雨提供的旧案合同摘要中看到相同结构。",
      "state_changes": [
        "何盛提出恢复林照技术顾问身份和补偿谈判，条件是把公开问题定性为口径误会",
        "林照识破临时协议中的追溯确认条款，拒绝配合联合口径",
        "林照要求删除追溯确认条款、公开保全日志，并让东澜医药单独说明验收状态",
        "秦暮雨向林照展示父亲旧案合同摘要，追溯确认结构首次与旧案建立相似性",
        "V2.5 发现 arc_001 规划边界不足，需要第 4-10 章短程小纲"
      ],
      "open_threads_touched": [
        "thread_001",
        "thread_002",
        "thread_003"
      ]
    },
    {
      "chapter": 5,
      "title": "验收改口",
      "path": "chapters/ch_0005.md",
      "summary": "发布会恢复后，星阈试图用东澜医药补充说明将未验收问题改口为业务侧基本完成；林照通过版本记录和签署时间证明补充说明创建于发布会暂停后，并让东澜代表承认发布会前未签正式验收。",
      "state_changes": [
        "发布会恢复后，星阈以东澜医药补充说明试图将未验收问题改口为业务侧基本完成",
        "林照通过版本记录、创建时间和签署时间栏证明补充说明创建于发布会暂停后",
        "东澜代表公开承认发布会开始前未签署正式验收确认",
        "秦暮雨要求保全补充说明的版本记录、上传路径和沟通记录",
        "秦暮雨收到疑似东澜真实项目负责人的私信，提示改口存在外部压力"
      ],
      "open_threads_touched": [
        "thread_001",
        "thread_002",
        "thread_003"
      ]
    }
  ]
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
