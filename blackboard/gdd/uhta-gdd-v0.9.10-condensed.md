# uhta — Game Design Document

> **Version 0.9.10 (condensed) · 21 August 2026 · Nicholas Rouke**
> v0.9.10 delta from v0.9.9: §1 Tone and §2 gain **the tellings** — the one sanctioned text surface after the first dawn — transcribed from the Director's canon ruling of 2026-08-21 (`canon/CANON-RULING.json`, rule `sonder-telling-surface`, AMENDED). §3 and §5 name the Sonder engine. Nothing else changes.
> ELVTR Multi-Agent AI for Game Development — Assignment 2, Final GDD
> Structured around Avery's four Assignment-1 notes. Every binding number is live in `rules-v3.9.1-C.json`. Agent outputs and orchestration code ship with Assignment 3 (due 4 Aug) and are not reproduced here.

---

## 1. Summary

**Title:** *uhta* — from *ūhta* (m.), Old English: "the last part of the night, before dawn."

**Genre / platform:** God-game / emotional strategy. Browser (Phaser 3), keyboard + mouse.

**Core loop:** Wake with a limited stamina budget, influence nomadic tribes toward Hope or Fear, then Sleep — a generation passes and the world reshapes itself around what you inspired.

**Pitch:** You are an unnamed kaiju-scale being, born as a counterpoint to the world's ruling god — Uhtcearu, whose grief holds people and landscape in mourning. *Counterpoint* in the musical sense: a second voice bound to answer the first, not predisposed to oppose it with light. The white flame you carry is genuinely undetermined. Between sleeps the world grows without you: tribes gather, settle, colonize, fight, and visibly age through three eras — nomad camps, villages, then Victorian towns with clocktowers and smoking factories. The game asks one question: **what will you make people feel, and what will that do to the world?**

**Art direction:** grey-box now, stylistic later — in a wordless game the visual language carries every reading the player gets, so it is deliberately the last thing locked.

**Tone:** Mournful, mythic, wordless — *after the first dawn*. A narrator names each verb the first time you use it; the words end permanently at your first Sleep. **One exception, ruled v0.9.10:** at a conversion the game may hold the world and show a *telling* — a few sentences of how a person who lived under the flame remembers it, ending on a question it does not answer (§2, The tellings). Outside those cards the silence stands.

**Design stance:** **Fear is the easy path** — it breaks and coerces. **Hope is the hard path** — it must convert, and wins by patience and depth. Intent, not measured result: the bot proxies currently read hope-favored and are being re-benchmarked.

## 2. Game Mechanics

**Core mechanic — emotional contagion across generations.** Everyone in the world sits somewhere on one scale: deep Fear at one end, grey Apathy at the middle, deep Hope at the other — twelve steps either side of centre. Where a person sits is legible on sight: the colour they carry, how they stand, whether they follow anyone. Four bands matter — grey, tentative, devout, and the **zealot** at each extreme, who has stopped moving entirely and now moves others.

What moves people is everyone else. A zealot pulls hardest and its followers pull with it; ordinary neighbours pull on each other, which means apathy spreads exactly the way belief does. Grief drags all of it back toward grey. Your own pressure is one more voice in that sum — and usually not the loudest in the room.

**Two caps make this a game instead of a slider.** First, nobody moves more than one step at a time, however much pressure lands on them: you cannot buy a convert with one overwhelming act, because belief is paid for in generations rather than gestures. Second, too much of the *same* pressure at once **breaks** a person instead of converting them — they freeze grey, ringed in the colour they used to carry, and only the opposite feeling can bring them back. Push too hard for what you want and you destroy the thing you were making.

Sleep skips a generation forward and lets all of it compound without you. You set the conditions; you do not micromanage what grows — with one exception, below.

**Player verbs.** Each spends a per-wake stamina budget. When it is gone, only Sleep remains. No action is neutral, including Wait and *where* you lie down.

| Verb | Cost | Effect |
|---|---|---|
| **Walk** | 0.5/tile (0.4 roaded) | Walked tiles become roads carrying **your color** |
| **Flame** | 2.5 | ±2.0 within r3 toward your alignment; the *save* for opposite-burned NPCs |
| **Roar** | ½ walk cost of distance | Carves a road line; unconditional Fear push 2.8 on all witnesses within r6 — *whatever your color*; the save for hope-burned |
| **Beacon** | 3 | Permanent aura (0.35/tick, r4) in your color; the 5 ruined basins also reveal map and pay stamina |
| **Raze** | 4 + 0.5·devout | Fear spike 2.5 within r5 — Fear's hammer |
| **Wait** | 0 | Witnessed inaction pushes toward Apathy (0.5) |
| **Sleep** | ends cycle | Advances a generation; your sleeping body radiates your color |

**Systems that respond.** **Burnout** is the break described above; only the opposing act saves them, and the save costs more than the conversion would have. **Genesis** — the world forms itself from a scatter of grey nomads and one founding zealot per pole, who gather followers and put down roots. **Settling** roots a tribe permanently, and a rooted tribe resists you *except* along your own roads — which is why influence costs footwork rather than standing still. **Schism** — a tribe that grows large and certain enough splits, sending a daughter zealot far away: the world grows by spreading. **Faction fights** are asymmetric — Fear breaks its opponents toward burnout; Hope bends, but resists in proportion to its depth, so a deep congregation outlasts a siege. **Zealot fate** — Hope converts a fear-zealot its own tribe has turned against, gaining a second engine; Fear simply expels the equivalent. **Ascension** — as believers multiply you grow: more stamina, more beacons, and a body that visibly changes, vines for Hope and glowing veins for Fear. **Worship** funds all of it, with a floor low enough that a losing player always has moves left.

**Encounters — the one place you touch a person.** Everything above is population-scale: you apply pressure and live with the arithmetic. Encounters are the exception, and they exist because a god-game with no moment of contact is a spreadsheet with weather. When you meet a group directly the simulation pauses and you play a short, wordless, diegetic exchange — no interface, no text, only your body and theirs. **This is the only time you act on individuals rather than a population**, and the two poles never play the same game.

| Encounter | Hope — patience, depth, few | Fear — speed, force, many |
|---|---|---|
| **First contact** — an unaligned nomad band | *Steady the flame.* They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less. Few converts, and they arrive already devout | *The scatter.* You roar, the band breaks, and you have a handful of strides to cut off the runners. Everyone you head off turns; everyone who escapes carries the story outward. Many converts, every one of them shallow |
| **The vigil** — the moment of Sleep, every generation | *The weaving.* Your believers hang in the dark and you trace lines between them with your last stamina. Completed chains become channels belief travels while you are gone; longer chains reach further and are harder to hold | *The watch.* Your believers are points of light and the dark presses in. You shield what you can and you cannot shield everything. Fear's version is triage — choosing who to abandon before dawn |
| **The holding** — pressing a rooted settlement, eras 2–3 | *The procession.* Roads are the only way in. Converts fall in behind you as you walk and the line breaks if you move too fast or turn too sharply; whoever is still with you at the heart converts a resident | *The breaking.* Resistance shows as a ring. Strike where it is thinnest — but each strike hardens the arc beside it, so winning means finding the collapsing sequence before your stamina runs out |

**Where this sits, honestly.** Encounters are designed and unbuilt, and they sit on the far side of the §3 stop rule — the largest scope addition since the graded draft, proposed right after a document that says nothing new gets built until a stranger has played the loop. That ordering is deliberate. If the stranger test says the generational loop reads as arithmetic, encounters are the designed answer and they are built first; if the loop already lands without them, they stay on paper. **The test decides, not the appetite.**

**The tellings — the one text after the dawn (v0.9.10).** The people you convert had lives before you arrived, and the game now has a way to say so. *sonder* (the A8 narrative engine, `sonder/`) is a played text adventure inside this world: each playthrough deals the player one person in a band — in the camps, the villages, or the towns; the six nomads or their descendants, carrying the same habits and the same handed-down objects — on the nights the being comes down the ridge. Every finished playthrough is banked as a **telling**: third person, four to six sentences, in the uhta register, gated in code (no digits, no exclamation, no interface words, never the word *zealot*), ending on the one choice that playthrough turned on, put as a question. **Ruled (2026-08-21, `sonder-telling-surface` AMENDED):** a telling may be shown in play under four scopes and no others — *when:* at a conversion (an NPC entering devout under your colour) or your first contact with a settlement of the opposing colour; *where:* as a paused card over the held world, dismissed by any input, never on the overworld or the HUD; *which:* drawn from the bank to match your colour — a fear story for a Fear run — preferring the settlement's era; *how often:* once per conversion, at least one Sleep between cards, never during the sleep-0 narrated cycle. The question at the end of a telling is left on screen unanswered. This is an encounter-class surface: the same class the 2026-08-19 presentation amendment proposes for encounters, and it is ruled here on its own, with those three proposals still open.

**The antagonist — the Grief Front.** Grief has no position on the scale, because grief is not a pole — **it is the gravity**. The passive decay toward 0 *is* Uhtcearu, and apathy is what he leaves behind. His active form is on screen: past 0.55 dominance a desaturating fog bank condenses **on the winner's largest tribe** for three sleeps. Inside it, grief exactly cancels a zealot's pull — the shepherded **stall**, never flipped or killed, while unshepherded believers grey quickly. It wears only the dominant pole's colors and cannot fire in a do-nothing run. *Grief takes the stragglers; the shepherded stand.*

**Win state / lose state** — both are unification events, checked every tick.

- **WIN:** your pole holds ≥0.8 of the population for 6 ticks spanning a generation, with **no living opposing zealot**, and only while you are acting. You win by doing, never by drifting.
- **LOSS:** grey + burned ≥0.8 of the population. The loss check always runs, and **a same-tick tie resolves to the loss** — your excess feeds the sky. The counts are disjoint, so a completed win-hold can never flip; a coasting brink can (measured 1 run in 20 — intended).

## 3. Build order — core, then nice

*Answering: "figure out early which are core that should get built first and which are nice."*

| Tier | Contents | Status |
|---|---|---|
| **CORE** — remove one and there is no game | The −12..+12 scale; Flame / Roar / Wait / Sleep + Walk; generational Sleep; the unification win/loss check | Built |
| **PASS 1** — makes the core legible and dramatic | Burnout + the save; genesis; settling; beacons; worship→stamina; ascension; peer contagion; **the Grief Front** — a loop with no opposing force is a sandbox, not a game | Built |
| **PASS 2** — texture and consequence | Road allegiance, Raze and zealot fate earned their place as anti-entrenchment counter-routes. **Schism, faction fights, era art and beacon basins were built too early** — surface added before anyone outside this room had read the core | Built |
| **NICE** — ordered, unbuilt | 1. narrated teaching opening · 2. wordless endscreen · 3. visible trader agents · 4. interactive structures · 5. procedural maps | #1 is the only one blocking playability |
| **PROPOSED** — designed, gated on the stranger test | **Encounter mini-games** (§2) — three encounter types × two poles, the only moment the player touches individuals | Unbuilt. First in line if §4 says the loop reads as arithmetic; dropped if it says the loop already lands |
| **RULED, unwired** | **The tellings** (§2) — the Sonder bank + `bank/sonder-teller.js`, one call at the conversion event | Engine built and banked (A8); the hook in `uhta-slice.html` is the next commit, under `sonder-telling-surface` |
| **CUT** until the loop is proven fun | `hope_trade` as designed; road-tier chains; traversal cinematic; final art and audio | Out |

**The stop rule.** Nothing new gets built below the CORE/PASS-1 line until §4 passes with a stranger at the keyboard — *except* work that unblocks a §4 criterion, which is the gate rather than a violation. My first draft of this rule banned the narrated opening, the only work that could satisfy the criteria it blocks.

## 4. Definition of Playable — the acceptance test

*Answering: "really nail down what a playable version looks like so you can start testing the gameplay loop." A stranger sits down at `uhta-slice.html` with no instruction from me, and:*

| # | Criterion | Status |
|---|---|---|
| 1 | Reaches their first Sleep without being told what any key does | **Blocked** — needs the narrated opening |
| 2 | Can state unprompted what changed while they slept | Untested — predicted pass |
| 3 | Can name the two things they can make people feel, and which they are doing | **Blocked** — same dependency |
| 4 | Reaches a terminal within ~30 min / 10–30 sleeps | Untested — the sleep envelope is bot-measured; the wall clock never has been |
| 5 | Can point at the fog bank and say what it is doing to them | Untested — at risk |
| 6 | After losing, can say what they would do differently | **Untested — the one that matters** |

**Tally: 0 of 6 tested.** Thirteen ruleset generations of verified mechanics, and the loop has never been played by anyone but me. Every claim about *feel* here is mine, measured against bots. **Protocol once 1/3/5 clear:** five think-aloud sessions, one question at every sleep boundary — "what changed, and why?" — recording sleeps-to-terminal, wall-clock time, and every moment the player hunts for a UI that isn't there.

**Scope and constraints.** CORE, PASS 1 and PASS 2 all run in the grey-box slice (48×48 tiles, fog-of-war, on-load self-test 11/11 asserting the JS port matches the reference sim tick-for-tick). Three constraints: **(1)** one person, part-time, to a 9/1 capstone — hence a queue of exactly three items: narrated opening → front-render legibility → five playtests; **(2)** the Director is new to game engines, which is why an engine-free reference simulator exists at all; **(3)** the binding technical risk — **the exploit surface has not been re-attacked under the combined genesis + schism + road-allegiance model**, each verified only in isolation.

## 5. AI Architecture

*Answering: "tweak and improve your agent list."* One agent, one system; every output gated by the human Director. Shared memory is a **blackboard** of versioned repo files, so no run depends on another's live context.

| Agent | Owns (the one wow) | Produces — format |
|---|---|---|
| **Director** (human) | Every gate, all tuning, canon | Approve / revise / redirect; git commits |
| **Orchestrator** | Dispatch only — who runs next, with which packet. Never gates, never authors | Run manifest: agent, packet path, expected artifact path |
| **Mechanic Designer** | The tunable ruleset | 2–3 testable variants as `rules-vN.json`, each citing the GDD section it answers |
| **Red-Teamer** | Degenerate-strategy attacks | `attacks-vN.md` — every attack harness-reproducible |
| **Keeper** | Canon coherence | Context packets + `reports/contradictions-runN.md` |
| **Playtester** | Engine-free reference sim + bot policies | `metrics-vN.md` — measures shape, never judges fun |
| **Programmer** | Phaser/JS build, spec before code | `SPEC.md` → `uhta-slice.html`, self-test green |
| **Aesthetic Director** | Visual language; render layer only, **never** belief math | Sprite atlases + render diffs + screenshots at gate |
| **Writer** | Game-facing text: narration, era flavor, endscreen | Line sets in the game's register — short, declarative, no mythology |
| **Critic** | Lore and tone compliance of generated text | Pass/fail note per line set, quoting the chunk the line breaks or honors |
| **Sonder DM** (A8) | The people's side of the story: interpreter + narrator over a facts ledger the model never writes | `sessions/<id>/story.json` → `bank/sonder-bank.js`, every telling style-gated, ending on a question |

The Orchestrator is the addition that needs justifying, and headcount is not the justification: with the Writer and Critic running batch generation, the run manifest is the only thing guaranteeing a generated line set reaches the Critic *before* it reaches the build.

*Data flow: Director → Orchestrator → Keeper → specialist → Keeper diff → Director gate → commit → build. Every specialist writes to the blackboard, which feeds the Keeper's next packet and the build's data files. The Mermaid architecture diagram ships with Assignment 3.*

**What a contradiction actually does.** *Answering Avery's main note.* The Keeper diffs every output against `CANON.md` and files a report **before** I read the output — the two are stapled, so I never see a proposal without its diff on top. Every flag is one of exactly four classes — `CONTRADICTS-LOCKED`, `EXCEEDS-SCOPE`, `UNGROUNDED`, `TUNING-ONLY` — and each quotes **both sides**: the offending line and the canon line it violates, cited to a section. Flags never gate; **they block silence.** A `CONTRADICTS-LOCKED` flag cannot be closed by ignoring it — before the commit lands the ruling must be **UPHOLD**, **AMEND** (canon changes, transcribed with run-number provenance) or **DEFER** (it becomes a named open question), written into that run's report so report and ruling land in one commit. "No ruling" is not a state a commit can be in. The mechanism has caught one real bug in shipped code — and passed over it four times first.

**What the player ever notices.** *Answering Avery's Player Experience note.* These are invisible in play — they should be — but invisible is not inconsequential. The **context packet** is why a captured fear-zealot correctly counts toward your unification, instead of a board you can see you have won but the game will not end. The **Keeper pass** is why the tie you lose is the tie the endscreen told you you would lose. `rules-vN.json` is every number the game feels like; `attacks-vN.md` is why a frontal flame siege converts zero heads, so influence costs footwork instead of holding a button. If an agent cannot earn a line here, it should not be seated.

## 6. Technical Strategy

**Pipeline:** prompt → artifact → Keeper contradiction check → harness verification → Director gate → commit → engine. Rule variants are data files the build loads at runtime, so a post-playtest tuning change reaches the player **without a code review**. Prompts and outputs are versioned together; nothing auto-promotes. **Routing:** Opus-class only where the output is judgment (rules, attacks, canon diffs); Sonnet-class for anything verifiable by running it.

**Verification — three layers, none of which covers fun.** Coherence (the Keeper diff), behavioral (the harness runs every variant and attack headlessly, so a broken invariant surfaces before it is gated), implementation (build self-test 11/11). Fun is §4's stranger test — the layer this crew does not have.

**Token budget — projections vs. measured actuals.** Lean single-pass runs were projected at ~15–20K tokens ($0.03–0.35 each). Agentic runs that verify their own output with harness batteries measured **4–6× that** — the Mechanic Designer run came in at **71K actual against 19K projected**, and art passes at **85–135K**, a category the original budget omitted entirely. Revised projection through capstone: **~$25–40** API-priced. The original conclusion survives strengthened: **the binding constraint is Director review time, not tokens** — a full design → attack → salvage → verify → port cycle costs single-digit dollars and paces entirely on human gate decisions. Tasks no agent may perform: fun-tuning by playtest, win/loss sign-off, the difficulty stance, naming and tone, commits, and the ruling on every contradiction.

## 7. Revision & Growth

| Avery's Assignment-1 note | Landed in |
|---|---|
| *"Specify what the Keeper actually does when it detects a contradiction — a structured report format, a blocking prompt, a diff against CANON.md."* | **§5** — all three adopted, as a blocking *construct* rather than a blocking prompt so the agent still cannot gate. Writing it down exposed three defects in the mechanism as run. |
| *"'Keeper pass' and 'context packet' … without translating what the player would ever notice."* | **§5** — every agent artifact mapped to a player-facing consequence, those two first; a role that cannot earn a line there should be unseated. |
| *"Figure out early which are core that should get built first and which are nice."* | **§3** — a five-tier build order plus a stop rule, naming *which* Pass-2 items were built too early rather than excusing the tier. |
| *"Really nail down what a playable version looks like so you can start testing the gameplay loop."* | **§4** — a six-criterion pass/fail test, with the number that matters printed: **0 of 6 tested.** |

## 8. Logic Gaps and Open Questions

**Resolved.** **The one text after the dawn (v0.9.10):** a `CONTRADICTS-LOCKED` flag against §1 Tone, raised when the Sonder engine landed, ruled AMEND with scope — tellings at conversions as paused cards, nothing else; ruling and this transcription land in one commit, as §5 requires. Worship grants stamina, with an action floor preserving agency. The scale widened to −12..+12 with burnout semantics. Roar's Fear-coding resolved by witness radius: out-of-radius roaring is free terrain work, witnessed roaring is a Fear act, roaring at the hope-burned is the save. The antagonist stopped being a hidden coefficient — a deferred Uhtcearu voided balance, drama and exploit-counter at once — and became the Grief Front.

**Open, ordered.** (1) The loop has never been tested by a stranger; §4 turns that from an embarrassment into a gate. (2) The combined-model exploit re-attack (§4). (3) The Keeper's report discipline lapsed after run 19 — fifteen reports for twenty-three runs, and the one contradiction the crew ever caught has no committed diff. A contract is worth what the trail behind it is worth. **Dials deferred to playtest:** front render legibility, era thresholds, the wordless endscreen, a bounded counter-pole mercy, zealot-death cost, run-length envelope.

## 9. Proposal — the Temple endgame (2026-08-21, pre-ruling)

> **Status: PROPOSED, not canon.** Director pitch for a game-balance run; every number below is a hypothesis for the Mechanic Designer to vary and the harness to measure. This section is the sim-facing brief only. The presentation design (the temple interior scene, the terminal paintings, the start menu) is in `blackboard/gdd/CONCEPT-temple-endgame-and-start-menu.md` and is not the Designer's concern.

**The change in one line.** The antagonist gets a fixed location on the map. A **Temple** structure is placed at a random site at genesis; a permanent fog column is rendered above it; the Grief Front event originates from the temple rather than appearing at its target; and the win terminal becomes two-phase — it *arms* when the unification hold completes and *fires* when the player avatar reaches the temple tile. The loss terminal is unchanged.

**Placement constraints for the random roll.** ≥14 tiles from the cave `[24,24]`; ≥6 tiles from every beacon basin (`[[7,7],[41,7],[7,41],[41,41],[24,44]]`) and from the map edge (multi-tile footprint must fit); never inside a tribe's genesis position; drawn from the run seed so harness replays are deterministic.

**Variants requested — all three, harness decides.**

- **A — presentation only.** Temple and fog column are render-layer only; the Front is exactly `rules-v3.9.1-C`. Zero sim change. The control arm.
- **B — origin change.** Front spawns at the temple position and travels to `largest_dominant_pole_tribe_position`; `duration_sleeps` counts from arrival; `move_tiles_per_sleep` must rise above 1 or it never arrives on a 48×48 map — that is the tuning question. The *target* is unchanged from Run 23b; only origin and travel change.
- **C — local decay zone.** Elevated passive decay within a radius of the temple (the `LANDMARKS` §7 hook), so the walk from the hold to the temple costs something. Interacts with the Front; needs the full arm treatment.

**Two-phase terminal (all variants).** WIN: the existing hold (≥0.8, 6 ticks spanning a generation, no living opposing zealot, |S| ≥ 3) sets a `win_armed` flag; the terminal fires on temple entry. LOSS: unchanged, always live, including while `win_armed` — a same-tick tie still resolves to the loss. The stamina floor (~5 actions) is unchanged, so the armed state has nothing new to farm. The win/loss *definitions* are locked canon and do not change; only the moment the win terminal is evaluated moves.

**Known canon contact, for the Keeper.** B and C touch the Run 23b `spawn_at` salvage (origin becomes geographic again; target does not). The two-phase terminal touches "checked every tick, terminal immediately." The fixed `[24,6]` temple coordinate in `art/LANDMARKS.md` was proposed, never ruled. The §3 stop rule gates the *build* of this (NICE #2), not this proposal run.

**Questions for this run.** Does a fixed origin re-enable the centroid-steering attack that Run 23b closed? Can the hold-to-temple walk be lost, farmed, or trivialised? Does variant C make Hope runs unwinnable? Median added sleeps per variant against v3.9.1? Can any variant make the Front fire in a do-nothing run?
