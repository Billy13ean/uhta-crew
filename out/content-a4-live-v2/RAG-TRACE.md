# RAG-TRACE — query → retrieved chunk → output

> Retrieval is deterministic. Every selection and every cut below was produced by `content/retriever.py`, not by a model.
>
> Run `content-a4-live-v2` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-07 01:47:04

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

**Output** (8 candidates, 2 cleared the Critic):

- `FAIL/GENERIC` You hold a white flame that becomes whatever you do with it.
- `FAIL/WRONG-REGISTER` The flame in your hand is undetermined — it will become what you make people feel.
- `FAIL/GENERIC` Your flame is white, and nothing about it is decided yet.
- `PASS` You carry a white flame that lights only the stone around you — it becomes whatever you do with it.
- `FAIL/WRONG-REGISTER` The flame is white — genuinely undetermined — and being born against the sky says nothing about what you will sing back at it.
- `FAIL/GENERIC` You hold a flame that is neither Hope nor Fear — only what you will make it.
- `PASS` The white flame becomes whatever you do with it — nothing is locked.
- `FAIL/GENERIC` Your flame is white and will take the shape of what you inspire.

### n2 — First Walk — the ground remembers

**Query 1 (mechanic):** `Walk stamina per tile every tile walked becomes a compacted road NPCs traverse faster roads carry your color allegiance leash`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 29.16**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 3 cleared the Critic):

- `FAIL/GENERIC` You walk. The ground remembers you — the tile you cross becomes a road that carries your color, and people will travel it.
- `PASS` Walk. Every tile you cross becomes a road — compacted, faster to traverse, and it carries your color now.
- `FAIL/GENERIC` You walk, and the ground remembers: the path you make is a road, and roads carry your color forward.
- `FAIL/GENERIC` Walk. The earth compacts where you step — a road forms, colored by what you feel, and others will follow it.
- `PASS` You walk. What you cross becomes road — people traverse it faster, and it carries the color you hold.
- `FAIL/WRONG-REGISTER` Walk, and the ground answers: your path becomes a road that holds your color and beckons travelers.
- `FAIL/GENERIC` You walk. The tile remembers — it becomes a road others will travel, painted in what you carry.
- `PASS` Walk. Where you step, the earth compacts into road — faster for those who follow, and stained with your flame's color.

### n3 — First Flame — it applies what you feel

**Query 1 (mechanic):** `Raise wave the flame clears fog locally applies the flame's current alignment to NPCs in radius grows with Ascension`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 32.10**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/EXCEEDS-SCOPE` Raise the flame — it applies what you feel right now.
- `FAIL/GENERIC` Wave the flame. It spreads whatever color you are.
- `PASS` Raise the flame — it clears the fog and pushes your current feeling outward.
- `FAIL/EXCEEDS-SCOPE` The flame applies what you feel. Raise it to share that feeling with everyone who hears you.
- `FAIL/GENERIC` Raise the flame. Whatever you are, they become.
- `FAIL/EXCEEDS-SCOPE` Wave the flame — it isn't a cure, it's whatever you currently are.
- `FAIL/GENERIC` Raise the flame. It applies your alignment, not theirs.
- `FAIL/GENERIC` The flame spreads your feeling, not hope or fear — whatever you hold when you raise it.

### n4 — First Roar — whatever you intend

**Query 1 (mechanic):** `Roar shatters a line of tiles NPCs within witness radius take an unconditional Fear push regardless of flame color out-of-radius free`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 36.17**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `FAIL/GENERIC` You roar. Everyone who witnesses it is frightened, whatever you intend.
- `PASS` Roar. All who witness the line are pushed to fear — the flame's color does not protect them.
- `FAIL/GENERIC` This is Roar. It frightens everyone who sees it, no matter what the flame carries.
- `PASS` You can roar a path through stone. Everyone who witnesses the break feels fear.
- `PASS` Roar shatters the ground ahead. Witness it and you are frightened — your alignment, theirs, nothing stops this.
- `FAIL/GENERIC` When you roar, the earth breaks and all who see it are afraid. The flame cannot change this.
- `FAIL/GENERIC` Roar. The line frightens every witness regardless of what you feel or what they do.
- `PASS` You roar and the stone splits. Fear reaches everyone in sight of the break, even those already aligned to you.

### n5 — First Wait — inaction is an action

**Query 1 (mechanic):** `Wait do nothing free ends an encounter deliberate non-response witnessed inaction pushes nearby NPCs toward Apathy no action is neutral`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 38.57**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/WRONG-REGISTER` To wait is to teach them you do not matter.
- `FAIL/EXCEEDS-SCOPE` Withhold, and they learn you are nothing.
- `FAIL/EXCEEDS-SCOPE` Wait. They watch you choose irrelevance.
- `PASS` Do nothing. Whoever watches drifts toward apathy.
- `FAIL/GENERIC` Wait, and those who see you fade toward grey.
- `FAIL/GENERIC` Inaction is a lesson: you can be ignored.
- `FAIL/WRONG-REGISTER` To withhold is to push them toward not caring.
- `FAIL/EXCEEDS-SCOPE` Wait. The witness learns indifference.

### n6 — The found basin — the beacon that gives strength

**Query 1 (mechanic):** `light a beacon permanent aura radiates the flame's current color every generation tick discoverable ruined basin reveal stamina bonus`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 23.58**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 1 cleared the Critic):

- `FAIL/GENERIC` You light a basin and it gives you strength that does not fade.
- `FAIL/EXCEEDS-SCOPE` Light the basin. It reveals the land and the strength it gives persists.
- `FAIL/GENERIC` The basin, lit, gives strength — and the strength remains.
- `FAIL/EXCEEDS-SCOPE` You light a basin. The fog clears. The strength you gain lasts.
- `FAIL/EXCEEDS-SCOPE` Light a basin: it shows you the region and makes you stronger, even after you leave.
- `FAIL/GENERIC` The basin gives lasting strength when you light it.
- `FAIL/EXCEEDS-SCOPE` Light the ruined basin. It clears the fog around it and the strength it grants does not end.
- `PASS` You light a basin and gain strength that survives the cycle.

### n7 — First Sleep — where you lie down matters

**Query 1 (mechanic):** `Sleep ends the cycle advances one generation positional the sleeping body radiates the flame's emotion over a radius for every tick`

**Query 2 (experience):** `first cycle tutorial disguised as myth teacher narrator speaks names each verb as first used states consequence plainly short declarative no mythology cave white flame two paths shadows`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.2` — *2.2 Player verbs / actions* — **bm25 29.01**, 429 words, ~652 est. tokens

  > ### 2.2 Player verbs / actions Each waking cycle grants a stamina budget. Every verb spends it; when stamina is gone, the only remaining verb is Sleep. (Costs below are the current tuning values in `rules-v3.9.1-C.json`, the ratified ruleset; all remain fun-tuning dials, §6.) | Verb | Cost | Effect | |---|---|---| | **Walk** | ~0.5 stamina/tile; ~0.4 on existing roads | Moves the player; every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color** (see Roa…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 47.03**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 3 cleared the Critic):

- `PASS` You sleep. A generation passes. Where you lie down, your light keeps working.
- `FAIL/WRONG-REGISTER` Sleep ends the cycle. The body you leave behind radiates for every tick of the generation that follows.
- `FAIL/GENERIC` When you sleep, a whole generation passes—and the sleeping body keeps glowing.
- `FAIL/CONTRADICTS-CHUNK` Sleep. One generation turns while you rest, and where you lie becomes a beacon until you wake.
- `FAIL/WRONG-REGISTER` You sleep, and the world moves on without you. But the ground where you lay remembers what you felt.
- `PASS` Sleep advances a generation. Your body stays—a light that works through every tick you're gone.
- `FAIL/EXCEEDS-SCOPE` When stamina runs out, you sleep. A generation passes. Where you choose to rest, your flame never stops.
- `PASS` Sleep. The generation turns, and wherever you laid down keeps radiating until dawn.

### n8 — First waking — and the last words

**Query 1 (mechanic):** `generational sleep time only advances while the player sleeps contagion resolves tribes wander population grows landscape tint shifts`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 18.47**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `PASS` A generation has passed, and the world moved without you.
- `FAIL/GENERIC` The world moved while you slept.
- `FAIL/GENERIC` They went on without you.
- `FAIL/GENERIC` Time passed. The world answered.
- `PASS` A generation turned. What you did has already become something else.
- `PASS` The world moved. What you find now is what everything became.
- `FAIL/GENERIC` While you slept, the world became what it would.
- `PASS` You wake, and the world has already answered.

### e1 — Era 1 — Nomad / Tribal

**Query 1 (mechanic):** `era progression nomad tribal dress hood staffs satchels camps settling rule walled camp open settlement structures landscape tint feeling`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 20.95**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` Hoods and loose wraps, the color of dirt. Gathered stones marking where they slept last. Trails of compacted earth leading nowhere yet.
- `FAIL/GENERIC` They wear what keeps them warm — hides and rough cloth, grey as the fog. No walls. What they build, they build to leave: circles of stone, embers still glowing.
- `PASS` Nomads in worn hoods, carrying what they own. Their camps are rings of stone and ash — marks that say someone rested here, then moved on.
- `PASS` Hooded figures, feet wrapped, shoulders bent under the weight of wandering. Where they stop, stones arranged in circles. Where they walk, the ground remembers.
- `FAIL/GENERIC` Coarse wraps and hoods pulled low. They gather in clearings marked only by stones and cold fire pits — places to sleep, not to stay.
- `PASS` They dress in layers of hide and rough-spun cloth, grey and brown. Their camps are temporary — stone circles, dying fires, trails of compacted earth where they walked together.
- `FAIL/GENERIC` Hoods and simple wraps, no two exactly alike. When they settle for the night, they mark it with stones. When they leave, only the flattened ground remains.
- `PASS` Cloaked in whatever keeps the cold out — hides, rough fabric, hoods shadowing their faces. They build nothing that can't be abandoned: rings of stone, paths of packed dirt, embers.

### e2 — Transition — Nomad into Village

**Query 1 (mechanic):** `era progression village sleep thresholds derived from sleep count NPC dress coif settlement structures villages roads compacted earth paver stone`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.71**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `FAIL/EXCEEDS-SCOPE` The paths you walked have hardened into stone.
- `PASS` The wanderers you met have built walls, or villages, or vanished entirely.
- `PASS` The ground you crossed is paved now, and people walk it in your color.
- `FAIL/GENERIC` Settlements stand where there were only grey huddles before.
- `PASS` Where tribes held conviction long enough, they stopped moving and built.
- `PASS` The earth remembers your steps as stone; the fearful have dug in; the hopeful have raised roofs.
- `PASS` What was dirt when you slept is pavement now, and the grey who watched you have chosen sides or disappeared.
- `FAIL/WRONG-REGISTER` The trails are roads, the wanderers are builders, and the world has aged while you rested.

### e3 — Era 2 — Village

**Query 1 (mechanic):** `village era settlement structures roads paver stone after one generation allegiance colors green Hope red Fear ruins scar tissue`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 21.07**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 7 cleared the Critic):

- `PASS` The places you walked are stone now. The people who believed have built what they felt.
- `FAIL/GENERIC` Settlements stand where tribes stopped wandering. The roads you made have hardened into permanence.
- `PASS` What was dirt is paver stone. What was wandering is walls and rooftops.
- `PASS` The paths you walked have become roads. The devout have stopped moving and built where they stood.
- `PASS` Villages root where conviction reached the threshold. The ground you crossed a generation ago is stone beneath their feet.
- `PASS` Your trails are stone roads now. Settlements mark where belief crossed into devotion and people stopped wandering.
- `PASS` The paths harden. The faithful settle. What you walked as dirt, travelers now cross as stone.
- `PASS` Where tribes held deep feeling, they built. Where you walked, the earth remembers—compacted dirt aged into paver stone.

### e4 — Transition — Village into Victorian

**Query 1 (mechanic):** `Victorian town clocktowers smoking factories top hat canes garment folds era art communicates time base land art never ages`

**Query 2 (experience):** `waking emotional centerpiece generation passed world moved on its own landscape same but different roads harden tribes built land turned`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.63**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 28.43**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 4 cleared the Critic):

- `PASS` The ground remembers enough generations now that clocktowers rise where the devout have stood, and smoke climbs from the places where belief dug in deep enough to build machines.
- `FAIL/GENERIC` What began as huddles wearing hoods now wear top hats and carry canes; the settlements that rooted have grown tall enough to need clocktowers, and some burn coal.
- `PASS` The people have aged through enough sleeps that their dress has folds and their towns have towers; where fear built walls, factories smoke, and where hope built open, clocks mark the hours.
- `FAIL/WRONG-REGISTER` Enough generations have turned that the coifs have become top hats, the villages have become towns with smoking stacks, and the believers carry staffs that have become canes.
- `PASS` The world has lived long enough that what you meet now wears top hats instead of hoods, and the places that settled have built upward—clocktowers where hope took root, smoking factories where fear did.
- `FAIL/WRONG-REGISTER` Time has passed in enough three-tick cycles that the nomads are Victorians now, their settlements grown into towns with clock faces and coal smoke marking where devotion hardened into industry.
- `FAIL/GENERIC` The sleeps have stacked high enough that dress has evolved to top hats and canes, and the architecture has climbed—clocktowers and factory smoke rising from the sites where belief held long enough to build a second age.
- `PASS` Where once you woke to hoods and camps, now top hats and smoking chimneys; the people and their structures have aged together, clocktowers standing over hope's towns and coal-dark stacks over fear's.

### e5 — Ruins — what a burned-out settlement leaves

**Query 1 (mechanic):** `ruins abandoned structures remain scar tissue burned-out settlement grey people standing still in the place they built when they believed burnout`

**Query 2 (experience):** `waking landscape roads harden tribes stopped wandering and built devotion reads as architecture land turned green and growing sharp and industrial ash`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.3` — *2.3 Systems* — **bm25 19.25**, 2867 words, ~4563 est. tokens

  > ### 2.3 Systems *The systems below are specified to implementation precision — integers, thresholds, and flags, current as of `rules-v3.9.1-C.json` (schema 3.9.2), the ratified ruleset. §2.5 describes what the player experiences of them, with no numbers at all. Every value here is a tunable dial unless marked locked.* **The tile map.** The world is an explicit square-tile grid (**48×48** in the slice). Every spatial system reads and writes tile state — each tile carries `{terrain cost, road tie…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 39.96**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 3 cleared the Critic):

- `PASS` Grey people standing still in the place they built when they believed.
- `PASS` What remains when a settled tribe burns out and scatters — grey figures motionless in the structures their devotion raised.
- `FAIL/CONTRADICTS-CHUNK` The burned stand where they rooted, grey and still, while their settlement crumbles around them.
- `FAIL/CONTRADICTS-CHUNK` A settlement emptied by burnout — its people frozen grey in the walls and roads they built before they felt nothing.
- `FAIL/CONTRADICTS-CHUNK` When conviction breaks, the tribe scatters as wanderers, but the structures stay — and so do the grey ones who cannot leave.
- `PASS` Ruins mark where belief settled and then shattered — grey forms standing in the architecture of what they once felt.
- `FAIL/CONTRADICTS-CHUNK` The forensic image: a camp or village, its builders burned grey and motionless, the ground still remembering their color.
- `FAIL/CONTRADICTS-CHUNK` Where a tribe settled, believed deeply, then burned out — structures standing, people grey and still, allegiance lost.

### s1 — Win — the sky turns your color

**Query 1 (mechanic):** `win unification threshold contagion-dominant held across a generation no living opposing zealot player replaces Uhtcearu as the sky`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.4` — *2.4 Win state / lose state* — **bm25 28.79**, 314 words, ~501 est. tokens

  > ### 2.4 Win state / lose state Both are **unification events** — the run ends when the region stabilizes under a single emotion; the readout tells win from loss by *whose* emotion it is. - **Win:** the player's cultivated emotion becomes contagion-dominant past the **unification threshold (0.8 of population, tunable)**, held across a generation, **with no living opposing zealot** — it spreads uncounterable, opposing zealots are expelled or converted, and the player replaces Uhtcearu as the sky.…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 3 cleared the Critic):

- `FAIL/WRONG-REGISTER` You replaced Uhtcearu as the sky.
- `FAIL/GENERIC` The world moved on its own, and your color crossed the whole map.
- `PASS` Opposing zealots were expelled or converted. The sky turns.
- `FAIL/WRONG-REGISTER` Your cultivated emotion became contagion-dominant, and the player replaces Uhtcearu as the sky.
- `PASS` What you did outlived you, uncounterable, until the sky turned your color.
- `FAIL/CONTRADICTS-CHUNK` You spread uncounterable past the threshold. The sky answers.
- `PASS` Your color crossed the whole map. Opposing zealots gone. You are the sky now.
- `FAIL/GENERIC` The region stabilized under your emotion, and you replaced Uhtcearu as the sky.

### s2 — Loss — the grey closes in

**Query 1 (mechanic):** `loss your actions stop mattering apathy soft grey plus burned passes the dominance threshold grey retakes the map player shrunk back into the cave`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §2.4` — *2.4 Win state / lose state* — **bm25 37.71**, 314 words, ~501 est. tokens

  > ### 2.4 Win state / lose state Both are **unification events** — the run ends when the region stabilizes under a single emotion; the readout tells win from loss by *whose* emotion it is. - **Win:** the player's cultivated emotion becomes contagion-dominant past the **unification threshold (0.8 of population, tunable)**, held across a generation, **with no living opposing zealot** — it spreads uncounterable, opposing zealots are expelled or converted, and the player replaces Uhtcearu as the sky.…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 5 cleared the Critic):

- `PASS` The burned were yours.
- `FAIL/GENERIC` You fed the grey with your own flame.
- `PASS` What you made too bright became ash, and the ash became his.
- `PASS` The burned count toward the grey now.
- `FAIL/GENERIC` Your excess became apathy.
- `PASS` Those you burned fed the sky.
- `FAIL/GENERIC` Where you pushed too hard, the grey grew back.
- `PASS` The ones you burned are counted as grey.

### s3 — The teacher returns — one last line

**Query 1 (mechanic):** `tone mournful mythic wordless after the first dawn one voice spent in the first cycle never heard again the silence afterward is itself a statement`

**Query 2 (experience):** `victory your color crossing the whole map until the sky turns defeat grey closing in player shrunk back into the cave both endings seen coming`

**Retrieved:**

- `uhta-gdd-v0.9.7-full.md §1` — *1. Executive Summary* — **bm25 38.28**, 573 words, ~858 est. tokens

  > ## 1. Executive Summary **Title:** uhta *ūhta* (m.) — *"the last part of the night, before dawn."* **Concept:** You play an unnamed kaiju-scale being born as a counterpoint to the world's ruling god — Uhtcearu, whose grief has held the people and the landscape in mourning. *Counterpoint* is meant in the musical sense: a second, independent voice set against the ruling theme — bound to answer it, but not predisposed to oppose it with light. The white flame is genuinely undetermined; being born *…

- `uhta-gdd-v0.9.7-full.md §2.5` — *2.5 Player experience* — **bm25 32.19**, 718 words, ~1015 est. tokens

  > ### 2.5 Player experience **The first cycle is a tutorial disguised as a myth — and it is narrated (v0.9.2).** A text narrator, the teacher, speaks only during this cycle: as each verb is first used, it is named and its consequence stated plainly — the flame applies what you feel; the roar frightens all who witness it, whatever you intend; waiting teaches people you don't matter; where you sleep, your light keeps working. The narration is instrumentation, not lore — short declarative lines, no…

**Output** (8 candidates, 2 cleared the Critic):

- `FAIL/WRONG-REGISTER` You raised the flame. You walked. You slept. The ground remembers you.
- `FAIL/EXCEEDS-SCOPE` The world moved on its own. You were the second voice.
- `FAIL/GENERIC` You lit what was dark. You walked where nothing walked. The landscape is the answer.
- `PASS` Every place you slept kept working. The sky turned because you did.
- `FAIL/GENERIC` You chose what people would feel. They built what you inspired.
- `FAIL/GENERIC` The flame became what you did with it. The world became what they did with that.
- `FAIL/WRONG-REGISTER` You were born against the sky. You sang something back. This is what it made.
- `PASS` Where you walked, the ground remembers. Where you slept, your light kept working. The sky answers.

