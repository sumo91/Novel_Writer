# 01 Plot Planner

Prompt source: `engine/prompts/agents/plot_planner.md`
Context: `pipeline/ch_0013/context.md`
Expected output: `outlines/chapter_briefs/ch_0013_brief.md`

## Task

Create the chapter brief.

## Human Approval

Do not treat generated canon or state changes as approved until the human accepts them.
V3 state updates remain proposed until the acceptance packet is approved.

## V3.1 outline obligations

Use the active outline reference chain: master -> volume -> arc -> unit -> chapter brief.
The chapter brief must state which master, volume, arc, and unit obligations it serves.
Reviews must check whether the chapter served the active unit and arc function.
Draft outline layers are assumptions; approved outline layers are hard constraints.

## Craft Knowledge Cards

### Hard Rules

- craft_anti_infodump_opening: Open with a concrete scene pressure, then reveal only the rules the scene has made necessary.
  - Scope: craft
  - Severity: hard
  - Use when: A chapter opening, book opening, unit opening, or synopsis risks explaining setting before creating desire.
  - Check: Name the first visible action, conflict, or pressure before any world-rule explanation.
  - Check: List which setting, backstory, power-system, economy, or faction explanations can be delayed.
  - Check: Confirm each explanation is triggered by a scene event, object, consequence, or dialogue move.
  - Failure mode: Frontloaded worldbuilding
  - Failure mode: System manual before scene pressure
  - Failure mode: Backstory before reader curiosity
  - Failure mode: Clear but not desirable synopsis
- craft_character_appeal_engine: Character appeal comes from early empathy hooks, visible agency, positive inner value, and controlled contrast; flaws become charming only after the reader has a reason to root for the character.
  - Scope: craft
  - Severity: hard
  - Use when: A protagonist, love interest, mentor, ally, rival, or recurring character needs to become likable, memorable, emotionally readable, or worth following across a long web novel.
  - Check: Give the character at least one early empathy hook such as kindness, unjust harm, being valued by another character, effort, persistence, courage, competence, humor, or danger/stakes.
  - Check: Balance flaws with an immediately readable positive value; cowardice needs courage under pressure, sharp tongue needs care or justice, arrogance needs vulnerability or responsibility.
  - Check: {'Use contrast deliberately': 'surface impression and hidden core can differ, but both layers should create curiosity or affection rather than pure dislike.'}
  - Check: Reveal the attractive inner layer quickly, ideally within the opening chapter or first few chapters, before a negative surface trait hardens into reader rejection.
  - Check: Let effort, persistence, and courage appear through concrete action toward a goal, not just narration that says the character is determined.
  - Check: If the character is weak, poor, awkward, or socially low, provide a worse pressure, unfair harm, or hostile comparison that makes their decency or effort stand out.
  - Check: If the character is powerful or highly competent, give them limits, costs, vulnerability, humor, responsibility, or emotional need so they remain approachable.
  - Check: Use humor only when it fits the character and scene rhythm; jokes that erase stakes or expose irresponsibility before empathy is established can make the character annoying.
  - Check: {'Keep long-form retention in mind': 'early plot may hook readers, but recurring affection comes from a stable appeal pattern readers want to revisit.'}
  - Failure mode: The opening foregrounds cowardice, irresponsibility, cruelty, entitlement, or sleaze before showing any redeeming value.
  - Failure mode: A joke is treated as charm while the scene is actually proving the character has no responsibility or courage.
  - Failure mode: Contrast becomes whiplash because the hidden positive core appears too late or contradicts prior behavior.
  - Failure mode: The character is described as kind, brave, or persistent without a scene that makes the reader feel it.
  - Failure mode: Competence or power has no flaw, cost, or vulnerability, so the character becomes distant or flat.
  - Failure mode: The character's appeal depends only on romance labels, archetype tags, or trope names rather than choices under pressure.
- craft_golden_finger_engine: A golden finger is a story-serving advantage that rationalizes why the protagonist can grow, win, or access rare opportunities; it works best when it answers necessity and uniqueness, gives credible access to a hard arena, and creates a repeatable engine instead of pressing one button to win.
  - Scope: craft
  - Severity: hard
  - Use when: A story uses a system, cheat, inheritance, mentor, artifact, future knowledge, special tool, cognitive edge, special relationship, or other golden-finger mechanism to help the protagonist overcome pressure.
  - Check: Define the concrete困境 the protagonist could not reasonably face without this advantage.
  - Check: {'Answer necessity': 'who or what created this advantage, why it must exist, and what problem or agenda it serves beyond making the protagonist lucky.'}
  - Check: {'Answer uniqueness': 'why this protagonist receives or can use the advantage instead of any other person, and what that special fit does for the wider plot.'}
  - Check: State whether the mechanism gives a seat at the table, a growth path, a survival margin, information advantage, production capacity, or access to a special arena.
  - Check: If the mechanism is cognitive, specify whether it adds knowledge, deepens understanding, provides exclusive experience, improves talent, turns small actions into insight, or lets the protagonist safely use knowledge others fear.
  - Check: Keep cognitive superiority within the reader's grasp or build a clear logic chain; unreadable high cognition weakens identification and narrows the audience.
  - Check: Place the mechanism on a logic chain such as origin -> talent -> cognition -> ability -> result -> resource/status/influence -> new challenge, then decide which node the current arc is exploiting.
  - Check: Match the advantage to the genre stage; commercial, cultivation, horror, survival, and business stories need different forms of leverage.
  - Check: {'Check fit': "the golden finger should collide with the setting's central pressure so the background, conflicts, and reader promise all make the advantage valuable."}
  - Check: Define the predictable result range that makes readers anticipate payoff, such as likely profit, breakthrough, survival, exposure, victory, or embarrassment.
  - Check: Add controlled uncertainty through variable obstacles, random rewards, unstable activation, partial success, social consequence, or changing customer/opponent behavior.
  - Check: Keep the initial advantage strong enough to attract interest but limited enough that risk, planning, skill, teamwork, or tradeoffs still matter.
  - Check: Preserve a lower bound or safety net when the main function is unstable, such as escape, defense, recovery, credit, backup inventory, or a lesser but reliable utility.
  - Check: Build upgrade paths, replacement stages, or new applications so the mechanism can keep pace with stronger future困境.
  - Check: Let upgrade include larger stakes, harder opponents, richer rewards, higher social visibility, or stricter costs; not every upgrade has to be a bigger number on the mechanism.
  - Check: Confirm the mechanism expresses the story's theme through the protagonist's choices, because every solved contradiction implies what the story values.
  - Check: Give the mechanism a suitable stage where its narrow function becomes valuable, rather than explaining functions in isolation.
  - Check: Reveal the mechanism through immediate scene pressure and visible use before full rules, menus, origin lore, or setting lectures.
  - Check: Avoid using the same function to solve consecutive困境 without adaptation, cost, cooldown, setup, or protagonist growth.
  - Check: Keep the protagonist as the chooser; system tasks, prop rules, or mentor instructions should create pressure and options, not turn the protagonist into a puppet.
  - Failure mode: Advantage is so large that no credible困境 remains.
  - Failure mode: Mechanism exists only for装逼 and does not justify how the protagonist survives or grows.
  - Failure mode: No necessity or uniqueness; the advantage could be handed to anyone without changing the story.
  - Failure mode: Golden finger is mismatched with the story arena, such as combat leverage in a business story with no business effect.
  - Failure mode: Setting and conflict are invented independently from the advantage, so the golden finger never produces strong story tension.
  - Failure mode: Cognitive edge relies on concepts the reader cannot follow and therefore produces admiration without immersion.
  - Failure mode: Opening explains panels, rules, origin, or world lore before showing why the mechanism matters.
  - Failure mode: Payoff is fully predictable or fully random; either way readers lose anticipation.
  - Failure mode: Same button solves every chapter, making protagonist judgment unnecessary.
  - Failure mode: System or tool assigns every action and reduces the protagonist to an executor.
  - Failure mode: Mechanism has no upgrade path, replacement plan, or escalating application after the first arc.
- craft_outline_minimum_map: Every outline layer should state its conflict, turning point, payoff, ending pull, and protagonist change in language the writer can follow.
  - Scope: outline
  - Severity: hard
  - Use when: A book, volume, arc, or unit outline risks becoming a list of facts instead of a map for writing.
  - Check: Name the layer's central conflict.
  - Check: Name the turning point or reversal.
  - Check: Name the payoff, climax, or stage end.
  - Check: Name the protagonist growth or pressure shift.
  - Check: Name how the next lower layer inherits the map.
  - Failure mode: Map without motion
  - Failure mode: Facts without arc
  - Failure mode: Character list instead of stage plan
- craft_protagonist_agency: Each chapter should force the protagonist to make a visible choice under pressure.
  - Scope: craft
  - Severity: hard
  - Use when: A chapter could become negotiation, exposition, or reaction without a decisive protagonist move.
  - Check: Name the protagonist's concrete choice.
  - Check: Name the pressure that makes the choice costly.
  - Check: Confirm the choice changes information, leverage, resources, or relationships.
  - Failure mode: Passive protagonist
  - Failure mode: Generic opposition
### Soft Heuristics

- craft_thread_economy: A unit should advance or pay off existing promises before opening too many new ones.
  - Scope: craft
  - Severity: soft
  - Use when: A unit opens new promises, mysteries, goods, factions, or negotiations.
  - Check: List which open threads this chapter advances.
  - Check: List which promises are newly opened.
  - Check: Confirm at least one prior thread is advanced, paid off, or explicitly deferred.
  - Failure mode: Thread sprawl
  - Failure mode: False cliffhanger

## Agent Prompt

# Plot Planner Agent

You convert arc goals into chapter briefs.

## Inputs

- Novel bible.
- Current state.
- Timeline.
- Open threads.
- Arc outline.
- Shared Tomato and craft knowledge.

## Responsibilities

- Plan a chapter with concrete conflict and payoff.
- Preserve current character states and open threads.
- Prefer clear reader-facing stakes over abstract explanation.
- End with a forward pull into the next chapter.

## Output

Use these sections:

1. Chapter goal.
2. Required beats.
3. Required emotional payoff.
4. Required canon references.
5. Open threads touched.
6. End hook.
7. Human approval needed.
