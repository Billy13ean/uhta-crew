# RAG-TRACE — query → retrieved chunk → output

> Retrieval is deterministic. Every selection and every cut below was produced by `content/retriever.py`, not by a model.
>
> Run `content-a4-live` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-06 21:48:02

## Corpus

Chunk rule: **one `###` subsection** (GDD §4.5 — "the section boundary *is* the chunk boundary"); a `##` section with no `###` children is one chunk. Headings inside fenced code blocks are not headings.

Scorer: **BM25**, pure Python (`content/retriever.py`), k1=1.5, b=0.75, non-negative IDF. Score threshold **8.0**, token budget **6000** (estimated tokens).

| | chunks | words |
|---|---|---|
| **indexed** | 24 | 12,315 |
| **excluded by corpus policy** | 28 | 13,311 |
| total parsed | 52 | 25,626 |

### Corpus policy — `game-material-only v1`

The GDD is two documents in one binding — the design of uhta, and the design of the pipeline that builds uhta. Only the first is a knowledge base for writing the game's text. A Writer that can read §4.5 is not generating a narration line; it is handing the Director's own worked example back.

**Every excluded chunk, with its reason** (not a summary — the list):

| chunk | heading | words | reason |
|---|---|---|---|
| `CANON.md#front-matter` | front matter | 96 | Version preamble / changelog. Describes what changed between GDD revisions, not what is true in the world. |
| `CANON-process.md#front-matter` | front matter | 89 | Process canon — Keeper escalation, build order, artifact counts. Governs how the project runs; contains no game material. |
| `CANON-process.md#sec-1` | Delta from v16 — process canon (Assignment-1 grader closeout | 1143 | Process canon — Keeper escalation, build order, artifact counts. Governs how the project runs; contains no game material. |
| `uhta-gdd-v0.9.7-full.md#front-matter` | front matter | 1369 | Version preamble / changelog. Describes what changed between GDD revisions, not what is true in the world. |
| `uhta-gdd-v0.9.7-full.md#3` | 3. AI Architecture | 53 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.1` | 3.1 Agent roster — one agent, one wow | 931 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.2` | 3.2 The Keeper contract — what a contradiction actually does | 1551 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.3` | 3.3 Orchestration & human gates | 330 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.4` | 3.4 Shared memory — the blackboard pattern | 262 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.5` | 3.5 What agents output and what it changes in the game | 555 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#3.6` | 3.6 Verification layers | 156 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-full.md#4.1` | 4.1 Pillar 1 — AI dev pipeline map | 122 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-full.md#4.2` | 4.2 Pillar 2 — Technical requirements & constraints | 198 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-full.md#4.3` | 4.3 Pillar 3 — Token budgets & projections | 344 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-full.md#4.4` | 4.4 Prompt constraints & versioning | 112 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-full.md#4.5` | 4.5 The blackboard as a RAG corpus | 940 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-abridged.md#front-matter` | front matter | 336 | Version preamble / changelog. Describes what changed between GDD revisions, not what is true in the world. |
| `uhta-gdd-v0.9.7-abridged.md#3` | 3. AI Architecture | 66 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#3.1` | 3.1 Roster | 469 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#3.2` | 3.2 The Keeper contract — what a contradiction actually does | 1397 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#3.3` | 3.3 Orchestration and shared memory | 475 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#3.4` | 3.4 What the player ever notices of any of this | 401 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#3.5` | 3.5 Verification layers | 155 | §3 is the AI-architecture / agent-roster section — how the game is built, not what is in it. A narration line grounded in the crew roster would be about the pipeline. |
| `uhta-gdd-v0.9.7-abridged.md#4.1` | 4.1 Pipeline and routing | 56 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-abridged.md#4.2` | 4.2 The blackboard as a RAG corpus | 927 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-abridged.md#4.3` | 4.3 Budgets — projections vs. measured actuals | 131 | §4 is technical strategy, budgets, and the RAG design itself. §4.5 in particular carries the Director's hand-written worked narration example; indexing it lets the Writer retrieve the answer instead of writing one. |
| `uhta-gdd-v0.9.7-abridged.md#7.1` | 7.1 This revision (v0.9.6-abridged → v0.9.7), traced to the  | 392 | §7 is revision provenance — a record of document history, not game material. |
| `uhta-gdd-v0.9.7-abridged.md#7.2` | 7.2 The prior revision (v0.7-abridged → v0.9.6), traced to t | 255 | §7 is revision provenance — a record of document history, not game material. |

### What is in the index

| chunk | heading | words | est. tokens |
|---|---|---|---|
| `CANON.md#sub-2` | Runs 20–22 — the living world, now canon (was WIP at v15) | 198 | 338 |
| `CANON.md#sub-3` | Review-board closeout — Director rulings (GDD v0.9.1, v0.9.2 | 221 | 372 |
| `CANON.md#sub-4` | Run 23 → 23b — Uhtcearu active events: the GRIEF FRONT (rule | 213 | 392 |
| `CANON.md#sub-5` | Pipeline status | 73 | 133 |
| `CANON.md#sub-6` | Remaining work — human-owned / post-gate | 50 | 100 |
| `CANON.md#sec-7` | Open questions (delta from v16) | 84 | 167 |
| `uhta-gdd-v0.9.7-full.md#1` | 1. Executive Summary | 573 | 858 |
| `uhta-gdd-v0.9.7-full.md#2.1` | 2.1 Core mechanic | 214 | 333 |
| `uhta-gdd-v0.9.7-full.md#2.2` | 2.2 Player verbs / actions | 429 | 652 |
| `uhta-gdd-v0.9.7-full.md#2.3` | 2.3 Systems | 2867 | 4563 |
| `uhta-gdd-v0.9.7-full.md#2.4` | 2.4 Win state / lose state | 314 | 501 |
| `uhta-gdd-v0.9.7-full.md#2.5` | 2.5 Player experience | 718 | 1015 |
| `uhta-gdd-v0.9.7-full.md#2.6` | 2.6 Scope | 422 | 778 |
| `uhta-gdd-v0.9.7-full.md#2.7` | 2.7 Build order — what is core, what is nice, and the stop r | 649 | 958 |
| `uhta-gdd-v0.9.7-full.md#2.8` | 2.8 Definition of Playable — the acceptance test | 386 | 548 |
| `uhta-gdd-v0.9.7-full.md#5` | 5. Identified Logic Gaps & the Red-Team Arc | 1016 | 1672 |
| `uhta-gdd-v0.9.7-full.md#6` | 6. Open Questions (tuning — deferred to playtest, distinct f | 742 | 1209 |
| `uhta-gdd-v0.9.7-full.md#Appendix A` | Appendix A — Changelog: v0.8.1 → v0.9.7 (mapped to runs & ru | 410 | 593 |
| `uhta-gdd-v0.9.7-abridged.md#1` | 1. Summary | 323 | 506 |
| `uhta-gdd-v0.9.7-abridged.md#2` | 2. Game Mechanics | 801 | 1231 |
| `uhta-gdd-v0.9.7-abridged.md#2.7` | 2.7 Build order — what is core, what is nice, and the stop r | 620 | 908 |
| `uhta-gdd-v0.9.7-abridged.md#2.8` | 2.8 Definition of Playable — the acceptance test | 480 | 695 |
| `uhta-gdd-v0.9.7-abridged.md#5` | 5. Identified Logic Gaps (resolution trail) | 447 | 712 |
| `uhta-gdd-v0.9.7-abridged.md#6` | 6. Open Questions (deferred to playtest — dials, not gaps) | 65 | 112 |

---

## Per-beat trace

Each beat runs **two** queries and unions their cuts — the GDD §4.5 two-chunk rule. Query 1 is the mechanical consequence; query 2 is the experience.

### n1 — The cave — the undetermined flame

**Query 1 (mechanic):** `player alignment flame Fear red Neutral white Hope green nothing locks the flame cave choice sets only the starting tint re-tints continuously`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 21.76**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

- `uhta-gdd-v0.9.7-full.md §1` — *1. Executive Summary* — **bm25 18.91**, 573 words, ~858 est. tokens

  > ## 1. Executive Summary **Title:** uhta *ūhta* (m.) — *"the last part of the night, before dawn."* **Concept:** You play an unnamed kaiju-scale being born as a counterpoint to the world's ruling god — Uhtcearu, whose grief has held the people and the landscape in mourning. *Counterpoint* is meant in the musical sense: a second, independent voice set against the ruling theme — bound to answer it, but not predisposed to oppose it with light. The white flame is genuinely undetermined; being born *…

**Output** (8 candidates, 3 cleared the Critic):

- `PASS` You hold a white flame that lights only the stone around you.
- `FAIL/GENERIC` The flame in your hand is white and undetermined.
- `FAIL/GENERIC` A white flame — what it becomes is not yet decided.
- `FAIL/GENERIC` You carry a flame that has no color of its own.
- `PASS` The white flame waits — it will become whatever you do with it.
- `FAIL/GENERIC` In your hand: a flame, white, holding no feeling yet.
- `FAIL/GENERIC` The flame is yours, white and empty of intent.
- `PASS` You wake holding white fire — neither path is written into it.

### n2 — First Walk — the ground remembers

**Query 1 (mechanic):** `Walk stamina per tile every tile walked becomes a compacted road NPCs traverse faster roads carry your color allegiance leash`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 29.16**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 6 cleared the Critic):

- `PASS` You walk, and the ground remembers you — every tile you cross becomes a road that carries your color.
- `PASS` Walk. The ground remembers you. Every tile becomes a road, and roads carry your color forward.
- `PASS` Where you walk, the earth becomes road — and roads carry your color to those who travel them.
- `FAIL/GENERIC` Walk across the land. Each tile you cross becomes a road. Roads carry your color.
- `PASS` You walk. The ground you cross becomes road, and every road now carries your color.
- `PASS` Walk: the tiles you cross become roads. Roads carry your color, and people will travel them.
- `PASS` Each step makes road. Roads carry your color — and people follow roads.
- `FAIL/WRONG-REGISTER` Walk. Every tile becomes a road that carries what you are, and people will walk it after you.

### n3 — First Flame — it applies what you feel

**Query 1 (mechanic):** `Raise wave the flame clears fog locally applies the flame's current alignment to NPCs in radius grows with Ascension`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 32.10**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `FAIL/EXCEEDS-SCOPE` Raise the flame. It applies what you feel right now.
- `FAIL/GENERIC` Wave the flame — it spreads whatever color you're holding.
- `PASS` Raise the flame. Everyone who sees it takes on your current feeling.
- `FAIL/GENERIC` The flame clears fog and applies your alignment to those nearby.
- `PASS` Raise the flame — it pushes your present emotion outward.
- `PASS` Wave the flame. It isn't healing. It's whatever you are.
- `PASS` Raise the flame. It spreads the feeling you carry, not the one they need.
- `FAIL/GENERIC` The flame applies its current color to everyone in reach.

### n4 — First Roar — whatever you intend

**Query 1 (mechanic):** `Roar shatters a line of tiles NPCs within witness radius take an unconditional Fear push regardless of flame color out-of-radius free`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 36.17**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` You can roar — and everyone who witnesses it will fear you, whatever you intend.
- `PASS` Roar. The earth shatters ahead of you, and everyone who sees it is frightened — even if your flame burns hope.
- `FAIL/GENERIC` This is the roar. It frightens all who witness it, no matter what your flame carries.
- `FAIL/GENERIC` You roar to shatter the ground — but know this: everyone within sight will fear you, regardless of your light.
- `PASS` The roar clears distance fast, but whoever witnesses the line takes fear — your flame's color cannot protect them.
- `FAIL/WRONG-REGISTER` Roar, and the stone breaks open — yet every soul who sees you do it learns fear, whether you mean them to or not.
- `PASS` You can roar a path through the earth. Everyone who watches will be pushed toward fear. Your intention does not matter.
- `PASS` This is roar: it splits the ground and makes witnesses afraid, even when your flame is green.

### n5 — First Wait — inaction is an action

**Query 1 (mechanic):** `Wait do nothing free ends an encounter deliberate non-response witnessed inaction pushes nearby NPCs toward Apathy no action is neutral`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 38.57**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` You wait. Those who watch learn you do not matter.
- `PASS` When you withhold, the watchers drift toward apathy.
- `FAIL/GENERIC` You do nothing. Nearby, indifference takes root.
- `PASS` Wait, and you teach the people watching that you are not worth their feeling.
- `PASS` Inaction is witnessed. It pushes them toward grey.
- `FAIL/GENERIC` To wait is to be forgotten. The nearby lose their color.
- `PASS` You hold back. Those who see it move toward apathy.
- `FAIL/GENERIC` Waiting is a choice. It makes you matter less to those who witness it.

### n6 — The found basin — the beacon that gives strength

**Query 1 (mechanic):** `light a beacon permanent aura radiates the flame's current color every generation tick discoverable ruined basin reveal stamina bonus`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 23.58**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/GENERIC` You light the basin. It reveals the land around you and gives you strength that lasts.
- `FAIL/EXCEEDS-SCOPE` Light a beacon. It clears the fog and the strength it gives you persists.
- `PASS` You light the ruined basin. The land reveals itself, and you are made stronger.
- `FAIL/EXCEEDS-SCOPE` Light a beacon. The world around it becomes visible, and its strength becomes yours.
- `FAIL/WRONG-REGISTER` The basin lights. Fog lifts where it burns, and the strength you gain does not fade.
- `FAIL/EXCEEDS-SCOPE` You light a beacon. It shows you the hidden land and its power stays with you.
- `FAIL/GENERIC` Light the basin. It reveals what was hidden and makes you stronger, even after you leave.
- `FAIL/EXCEEDS-SCOPE` You light a beacon. The fog around it clears, and you carry its strength forward.

### n7 — First Sleep — where you lie down matters

**Query 1 (mechanic):** `Sleep ends the cycle advances one generation positional the sleeping body radiates the flame's emotion over a radius for every tick`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 29.01**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/WRONG-REGISTER` You sleep. A generation passes — and your body keeps radiating, every tick, over everyone near where you lie down.
- `PASS` Sleep ends the cycle. The world moves without you, but where you sleep, the flame keeps working.
- `FAIL/GENERIC` You sleep here. Generations pass. The ground around your body glows with what you feel, until you wake.
- `FAIL/WRONG-REGISTER` Sleep. One generation. Your sleeping body radiates over the ground you chose — the flame never stops.
- `FAIL/GENERIC` You sleep — and a generation turns. Where you lie down matters: your light keeps spreading while you dream.
- `FAIL/GENERIC` Sleep advances time. Your body stays, glowing, touching everyone near where you chose to rest.
- `FAIL/WRONG-REGISTER` You sleep. The world ages. The sleeping body radiates your color across the ground, every tick, until dawn.
- `FAIL/GENERIC` Sleep here and the cycle ends. A generation passes over your glowing body — location is the last choice you make.

### n8 — First waking — and the last words

**Query 1 (mechanic):** `generational sleep time only advances while the player sleeps contagion resolves tribes wander population grows landscape tint shifts`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 18.47**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 6 cleared the Critic):

- `PASS` A generation has passed, and the world moved without you.
- `FAIL/GENERIC` The world has changed while you slept.
- `PASS` They built what you left behind.
- `PASS` A generation passed. The ground remembers.
- `FAIL/GENERIC` While you slept, the world answered.
- `PASS` What you did outlasted you — or it didn't.
- `PASS` The world moved on its own.
- `PASS` You wake. A generation has passed, and they chose.

### e1 — Era 1 — Nomad / Tribal

**Query 1 (mechanic):** `era progression nomad tribal dress hood staffs satchels camps settling rule walled camp open settlement structures landscape tint feeling`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 20.95**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/GENERIC` Gathered figures in rough hoods, hands empty, standing where they stopped wandering — tents of hide and cloth, no walls, fires in open pits.
- `FAIL/GENERIC` The nomads wear simple hoods that cover their heads, shoulders bare or wrapped in undyed cloth, carrying nothing but what they can walk with.
- `FAIL/GENERIC` Compacted earth paths between hide shelters — no stone, no permanence — the people dressed in hoods and wraps, their camps circles of bent poles and stretched skins.
- `FAIL/GENERIC` Rough hoods and loose garments, all of it meant to be carried, and the settlements are just where they set it down — rings of low tents around communal fires.
- `PASS` The wanderers wear hoods that shadow their faces, garments loose enough to walk in, and when they settle they build only what can be made from what the land gives — bent wood, stretched hide, stacked stone.
- `FAIL/GENERIC` Hoods pulled forward, cloth wrapping the body in layers that can be shed or added, and the camps are temporary even when they root — circles of hide tents, fire-rings, and beaten earth.
- `FAIL/GENERIC` They dress in hooded wraps and carry their belongings on their backs, and where they settle the structures are low and open — bent frames covered in skins, smoke rising from uncovered fires.
- `FAIL/GENERIC` Simple hoods and layered cloth, no decoration, no metal, and the settlements are clusters of rounded shelters made from what grows or can be dragged — timber frames, hides, woven grass, and the ground they've trampled flat.

### e2 — Transition — Nomad into Village

**Query 1 (mechanic):** `era progression village sleep thresholds derived from sleep count NPC dress coif settlement structures villages roads compacted earth paver stone`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.71**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 7 cleared the Critic):

- `PASS` The paths you walked last season have hardened into stone.
- `PASS` Where grey wanderers drifted, a settlement now stands.
- `PASS` The huddle you met is gone. In its place, walls.
- `PASS` Dirt trails you pressed with your feet now carry travelers in your color.
- `PASS` The people you left behind have stopped wandering and built.
- `PASS` The ground you walked remembers you — your trails are now paved.
- `FAIL/GENERIC` A generation has passed. The nomads have chosen where to root.
- `PASS` What was loose earth beneath your feet is now worked stone.

### e3 — Era 2 — Village

**Query 1 (mechanic):** `village era settlement structures roads paver stone after one generation allegiance colors green Hope red Fear ruins scar tissue`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 21.07**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` The dirt paths you walked are paver stone now. The huddles you met have settled and built. A generation has passed, and the world has moved on its own.
- `FAIL/GENERIC` Where people stopped wandering, they built. Roads have hardened into stone. The settlements that rooted here carry what you did, and what the world did without you.
- `PASS` The ground remembers everywhere you walked — stone roads now, carrying travelers in your color. Where tribes crossed the threshold of feeling, they stopped moving and raised walls.
- `PASS` Trails have become stone. The nomads you met have children now, and some have built where they stopped believing motion mattered more than what they felt.
- `FAIL/GENERIC` The paths are stone. The wanderers have settled. What was temporary when you last woke has rooted — villages stand where devotion held, and the roads you walked carry the next generation.
- `PASS` Stone roads connect what were dirt paths. Tribes that reached conviction have built and stopped wandering. The landscape answers what happened while you slept — settlements, walls, and the hardened ground you made by walking.
- `PASS` Your footprints are stone roads now. Tribes have stopped drifting and raised what they believe — walled camps, settlements, the bones of permanence. The world has aged a generation since you last opened your eyes.
- `FAIL/GENERIC` The trails are stone. Where feeling took root, people built and stayed. The world you wake to is no longer scattered and grey — it has hardened into roads, walls, and the choices that outlived you.

### e4 — Transition — Village into Victorian

**Query 1 (mechanic):** `Victorian town clocktowers smoking factories top hat canes garment folds era art communicates time base land art never ages`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.63**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` The wanderers have built clocktowers. The chimneys are smoking now.
- `PASS` Top hats and canes. The settlements have grown factories, and time has written itself in brick.
- `PASS` The coifs are gone — everyone is wearing top hats now, and the villages have become towns with smoking stacks.
- `PASS` Clocktowers stand where the villages were. The people wear top hats and carry canes, and the factories are already smoking.
- `FAIL/EXCEEDS-SCOPE` The second age: factories rise where settlements stood, their smoke climbing into the grey. Everyone who built them is wearing a top hat.
- `FAIL/GENERIC` The settlements have aged into towns. Clocktowers mark the hours now, and smoke rises from every roof.
- `FAIL/GENERIC` Top hats and factory smoke. The villages have become industrial, and the people dress like they remember when they weren't.
- `PASS` The world has built its second skin: clocktowers, smoking chimneys, top hats on everyone who used to wear a coif.

### e5 — Ruins — what a burned-out settlement leaves

**Query 1 (mechanic):** `ruins abandoned structures remain scar tissue burned-out settlement grey people standing still in the place they built when they believed burnout`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.25**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `PASS` Grey people standing still in the place they built when they believed.
- `FAIL/EXCEEDS-SCOPE` They stand motionless where their settlement once rooted, grey now, the color they wore before the burnout drained from their bodies.
- `PASS` The structures remain where devotion settled them, but the people inside are grey and still, wearing faint rings of what they used to feel.
- `PASS` What's left when a settled tribe burns out: grey figures that no longer wander, standing in the architecture their conviction built.
- `FAIL/WRONG-REGISTER` A settlement emptied of belief but not of people — they stand where they rooted, grey, the burnout flag still faintly visible as rings around them.
- `PASS` The buildings mark where they stopped wandering and dug in; the grey motionless figures inside mark where their feeling broke.
- `FAIL/CONTRADICTS-CHUNK` Ruins are not empty — grey people stand in them, still settled, no longer able to leave, wearing the faint trace of the pole that burned them out.
- `FAIL/CONTRADICTS-CHUNK` Where a tribe settled and then shattered: the walls or camps remain, and inside them the burned stand grey and motionless, exiled from movement but rooted by the settling rule.

### s1 — Win — the sky turns your color

**Query 1 (mechanic):** `win unification threshold contagion-dominant held across a generation no living opposing zealot player replaces Uhtcearu as the sky`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.4` — *2.4 Win state / lose state* — **bm25 28.79**, 314 words, ~501 est. tokens

  > ### 2.4 Win state / lose state Both are **unification events** — the run ends when the region stabilizes under a single emotion; the readout tells win from loss by *whose* emotion it is. - **Win:** the player's cultivated emotion becomes contagion-dominant past the **unification threshold (0.8 of population, tunable)**, held across a generation, **with no living opposing zealot** — it spreads uncounterable, opposing zealots are expelled or converted, and the player replaces Uhtcearu as the sky.…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 3 cleared the Critic):

- `PASS` You walked, and the ground remembered you. You roared, and they heard. You slept where your light could work. The sky is yours.
- `FAIL/GENERIC` They cowered. They straightened. They built in your color. The world moved on its own, and it moved toward you.
- `FAIL/GENERIC` The huddle you met is gone. What you find instead is the answer. The sky turns.
- `FAIL/WRONG-REGISTER` You lit the basin. You spent your last action. You slept, and your light kept working. They are yours now.
- `FAIL/GENERIC` Every settlement that formed, every road that hardened, every tribe that stopped wandering — the landscape is the score. You won it.
- `FAIL/CONTRADICTS-CHUNK` The grey closed in, then turned. The zealot you never met now burns for you. The sky answers: it is your color.
- `PASS` You raised the flame and the fog cleared. You walked and they followed. You slept and the world became you. The sky has turned.
- `PASS` Where you chose to lie down mattered. The sleeping body glowed. The generations passed. What they built, they built in your color.

### s2 — Loss — the grey closes in

**Query 1 (mechanic):** `loss your actions stop mattering apathy soft grey plus burned passes the dominance threshold grey retakes the map player shrunk back into the cave`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.4` — *2.4 Win state / lose state* — **bm25 37.71**, 314 words, ~501 est. tokens

  > ### 2.4 Win state / lose state Both are **unification events** — the run ends when the region stabilizes under a single emotion; the readout tells win from loss by *whose* emotion it is. - **Win:** the player's cultivated emotion becomes contagion-dominant past the **unification threshold (0.8 of population, tunable)**, held across a generation, **with no living opposing zealot** — it spreads uncounterable, opposing zealots are expelled or converted, and the player replaces Uhtcearu as the sky.…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 6 cleared the Critic):

- `PASS` The burned count toward the grey.
- `FAIL/WRONG-REGISTER` Your excess fed the sky.
- `PASS` What you burned became his.
- `PASS` The grey you made closed in.
- `FAIL/GENERIC` Apathy claimed what you left behind.
- `PASS` The burned were counted against you.
- `PASS` You fed Uhtcearu his victory.
- `PASS` Where you overdosed, the grey retook the map.

### s3 — The teacher returns — one last line

**Query 1 (mechanic):** `tone mournful mythic wordless after the first dawn one voice spent in the first cycle never heard again the silence afterward is itself a statement`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §1` — *1. Executive Summary* — **bm25 38.28**, 573 words, ~858 est. tokens

  > ## 1. Executive Summary **Title:** uhta *ūhta* (m.) — *"the last part of the night, before dawn."* **Concept:** You play an unnamed kaiju-scale being born as a counterpoint to the world's ruling god — Uhtcearu, whose grief has held the people and the landscape in mourning. *Counterpoint* is meant in the musical sense: a second, independent voice set against the ruling theme — bound to answer it, but not predisposed to oppose it with light. The white flame is genuinely undetermined; being born *…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `PASS` You walked. The ground remembered you.
- `FAIL/GENERIC` You raised the flame, and they answered.
- `PASS` You slept where light could reach them.
- `FAIL/GENERIC` The world moved. You moved with it.
- `PASS` You spent everything. They built the rest.
- `FAIL/GENERIC` What you felt, they carried forward.
- `PASS` You chose, and the land turned.
- `FAIL/EXCEEDS-SCOPE` They stopped wandering. You showed them why.

