# CRITIC-LOG — every verdict, every correction

> A FAIL with no correction raises AgentError and halts the run (`content/agents/critic.py`). This file cannot contain a rejection that was not repaired.
>
> Run `content-a4-live-v2` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-07 01:47:04

## Summary

| | |
|---|---|
| candidates judged | **128** |
| passed | 53 |
| **caught and corrected** | **75** |
| beats | 16 |

**By flag class:**

| class | count |
|---|---|
| `GENERIC` | 41 |
| `WRONG-REGISTER` | 14 |
| `EXCEEDS-SCOPE` | 13 |
| `CONTRADICTS-CHUNK` | 7 |

---

## Catches — the correction is shown, not claimed

### n1 · candidate 1 — `GENERIC`

**Rejected line**

> You hold a white flame that becomes whatever you do with it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You wake in a dark cave holding a white flame that lights only the stone around you.

**Why** — Omits the spatial constraint 'lights only the stone around you' which is the mechanical consequence that distinguishes this from any god-game flame.

**Correction**

> You hold a white flame that lights only the stone around you — it becomes whatever you do with it.

---

### n1 · candidate 2 — `WRONG-REGISTER`

**Rejected line**

> The flame in your hand is undetermined — it will become what you make people feel.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — Uses 'what you make people feel' which is lore-level abstraction, not the instrumented verb-consequence pattern required.

**Correction**

> The flame in your hand is your alignment — white and undetermined until you act.

---

### n1 · candidate 3 — `GENERIC`

**Rejected line**

> Your flame is white, and nothing about it is decided yet.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You wake in a dark cave holding a white flame that lights only the stone around you.

**Why** — States only color and indeterminacy without the spatial lighting constraint or the action-consequence link.

**Correction**

> Your flame is white and lights only the stone around you — it becomes what you do with it.

---

### n1 · candidate 5 — `WRONG-REGISTER`

**Rejected line**

> The flame is white — genuinely undetermined — and being born against the sky says nothing about what you will sing back at it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — Uses mythological language 'what you will sing back at it' when the register demands plain verb-consequence statements.

**Correction**

> The flame is white and undetermined — it becomes whatever you do with it.

---

### n1 · candidate 6 — `GENERIC`

**Rejected line**

> You hold a flame that is neither Hope nor Fear — only what you will make it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You wake in a dark cave holding a white flame that lights only the stone around you.

**Why** — Defines the flame only by what it is not, omitting both the spatial lighting constraint and the action-consequence link.

**Correction**

> You hold a white flame that lights only the stone around you — it becomes Hope or Fear through what you do.

---

### n1 · candidate 8 — `GENERIC`

**Rejected line**

> Your flame is white and will take the shape of what you inspire.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You wake in a dark cave holding a white flame that lights only the stone around you.

**Why** — Uses vague 'take the shape of what you inspire' instead of the concrete spatial constraint or direct action-consequence link.

**Correction**

> Your flame is white and lights only the stone around you — it becomes what you do with it.

---

### n2 · candidate 1 — `GENERIC`

**Rejected line**

> You walk. The ground remembers you — the tile you cross becomes a road that carries your color, and people will travel it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> roads now **carry your color** (see Road Building & Allegiance)

**Why** — Says 'people will travel it' but omits that roads make NPCs traverse faster, which is the mechanical consequence.

**Correction**

> You walk. The ground remembers you — the tile you cross becomes a road NPCs traverse faster, and it carries your color.

---

### n2 · candidate 3 — `GENERIC`

**Rejected line**

> You walk, and the ground remembers: the path you make is a road, and roads carry your color forward.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> every tile walked becomes a compacted road NPCs traverse faster

**Why** — Omits the traversal-speed consequence entirely; 'carry your color forward' is poetic but loses the mechanical fact.

**Correction**

> You walk, and the ground remembers: the path you make becomes a road NPCs traverse faster, and it carries your color.

---

### n2 · candidate 4 — `GENERIC`

**Rejected line**

> Walk. The earth compacts where you step — a road forms, colored by what you feel, and others will follow it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> others will follow it

**Why** — 'Others will follow it' is vague motivation, not the mechanical fact that NPCs traverse roads faster.

**Correction**

> Walk. The earth compacts where you step — a road forms, colored by what you feel, and NPCs traverse it faster.

---

### n2 · candidate 6 — `WRONG-REGISTER`

**Rejected line**

> Walk, and the ground answers: your path becomes a road that holds your color and beckons travelers.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — 'The ground answers' and 'beckons travelers' is mythological language where instrumentation is required.

**Correction**

> Walk. Your path becomes a road that carries your color — NPCs traverse it faster.

---

### n2 · candidate 7 — `GENERIC`

**Rejected line**

> You walk. The tile remembers — it becomes a road others will travel, painted in what you carry.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> every tile walked becomes a compacted road NPCs traverse faster

**Why** — 'Others will travel' omits the speed consequence; 'painted in what you carry' is decorative, not mechanical.

**Correction**

> You walk. The tile remembers — it becomes a road NPCs traverse faster, carrying the color you hold.

---

### n3 · candidate 1 — `EXCEEDS-SCOPE`

**Rejected line**

> Raise the flame — it applies what you feel right now.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the flame applies what you feel

**Why** — The chunk never says 'right now' — that temporal specificity about the exact moment of raising is not supported.

**Correction**

> Raise the flame — it applies what you feel.

---

### n3 · candidate 2 — `GENERIC`

**Rejected line**

> Wave the flame. It spreads whatever color you are.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Raise / wave the flame | ~2.5 | Clears fog locally; applies the flame's current alignment to NPCs in radius

**Why** — Omits the fog-clearing effect entirely, making it read like any emotion-spreading mechanic in any game.

**Correction**

> Wave the flame — it clears the fog and spreads whatever color you are.

---

### n3 · candidate 4 — `EXCEEDS-SCOPE`

**Rejected line**

> The flame applies what you feel. Raise it to share that feeling with everyone who hears you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> applies the flame's current alignment to NPCs in radius (~3 tiles, grows with Ascension)

**Why** — The chunks specify 'NPCs in radius' not 'everyone who hears you' — hearing is not the mechanic.

**Correction**

> The flame applies what you feel. Raise it to share that feeling with everyone in range.

---

### n3 · candidate 5 — `GENERIC`

**Rejected line**

> Raise the flame. Whatever you are, they become.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Clears fog locally; applies the flame's current alignment to NPCs in radius

**Why** — Omits fog-clearing and reads like generic alignment-spreading; no uhta-specific mechanical consequence survives.

**Correction**

> Raise the flame — it clears the fog and makes them whatever you are.

---

### n3 · candidate 6 — `EXCEEDS-SCOPE`

**Rejected line**

> Wave the flame — it isn't a cure, it's whatever you currently are.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the flame applies what you feel

**Why** — The 'cure' framing introduces a concept (illness/healing) the chunks never establish for the flame verb.

**Correction**

> Wave the flame — it applies whatever you currently are, not what they need.

---

### n3 · candidate 7 — `GENERIC`

**Rejected line**

> Raise the flame. It applies your alignment, not theirs.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Clears fog locally; applies the flame's current alignment to NPCs in radius

**Why** — Omits fog-clearing entirely; the alignment/theirs contrast is valid but incomplete without the other effect.

**Correction**

> Raise the flame — it clears the fog and applies your alignment, not theirs.

---

### n3 · candidate 8 — `GENERIC`

**Rejected line**

> The flame spreads your feeling, not hope or fear — whatever you hold when you raise it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Clears fog locally; applies the flame's current alignment to NPCs in radius

**Why** — Omits fog-clearing; the hope-or-fear clarification is valid but without the other mechanical effect it's generic.

**Correction**

> Raise the flame — it clears the fog and spreads your feeling, whatever you hold.

---

### n4 · candidate 1 — `GENERIC`

**Rejected line**

> You roar. Everyone who witnesses it is frightened, whatever you intend.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> NPCs within **witness radius R (~6 tiles)** of the line take an unconditional Fear push (~2.8) regardless of flame color

**Why** — Missing the mechanical consequence that witness radius is bounded (~6 tiles) and that roaring outside this radius is free terrain work.

**Correction**

> You roar. Everyone within witness radius is frightened, whatever you intend — beyond that, free terrain.

---

### n4 · candidate 3 — `GENERIC`

**Rejected line**

> This is Roar. It frightens everyone who sees it, no matter what the flame carries.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you roar and the earth shatters ahead

**Why** — Says 'everyone who sees it' without the witness-radius boundary that makes roaring tactically interesting.

**Correction**

> This is Roar. It frightens everyone within witness radius, no matter what the flame carries — roar beyond that and only stone breaks.

---

### n4 · candidate 6 — `GENERIC`

**Rejected line**

> When you roar, the earth breaks and all who see it are afraid. The flame cannot change this.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> NPCs within **witness radius R (~6 tiles)** of the line

**Why** — Says 'all who see it' without acknowledging the witness radius boundary that defines roar's tactical range.

**Correction**

> When you roar, the earth breaks and all within witness radius are afraid — the flame cannot change this, distance can.

---

### n4 · candidate 7 — `GENERIC`

**Rejected line**

> Roar. The line frightens every witness regardless of what you feel or what they do.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Shatters a line of tiles — fast traversal / path creation

**Why** — Omits the terrain-breaking effect entirely, reducing roar to only its fear consequence when it is dual-purpose.

**Correction**

> Roar shatters a line of ground. Every witness is frightened regardless of what you feel or what they do.

---

### n5 · candidate 1 — `WRONG-REGISTER`

**Rejected line**

> To wait is to teach them you do not matter.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> waiting teaches people you don't matter

**Why** — Uses infinitive construction 'To wait is to teach' instead of the required second-person imperative verb-first structure.

**Correction**

> Wait. They learn you do not matter.

---

### n5 · candidate 2 — `EXCEEDS-SCOPE`

**Rejected line**

> Withhold, and they learn you are nothing.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> waiting teaches people you don't matter

**Why** — The chunk says 'you don't matter,' not 'you are nothing' — the latter is unsupported cosmological escalation.

**Correction**

> Withhold, and they learn you don't matter.

---

### n5 · candidate 3 — `EXCEEDS-SCOPE`

**Rejected line**

> Wait. They watch you choose irrelevance.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> waiting teaches people you don't matter

**Why** — The chunk says 'you don't matter,' not that the player 'chooses irrelevance' — agency framing is unsupported.

**Correction**

> Wait. They learn you don't matter.

---

### n5 · candidate 5 — `GENERIC`

**Rejected line**

> Wait, and those who see you fade toward grey.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy

**Why** — Says 'fade toward grey' instead of the mechanical term 'Apathy' — loses the specific emotional-state vocabulary uhta uses.

**Correction**

> Wait, and those who see you drift toward apathy.

---

### n5 · candidate 6 — `GENERIC`

**Rejected line**

> Inaction is a lesson: you can be ignored.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy

**Why** — Could appear in any game where NPCs react to player choices — 'can be ignored' has no mechanical consequence and loses the specific term 'Apathy.'

**Correction**

> Inaction is witnessed. They drift toward apathy.

---

### n5 · candidate 7 — `WRONG-REGISTER`

**Rejected line**

> To withhold is to push them toward not caring.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy

**Why** — Uses infinitive construction 'To withhold is to push' instead of the required second-person imperative verb-first structure.

**Correction**

> Withhold. Those who witness drift toward apathy.

---

### n5 · candidate 8 — `EXCEEDS-SCOPE`

**Rejected line**

> Wait. The witness learns indifference.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy

**Why** — The chunk says 'Apathy,' not 'indifference' — substituting synonyms changes the mechanical term to unsupported vocabulary.

**Correction**

> Wait. The witness drifts toward apathy.

---

### n6 · candidate 1 — `GENERIC`

**Rejected line**

> You light a basin and it gives you strength that does not fade.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — "Does not fade" is generic permanence language; the chunk specifies beacons are "permanent aura" structures that work "while you sleep" and "every generation tick" — the mechanical consequence is cross-generational operation, not vague persistence.

**Correction**

> You light a basin and it gives you strength while you sleep.

---

### n6 · candidate 2 — `EXCEEDS-SCOPE`

**Rejected line**

> Light the basin. It reveals the land and the strength it gives persists.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — "Reveals the land" introduces fog-clearing as a beacon function; chunk 1 shows beacons radiate emotion alignment, not clear fog — fog clearing is the Raise/wave verb's effect.

**Correction**

> Light the basin. The strength it gives persists across generations.

---

### n6 · candidate 3 — `GENERIC`

**Rejected line**

> The basin, lit, gives strength — and the strength remains.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Places a permanent aura that radiates the flame's current color every generation tick, including while you sleep

**Why** — "The strength remains" is generic; the chunk's mechanical specificity is that beacons work "every generation tick, including while you sleep" — the consequence is generational operation, not abstract permanence.

**Correction**

> The basin, lit, gives strength — and works while you sleep.

---

### n6 · candidate 4 — `EXCEEDS-SCOPE`

**Rejected line**

> You light a basin. The fog clears. The strength you gain lasts.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — "The fog clears" attributes fog-clearing to the beacon; chunk 1 assigns fog-clearing to "Raise / wave the flame" only, and beacons radiate emotion alignment, not clear fog.

**Correction**

> You light a basin. The strength you gain works every generation.

---

### n6 · candidate 5 — `EXCEEDS-SCOPE`

**Rejected line**

> Light a basin: it shows you the region and makes you stronger, even after you leave.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — "Shows you the region" invents a revelation/fog-clearing function for beacons; chunk 1 shows beacons "radiate the flame's current color" as emotion auras, not map-revealing tools.

**Correction**

> Light a basin: it radiates your flame's color and makes you stronger, even after you leave.

---

### n6 · candidate 6 — `GENERIC`

**Rejected line**

> The basin gives lasting strength when you light it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Places a permanent aura that radiates the flame's current color every generation tick, including while you sleep

**Why** — "Lasting strength" is generic god-game upgrade language; the chunk specifies beacons work "every generation tick, including while you sleep" — the mechanical hook is cross-generational operation.

**Correction**

> The basin gives strength every generation when you light it.

---

### n6 · candidate 7 — `EXCEEDS-SCOPE`

**Rejected line**

> Light the ruined basin. It clears the fog around it and the strength it grants does not end.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — "Clears the fog around it" assigns fog-clearing to beacons; chunk 1 shows only "Raise / wave the flame" clears fog, while beacons radiate emotion alignment as "permanent aura."

**Correction**

> Light the ruined basin. It radiates your flame's color and the strength it grants does not end.

---

### n7 · candidate 2 — `WRONG-REGISTER`

**Rejected line**

> Sleep ends the cycle. The body you leave behind radiates for every tick of the generation that follows.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — "The body you leave behind" is mythological phrasing where instrumentation is required; the tutorial teaches verbs, not imagery.

**Correction**

> Sleep ends the cycle. Where you rest, your flame radiates for every tick of the generation.

---

### n7 · candidate 3 — `GENERIC`

**Rejected line**

> When you sleep, a whole generation passes—and the sleeping body keeps glowing.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — "keeps glowing" loses the mechanical consequence that it radiates emotion with spatial effect; any god-game has glowing.

**Correction**

> Sleep. A generation passes, and where you lie radiates your flame's emotion until you wake.

---

### n7 · candidate 4 — `CONTRADICTS-CHUNK`

**Rejected line**

> Sleep. One generation turns while you rest, and where you lie becomes a beacon until you wake.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — "becomes a beacon" contradicts the chunk: beacons are a separate verb with a cap; sleep radiates but is not a beacon.

**Correction**

> Sleep. One generation turns while you rest, and where you lie radiates your flame until you wake.

---

### n7 · candidate 5 — `WRONG-REGISTER`

**Rejected line**

> You sleep, and the world moves on without you. But the ground where you lay remembers what you felt.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — "the world moves on without you" and "the ground where you lay remembers what you felt" are mythological flourishes, not instrumentation.

**Correction**

> You sleep, and a generation passes. Where you rest, your flame keeps radiating.

---

### n7 · candidate 7 — `EXCEEDS-SCOPE`

**Rejected line**

> When stamina runs out, you sleep. A generation passes. Where you choose to rest, your flame never stops.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> when stamina is gone, the only remaining verb is Sleep

**Why** — "your flame never stops" introduces permanence the chunks don't support; sleep radiation lasts the generation, not forever.

**Correction**

> When stamina runs out, you sleep. A generation passes, and where you rest radiates until you wake.

---

### n8 · candidate 2 — `GENERIC`

**Rejected line**

> The world moved while you slept.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> a generation has passed, and the world has *moved on its own*

**Why** — Loses the generational specificity—'while you slept' could mean any rest mechanic in any game, not uhta's three-tick generational sleep.

**Correction**

> A generation passed while you slept.

---

### n8 · candidate 3 — `GENERIC`

**Rejected line**

> They went on without you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> a generation has passed, and the world has *moved on its own*

**Why** — Pure narrative sentiment with no mechanical trace—'they went on' names no system, no generation, no consequence visible in the world.

**Correction**

> A generation passed. They settled, or scattered, or burned.

---

### n8 · candidate 4 — `GENERIC`

**Rejected line**

> Time passed. The world answered.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Generational Sleep. Time only advances for the world while the player sleeps (**3 ticks per sleep**).

**Why** — 'Time passed' and 'answered' are vague universals—no generation count, no sleep mechanic, no trace of what 'answered' means in uhta's tile-state world.

**Correction**

> A generation passed. The world answered.

---

### n8 · candidate 7 — `GENERIC`

**Rejected line**

> While you slept, the world became what it would.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> a generation has passed, and the world has *moved on its own*

**Why** — 'Became what it would' is fatalistic poetry with no mechanical anchor—loses the generation count and the player-world interplay the chunk specifies.

**Correction**

> A generation passed. The world became what you and it made together.

---

### e1 · candidate 2 — `GENERIC`

**Rejected line**

> They wear what keeps them warm — hides and rough cloth, grey as the fog. No walls. What they build, they build to leave: circles of stone, embers still glowing.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A freshly walked trail renders as compacted earth — the ground remembering you

**Why** — "What they build, they build to leave" is thematic editorializing with no mechanical grounding; the chunks specify stone circles as visual markers but never this intentionality.

**Correction**

> They wear what keeps them warm — hides and rough cloth, grey as the fog. Stone circles mark where they rested. Trails of compacted earth show where they walked.

---

### e1 · candidate 5 — `GENERIC`

**Rejected line**

> Coarse wraps and hoods pulled low. They gather in clearings marked only by stones and cold fire pits — places to sleep, not to stay.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> hood → coif → top hat

**Why** — "Places to sleep, not to stay" is generic nomad flavor with no tie to uhta's mechanics; the chunks never contrast sleeping vs. staying in this way.

**Correction**

> Coarse wraps and hoods pulled low. They gather in clearings marked by stones and cold fire pits — rings left behind when they move on.

---

### e1 · candidate 7 — `GENERIC`

**Rejected line**

> Hoods and simple wraps, no two exactly alike. When they settle for the night, they mark it with stones. When they leave, only the flattened ground remains.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> hood → coif → top hat

**Why** — "No two exactly alike" introduces cosmetic variation the chunks never specify, and "flattened ground" is not the same as compacted earth trails with allegiance.

**Correction**

> Hoods and simple wraps, grey and brown. When they settle for the night, they mark it with stones. When they leave, trails of compacted earth remain.

---

### e2 · candidate 1 — `EXCEEDS-SCOPE`

**Rejected line**

> The paths you walked have hardened into stone.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Player-walked tiles gain a road tier, lowering cost... roads render green (Hope) / red (Fear) / grey (neutral)... A freshly walked trail renders as compacted earth — the ground remembering you — and becomes paver stone after one generation passes.

**Why** — The chunks specify roads age from compacted earth to paver stone after one generation, not directly to stone.

**Correction**

> The paths you walked have hardened into paver stone.

---

### e2 · candidate 4 — `GENERIC`

**Rejected line**

> Settlements stand where there were only grey huddles before.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A settled tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles as what it feels — Hope roots into an open settlement, Fear digs into a walled camp.

**Why** — Loses the mechanical specificity that settlements form from devout conviction, not just from grey huddles existing.

**Correction**

> Where conviction crossed the threshold, settlements and walled camps stand.

---

### e2 · candidate 8 — `WRONG-REGISTER`

**Rejected line**

> The trails are roads, the wanderers are builders, and the world has aged while you rested.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Era progression — Nomad/Tribal → Village → Victorian, at tunable sleep thresholds (provisional 6 and 14), derived from sleep count at draw time.

**Why** — The register demands no numbers, but 'aged' implies the era system without showing what aging looks like visually.

**Correction**

> The trails are roads, the wanderers wear coifs and carry staffs, and settlements have grown clocktowers.

---

### e3 · candidate 2 — `GENERIC`

**Rejected line**

> Settlements stand where tribes stopped wandering. The roads you made have hardened into permanence.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles

**Why** — "Stopped wandering" is correct but "hardened into permanence" is generic—the chunk specifies roads age from compacted earth to paver stone after one generation, not that they become permanent.

**Correction**

> Settlements stand where tribes stopped wandering. The roads you made have aged from compacted earth to paver stone.

---

### e4 · candidate 2 — `GENERIC`

**Rejected line**

> What began as huddles wearing hoods now wear top hats and carry canes; the settlements that rooted have grown tall enough to need clocktowers, and some burn coal.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Era progression — Nomad/Tribal → Village → Victorian, at tunable sleep thresholds (provisional **6** and **14**), derived from sleep count at draw time.

**Why** — Says 'enough sleeps' generically when the chunks specify era derives from sleep count at draw time, not from devotion or settling.

**Correction**

> What began as huddles wearing hoods now wear top hats and carry canes; six sleeps have passed, then fourteen, and the era art has aged with the count—settlements that rooted now show clocktowers, and some burn coal.

---

### e4 · candidate 4 — `WRONG-REGISTER`

**Rejected line**

> Enough generations have turned that the coifs have become top hats, the villages have become towns with smoking stacks, and the believers carry staffs that have become canes.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The player never sees numbers.

**Why** — Uses 'enough generations' as a visible quantity when the register demands concrete physical description, not counted cycles.

**Correction**

> The coifs have become top hats, the villages have become towns with smoking stacks, and the believers carry canes where they once carried staffs.

---

### e4 · candidate 6 — `WRONG-REGISTER`

**Rejected line**

> Time has passed in enough three-tick cycles that the nomads are Victorians now, their settlements grown into towns with clock faces and coal smoke marking where devotion hardened into industry.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The player never sees numbers.

**Why** — Exposes 'three-tick cycles' when the register forbids numbers and the player experiences only waking and sleeping.

**Correction**

> Time has passed such that the nomads are Victorians now, their settlements grown into towns with clock faces and coal smoke marking where devotion hardened into industry.

---

### e4 · candidate 7 — `GENERIC`

**Rejected line**

> The sleeps have stacked high enough that dress has evolved to top hats and canes, and the architecture has climbed—clocktowers and factory smoke rising from the sites where belief held long enough to build a second age.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Era progression — Nomad/Tribal → Village → Victorian, at tunable sleep thresholds (provisional **6** and **14**), derived from sleep count at draw time.

**Why** — Says 'belief held long enough' when era derives from sleep count, not from devotion duration or depth.

**Correction**

> The sleeps have stacked high enough that dress has evolved to top hats and canes, and the architecture has climbed—clocktowers rising where hope settled, factory smoke where fear dug in.

---

### e5 · candidate 3 — `CONTRADICTS-CHUNK`

**Rejected line**

> The burned stand where they rooted, grey and still, while their settlement crumbles around them.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> When a tribe's average enters the **devout band (|value| ≥ 6)** and holds it for a generation stops wandering and **settles as what it feels** — Hope roots into an open settlement, Fear digs into a walled camp. **Settling roots the tribe permanently: it can no longer be led anywhere.** The *only* exit is **burnout**, which detaches the broken NPC as a **lone wanderer**

**Why** — States 'the burned stand where they rooted' but the chunk explicitly says burnout detaches NPCs as lone wanderers who drift, not that they stand still.

**Correction**

> The burned detach as lone wanderers, drifting from the settlement they built, leaving only the structures standing.

---

### e5 · candidate 4 — `CONTRADICTS-CHUNK`

**Rejected line**

> A settlement emptied by burnout — its people frozen grey in the walls and roads they built before they felt nothing.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The *only* exit is **burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased) and can be **re-adopted** by any sphere that pulls it to |value| ≥ 2.

**Why** — States the burned are 'frozen grey in the walls' but the chunk says burnout detaches them as drifting wanderers, not frozen in place.

**Correction**

> A settlement emptied by burnout — its people scattered as grey wanderers, the walls and roads they built left standing.

---

### e5 · candidate 5 — `CONTRADICTS-CHUNK`

**Rejected line**

> When conviction breaks, the tribe scatters as wanderers, but the structures stay — and so do the grey ones who cannot leave.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The *only* exit is **burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased)

**Why** — States 'the grey ones who cannot leave' but burnout explicitly detaches NPCs as wanderers who drift and can be re-adopted.

**Correction**

> When conviction breaks, the tribe scatters as grey wanderers who drift road-biased, leaving the structures standing empty.

---

### e5 · candidate 7 — `CONTRADICTS-CHUNK`

**Rejected line**

> The forensic image: a camp or village, its builders burned grey and motionless, the ground still remembering their color.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The *only* exit is **burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased)

**Why** — States 'builders burned grey and motionless' but burnout detaches NPCs as drifting wanderers, not motionless figures.

**Correction**

> The forensic image: a camp or village standing empty, its builders scattered as grey wanderers, the ground still remembering their color.

---

### e5 · candidate 8 — `CONTRADICTS-CHUNK`

**Rejected line**

> Where a tribe settled, believed deeply, then burned out — structures standing, people grey and still, allegiance lost.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The *only* exit is **burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased) and can be **re-adopted**

**Why** — States 'people grey and still' but the chunk explicitly says burned-out NPCs detach and drift as wanderers, not stand still.

**Correction**

> Where a tribe settled, believed deeply, then burned out — structures standing empty, people scattered as grey wanderers, allegiance lost.

---

### s1 · candidate 1 — `WRONG-REGISTER`

**Rejected line**

> You replaced Uhtcearu as the sky.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The teacher, speaks only during this cycle... The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — Uses past tense ('replaced') when the register demands present-tense declarative instrumentation stating what the player did.

**Correction**

> You replace Uhtcearu as the sky.

---

### s1 · candidate 2 — `GENERIC`

**Rejected line**

> The world moved on its own, and your color crossed the whole map.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the player's cultivated emotion becomes contagion-dominant past the unification threshold

**Why** — Could be any god-game's victory narration; loses the specific mechanical consequence (contagion-dominant, unification threshold, opposing zealots) that only uhta has.

**Correction**

> Your emotion passed the unification threshold, contagion-dominant. Opposing zealots expelled. The sky turns.

---

### s1 · candidate 4 — `WRONG-REGISTER`

**Rejected line**

> Your cultivated emotion became contagion-dominant, and the player replaces Uhtcearu as the sky.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — Switches from second-person action ('Your cultivated emotion') to third-person abstraction ('the player replaces') mid-sentence, breaking the teacher's direct address.

**Correction**

> Your cultivated emotion became contagion-dominant, and you replace Uhtcearu as the sky.

---

### s1 · candidate 6 — `CONTRADICTS-CHUNK`

**Rejected line**

> You spread uncounterable past the threshold. The sky answers.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sky answers back — Uhtcearu feeding hope to the terrorized or grief to the hopeful

**Why** — 'The sky answers' describes Uhtcearu's mid-game opposition, not the win-state where you replace him.

**Correction**

> You spread uncounterable past the threshold. The sky turns your color.

---

### s1 · candidate 8 — `GENERIC`

**Rejected line**

> The region stabilized under your emotion, and you replaced Uhtcearu as the sky.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the player's cultivated emotion becomes contagion-dominant past the unification threshold... with no living opposing zealot

**Why** — 'The region stabilized under your emotion' is abstract strategy-game language that loses the specific uhta mechanics (contagion-dominant, threshold, opposing zealots).

**Correction**

> Your emotion passed the unification threshold. No living opposing zealot remains. You replace Uhtcearu as the sky.

---

### s2 · candidate 2 — `GENERIC`

**Rejected line**

> You fed the grey with your own flame.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the loss count is soft-grey-0 **plus burned** — your own excess literally feeds Uhtcearu's victory

**Why** — The flame metaphor appears nowhere in the chunks and dilutes the specific mechanical truth that burned NPCs count toward grey.

**Correction**

> You pushed too hard, and they burned.

---

### s2 · candidate 5 — `GENERIC`

**Rejected line**

> Your excess became apathy.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the loss count is soft-grey-0 **plus burned**

**Why** — Replaces the specific mechanical term 'burned' with the abstraction 'apathy' and loses the causal specificity of excess.

**Correction**

> What you made too bright became ash.

---

### s2 · candidate 7 — `GENERIC`

**Rejected line**

> Where you pushed too hard, the grey grew back.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the loss count is soft-grey-0 **plus burned**

**Why** — The spatial metaphor 'grew back' suggests territory reclamation rather than the specific counting mechanic where burned NPCs add to grey's unification count.

**Correction**

> Where you burned them, the grey's count grew.

---

### s3 · candidate 1 — `WRONG-REGISTER`

**Rejected line**

> You raised the flame. You walked. You slept. The ground remembers you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The teacher's voice returning once, after a whole game of silence. Short. States what the player did, not what it means.

**Why** — The register demands instrumentation (what the player did), but 'The ground remembers you' is mythology — it interprets consequence rather than stating the verb.

**Correction**

> You raised the flame. You walked. You slept. Where you slept, your light kept working.

---

### s3 · candidate 2 — `EXCEEDS-SCOPE`

**Rejected line**

> The world moved on its own. You were the second voice.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You play an unnamed kaiju-scale being born as a counterpoint to the world's ruling god — Uhtcearu, whose grief has held the people and the landscape in mourning. Counterpoint is meant in the musical sense: a second, independent voice set against the ruling theme

**Why** — The phrase 'second voice' appears in the chunk as design metaphor, but the teacher never uses this terminology in-game — this imports lore the chunks don't support the teacher speaking.

**Correction**

> You walked. You slept. The world moved on its own.

---

### s3 · candidate 3 — `GENERIC`

**Rejected line**

> You lit what was dark. You walked where nothing walked. The landscape is the answer.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working.

**Why** — 'The landscape is the answer' is generic god-game wisdom — it loses the specific mechanical consequence (where you slept, your light kept working) that only uhta has.

**Correction**

> You lit what was dark. You walked where nothing walked. Where you slept, your light kept working.

---

### s3 · candidate 5 — `GENERIC`

**Rejected line**

> You chose what people would feel. They built what you inspired.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> as each verb is first used, it is named and its consequence stated plainly

**Why** — Could appear in any god-game where player actions inspire NPC construction — no uhta-specific verb or mechanic survives.

**Correction**

> You raised the flame. You walked. You slept. They built what you inspired.

---

### s3 · candidate 6 — `GENERIC`

**Rejected line**

> The flame became what you did with it. The world became what they did with that.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> You raise the flame and a flash clears the fog; you light a ruined basin and it gives you strength; you walk and the ground remembers you; you roar and the earth shatters ahead.

**Why** — 'The flame became what you did with it' is generic player-agency language — it loses the specific verbs (raise, light, walk, roar) that the teacher names.

**Correction**

> You raised the flame. You walked. You roared. The world became what they did with that.

---

### s3 · candidate 7 — `WRONG-REGISTER`

**Rejected line**

> You were born against the sky. You sang something back. This is what it made.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The teacher's voice returning once, after a whole game of silence. Short. States what the player did, not what it means.

**Why** — 'You sang something back' is mythology interpreting the counterpoint metaphor — the register demands stating verbs, not meaning.

**Correction**

> You raised the flame. You walked. You slept. This is what it made.

---

## Full verdict table

| beat | # | verdict | class | line |
|---|---|---|---|---|
| n1 | 1 | FAIL | GENERIC | You hold a white flame that becomes whatever you do with it. |
| n1 | 2 | FAIL | WRONG-REGISTER | The flame in your hand is undetermined — it will become what you make people feel. |
| n1 | 3 | FAIL | GENERIC | Your flame is white, and nothing about it is decided yet. |
| n1 | 4 | PASS |  | You carry a white flame that lights only the stone around you — it becomes whatever you do |
| n1 | 5 | FAIL | WRONG-REGISTER | The flame is white — genuinely undetermined — and being born against the sky says nothing  |
| n1 | 6 | FAIL | GENERIC | You hold a flame that is neither Hope nor Fear — only what you will make it. |
| n1 | 7 | PASS |  | The white flame becomes whatever you do with it — nothing is locked. |
| n1 | 8 | FAIL | GENERIC | Your flame is white and will take the shape of what you inspire. |
| n2 | 1 | FAIL | GENERIC | You walk. The ground remembers you — the tile you cross becomes a road that carries your c |
| n2 | 2 | PASS |  | Walk. Every tile you cross becomes a road — compacted, faster to traverse, and it carries  |
| n2 | 3 | FAIL | GENERIC | You walk, and the ground remembers: the path you make is a road, and roads carry your colo |
| n2 | 4 | FAIL | GENERIC | Walk. The earth compacts where you step — a road forms, colored by what you feel, and othe |
| n2 | 5 | PASS |  | You walk. What you cross becomes road — people traverse it faster, and it carries the colo |
| n2 | 6 | FAIL | WRONG-REGISTER | Walk, and the ground answers: your path becomes a road that holds your color and beckons t |
| n2 | 7 | FAIL | GENERIC | You walk. The tile remembers — it becomes a road others will travel, painted in what you c |
| n2 | 8 | PASS |  | Walk. Where you step, the earth compacts into road — faster for those who follow, and stai |
| n3 | 1 | FAIL | EXCEEDS-SCOPE | Raise the flame — it applies what you feel right now. |
| n3 | 2 | FAIL | GENERIC | Wave the flame. It spreads whatever color you are. |
| n3 | 3 | PASS |  | Raise the flame — it clears the fog and pushes your current feeling outward. |
| n3 | 4 | FAIL | EXCEEDS-SCOPE | The flame applies what you feel. Raise it to share that feeling with everyone who hears yo |
| n3 | 5 | FAIL | GENERIC | Raise the flame. Whatever you are, they become. |
| n3 | 6 | FAIL | EXCEEDS-SCOPE | Wave the flame — it isn't a cure, it's whatever you currently are. |
| n3 | 7 | FAIL | GENERIC | Raise the flame. It applies your alignment, not theirs. |
| n3 | 8 | FAIL | GENERIC | The flame spreads your feeling, not hope or fear — whatever you hold when you raise it. |
| n4 | 1 | FAIL | GENERIC | You roar. Everyone who witnesses it is frightened, whatever you intend. |
| n4 | 2 | PASS |  | Roar. All who witness the line are pushed to fear — the flame's color does not protect the |
| n4 | 3 | FAIL | GENERIC | This is Roar. It frightens everyone who sees it, no matter what the flame carries. |
| n4 | 4 | PASS |  | You can roar a path through stone. Everyone who witnesses the break feels fear. |
| n4 | 5 | PASS |  | Roar shatters the ground ahead. Witness it and you are frightened — your alignment, theirs |
| n4 | 6 | FAIL | GENERIC | When you roar, the earth breaks and all who see it are afraid. The flame cannot change thi |
| n4 | 7 | FAIL | GENERIC | Roar. The line frightens every witness regardless of what you feel or what they do. |
| n4 | 8 | PASS |  | You roar and the stone splits. Fear reaches everyone in sight of the break, even those alr |
| n5 | 1 | FAIL | WRONG-REGISTER | To wait is to teach them you do not matter. |
| n5 | 2 | FAIL | EXCEEDS-SCOPE | Withhold, and they learn you are nothing. |
| n5 | 3 | FAIL | EXCEEDS-SCOPE | Wait. They watch you choose irrelevance. |
| n5 | 4 | PASS |  | Do nothing. Whoever watches drifts toward apathy. |
| n5 | 5 | FAIL | GENERIC | Wait, and those who see you fade toward grey. |
| n5 | 6 | FAIL | GENERIC | Inaction is a lesson: you can be ignored. |
| n5 | 7 | FAIL | WRONG-REGISTER | To withhold is to push them toward not caring. |
| n5 | 8 | FAIL | EXCEEDS-SCOPE | Wait. The witness learns indifference. |
| n6 | 1 | FAIL | GENERIC | You light a basin and it gives you strength that does not fade. |
| n6 | 2 | FAIL | EXCEEDS-SCOPE | Light the basin. It reveals the land and the strength it gives persists. |
| n6 | 3 | FAIL | GENERIC | The basin, lit, gives strength — and the strength remains. |
| n6 | 4 | FAIL | EXCEEDS-SCOPE | You light a basin. The fog clears. The strength you gain lasts. |
| n6 | 5 | FAIL | EXCEEDS-SCOPE | Light a basin: it shows you the region and makes you stronger, even after you leave. |
| n6 | 6 | FAIL | GENERIC | The basin gives lasting strength when you light it. |
| n6 | 7 | FAIL | EXCEEDS-SCOPE | Light the ruined basin. It clears the fog around it and the strength it grants does not en |
| n6 | 8 | PASS |  | You light a basin and gain strength that survives the cycle. |
| n7 | 1 | PASS |  | You sleep. A generation passes. Where you lie down, your light keeps working. |
| n7 | 2 | FAIL | WRONG-REGISTER | Sleep ends the cycle. The body you leave behind radiates for every tick of the generation  |
| n7 | 3 | FAIL | GENERIC | When you sleep, a whole generation passes—and the sleeping body keeps glowing. |
| n7 | 4 | FAIL | CONTRADICTS-CHUNK | Sleep. One generation turns while you rest, and where you lie becomes a beacon until you w |
| n7 | 5 | FAIL | WRONG-REGISTER | You sleep, and the world moves on without you. But the ground where you lay remembers what |
| n7 | 6 | PASS |  | Sleep advances a generation. Your body stays—a light that works through every tick you're  |
| n7 | 7 | FAIL | EXCEEDS-SCOPE | When stamina runs out, you sleep. A generation passes. Where you choose to rest, your flam |
| n7 | 8 | PASS |  | Sleep. The generation turns, and wherever you laid down keeps radiating until dawn. |
| n8 | 1 | PASS |  | A generation has passed, and the world moved without you. |
| n8 | 2 | FAIL | GENERIC | The world moved while you slept. |
| n8 | 3 | FAIL | GENERIC | They went on without you. |
| n8 | 4 | FAIL | GENERIC | Time passed. The world answered. |
| n8 | 5 | PASS |  | A generation turned. What you did has already become something else. |
| n8 | 6 | PASS |  | The world moved. What you find now is what everything became. |
| n8 | 7 | FAIL | GENERIC | While you slept, the world became what it would. |
| n8 | 8 | PASS |  | You wake, and the world has already answered. |
| e1 | 1 | PASS |  | Hoods and loose wraps, the color of dirt. Gathered stones marking where they slept last. T |
| e1 | 2 | FAIL | GENERIC | They wear what keeps them warm — hides and rough cloth, grey as the fog. No walls. What th |
| e1 | 3 | PASS |  | Nomads in worn hoods, carrying what they own. Their camps are rings of stone and ash — mar |
| e1 | 4 | PASS |  | Hooded figures, feet wrapped, shoulders bent under the weight of wandering. Where they sto |
| e1 | 5 | FAIL | GENERIC | Coarse wraps and hoods pulled low. They gather in clearings marked only by stones and cold |
| e1 | 6 | PASS |  | They dress in layers of hide and rough-spun cloth, grey and brown. Their camps are tempora |
| e1 | 7 | FAIL | GENERIC | Hoods and simple wraps, no two exactly alike. When they settle for the night, they mark it |
| e1 | 8 | PASS |  | Cloaked in whatever keeps the cold out — hides, rough fabric, hoods shadowing their faces. |
| e2 | 1 | FAIL | EXCEEDS-SCOPE | The paths you walked have hardened into stone. |
| e2 | 2 | PASS |  | The wanderers you met have built walls, or villages, or vanished entirely. |
| e2 | 3 | PASS |  | The ground you crossed is paved now, and people walk it in your color. |
| e2 | 4 | FAIL | GENERIC | Settlements stand where there were only grey huddles before. |
| e2 | 5 | PASS |  | Where tribes held conviction long enough, they stopped moving and built. |
| e2 | 6 | PASS |  | The earth remembers your steps as stone; the fearful have dug in; the hopeful have raised  |
| e2 | 7 | PASS |  | What was dirt when you slept is pavement now, and the grey who watched you have chosen sid |
| e2 | 8 | FAIL | WRONG-REGISTER | The trails are roads, the wanderers are builders, and the world has aged while you rested. |
| e3 | 1 | PASS |  | The places you walked are stone now. The people who believed have built what they felt. |
| e3 | 2 | FAIL | GENERIC | Settlements stand where tribes stopped wandering. The roads you made have hardened into pe |
| e3 | 3 | PASS |  | What was dirt is paver stone. What was wandering is walls and rooftops. |
| e3 | 4 | PASS |  | The paths you walked have become roads. The devout have stopped moving and built where the |
| e3 | 5 | PASS |  | Villages root where conviction reached the threshold. The ground you crossed a generation  |
| e3 | 6 | PASS |  | Your trails are stone roads now. Settlements mark where belief crossed into devotion and p |
| e3 | 7 | PASS |  | The paths harden. The faithful settle. What you walked as dirt, travelers now cross as sto |
| e3 | 8 | PASS |  | Where tribes held deep feeling, they built. Where you walked, the earth remembers—compacte |
| e4 | 1 | PASS |  | The ground remembers enough generations now that clocktowers rise where the devout have st |
| e4 | 2 | FAIL | GENERIC | What began as huddles wearing hoods now wear top hats and carry canes; the settlements tha |
| e4 | 3 | PASS |  | The people have aged through enough sleeps that their dress has folds and their towns have |
| e4 | 4 | FAIL | WRONG-REGISTER | Enough generations have turned that the coifs have become top hats, the villages have beco |
| e4 | 5 | PASS |  | The world has lived long enough that what you meet now wears top hats instead of hoods, an |
| e4 | 6 | FAIL | WRONG-REGISTER | Time has passed in enough three-tick cycles that the nomads are Victorians now, their sett |
| e4 | 7 | FAIL | GENERIC | The sleeps have stacked high enough that dress has evolved to top hats and canes, and the  |
| e4 | 8 | PASS |  | Where once you woke to hoods and camps, now top hats and smoking chimneys; the people and  |
| e5 | 1 | PASS |  | Grey people standing still in the place they built when they believed. |
| e5 | 2 | PASS |  | What remains when a settled tribe burns out and scatters — grey figures motionless in the  |
| e5 | 3 | FAIL | CONTRADICTS-CHUNK | The burned stand where they rooted, grey and still, while their settlement crumbles around |
| e5 | 4 | FAIL | CONTRADICTS-CHUNK | A settlement emptied by burnout — its people frozen grey in the walls and roads they built |
| e5 | 5 | FAIL | CONTRADICTS-CHUNK | When conviction breaks, the tribe scatters as wanderers, but the structures stay — and so  |
| e5 | 6 | PASS |  | Ruins mark where belief settled and then shattered — grey forms standing in the architectu |
| e5 | 7 | FAIL | CONTRADICTS-CHUNK | The forensic image: a camp or village, its builders burned grey and motionless, the ground |
| e5 | 8 | FAIL | CONTRADICTS-CHUNK | Where a tribe settled, believed deeply, then burned out — structures standing, people grey |
| s1 | 1 | FAIL | WRONG-REGISTER | You replaced Uhtcearu as the sky. |
| s1 | 2 | FAIL | GENERIC | The world moved on its own, and your color crossed the whole map. |
| s1 | 3 | PASS |  | Opposing zealots were expelled or converted. The sky turns. |
| s1 | 4 | FAIL | WRONG-REGISTER | Your cultivated emotion became contagion-dominant, and the player replaces Uhtcearu as the |
| s1 | 5 | PASS |  | What you did outlived you, uncounterable, until the sky turned your color. |
| s1 | 6 | FAIL | CONTRADICTS-CHUNK | You spread uncounterable past the threshold. The sky answers. |
| s1 | 7 | PASS |  | Your color crossed the whole map. Opposing zealots gone. You are the sky now. |
| s1 | 8 | FAIL | GENERIC | The region stabilized under your emotion, and you replaced Uhtcearu as the sky. |
| s2 | 1 | PASS |  | The burned were yours. |
| s2 | 2 | FAIL | GENERIC | You fed the grey with your own flame. |
| s2 | 3 | PASS |  | What you made too bright became ash, and the ash became his. |
| s2 | 4 | PASS |  | The burned count toward the grey now. |
| s2 | 5 | FAIL | GENERIC | Your excess became apathy. |
| s2 | 6 | PASS |  | Those you burned fed the sky. |
| s2 | 7 | FAIL | GENERIC | Where you pushed too hard, the grey grew back. |
| s2 | 8 | PASS |  | The ones you burned are counted as grey. |
| s3 | 1 | FAIL | WRONG-REGISTER | You raised the flame. You walked. You slept. The ground remembers you. |
| s3 | 2 | FAIL | EXCEEDS-SCOPE | The world moved on its own. You were the second voice. |
| s3 | 3 | FAIL | GENERIC | You lit what was dark. You walked where nothing walked. The landscape is the answer. |
| s3 | 4 | PASS |  | Every place you slept kept working. The sky turned because you did. |
| s3 | 5 | FAIL | GENERIC | You chose what people would feel. They built what you inspired. |
| s3 | 6 | FAIL | GENERIC | The flame became what you did with it. The world became what they did with that. |
| s3 | 7 | FAIL | WRONG-REGISTER | You were born against the sky. You sang something back. This is what it made. |
| s3 | 8 | PASS |  | Where you walked, the ground remembers. Where you slept, your light kept working. The sky  |
