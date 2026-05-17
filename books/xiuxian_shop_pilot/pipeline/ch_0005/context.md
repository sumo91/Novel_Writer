# Chapter 0005 Context Pack

## Book Metadata

- Book ID: xiuxian_shop_pilot
- Title: 我家小卖部通修仙界
- Chapter: 5

## Outline Reference Chain

master -> volume_001 -> arc_001 -> unit_0001 -> chapter_0005

## Story Bible

Source: `canon/novel_bible.yaml`

```yaml
premise: "陈安继承爷爷留下的破旧小卖部，本以为只剩债务和逼卖铺子的亲戚，没想到午夜仓库后门会通向修仙界坊市。他用现代小商品和修仙界低阶资源做交易，一边盘活现实小店，一边揭开爷爷当年留下这扇门的原因。"
platform_style: "tomato"
target_reader: "喜欢轻松修仙、两界倒卖、经营升级、低门槛爽点和小人物翻身的男频读者"
story_promise: "一个快倒闭的小卖部，靠每天午夜开启一个时辰的修仙界后门，从一包盐、一只打火机开始，慢慢变成两界都离不开的神秘铺子。"
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

## Master Outline

Source: `outlines/master_outline.yaml`

```yaml
logline: 继承破旧小卖部的陈安，发现仓库后门每天午夜通往修仙界坊市，他从细盐、打火机和基础小商品开始做两界生意，在现实债务、亲戚逼卖、丹铺压价和坊市规矩夹缝中，把爷爷留下的小店盘成自己的立身之本。
story_promise: 小人物靠经营、定价、守边界和信息差，在两界商业压力中一点点把破店变成安全入口；每个阶段都要有交易兑现、规则升级、现实收益和爷爷旧线索。
full_book_arc: 第一阶段盘活小店并确认两界通道；第二阶段建立稳定货源和修仙界客户；第三阶段发现爷爷当年并非偶然守店，而是在替两界某个旧约收尾；终局陈安以店主身份制定自己的交易规矩。
opening_state:
  protagonist: 陈安继承爷爷陈守业留下的破旧小卖部，现实中被亲戚逼卖和房租债务压住。
  world: 现实老街小卖部与午夜后门外的青石坊同时存在；青石坊底层散修需要便宜实用货物，丹铺和巡卫掌握规则压力。
  first_pressure: 刘素芬等现实亲戚逼卖小店，房东催租；午夜后门开启后，许青用碎灵询问细盐和火折。
  first_hook: 仓库后门在午夜开启，门外不是后巷，而是青石坊。
ending_state:
  protagonist: 陈安从被动守店的负债继承人，成长为能制定两界交易规矩的店主。
  shop: 小卖部从破旧负资产变成稳定、安全、可控的两界交易入口。
  two_world_order: 陈安不依附单一丹铺或势力，而是建立按规矩交易、分层供货、风险隔离的两界小商业秩序。
  final_emotional_image: 陈安在午夜关门前合上爷爷旧账本，门外有人按新规矩排队，门内小店灯还亮着。
three_act_structure:
  act_1:
    chapter_range: 1-80
    function: 确认后门、完成基础交易闭环、守住小店，建立不出门、不签独家、不暴露仓库的第一套规矩。
    major_turning_points:
    - 第1章：后门通向青石坊。
    - 第2章：细盐、打火机、夜明筒换到碎灵和黄芽草。
    - 第3章：黄芽草现实小额变现，回春丹铺注意到货源。
    - 第4章：陈安拒绝丹铺独家，获得十三枚碎灵和青石坊价目半册。
    act_climax: 陈安中和或击退第一轮丹铺锁货压力，确认自己可以按店主规矩做两界生意。
  act_2:
    chapter_range: 81-260
    function: 扩大货品、客户和风险，揭开爷爷旧账本与青石坊旧交易规则，面对更高层势力的价格、保护和通道争夺。
    major_turning_points: []
    midpoint: 陈安发现爷爷当年不是偶然经营小卖部，而是长期处理两界交易旧约。
    act_climax: 两界入口暴露风险升级，陈安必须在现实与青石坊同时保店。
  act_3:
    chapter_range: 261+
    function: 回收爷爷旧约、通道来源和两界交易秩序，完成陈安从经营者到规则制定者的成长。
    major_turning_points: []
    final_climax: 陈安在两界多方压力下守住入口，拒绝成为任何势力后仓。
    ending: 小卖部成为陈安掌控下的安全交易点。
protagonist_growth_curve:
  start: 被债务和亲戚压迫，只想保住爷爷留下的小店。
  act_1_end: 学会用现代商品、价格表和交易边界建立第一套生意规则。
  midpoint: 能主动设计货品、客户和信息差，不再只等午夜门开。
  act_2_end: 能同时处理现实和修仙界势力压力，开始理解爷爷旧约。
  end: 成为能保护入口、客户和自己规矩的两界店主。
core_mystery:
  question: 爷爷陈守业为什么熟悉青石坊价格与青灯草交易，后门又为何只在小卖部午夜开启？
  answer_direction: 爷爷长期参与或守护两界交易旧约，小卖部不是偶然通门，而是旧规则的一处安全入口。
  reveal_stages:
  - 第1-4章：旧账本、价目半册和青灯草重合，证明爷爷熟悉青石坊。
  - 第5-20章：通过价目半册、赵掌柜和散修口碑确认爷爷当年留下的交易痕迹。
  - 后续：揭示后门来源、旧约代价和爷爷为何离开。
core_rules_locked:
- 后门每天午夜开启一个中国时辰，约两个小时。
- 陈安不出后门、不暴露仓库、不把小卖部变成任何势力后仓。
- 现代货物有价值，但显眼货物会带来巡卫、丹铺或更高势力风险。
- 碎灵是青石坊低阶交易货币单位。
locked_story_promises:
- opening_state
- ending_direction
- three_act_structure
- core_rules_locked
- protagonist_growth_curve.end
- core_mystery.answer_direction
open_story_spaces:
- chapter-level scene execution
- minor characters
- local reversals
- exact goods and trades
volume_plan:
- id: volume_001
  title: 午夜后门
  chapters: 1-50
  goal: 守住小卖部，建立稳定两界交易入口，熬过回春丹铺和巡卫带来的第一阶段商业压力。
  payoff: 陈安确认小卖部不是负资产，而是两界通道；他用价格、货品和规矩反制第一批压价者。
major_turning_points:
- 第1章：仓库后门通向修仙界坊市。
- 第2章：陈安完成第一笔两界交易。
- 第3章：现实变现和丹铺注意力同时出现。
- 第4章：陈安拒绝独家，获得价目半册和青灯草线索。
- draft 第5章：赵掌柜亲自来谈，陈安必须用价目半册和备货思路主动应对。
ending_direction: 陈安守住小卖部，并把它从爷爷留下的旧铺子变成两界交易的安全入口。
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - V3.1 long-form outline draft. Confirm before treating as hard canon.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Economy

Source: `canon/economy.yaml`

```yaml
currencies:
- id: spirit_fragment
  name: 碎灵
  world: qingshifang
  tier: low
  purchasing_power_notes:
  - 第4章：细盐、纱布、创可贴、碘伏棉签合计换得十三枚碎灵。
  - 第4章：回春丹铺莫账房开价细盐三枚碎灵、火折一枚碎灵、夜明筒十枚碎灵。
real_world_money:
  currency: CNY
  pressure_points:
  - 第3章：黄芽草叶尖小额变现三千元。
  - 第3章：陈安补交一个月部分房租二千五。
price_index:
- item: 黄芽草叶尖
  world: 现实
  price: CNY 3000 sample sale
  source_chapter: 3
  confidence: approved_fact
- item: 细盐
  world: 青石坊
  price: 3 spirit_fragment quoted by 回春丹铺莫账房
  source_chapter: 4
  confidence: approved_fact
- item: 火折/打火机
  world: 青石坊
  price: 1 spirit_fragment quoted by 回春丹铺莫账房
  source_chapter: 4
  confidence: approved_fact
- item: 夜明筒/手电筒
  world: 青石坊
  price: 10 spirit_fragment quoted by 回春丹铺莫账房
  source_chapter: 4
  confidence: approved_fact
- item: 基础医疗小商品组合
  world: 青石坊
  price: part of chapter 4 bundle worth 13 spirit_fragment total with salt and price
    booklet
  source_chapter: 4
  confidence: approved_fact
trade_rules:
- rule: 后门每天午夜开启一个时辰，约两个小时。
  source: approved project fact / chapters 1-2
- rule: 陈安当前底线：不出后门、不暴露仓库、不签独家、按次交易。
  source: chapter 4
- rule: 现实变现必须小额谨慎，不能公开大规模出售修仙界材料。
  source: chapter 3 pending-approved direction
locked_constraints:
- 现代显眼货物会触发青石坊巡卫风险。
- 大规模现实变现会触发现实侧怀疑。
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - Economy facts are drawn from accepted chapters 1-4; future purchasing power remains
    draft.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Factions

Source: `canon/factions.yaml`

```yaml
factions:
- id: huichun_pill_shop
  name: 回春丹铺
  world: qingshifang
  public_role: 青石坊丹药与伤药相关商铺。
  private_interest: 锁定陈安的无灵力实用货源，尤其细盐、夜明筒和基础医疗小商品。
  current_pressure: 莫账房已试探独家供货；赵掌柜将亲自谈判。
  escalation_path:
  - 莫账房带价试探。
  - 赵掌柜亲自压价或谈长期供货。
  - 可能借巡卫保护、坊市规矩或客户入口继续施压。
  relationship_to_protagonist: 第一阶段主要商业压力，不是盟友。
  source_chapter: 4
- id: qingshifang_patrol
  name: 青石坊巡卫
  world: qingshifang
  public_role: 盘查坊市异常物品和来路的规矩执行者。
  private_interest: 未知；当前至少会扣押无灵力发光物并追问来历。
  current_pressure: 夜明筒曾被巡卫扣下，现代货物风险已暴露。
  escalation_path:
  - 盘问许青。
  - 通过丹铺或市场传闻注意陈掌柜。
  - 未来可能试图追查货源入口。
  relationship_to_protagonist: 外部规则压力。
  source_chapter: 2
- id: low_level_loose_cultivators
  name: 底层散修
  world: qingshifang
  public_role: 青石坊低阶消费者，缺便宜实用物资。
  private_interest: 用较低成本解决盐、光源、小伤处理等实际问题。
  current_pressure: 许青已证明这类客户能带来交易和信息。
  escalation_path:
  - 从许青单点交易扩展到口碑客户。
  - 需求变多后会引来丹铺和巡卫关注。
  relationship_to_protagonist: 潜在客户与信息来源。
  source_chapter: 1
- id: real_world_relatives
  name: 刘素芬等现实亲戚
  world: real_world
  public_role: 陈安现实亲戚与逼卖压力来源。
  private_interest: 怀疑爷爷留下隐藏财产，想逼陈安卖掉或交出小店利益。
  current_pressure: 第3章继续怀疑陈安藏有爷爷遗产。
  escalation_path:
  - 逼卖小店。
  - 追问资金来源。
  - 未来可能引发现实侧保密风险。
  relationship_to_protagonist: 现实侧压力。
  source_chapter: 1
- id: old_street_landlord_neighbors
  name: 现实老街房东与街坊
  world: real_world
  public_role: 小卖部现实经营环境。
  private_interest: 关注租金、店铺是否继续经营和陈安资金来源。
  current_pressure: 房租催缴已迫使陈安进行黄芽草小额变现。
  escalation_path:
  - 租金压力。
  - 经营改善后引来询问。
  relationship_to_protagonist: 现实经营约束。
  source_chapter: 3
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - Faction map is V3.1 draft based on accepted chapters 1-4.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Timeline

Source: `canon/timeline.yaml`

```yaml
events:
- id: t001
  when: 第 1 章
  summary: 陈安继承爷爷留下的小卖部，现实中被亲戚逼卖和催租压迫；午夜仓库后门开启，门外通向青石坊，第一位灰袍散修用碎灵询问细盐和火折。
- id: t002
  when: 第 2 章
  summary: 陈安站在后门内完成第一笔两界交易，用细盐、打火机和手电筒换到两枚碎灵与黄芽草；许青带走夜明筒后被青石坊巡卫盘问，陈安意识到现代货物既能救命也会惹祸。
- id: t003
  when: 第 3 章
  summary: 陈安谨慎验证碎灵和黄芽草，将黄芽草叶尖小额变现并补交部分房租；许青午夜回来说夜明筒被巡卫扣下，回春丹铺盯上细盐和夜明筒，要求见夜里开门的陈掌柜。
- id: t004
  when: 第 4 章
  summary: 回春丹铺莫账房带价来谈，试图用巡卫保护和独家供货压住陈安；陈安坚持按次交易、不出门、不签独家，用细盐、纱布、创可贴和碘伏棉签换到十三枚碎灵与青石坊价目半册，并发现价目半册里的青灯草与爷爷旧账本十年前记录重合。
```

## Character States

Source: `canon/character_states.yaml`

```yaml
characters:
  chen_an:
    display_name: 陈安
    physical_state: 无伤，但谈判结束后手心出汗，压力明显
    social_state: 在回春丹铺面前初步建立按次交易、不签独家、不出门的陈掌柜形象
    emotional_state: 紧张但稳住底线，开始主动用规则反压对方
    current_goal: 守住后门秘密，拿到青石坊价格体系，准备应对赵掌柜亲自谈判
    known_secrets: &id001
    - 小卖部后门每天午夜开启一个时辰
    - 爷爷旧账本十年前记录过青灯草交易
    public_knowledge: &id002
    - 陈掌柜手里有细盐、纱布、创可贴、碘伏棉签等无灵力货物
    relationship_changes: &id003
    - 与许青从单纯交易推进到信息交换
    - 与回春丹铺进入按次交易但互相试探的关系
    voice_notes: &id004
    - 谈判时短句、算账、守边界，不解释现代知识原理过深
    last_updated_chapter: 4
    history:
    - display_name: 陈安
      physical_state: 无伤，但谈判结束后手心出汗，压力明显
      social_state: 在回春丹铺面前初步建立按次交易、不签独家、不出门的陈掌柜形象
      emotional_state: 紧张但稳住底线，开始主动用规则反压对方
      current_goal: 守住后门秘密，拿到青石坊价格体系，准备应对赵掌柜亲自谈判
      known_secrets: *id001
      public_knowledge: *id002
      relationship_changes: *id003
      voice_notes: *id004
      last_updated_chapter: 4
      chapter: 4
  xu_qing:
    display_name: 许青
    physical_state: 左手仍有巡卫勒伤痕迹
    social_state: 夹在回春丹铺与陈掌柜之间的底层散修/传话人
    emotional_state: 畏惧丹铺但对陈安守价和赠药棉产生佩服与感激
    current_goal: 避免得罪丹铺，同时继续保留从陈安处获取实用货物的机会
    known_secrets: &id005
    - 陈安不愿签独家，也不愿暴露货源
    public_knowledge: &id006 []
    relationship_changes: &id007
    - 接受陈安赠送的碘伏棉签和创可贴，并提供赵掌柜情报
    voice_notes: &id008
    - 说话谨慎，常压低声音提醒风险
    last_updated_chapter: 4
    history:
    - display_name: 许青
      physical_state: 左手仍有巡卫勒伤痕迹
      social_state: 夹在回春丹铺与陈掌柜之间的底层散修/传话人
      emotional_state: 畏惧丹铺但对陈安守价和赠药棉产生佩服与感激
      current_goal: 避免得罪丹铺，同时继续保留从陈安处获取实用货物的机会
      known_secrets: *id005
      public_knowledge: *id006
      relationship_changes: *id007
      voice_notes: *id008
      last_updated_chapter: 4
      chapter: 4
  mo_zhangfang:
    display_name: 莫账房
    physical_state: 无伤，携带算盘与回春丹铺账房身份登场
    social_state: 回春丹铺派出的谈判代表
    emotional_state: 表面客气，实际持续试探门、仓库、货源和陈安靠山
    current_goal: 为回春丹铺探明陈安货源价值，并尝试用独家供货锁定渠道
    known_secrets: &id009
    - 陈安不肯出门，也不肯让人看清仓库
    public_knowledge: &id010
    - 回春丹铺承认纱布、创可贴、碘伏棉签具备交易价值
    relationship_changes: &id011
    - 与陈安完成第一笔丹铺层面的按次交易
    voice_notes: &id012
    - 客气、慢压、用算盘和规矩施压
    last_updated_chapter: 4
    history:
    - display_name: 莫账房
      physical_state: 无伤，携带算盘与回春丹铺账房身份登场
      social_state: 回春丹铺派出的谈判代表
      emotional_state: 表面客气，实际持续试探门、仓库、货源和陈安靠山
      current_goal: 为回春丹铺探明陈安货源价值，并尝试用独家供货锁定渠道
      known_secrets: *id009
      public_knowledge: *id010
      relationship_changes: *id011
      voice_notes: *id012
      last_updated_chapter: 4
      chapter: 4
```

## Open Threads

Source: `canon/open_threads.yaml`

```yaml
threads:
- id: thread_0004_pill_shop_exclusive_pressure
  promise: 回春丹铺试图用巡卫保护和独家供货锁定陈安的异界货源。
  source_chapter: 4
  status: open
  last_touched: 4
  next_obligation: 第5章让赵掌柜亲自来谈，升级独家供货与长期供货压力。
  payoff_deadline: 6
  risk_if_ignored: 回春丹铺压力会显得虚弱，陈安立规矩的爽点无法继续兑现。
  history:
  - id: thread_0004_pill_shop_exclusive_pressure
    promise: 回春丹铺试图用巡卫保护和独家供货锁定陈安的异界货源。
    source_chapter: 4
    status: open
    last_touched: 4
    next_obligation: 第5章让赵掌柜亲自来谈，升级独家供货与长期供货压力。
    payoff_deadline: 6
    risk_if_ignored: 回春丹铺压力会显得虚弱，陈安立规矩的爽点无法继续兑现。
    chapter: 4
- id: thread_0004_grandpa_qingdengcao_record
  promise: 青灯草同时出现在青石坊价目半册和爷爷十年前旧账本中，暗示爷爷长期熟悉两界交易。
  source_chapter: 4
  status: open
  last_touched: 4
  next_obligation: 第5-6章继续通过旧账本或价目半册揭示爷爷当年交易规则。
  payoff_deadline: 8
  risk_if_ignored: 爷爷长线谜团会变成孤立彩蛋，削弱追读。
  history:
  - id: thread_0004_grandpa_qingdengcao_record
    promise: 青灯草同时出现在青石坊价目半册和爷爷十年前旧账本中，暗示爷爷长期熟悉两界交易。
    source_chapter: 4
    status: open
    last_touched: 4
    next_obligation: 第5-6章继续通过旧账本或价目半册揭示爷爷当年交易规则。
    payoff_deadline: 8
    risk_if_ignored: 爷爷长线谜团会变成孤立彩蛋，削弱追读。
    chapter: 4
```

## Resource Ledger

Source: `canon/resource_ledger.yaml`

```yaml
resources:
- id: res_chen_an_spirit_fragments
  owner: chen_an
  name: 碎灵
  category: money
  unit: 枚
  current_amount: 13
  history:
  - chapter: 4
    delta: 13
    reason: 第4章卖出细盐、纱布、创可贴和碘伏棉签所得
    owner: chen_an
    name: 碎灵
    category: money
    unit: 枚
  last_updated_chapter: 4
- id: res_chen_an_trade_goods_basic_medical
  owner: chen_an
  name: 基础医疗小商品库存
  category: trade_good
  unit: 批
  current_amount: -1
  history:
  - chapter: 4
    delta: -1
    reason: 卖出两卷纱布、十片创可贴、六支碘伏棉签，并赠许青一支碘伏棉签和一片创可贴
    owner: chen_an
    name: 基础医疗小商品库存
    category: trade_good
    unit: 批
  last_updated_chapter: 4
- id: res_chen_an_qingshifang_price_half_booklet
  owner: chen_an
  name: 青石坊废弃价目半册
  category: knowledge
  unit: 册
  current_amount: 1
  history:
  - chapter: 4
    delta: 1
    reason: 与莫账房交易时作为添头获得，可用于标尺化碎灵购买力
    owner: chen_an
    name: 青石坊废弃价目半册
    category: knowledge
    unit: 册
  last_updated_chapter: 4
```

## Payoff Ledger

Source: `canon/payoff_ledger.yaml`

```yaml
entries:
- chapter: 1
  promises_made: []
  payoffs_delivered:
  - 陈安继承爷爷留下的小卖部，现实中被亲戚逼卖和催租压迫；午夜仓库后门开启，门外通向青石坊，第一位灰袍散修用碎灵询问细盐和火折。
  frustration_level: controlled
  payoff_types: []
  delayed_payoffs: []
  risks: []
- chapter: 2
  promises_made: []
  payoffs_delivered:
  - 陈安站在后门内完成第一笔两界交易，用细盐、打火机和手电筒换到两枚碎灵与黄芽草；许青带走夜明筒后被青石坊巡卫盘问，陈安意识到现代货物既能救命也会惹祸。
  frustration_level: controlled
  payoff_types: []
  delayed_payoffs: []
  risks: []
- chapter: 3
  promises_made: []
  payoffs_delivered:
  - 陈安谨慎验证碎灵和黄芽草，将黄芽草叶尖小额变现并补交部分房租；许青午夜回来说夜明筒被巡卫扣下，回春丹铺盯上细盐和夜明筒，要求见夜里开门的陈掌柜。
  frustration_level: controlled
  payoff_types: []
  delayed_payoffs: []
  risks: []
- chapter: 4
  promises_made:
  - 赵掌柜明晚亲自来谈，回春丹铺会继续试探陈安长期供货能力。
  - 青灯草将连接爷爷旧账本和青石坊旧交易记录。
  payoffs_delivered:
  - 兑现第3章明晚带价来谈的钩子。
  - 陈安拒绝独家供货，建立按次交易、不出门、不卖门的初始规矩。
  - 陈安把纱布、创可贴和碘伏棉签卖出价值，获得十三枚碎灵和青石坊价目半册。
  - 许青提供赵掌柜信息，关系从单纯买货推进到信息中间人。
  frustration_level: controlled
  payoff_types:
  - 交易
  - 压价
  - 立规矩
  - 揭谜
  delayed_payoffs:
  - 赵掌柜亲自谈判
  - 爷爷旧账本与青石坊旧交易真相
  risks:
  - 第5章需要更强外部压力和主动进货兑现，避免连续谈判导致动作感不足
```

## Current Volume

Source: `outlines/volumes/volume_001.yaml`

Approval: approved.

```yaml
volume_id: volume_001
title: 午夜后门
chapter_range:
  start: 1
  end: 50
volume_goal: 守住小卖部，建立可重复、可定价、可隔离风险的两界交易模式，并在第一阶段不被回春丹铺、巡卫或现实亲戚夺走主动权。
reader_promise: 每几章都要有具体交易、现实收益、异界压力升级、陈安立规矩或爷爷旧线索。
main_pressure:
  antagonist_or_force: 回春丹铺、青石坊巡卫、现实亲戚与房租压力
  pressure_type: 商业压价 / 规则试探 / 入口保密 / 现实债务
  escalation_path:
  - 回春丹铺从许青传话到莫账房试探。
  - 赵掌柜亲自谈，试图锁定长期供货。
  - 巡卫和坊市规矩关注无灵力现代货物。
  - 现实亲戚继续怀疑陈安藏有爷爷遗产。
protagonist_progress:
  start_state: 被动继承小卖部，只想解决债务和保店。
  end_state: 建立第一套两界交易规矩，能主动选货、定价、拒绝独家和隔离风险。
core_payoffs:
- 第一笔交易闭环。
- 现实小额变现缓解房租。
- 拒绝丹铺独家，立下按次交易规矩。
- 通过价目半册初步建立青石坊价格标尺。
major_reveal: 爷爷旧账本与青石坊价目半册都出现青灯草，说明爷爷长期熟悉青石坊交易。
volume_climax: 陈安中和或击退回春丹铺第一轮锁货压力，在不暴露后门的前提下确立陈掌柜规矩。
ending_hook: 爷爷旧约和后门来源进入更高层势力视野。
required_threads:
- thread_0004_pill_shop_exclusive_pressure
- thread_0004_grandpa_qingdengcao_record
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - V3.1 volume draft for chapters 1-50.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Current Arc

Source: `outlines/arc_001.yaml`

Approval: approved.

```yaml
arc_id: arc_001
title: 第一套交易规矩
chapter_range:
  start: 1
  end: 20
parent_volume: volume_001
arc_goal: 从发现后门到建立第一套稳定交易边界：陈安要证明小卖部能赚钱，但不能被丹铺、巡卫或现实亲戚夺走主动权。
main_conflict: 两界货物有价值，但价值越明确，越会引来丹铺压价、巡卫盘查和现实怀疑。
stage_enemy_or_pressure: 回春丹铺赵掌柜线、青石坊巡卫规则、现实刘素芬/房租压力。
protagonist_move: 陈安从被动接客转为主动备货、分级售卖、按次交易、索要价格表并拒绝独家。
required_payoffs:
- 稳定价格标尺。
- 第一批复购或口碑客户。
- 小卖部现实经营改善。
- 爷爷旧账本线索推进。
required_threads:
- thread_0004_pill_shop_exclusive_pressure
- thread_0004_grandpa_qingdengcao_record
major_reveal_or_reversal: 青灯草和价目半册证明爷爷旧账本不是普通账本。
exit_state: 陈安拥有初步客户、价格表、备货策略和不签独家的店主规矩。
chapters: []
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - V3.1 arc draft; chapter functions live in unit_0001 first.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Current Unit

Source: `outlines/units/unit_0001.yaml`

Approval: approved.

```yaml
unit: 1
chapter_range:
  start: 1
  end: 10
parent_arc: arc_001
unit_goal: 完成后门发现、第一笔交易、现实收益、丹铺压力和陈安第一套交易规矩的建立。
stage_enemy: 回春丹铺与青石坊低阶规矩压力。
stage_payoffs:
- 后门钩子。
- 第一笔交易。
- 现实变现。
- 拒绝独家。
- 价格标尺。
- 爷爷旧线索。
stage_end_hook: 陈安从被动守门变成主动备货，准备面对更明确的坊市规则和爷爷旧约线索。
required_threads:
- thread_0004_pill_shop_exclusive_pressure
- thread_0004_grandpa_qingdengcao_record
chapters:
- chapter: 1
  function: 开局处境钩子；确立现实压力和午夜后门。
  opening_hook: 陈安继承破店，被亲戚逼卖和催租压住。
  main_payoff: 后门开启，青石坊散修许青登场询问细盐和火折。
  next_hook: 门外修仙界客户愿意用碎灵交易。
  state_obligation:
  - 记录后门开启。
  - 记录许青。
- chapter: 2
  function: 完成第一笔两界交易，明确后门时间规则和现代货物风险。
  opening_hook: 陈安试探细盐、打火机和夜明筒价值。
  main_payoff: 换到碎灵和黄芽草。
  next_hook: 夜明筒被巡卫注意。
  state_obligation:
  - 记录后门每天午夜一个时辰。
  - 记录碎灵和黄芽草。
- chapter: 3
  function: 现实收益兑现，并引出丹铺压力。
  opening_hook: 陈安验证黄芽草和碎灵价值。
  main_payoff: 黄芽草小额变现并补交房租。
  next_hook: 回春丹铺要求陈掌柜明晚带价来谈。
  state_obligation:
  - 记录黄芽草现实变现。
  - 记录回春丹铺注意货源。
- chapter: 4
  function: 丹铺第一次正式压价；陈安立按次交易规矩。
  opening_hook: 莫账房带价来谈，试图锁独家。
  main_payoff: 陈安拒绝独家，用基础医疗小商品换十三枚碎灵和价目半册。
  next_hook: 赵掌柜亲自来谈，青灯草连接爷爷旧账本。
  state_obligation:
  - 记录丹铺独家压力。
  - 记录青灯草旧线索。
  - 记录十三枚碎灵和价目半册。
- chapter: 5
  function: draft：赵掌柜亲自压价，陈安用价目半册和备货策略反守为攻。
  opening_hook: 赵掌柜亲自来谈。
  main_payoff: 陈安进一步确立不签独家、不出门、按次交易的店主规矩。
  next_hook: 价目半册或旧账本给出下一种关键货物线索。
  state_obligation:
  - 推进 thread_0004_pill_shop_exclusive_pressure。
  - 推进 thread_0004_grandpa_qingdengcao_record。
- chapter: 6
  function: draft：把谈判压力转成主动采购和第二轮交易。
  opening_hook: 陈安按价目半册筛选现实可替代货。
  main_payoff: 出现第一批明确复购或新客户。
  next_hook: 巡卫或坊市规则压力靠近。
  state_obligation:
  - 建立更清晰价格标尺。
- chapter: 7
  function: draft：现实亲戚/房租压力回压，让异界收益必须落到现实经营。
  opening_hook: 刘素芬或房租压力再度出现。
  main_payoff: 陈安用合规小额收益改善小店。
  next_hook: 现实侧有人怀疑爷爷遗产来源。
  state_obligation:
  - 记录现实压力变化。
- chapter: 8
  function: draft：爷爷旧账本线推进，青灯草不再只是彩蛋。
  opening_hook: 旧账本和价目半册出现第二处重合。
  main_payoff: 陈安确认爷爷曾长期按某套规矩交易。
  next_hook: 某个旧名号或旧价码浮出。
  state_obligation:
  - 推进爷爷旧账本长线。
- chapter: 9
  function: draft：丹铺或巡卫施加更直接风险，测试陈安规矩。
  opening_hook: 有人试图绕过许青或直接找门。
  main_payoff: 陈安守住不暴露仓库边界。
  next_hook: 第一阶段更大冲突逼近。
  state_obligation:
  - 更新入口保密风险。
- chapter: 10
  function: draft：10章小单元收束，形成第一套可持续交易流程。
  opening_hook: 多方压力同时指向陈安货源。
  main_payoff: 陈安完成第一套小店交易规矩和备货闭环。
  next_hook: 进入更大范围客户/势力压力。
  state_obligation:
  - 总结第一单元资源、客户、规则和未回收伏笔。
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - Chapters 1-4 are anchored to accepted facts; chapters 5-10 are draft planning
    assumptions.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Unit Plan

Source: `outlines/units/unit_0001.yaml`

```yaml
unit: 1
chapter_range:
  start: 1
  end: 10
parent_arc: arc_001
unit_goal: 完成后门发现、第一笔交易、现实收益、丹铺压力和陈安第一套交易规矩的建立。
stage_enemy: 回春丹铺与青石坊低阶规矩压力。
stage_payoffs:
- 后门钩子。
- 第一笔交易。
- 现实变现。
- 拒绝独家。
- 价格标尺。
- 爷爷旧线索。
stage_end_hook: 陈安从被动守门变成主动备货，准备面对更明确的坊市规则和爷爷旧约线索。
required_threads:
- thread_0004_pill_shop_exclusive_pressure
- thread_0004_grandpa_qingdengcao_record
chapters:
- chapter: 1
  function: 开局处境钩子；确立现实压力和午夜后门。
  opening_hook: 陈安继承破店，被亲戚逼卖和催租压住。
  main_payoff: 后门开启，青石坊散修许青登场询问细盐和火折。
  next_hook: 门外修仙界客户愿意用碎灵交易。
  state_obligation:
  - 记录后门开启。
  - 记录许青。
- chapter: 2
  function: 完成第一笔两界交易，明确后门时间规则和现代货物风险。
  opening_hook: 陈安试探细盐、打火机和夜明筒价值。
  main_payoff: 换到碎灵和黄芽草。
  next_hook: 夜明筒被巡卫注意。
  state_obligation:
  - 记录后门每天午夜一个时辰。
  - 记录碎灵和黄芽草。
- chapter: 3
  function: 现实收益兑现，并引出丹铺压力。
  opening_hook: 陈安验证黄芽草和碎灵价值。
  main_payoff: 黄芽草小额变现并补交房租。
  next_hook: 回春丹铺要求陈掌柜明晚带价来谈。
  state_obligation:
  - 记录黄芽草现实变现。
  - 记录回春丹铺注意货源。
- chapter: 4
  function: 丹铺第一次正式压价；陈安立按次交易规矩。
  opening_hook: 莫账房带价来谈，试图锁独家。
  main_payoff: 陈安拒绝独家，用基础医疗小商品换十三枚碎灵和价目半册。
  next_hook: 赵掌柜亲自来谈，青灯草连接爷爷旧账本。
  state_obligation:
  - 记录丹铺独家压力。
  - 记录青灯草旧线索。
  - 记录十三枚碎灵和价目半册。
- chapter: 5
  function: draft：赵掌柜亲自压价，陈安用价目半册和备货策略反守为攻。
  opening_hook: 赵掌柜亲自来谈。
  main_payoff: 陈安进一步确立不签独家、不出门、按次交易的店主规矩。
  next_hook: 价目半册或旧账本给出下一种关键货物线索。
  state_obligation:
  - 推进 thread_0004_pill_shop_exclusive_pressure。
  - 推进 thread_0004_grandpa_qingdengcao_record。
- chapter: 6
  function: draft：把谈判压力转成主动采购和第二轮交易。
  opening_hook: 陈安按价目半册筛选现实可替代货。
  main_payoff: 出现第一批明确复购或新客户。
  next_hook: 巡卫或坊市规则压力靠近。
  state_obligation:
  - 建立更清晰价格标尺。
- chapter: 7
  function: draft：现实亲戚/房租压力回压，让异界收益必须落到现实经营。
  opening_hook: 刘素芬或房租压力再度出现。
  main_payoff: 陈安用合规小额收益改善小店。
  next_hook: 现实侧有人怀疑爷爷遗产来源。
  state_obligation:
  - 记录现实压力变化。
- chapter: 8
  function: draft：爷爷旧账本线推进，青灯草不再只是彩蛋。
  opening_hook: 旧账本和价目半册出现第二处重合。
  main_payoff: 陈安确认爷爷曾长期按某套规矩交易。
  next_hook: 某个旧名号或旧价码浮出。
  state_obligation:
  - 推进爷爷旧账本长线。
- chapter: 9
  function: draft：丹铺或巡卫施加更直接风险，测试陈安规矩。
  opening_hook: 有人试图绕过许青或直接找门。
  main_payoff: 陈安守住不暴露仓库边界。
  next_hook: 第一阶段更大冲突逼近。
  state_obligation:
  - 更新入口保密风险。
- chapter: 10
  function: draft：10章小单元收束，形成第一套可持续交易流程。
  opening_hook: 多方压力同时指向陈安货源。
  main_payoff: 陈安完成第一套小店交易规矩和备货闭环。
  next_hook: 进入更大范围客户/势力压力。
  state_obligation:
  - 总结第一单元资源、客户、规则和未回收伏笔。
approval:
  status: approved
  approved_by: ''
  approved_at: ''
  notes:
  - Chapters 1-4 are anchored to accepted facts; chapters 5-10 are draft planning
    assumptions.
  note: Approved as V3.2 prewriting constraint for chapter 5; future draft beats remain
    adjustable through later outline approval.
```

## Current State

Source: `state/current_state.json`

```json
{
  "current_chapter": 4,
  "current_arc": "arc_001",
  "latest_location": "小卖部仓库后门 / 青石坊巷口",
  "active_characters": [
    "chen_an",
    "xu_qing",
    "mo_zhangfang"
  ],
  "active_conflicts": [
    "回春丹铺试图用巡卫保护和独家供货压住陈安货源",
    "陈安必须在不暴露后门和仓库的前提下建立交易规则",
    "爷爷旧账本与青石坊价目半册出现青灯草重合线索"
  ],
  "pending_approvals": [
    "是否沿用书名《我家小卖部通修仙界》。",
    "是否确认后门规则为每天午夜开启一个时辰。",
    "是否确认第一交易锚点为细盐和打火机。",
    "是否确认碎灵作为低阶交易货币单位。",
    "是否确认手电筒暂命名为夜明筒。",
    "是否确认许青被巡卫盘问作为第3章入口。",
    "是否确认黄芽草可在现实小额变现，但不能公开大规模出售。",
    "是否确认回春丹铺作为第一阶段异界商业压力。",
    "是否确认第4章进入回春丹铺谈价/试探。",
    "是否确认回春丹铺莫账房作为第4章谈判代表。",
    "是否确认回春丹铺赵掌柜作为第5章主要谈判压力。",
    "是否确认青灯草为爷爷旧账本与青石坊价目半册之间的第一条长线谜团线索。",
    "是否确认第4章交易结果：一包细盐、两卷纱布、十片创可贴、六支碘伏棉签换十三枚碎灵和价目半册。",
    "是否确认第5章由赵掌柜亲自来谈作为下一章主钩子。",
    "是否确认青灯草作为爷爷旧账本长线谜团的第一枚明确线索。"
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
      "title": "午夜后门",
      "path": "chapters/ch_0001.md",
      "summary": "陈安继承爷爷留下的小卖部，现实中被亲戚逼卖和催租压迫；午夜仓库后门开启，门外通向青石坊，第一位灰袍散修用碎灵询问细盐和火折。",
      "state_changes": [
        "陈安继承陈守业留下的小卖部，现实债务和亲戚逼卖成为开局压力。",
        "小卖部仓库后门在午夜开启，门外通向青石坊边缘巷口。",
        "旧账本出现两界交易记录：细盐、碎灵、黄芽草、火折。",
        "许青作为第一位修仙界交易对象在章末登场。"
      ],
      "open_threads_touched": []
    },
    {
      "chapter": 2,
      "title": "一包盐换一块灵石",
      "path": "chapters/ch_0002.md",
      "summary": "陈安站在后门内完成第一笔两界交易，用细盐、打火机和手电筒换到两枚碎灵与黄芽草；许青带走夜明筒后被青石坊巡卫盘问，陈安意识到现代货物既能救命也会惹祸。",
      "state_changes": [
        "陈安完成第一笔两界交易：一包细盐、两支打火机、一支手电筒换到两枚碎灵和一束黄芽草。",
        "后门规则进一步明确：午夜开启一个时辰，约两个小时，到时会强制闭合。",
        "许青确认青石坊巡卫会盘查来历不明且没有灵力波动的发光物。",
        "现代货物在修仙界具备交易价值，但手电筒等显眼货物会带来巡卫风险。",
        "陈安开始主动思考批发进货，现实危机与异界交易形成经营闭环。"
      ],
      "open_threads_touched": []
    },
    {
      "chapter": 3,
      "title": "黄芽草",
      "path": "chapters/ch_0003.md",
      "summary": "陈安谨慎验证碎灵和黄芽草，将黄芽草叶尖小额变现并补交部分房租；许青午夜回来说夜明筒被巡卫扣下，回春丹铺盯上细盐和夜明筒，要求见夜里开门的陈掌柜。",
      "state_changes": [
        "陈安将黄芽草叶尖以旧书样品名义小额变现三千元，并补交一个月部分房租二千五。",
        "碎灵粉末被现实便携检测初步判断为非普通材料，但陈安决定暂不公开出售。",
        "刘素芬怀疑陈安藏有爷爷遗产，现实逼卖压力继续存在。",
        "许青确认巡卫扣下夜明筒，但没有查到小卖部门。",
        "回春丹铺盯上细盐和夜明筒，要求见夜里开门的陈掌柜。",
        "陈安拒绝当天见客，要求回春丹铺明晚带价来谈，并明确小卖部不是丹铺后仓。"
      ],
      "open_threads_touched": []
    },
    {
      "chapter": 4,
      "title": "丹铺开价",
      "path": "chapters/ch_0004.md",
      "summary": "回春丹铺莫账房带价来谈，试图用巡卫保护和独家供货压住陈安；陈安坚持按次交易、不出门、不签独家，用细盐、纱布、创可贴和碘伏棉签换到十三枚碎灵与青石坊价目半册，并发现价目半册里的青灯草与爷爷旧账本十年前记录重合。",
      "state_changes": [
        "陈安按现实采购思路将货物分为可卖、试探和暂不外露三类，明确今晚谈判目标是不卖断货源、不签独家、先拿价格表、不出门。",
        "回春丹铺莫账房带价来谈，提出细盐三枚碎灵、火折一枚碎灵、夜明筒十枚碎灵，并试图用每月二十枚碎灵和巡卫保护换取独家供货。",
        "陈安拒绝独家供货和巡卫保护价码，坚持货少、按次交易、不签独家，并守住不出后门、不暴露仓库的边界。",
        "陈安用纱布、创可贴和碘伏棉签证明现代小商品可降低低阶散修小伤恶化风险，回春丹铺承认其交易价值。",
        "陈安以一包细盐、两卷纱布、十片创可贴、六支碘伏棉签换到十三枚碎灵和青石坊废弃价目半册。",
        "陈安赠予许青一支碘伏棉签和一片创可贴，换取赵掌柜更难缠、明晚可能亲自来谈的信息。",
        "价目半册中出现青灯草，陈安发现爷爷旧账本十年前也记有青灯草交易，确认爷爷曾长期熟悉青石坊价格与交易规则。"
      ],
      "open_threads_touched": [
        "thread_0004_pill_shop_exclusive_pressure",
        "thread_0004_grandpa_qingdengcao_record"
      ]
    }
  ]
}
```

## Hook Index

Source: `state/hook_index.json`

```json
{
  "hooks": [
    {
      "chapter": 4,
      "hook": "回春丹铺赵掌柜明晚亲自来谈，价目半册里的青灯草也与爷爷旧账本记录重合。",
      "obligation": "第5章展示赵掌柜亲自压价/试探，并让陈安用价目半册主动备货。",
      "target_chapter": 5,
      "status": "open"
    }
  ]
}
```

## Memory Index

Source: `state/memory_index.json`

```json
{
  "by_character": {
    "chen_an": [
      4
    ],
    "xu_qing": [
      4
    ],
    "mo_zhangfang": [
      4
    ]
  },
  "by_thread": {
    "thread_0004_pill_shop_exclusive_pressure": [
      4
    ],
    "thread_0004_grandpa_qingdengcao_record": [
      4
    ]
  },
  "by_location": {
    "小卖部仓库后门 / 青石坊巷口": [
      4
    ]
  },
  "by_resource": {
    "碎灵": [
      4
    ],
    "基础医疗小商品库存": [
      4
    ],
    "青石坊废弃价目半册": [
      4
    ]
  }
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
