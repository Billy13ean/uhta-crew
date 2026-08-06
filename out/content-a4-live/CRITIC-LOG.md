# CRITIC-LOG — every verdict, every correction

> A FAIL with no correction raises AgentError and halts the run (`content/agents/critic.py`). This file cannot contain a rejection that was not repaired.
>
> Run `content-a4-live` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-06 21:48:02

## Summary

| | |
|---|---|
| candidates judged | **128** |
| passed | 66 |
| **caught and corrected** | **62** |
| beats | 16 |

**By flag class:**

| class | count |
|---|---|
| `GENERIC` | 42 |
| `WRONG-REGISTER` | 9 |
| `EXCEEDS-SCOPE` | 8 |
| `CONTRADICTS-CHUNK` | 3 |

---

## Catches — the correction is shown, not claimed

### n1 · candidate 2 — `GENERIC`

**Rejected line**

> The flame in your hand is white and undetermined.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The white flame is genuinely undetermined

**Why** — Uses 'undetermined' as abstract descriptor rather than stating the mechanical consequence that makes it undetermined in uhta's system.

**Correction**

> The white flame becomes whatever you do with it.

---

### n1 · candidate 3 — `GENERIC`

**Rejected line**

> A white flame — what it becomes is not yet decided.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The white flame is genuinely undetermined

**Why** — Speaks about future possibility ('not yet decided') rather than naming the verb-consequence relationship the tutorial demands.

**Correction**

> The white flame takes the color of what you do.

---

### n1 · candidate 4 — `GENERIC`

**Rejected line**

> You carry a flame that has no color of its own.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The flame in your hand is your alignment

**Why** — Describes what the flame lacks rather than the mechanical consequence — no verb, no stated outcome.

**Correction**

> The flame in your hand is white — your actions will color it.

---

### n1 · candidate 6 — `GENERIC`

**Rejected line**

> In your hand: a flame, white, holding no feeling yet.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — The colon construction and 'holding no feeling yet' is descriptive mood rather than declarative instrumentation.

**Correction**

> The white flame holds no feeling — it will take yours.

---

### n1 · candidate 7 — `GENERIC`

**Rejected line**

> The flame is yours, white and empty of intent.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — 'Empty of intent' is abstract characterization; no verb named, no consequence stated.

**Correction**

> The flame is white — where you walk, what you do, it remembers.

---

### n2 · candidate 4 — `GENERIC`

**Rejected line**

> Walk across the land. Each tile you cross becomes a road. Roads carry your color.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> roads now carry your color

**Why** — Omits that roads carry your color, reducing it to generic path-making without uhta's specific allegiance mechanic.

**Correction**

> Walk across the land. Each tile you cross becomes a road that carries your color.

---

### n2 · candidate 8 — `WRONG-REGISTER`

**Rejected line**

> Walk. Every tile becomes a road that carries what you are, and people will walk it after you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The narration is instrumentation, not lore — short declarative lines, no mythology

**Why** — "carries what you are" is mythological phrasing where the register demands mechanical instrumentation like "carries your color."

**Correction**

> Walk. Every tile becomes a road that carries your color, and people will walk it after you.

---

### n3 · candidate 1 — `EXCEEDS-SCOPE`

**Rejected line**

> Raise the flame. It applies what you feel right now.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the flame applies what you feel

**Why** — The chunk says 'what you feel' not 'what you feel right now' — the temporal qualifier adds emphasis the source doesn't support and implies a volatility the mechanic doesn't have.

**Correction**

> Raise the flame. It applies what you feel.

---

### n3 · candidate 2 — `GENERIC`

**Rejected line**

> Wave the flame — it spreads whatever color you're holding.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> applies the flame's current alignment to NPCs in radius

**Why** — Could describe any alignment-spreading mechanic in any game — loses the emotional framing ('what you feel') that makes it uhta-specific.

**Correction**

> Wave the flame — it applies what you feel to everyone nearby.

---

### n3 · candidate 4 — `GENERIC`

**Rejected line**

> The flame clears fog and applies your alignment to those nearby.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the flame applies what you feel

**Why** — Reads like a feature list — 'clears fog and applies alignment' — with no emotional consequence surviving; could be any fog-of-war mechanic.

**Correction**

> The flame applies what you feel to those who see it.

---

### n3 · candidate 8 — `GENERIC`

**Rejected line**

> The flame applies its current color to everyone in reach.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the flame applies what you feel

**Why** — Completely mechanistic ('current color', 'everyone in reach') — the emotional source ('what you feel') that distinguishes uhta is absent.

**Correction**

> The flame applies what you feel to everyone in reach.

---

### n4 · candidate 3 — `GENERIC`

**Rejected line**

> This is the roar. It frightens all who witness it, no matter what your flame carries.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the roar frightens all who witness it, whatever you intend

**Why** — Loses the terrain-shattering effect entirely and 'what your flame carries' is vague where the chunk specifies 'whatever you intend' as the paradox.

**Correction**

> This is the roar. It shatters the ground ahead, and frightens all who witness it — whatever you intend.

---

### n4 · candidate 4 — `GENERIC`

**Rejected line**

> You roar to shatter the ground — but know this: everyone within sight will fear you, regardless of your light.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Shatters a line of tiles — fast traversal / path creation

**Why** — 'Clears distance fast' is missing from the chunk vocabulary; 'within sight' dilutes the witness-radius mechanic to generic visibility.

**Correction**

> You roar to shatter a line through the ground — but everyone who witnesses it will fear you, whatever you intend.

---

### n4 · candidate 6 — `WRONG-REGISTER`

**Rejected line**

> Roar, and the stone breaks open — yet every soul who sees you do it learns fear, whether you mean them to or not.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the roar frightens all who witness it, whatever you intend

**Why** — 'Every soul who sees you do it learns fear' mythologizes where the tutorial demands instrumentation; 'learns fear' is pedagogical metaphor, not mechanical consequence.

**Correction**

> Roar, and the stone breaks open — but everyone who witnesses it takes fear, whatever you intend.

---

### n5 · candidate 3 — `GENERIC`

**Rejected line**

> You do nothing. Nearby, indifference takes root.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy

**Why** — "Indifference takes root" is poetic metaphor where the chunks demand mechanical consequence—apathy is a push, not vegetation.

**Correction**

> You do nothing. Nearby NPCs drift toward apathy.

---

### n5 · candidate 6 — `GENERIC`

**Rejected line**

> To wait is to be forgotten. The nearby lose their color.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> waiting teaches people you don't matter

**Why** — "To be forgotten" romanticizes the mechanic into narrative consequence instead of stating the apathy push as instrumentation.

**Correction**

> You wait. The nearby lose feeling and drift toward grey.

---

### n5 · candidate 8 — `GENERIC`

**Rejected line**

> Waiting is a choice. It makes you matter less to those who witness it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> witnessed inaction pushes nearby NPCs toward Apathy (~0.5)

**Why** — "Makes you matter less" dilutes the mechanical apathy push into vague relational consequence any god-game could claim.

**Correction**

> Waiting is a choice. It pushes witnesses toward apathy.

---

### n6 · candidate 1 — `GENERIC`

**Rejected line**

> You light the basin. It reveals the land around you and gives you strength that lasts.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — The chunk specifies 'ruined basin' but the candidate says only 'basin,' losing the specific environmental detail that distinguishes uhta's world-building.

**Correction**

> You light the ruined basin. It reveals the land around you and gives you strength that lasts.

---

### n6 · candidate 2 — `EXCEEDS-SCOPE`

**Rejected line**

> Light a beacon. It clears the fog and the strength it gives you persists.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — The chunk calls it a 'ruined basin' not a 'beacon' — beacon is the verb name but the object in the tutorial moment is specifically a ruined basin.

**Correction**

> Light the ruined basin. It clears the fog and the strength it gives you persists.

---

### n6 · candidate 4 — `EXCEEDS-SCOPE`

**Rejected line**

> Light a beacon. The world around it becomes visible, and its strength becomes yours.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — Calls it 'a beacon' when the tutorial moment specifies 'a ruined basin' — the object type matters to the environmental storytelling.

**Correction**

> Light the ruined basin. The world around it becomes visible, and its strength becomes yours.

---

### n6 · candidate 5 — `WRONG-REGISTER`

**Rejected line**

> The basin lights. Fog lifts where it burns, and the strength you gain does not fade.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — Opens with 'The basin lights' (passive, mythological tone) instead of the required second-person imperative that names the verb.

**Correction**

> You light the ruined basin. Fog lifts where it burns, and the strength you gain does not fade.

---

### n6 · candidate 6 — `EXCEEDS-SCOPE`

**Rejected line**

> You light a beacon. It shows you the hidden land and its power stays with you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — Says 'a beacon' instead of 'a ruined basin' — loses the specific environmental object from the tutorial sequence.

**Correction**

> You light the ruined basin. It shows you the hidden land and its power stays with you.

---

### n6 · candidate 7 — `GENERIC`

**Rejected line**

> Light the basin. It reveals what was hidden and makes you stronger, even after you leave.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — Omits 'ruined' from 'ruined basin,' stripping the environmental specificity that makes this uhta's world rather than any god-game.

**Correction**

> Light the ruined basin. It reveals what was hidden and makes you stronger, even after you leave.

---

### n6 · candidate 8 — `EXCEEDS-SCOPE`

**Rejected line**

> You light a beacon. The fog around it clears, and you carry its strength forward.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength

**Why** — Calls it 'a beacon' when the chunk specifies the tutorial object is 'a ruined basin' — the distinction is load-bearing for the world's archaeology.

**Correction**

> You light the ruined basin. The fog around it clears, and you carry its strength forward.

---

### n7 · candidate 1 — `WRONG-REGISTER`

**Rejected line**

> You sleep. A generation passes — and your body keeps radiating, every tick, over everyone near where you lie down.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — The phrase 'every tick' exposes system implementation language that the player never sees in the register demanded.

**Correction**

> You sleep. A generation passes — and your body keeps radiating over everyone near where you lie down.

---

### n7 · candidate 3 — `GENERIC`

**Rejected line**

> You sleep here. Generations pass. The ground around your body glows with what you feel, until you wake.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — Loses the mechanical specificity that the radiation happens 'every tick' and affects NPCs, reducing it to vague glowing ground.

**Correction**

> You sleep here. Generations pass. Your body radiates over everyone nearby, every moment, until you wake.

---

### n7 · candidate 4 — `WRONG-REGISTER`

**Rejected line**

> Sleep. One generation. Your sleeping body radiates over the ground you chose — the flame never stops.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — The phrase 'One generation' as a sentence fragment breaks the declarative register and reads like stage direction.

**Correction**

> Sleep. A generation passes. Your sleeping body radiates over the ground you chose — the flame never stops.

---

### n7 · candidate 5 — `GENERIC`

**Rejected line**

> You sleep — and a generation turns. Where you lie down matters: your light keeps spreading while you dream.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — The phrase 'light keeps spreading' loses the mechanical truth that it radiates to NPCs, not just spreads aesthetically.

**Correction**

> You sleep — and a generation turns. Where you lie down matters: your flame keeps radiating while you dream.

---

### n7 · candidate 6 — `GENERIC`

**Rejected line**

> Sleep advances time. Your body stays, glowing, touching everyone near where you chose to rest.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — The phrase 'touching everyone' is metaphorical where the chunks specify mechanical radiation of emotion to NPCs.

**Correction**

> Sleep advances time. Your body stays, radiating the flame's emotion to everyone near where you chose to rest.

---

### n7 · candidate 7 — `WRONG-REGISTER`

**Rejected line**

> You sleep. The world ages. The sleeping body radiates your color across the ground, every tick, until dawn.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> short declarative lines, no mythology

**Why** — The phrase 'every tick, until dawn' exposes system timing language inappropriate for the tutorial register.

**Correction**

> You sleep. The world ages. Your sleeping body radiates your color across the ground until you wake.

---

### n7 · candidate 8 — `GENERIC`

**Rejected line**

> Sleep here and the cycle ends. A generation passes over your glowing body — location is the last choice you make.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation

**Why** — The phrase 'glowing body' aestheticizes what is mechanically a continuous emotional radiation to NPCs in radius.

**Correction**

> Sleep here and the cycle ends. A generation passes, and your body radiates over everyone nearby — location is the last choice you make.

---

### n8 · candidate 2 — `GENERIC`

**Rejected line**

> The world has changed while you slept.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> a generation has passed, and the world has *moved on its own*

**Why** — Loses the canonical 'moved on its own' phrasing that distinguishes uhta's generational agency from generic time-passage.

**Correction**

> A generation has passed. The world moved on its own.

---

### n8 · candidate 5 — `GENERIC`

**Rejected line**

> While you slept, the world answered.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the world has *moved on its own*

**Why** — Replaces the specific 'moved on its own' with vague 'answered' — loses the autonomous agency that defines generational sleep.

**Correction**

> The world moved on its own while you slept.

---

### e1 · candidate 1 — `GENERIC`

**Rejected line**

> Gathered figures in rough hoods, hands empty, standing where they stopped wandering — tents of hide and cloth, no walls, fires in open pits.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> hood → coif → top hat

**Why** — Describes generic nomad aesthetics without anchoring to uhta's era-progression system where hoods are the locked Nomad/Tribal costume that will age into coifs then top hats.

**Correction**

> Gathered figures in hoods — the Nomad dress, locked to this era — standing where they stopped wandering, tents of hide and cloth with no walls, fires in open pits.

---

### e1 · candidate 2 — `GENERIC`

**Rejected line**

> The nomads wear simple hoods that cover their heads, shoulders bare or wrapped in undyed cloth, carrying nothing but what they can walk with.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> hood → coif → top hat

**Why** — Generic description of nomad clothing with no mechanical or systemic anchor to uhta's era art or settling behavior.

**Correction**

> The nomads wear hoods — the first-era dress — shoulders bare or wrapped in undyed cloth, and they carry nothing because unsettled tribes drift as a cohesive body within a home box.

---

### e1 · candidate 3 — `GENERIC`

**Rejected line**

> Compacted earth paths between hide shelters — no stone, no permanence — the people dressed in hoods and wraps, their camps circles of bent poles and stretched skins.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A freshly walked trail renders as compacted earth — the ground remembering you

**Why** — Mentions compacted earth paths but divorces them from the player-walked road mechanic that creates them and their allegiance coloring.

**Correction**

> Compacted earth paths between hide shelters — player-walked trails, the ground remembering you — no stone yet, no permanence, the people in hoods and wraps, their camps circles of bent poles and stretched skins.

---

### e1 · candidate 4 — `GENERIC`

**Rejected line**

> Rough hoods and loose garments, all of it meant to be carried, and the settlements are just where they set it down — rings of low tents around communal fires.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles as what it feels

**Why** — Describes generic temporary camps without connecting to the settling rule — that these are unsettled tribes still drifting, not yet devout enough to root.

**Correction**

> Rough hoods and loose garments, all of it meant to be carried — unsettled tribes drifting within their home box — and the camps are just where they set it down, rings of low tents around communal fires, not yet rooted.

---

### e1 · candidate 6 — `GENERIC`

**Rejected line**

> Hoods pulled forward, cloth wrapping the body in layers that can be shed or added, and the camps are temporary even when they root — circles of hide tents, fire-rings, and beaten earth.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles

**Why** — Describes camps as 'temporary even when they root' which contradicts the settling rule that rooting is permanent and irreversible.

**Correction**

> Hoods pulled forward, cloth wrapping the body in layers that can be shed or added, and the camps are still temporary — circles of hide tents, fire-rings, and beaten earth — because these tribes have not yet held devout conviction long enough to settle permanently.

---

### e1 · candidate 7 — `GENERIC`

**Rejected line**

> They dress in hooded wraps and carry their belongings on their backs, and where they settle the structures are low and open — bent frames covered in skins, smoke rising from uncovered fires.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Unsettled tribes drift as a cohesive body within a home box (~9 tiles)

**Why** — Generic nomad imagery with no mechanical anchor to uhta's wander system, settling threshold, or the distinction between drifting and rooted tribes.

**Correction**

> They dress in hooded wraps and carry their belongings on their backs — unsettled, drifting within their home box — and where they stop the structures are low and open, bent frames covered in skins, smoke rising from uncovered fires, not yet permanent.

---

### e1 · candidate 8 — `GENERIC`

**Rejected line**

> Simple hoods and layered cloth, no decoration, no metal, and the settlements are clusters of rounded shelters made from what grows or can be dragged — timber frames, hides, woven grass, and the ground they've trampled flat.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> hood → coif → top hat

**Why** — Lists generic materials without connecting hoods to era-locked costume or trampled ground to the player-walked road system that creates compacted earth.

**Correction**

> Hoods — the Nomad-era dress — and layered cloth with no decoration, no metal, and the settlements are clusters of rounded shelters made from what grows or can be dragged, timber frames and hides, standing on ground trampled flat by wandering or compacted where the player walked.

---

### e2 · candidate 7 — `GENERIC`

**Rejected line**

> A generation has passed. The nomads have chosen where to root.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles as what it feels

**Why** — Says 'chosen where to root' when uhta's settling rule is mechanical (devout threshold held for a generation), not volitional choice.

**Correction**

> A generation has passed. The nomads who crossed the threshold have settled as what they feel.

---

### e3 · candidate 2 — `GENERIC`

**Rejected line**

> Where people stopped wandering, they built. Roads have hardened into stone. The settlements that rooted here carry what you did, and what the world did without you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Where tribes crossed the threshold of feeling, they stopped moving and raised walls.

**Why** — Loses the asymmetric settlement identity (Hope settlements vs Fear walled camps) that is core to uhta's pole mechanics.

**Correction**

> Roads have hardened into stone. Where tribes crossed the threshold of feeling, they stopped wandering — Hope rooted into settlements, Fear dug into walled camps.

---

### e3 · candidate 5 — `GENERIC`

**Rejected line**

> The paths are stone. The wanderers have settled. What was temporary when you last woke has rooted — villages stand where devotion held, and the roads you walked carry the next generation.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Each tribe adds ~2 regular NPCs per sleep (after the world forms; genesis suppresses births during formation, and schism's pop-cap bounds it thereafter). Newborns start at 0 — apathy.

**Why** — The phrase 'have children now' invokes the newborn mechanic but loses the critical detail that newborns are born grey/apathetic, not inheriting belief.

**Correction**

> The paths are stone. The wanderers have settled. What was temporary when you last woke has rooted — villages stand where devotion held, and the roads you walked carry the next generation born grey into a colored world.

---

### e3 · candidate 8 — `GENERIC`

**Rejected line**

> The trails are stone. Where feeling took root, people built and stayed. The world you wake to is no longer scattered and grey — it has hardened into roads, walls, and the choices that outlived you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> A tribe whose average enters the devout band (|value| ≥ 6) and holds it for a generation stops wandering and settles as what it feels — Hope roots into an open settlement, Fear digs into a walled camp.

**Why** — The phrase 'no longer scattered and grey' is generic; it loses the specific genesis state (grey nomad loners) and the asymmetric settlement forms.

**Correction**

> The trails are stone. Where feeling took root, people built and stayed — Hope settlements, Fear walled camps. The world you wake to has hardened into roads, walls, and the choices that outlived you.

---

### e4 · candidate 5 — `EXCEEDS-SCOPE`

**Rejected line**

> The second age: factories rise where settlements stood, their smoke climbing into the grey. Everyone who built them is wearing a top hat.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Settlement structures age with it — nomad camps → villages → towns with **clocktowers and smoking factories**.

**Why** — "Everyone who built them" implies NPCs constructed the factories, but the chunks specify only that structures age with era thresholds derived from sleep count — no builder agency is supported.

**Correction**

> Factories rise where settlements stood, their smoke climbing into the grey, and everyone is wearing a top hat now.

---

### e4 · candidate 6 — `GENERIC`

**Rejected line**

> The settlements have aged into towns. Clocktowers mark the hours now, and smoke rises from every roof.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Settlement structures age with it — nomad camps → villages → towns with **clocktowers and smoking factories**.

**Why** — "mark the hours" is generic clock symbolism; the chunk names clocktowers as a specific Victorian structure marker, not a functional timepiece.

**Correction**

> The settlements have aged into towns. Clocktowers stand above them now, and smoke rises from the factories.

---

### e4 · candidate 7 — `GENERIC`

**Rejected line**

> Top hats and factory smoke. The villages have become industrial, and the people dress like they remember when they weren't.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> NPC dress ages with it: **hood → coif → top hat**, gaining **staffs, satchels and canes**, garment folds and face shading.

**Why** — "dress like they remember when they weren't" is generic nostalgia; the chunk specifies dress ages with era thresholds, not that NPCs have memory or self-awareness about it.

**Correction**

> Top hats and factory smoke. The villages have become industrial towns, and the people wear Victorian dress now.

---

### e5 · candidate 2 — `EXCEEDS-SCOPE`

**Rejected line**

> They stand motionless where their settlement once rooted, grey now, the color they wore before the burnout drained from their bodies.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> burnout = grey with a faint ring of the frozen color

**Why** — Claims the burnout color 'drained from their bodies' — the chunks specify burnout shows as a faint ring, not that color drains or was previously visible on bodies.

**Correction**

> They stand motionless where their settlement once rooted, grey now, wearing faint rings of the color that froze when they burned out.

---

### e5 · candidate 5 — `WRONG-REGISTER`

**Rejected line**

> A settlement emptied of belief but not of people — they stand where they rooted, grey, the burnout flag still faintly visible as rings around them.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> burnout flag

**Why** — Uses 'burnout flag' — a system term from the implementation layer — where the register demands only what is visible.

**Correction**

> A settlement emptied of belief but not of people — they stand where they rooted, grey, wearing faint rings of what they used to feel.

---

### e5 · candidate 7 — `CONTRADICTS-CHUNK`

**Rejected line**

> Ruins are not empty — grey people stand in them, still settled, no longer able to leave, wearing the faint trace of the pole that burned them out.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased) and can be **re-adopted**

**Why** — Claims burned NPCs are 'no longer able to leave' and 'exiled from movement' — chunks state burnout detaches them as wanderers who drift.

**Correction**

> Ruins are not empty — grey people stand in them, detached as lone wanderers, wearing the faint trace of the pole that burned them out, drifting until re-adopted.

---

### e5 · candidate 8 — `CONTRADICTS-CHUNK`

**Rejected line**

> Where a tribe settled and then shattered: the walls or camps remain, and inside them the burned stand grey and motionless, exiled from movement but rooted by the settling rule.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> burnout**, which detaches the broken NPC as a **lone wanderer** (`loner_tribe_id −1`) that drifts (road-biased)

**Why** — States burned NPCs are 'rooted by the settling rule' and cannot move — chunks specify burnout detaches them as drifting loners.

**Correction**

> Where a tribe settled and then shattered: the walls or camps remain, and the burned detach as grey wanderers, wearing faint rings of the pole that broke them, drifting road-biased until re-adopted.

---

### s1 · candidate 2 — `GENERIC`

**Rejected line**

> They cowered. They straightened. They built in your color. The world moved on its own, and it moved toward you.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> the player replaces Uhtcearu as the sky

**Why** — "The world moved on its own" is the emotional centerpiece of waking, not the win state; this reads like any god-game's victory without citing the mechanical unification or sky-replacement.

**Correction**

> They cowered. They straightened. They built in your color. The unification held. The sky is yours.

---

### s1 · candidate 3 — `GENERIC`

**Rejected line**

> The huddle you met is gone. What you find instead is the answer. The sky turns.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The huddle you met is gone. What you find instead is the answer

**Why** — Quotes the waking moment but strips all mechanical consequence — "the answer" and "the sky turns" are empty without the unification threshold or color-replacement.

**Correction**

> The huddle you met is gone. What you find instead is the answer: the whole map in your color, and the sky turns.

---

### s1 · candidate 4 — `WRONG-REGISTER`

**Rejected line**

> You lit the basin. You spent your last action. You slept, and your light kept working. They are yours now.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> you light a ruined basin and it gives you strength... where you sleep, your light keeps working

**Why** — "They are yours now" implies possession of NPCs, but the win condition is unification-dominance and sky-replacement, not ownership — wrong framing for the thesis.

**Correction**

> You lit the basin. You spent your last action. You slept, and your light kept working. The sky has turned your color.

---

### s1 · candidate 5 — `GENERIC`

**Rejected line**

> Every settlement that formed, every road that hardened, every tribe that stopped wandering — the landscape is the score. You won it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The landscape is the score

**Why** — Correctly quotes that landscape-is-score but "you won it" is generic victory language; the win state is sky-replacement after unification, not territorial conquest.

**Correction**

> Every settlement that formed, every road that hardened, every tribe that stopped wandering — the landscape became the score, and the sky turned your color.

---

### s1 · candidate 6 — `CONTRADICTS-CHUNK`

**Rejected line**

> The grey closed in, then turned. The zealot you never met now burns for you. The sky answers: it is your color.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> no living opposing zealot

**Why** — "The zealot you never met now burns for you" describes a captured champion (mid-game forensics), but the win condition explicitly requires "no living opposing zealot."

**Correction**

> The grey closed in, then turned. The last opposing zealot fell. The sky answers: it is your color.

---

### s2 · candidate 2 — `WRONG-REGISTER`

**Rejected line**

> Your excess fed the sky.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> The teacher's voice returning once, after a whole game of silence. Short. States what the player did, not what it means.

**Why** — The register demands stating what the player did, but this interprets meaning ('fed the sky') rather than stating the mechanical action.

**Correction**

> You burned too many.

---

### s2 · candidate 5 — `GENERIC`

**Rejected line**

> Apathy claimed what you left behind.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Apathy (soft grey **plus burned** NPCs) passes the dominance threshold

**Why** — Generic god-game language ('claimed what you left behind') loses the specific mechanic that apathy is a counted band including burned NPCs.

**Correction**

> Apathy passed the threshold.

---

### s3 · candidate 2 — `GENERIC`

**Rejected line**

> You raised the flame, and they answered.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> as each verb is first used, it is named and its consequence stated plainly

**Why** — Says 'they answered' without stating what mechanical consequence the flame produces — could mean anything in any god-game.

**Correction**

> You raised the flame. It applied what you felt.

---

### s3 · candidate 4 — `GENERIC`

**Rejected line**

> The world moved. You moved with it.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> Waking is the emotional centerpiece. The landscape is the same, but different — a generation has passed, and the world has moved on its own.

**Why** — Describes the player moving with the world when the chunks establish the player wakes to find the world moved *without* them — inverts the core asymmetry.

**Correction**

> The world moved without you. You woke to what it became.

---

### s3 · candidate 6 — `GENERIC`

**Rejected line**

> What you felt, they carried forward.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> as each verb is first used, it is named and its consequence stated plainly

**Why** — Uses 'what you felt' as metaphor when the chunks demand plain statement of mechanical consequence — no verb is named.

**Correction**

> The flame applied what you felt. They became it.

---

### s3 · candidate 8 — `EXCEEDS-SCOPE`

**Rejected line**

> They stopped wandering. You showed them why.

**Chunk it breaks** (quoted by the Critic from the text the Writer was given)

> waiting teaches people you don't matter

**Why** — Inverts the waiting consequence — chunks say waiting teaches them you don't matter (they ignore you), not that you showed them why to stop wandering.

**Correction**

> You acted. They stopped wandering.

---

## Full verdict table

| beat | # | verdict | class | line |
|---|---|---|---|---|
| n1 | 1 | PASS |  | You hold a white flame that lights only the stone around you. |
| n1 | 2 | FAIL | GENERIC | The flame in your hand is white and undetermined. |
| n1 | 3 | FAIL | GENERIC | A white flame — what it becomes is not yet decided. |
| n1 | 4 | FAIL | GENERIC | You carry a flame that has no color of its own. |
| n1 | 5 | PASS |  | The white flame waits — it will become whatever you do with it. |
| n1 | 6 | FAIL | GENERIC | In your hand: a flame, white, holding no feeling yet. |
| n1 | 7 | FAIL | GENERIC | The flame is yours, white and empty of intent. |
| n1 | 8 | PASS |  | You wake holding white fire — neither path is written into it. |
| n2 | 1 | PASS |  | You walk, and the ground remembers you — every tile you cross becomes a road that carries  |
| n2 | 2 | PASS |  | Walk. The ground remembers you. Every tile becomes a road, and roads carry your color forw |
| n2 | 3 | PASS |  | Where you walk, the earth becomes road — and roads carry your color to those who travel th |
| n2 | 4 | FAIL | GENERIC | Walk across the land. Each tile you cross becomes a road. Roads carry your color. |
| n2 | 5 | PASS |  | You walk. The ground you cross becomes road, and every road now carries your color. |
| n2 | 6 | PASS |  | Walk: the tiles you cross become roads. Roads carry your color, and people will travel the |
| n2 | 7 | PASS |  | Each step makes road. Roads carry your color — and people follow roads. |
| n2 | 8 | FAIL | WRONG-REGISTER | Walk. Every tile becomes a road that carries what you are, and people will walk it after y |
| n3 | 1 | FAIL | EXCEEDS-SCOPE | Raise the flame. It applies what you feel right now. |
| n3 | 2 | FAIL | GENERIC | Wave the flame — it spreads whatever color you're holding. |
| n3 | 3 | PASS |  | Raise the flame. Everyone who sees it takes on your current feeling. |
| n3 | 4 | FAIL | GENERIC | The flame clears fog and applies your alignment to those nearby. |
| n3 | 5 | PASS |  | Raise the flame — it pushes your present emotion outward. |
| n3 | 6 | PASS |  | Wave the flame. It isn't healing. It's whatever you are. |
| n3 | 7 | PASS |  | Raise the flame. It spreads the feeling you carry, not the one they need. |
| n3 | 8 | FAIL | GENERIC | The flame applies its current color to everyone in reach. |
| n4 | 1 | PASS |  | You can roar — and everyone who witnesses it will fear you, whatever you intend. |
| n4 | 2 | PASS |  | Roar. The earth shatters ahead of you, and everyone who sees it is frightened — even if yo |
| n4 | 3 | FAIL | GENERIC | This is the roar. It frightens all who witness it, no matter what your flame carries. |
| n4 | 4 | FAIL | GENERIC | You roar to shatter the ground — but know this: everyone within sight will fear you, regar |
| n4 | 5 | PASS |  | The roar clears distance fast, but whoever witnesses the line takes fear — your flame's co |
| n4 | 6 | FAIL | WRONG-REGISTER | Roar, and the stone breaks open — yet every soul who sees you do it learns fear, whether y |
| n4 | 7 | PASS |  | You can roar a path through the earth. Everyone who watches will be pushed toward fear. Yo |
| n4 | 8 | PASS |  | This is roar: it splits the ground and makes witnesses afraid, even when your flame is gre |
| n5 | 1 | PASS |  | You wait. Those who watch learn you do not matter. |
| n5 | 2 | PASS |  | When you withhold, the watchers drift toward apathy. |
| n5 | 3 | FAIL | GENERIC | You do nothing. Nearby, indifference takes root. |
| n5 | 4 | PASS |  | Wait, and you teach the people watching that you are not worth their feeling. |
| n5 | 5 | PASS |  | Inaction is witnessed. It pushes them toward grey. |
| n5 | 6 | FAIL | GENERIC | To wait is to be forgotten. The nearby lose their color. |
| n5 | 7 | PASS |  | You hold back. Those who see it move toward apathy. |
| n5 | 8 | FAIL | GENERIC | Waiting is a choice. It makes you matter less to those who witness it. |
| n6 | 1 | FAIL | GENERIC | You light the basin. It reveals the land around you and gives you strength that lasts. |
| n6 | 2 | FAIL | EXCEEDS-SCOPE | Light a beacon. It clears the fog and the strength it gives you persists. |
| n6 | 3 | PASS |  | You light the ruined basin. The land reveals itself, and you are made stronger. |
| n6 | 4 | FAIL | EXCEEDS-SCOPE | Light a beacon. The world around it becomes visible, and its strength becomes yours. |
| n6 | 5 | FAIL | WRONG-REGISTER | The basin lights. Fog lifts where it burns, and the strength you gain does not fade. |
| n6 | 6 | FAIL | EXCEEDS-SCOPE | You light a beacon. It shows you the hidden land and its power stays with you. |
| n6 | 7 | FAIL | GENERIC | Light the basin. It reveals what was hidden and makes you stronger, even after you leave. |
| n6 | 8 | FAIL | EXCEEDS-SCOPE | You light a beacon. The fog around it clears, and you carry its strength forward. |
| n7 | 1 | FAIL | WRONG-REGISTER | You sleep. A generation passes — and your body keeps radiating, every tick, over everyone  |
| n7 | 2 | PASS |  | Sleep ends the cycle. The world moves without you, but where you sleep, the flame keeps wo |
| n7 | 3 | FAIL | GENERIC | You sleep here. Generations pass. The ground around your body glows with what you feel, un |
| n7 | 4 | FAIL | WRONG-REGISTER | Sleep. One generation. Your sleeping body radiates over the ground you chose — the flame n |
| n7 | 5 | FAIL | GENERIC | You sleep — and a generation turns. Where you lie down matters: your light keeps spreading |
| n7 | 6 | FAIL | GENERIC | Sleep advances time. Your body stays, glowing, touching everyone near where you chose to r |
| n7 | 7 | FAIL | WRONG-REGISTER | You sleep. The world ages. The sleeping body radiates your color across the ground, every  |
| n7 | 8 | FAIL | GENERIC | Sleep here and the cycle ends. A generation passes over your glowing body — location is th |
| n8 | 1 | PASS |  | A generation has passed, and the world moved without you. |
| n8 | 2 | FAIL | GENERIC | The world has changed while you slept. |
| n8 | 3 | PASS |  | They built what you left behind. |
| n8 | 4 | PASS |  | A generation passed. The ground remembers. |
| n8 | 5 | FAIL | GENERIC | While you slept, the world answered. |
| n8 | 6 | PASS |  | What you did outlasted you — or it didn't. |
| n8 | 7 | PASS |  | The world moved on its own. |
| n8 | 8 | PASS |  | You wake. A generation has passed, and they chose. |
| e1 | 1 | FAIL | GENERIC | Gathered figures in rough hoods, hands empty, standing where they stopped wandering — tent |
| e1 | 2 | FAIL | GENERIC | The nomads wear simple hoods that cover their heads, shoulders bare or wrapped in undyed c |
| e1 | 3 | FAIL | GENERIC | Compacted earth paths between hide shelters — no stone, no permanence — the people dressed |
| e1 | 4 | FAIL | GENERIC | Rough hoods and loose garments, all of it meant to be carried, and the settlements are jus |
| e1 | 5 | PASS |  | The wanderers wear hoods that shadow their faces, garments loose enough to walk in, and wh |
| e1 | 6 | FAIL | GENERIC | Hoods pulled forward, cloth wrapping the body in layers that can be shed or added, and the |
| e1 | 7 | FAIL | GENERIC | They dress in hooded wraps and carry their belongings on their backs, and where they settl |
| e1 | 8 | FAIL | GENERIC | Simple hoods and layered cloth, no decoration, no metal, and the settlements are clusters  |
| e2 | 1 | PASS |  | The paths you walked last season have hardened into stone. |
| e2 | 2 | PASS |  | Where grey wanderers drifted, a settlement now stands. |
| e2 | 3 | PASS |  | The huddle you met is gone. In its place, walls. |
| e2 | 4 | PASS |  | Dirt trails you pressed with your feet now carry travelers in your color. |
| e2 | 5 | PASS |  | The people you left behind have stopped wandering and built. |
| e2 | 6 | PASS |  | The ground you walked remembers you — your trails are now paved. |
| e2 | 7 | FAIL | GENERIC | A generation has passed. The nomads have chosen where to root. |
| e2 | 8 | PASS |  | What was loose earth beneath your feet is now worked stone. |
| e3 | 1 | PASS |  | The dirt paths you walked are paver stone now. The huddles you met have settled and built. |
| e3 | 2 | FAIL | GENERIC | Where people stopped wandering, they built. Roads have hardened into stone. The settlement |
| e3 | 3 | PASS |  | The ground remembers everywhere you walked — stone roads now, carrying travelers in your c |
| e3 | 4 | PASS |  | Trails have become stone. The nomads you met have children now, and some have built where  |
| e3 | 5 | FAIL | GENERIC | The paths are stone. The wanderers have settled. What was temporary when you last woke has |
| e3 | 6 | PASS |  | Stone roads connect what were dirt paths. Tribes that reached conviction have built and st |
| e3 | 7 | PASS |  | Your footprints are stone roads now. Tribes have stopped drifting and raised what they bel |
| e3 | 8 | FAIL | GENERIC | The trails are stone. Where feeling took root, people built and stayed. The world you wake |
| e4 | 1 | PASS |  | The wanderers have built clocktowers. The chimneys are smoking now. |
| e4 | 2 | PASS |  | Top hats and canes. The settlements have grown factories, and time has written itself in b |
| e4 | 3 | PASS |  | The coifs are gone — everyone is wearing top hats now, and the villages have become towns  |
| e4 | 4 | PASS |  | Clocktowers stand where the villages were. The people wear top hats and carry canes, and t |
| e4 | 5 | FAIL | EXCEEDS-SCOPE | The second age: factories rise where settlements stood, their smoke climbing into the grey |
| e4 | 6 | FAIL | GENERIC | The settlements have aged into towns. Clocktowers mark the hours now, and smoke rises from |
| e4 | 7 | FAIL | GENERIC | Top hats and factory smoke. The villages have become industrial, and the people dress like |
| e4 | 8 | PASS |  | The world has built its second skin: clocktowers, smoking chimneys, top hats on everyone w |
| e5 | 1 | PASS |  | Grey people standing still in the place they built when they believed. |
| e5 | 2 | FAIL | EXCEEDS-SCOPE | They stand motionless where their settlement once rooted, grey now, the color they wore be |
| e5 | 3 | PASS |  | The structures remain where devotion settled them, but the people inside are grey and stil |
| e5 | 4 | PASS |  | What's left when a settled tribe burns out: grey figures that no longer wander, standing i |
| e5 | 5 | FAIL | WRONG-REGISTER | A settlement emptied of belief but not of people — they stand where they rooted, grey, the |
| e5 | 6 | PASS |  | The buildings mark where they stopped wandering and dug in; the grey motionless figures in |
| e5 | 7 | FAIL | CONTRADICTS-CHUNK | Ruins are not empty — grey people stand in them, still settled, no longer able to leave, w |
| e5 | 8 | FAIL | CONTRADICTS-CHUNK | Where a tribe settled and then shattered: the walls or camps remain, and inside them the b |
| s1 | 1 | PASS |  | You walked, and the ground remembered you. You roared, and they heard. You slept where you |
| s1 | 2 | FAIL | GENERIC | They cowered. They straightened. They built in your color. The world moved on its own, and |
| s1 | 3 | FAIL | GENERIC | The huddle you met is gone. What you find instead is the answer. The sky turns. |
| s1 | 4 | FAIL | WRONG-REGISTER | You lit the basin. You spent your last action. You slept, and your light kept working. The |
| s1 | 5 | FAIL | GENERIC | Every settlement that formed, every road that hardened, every tribe that stopped wandering |
| s1 | 6 | FAIL | CONTRADICTS-CHUNK | The grey closed in, then turned. The zealot you never met now burns for you. The sky answe |
| s1 | 7 | PASS |  | You raised the flame and the fog cleared. You walked and they followed. You slept and the  |
| s1 | 8 | PASS |  | Where you chose to lie down mattered. The sleeping body glowed. The generations passed. Wh |
| s2 | 1 | PASS |  | The burned count toward the grey. |
| s2 | 2 | FAIL | WRONG-REGISTER | Your excess fed the sky. |
| s2 | 3 | PASS |  | What you burned became his. |
| s2 | 4 | PASS |  | The grey you made closed in. |
| s2 | 5 | FAIL | GENERIC | Apathy claimed what you left behind. |
| s2 | 6 | PASS |  | The burned were counted against you. |
| s2 | 7 | PASS |  | You fed Uhtcearu his victory. |
| s2 | 8 | PASS |  | Where you overdosed, the grey retook the map. |
| s3 | 1 | PASS |  | You walked. The ground remembered you. |
| s3 | 2 | FAIL | GENERIC | You raised the flame, and they answered. |
| s3 | 3 | PASS |  | You slept where light could reach them. |
| s3 | 4 | FAIL | GENERIC | The world moved. You moved with it. |
| s3 | 5 | PASS |  | You spent everything. They built the rest. |
| s3 | 6 | FAIL | GENERIC | What you felt, they carried forward. |
| s3 | 7 | PASS |  | You chose, and the land turned. |
| s3 | 8 | FAIL | EXCEEDS-SCOPE | They stopped wandering. You showed them why. |
