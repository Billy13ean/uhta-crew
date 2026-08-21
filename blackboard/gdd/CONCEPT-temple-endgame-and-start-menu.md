# Concept — the Temple of Grief endgame, and an interactive start menu

*2026-08-21 · Director pitch, pre-pipeline. Nothing here is canon until it has been through the crew and ruled on the bench. Companion to `art/LANDMARKS.md` §4/§7 (which already designed the temple and already flagged the storm-on-temple tradeoff) and `SHIP-CHECKLIST.md`.*

---

## Part 1 — The pitch, in the game's own terms

### 1.1 What changes

Today the antagonist is the **Grief Front**: a fog bank that condenses on the winner's largest tribe for 3 sleeps when dominance passes 0.55, then lifts (rules-v3.9.1-C, Run 23b). It is weather with no home.

Proposed: grief gets a **home**. A Temple spawns at a random site at genesis; the storm sits above it permanently, visible from anywhere as a dark column on the horizon. The Front still goes out to do its work, but it *comes from somewhere now*. When the player's unification hold completes, the storm dissipates, the temple opens, the player walks in, finds Uhtcearu — a seated figure larger than the avatar — and he fades to dust as the player approaches. Then a painted screen, pole-specific, shows the world remade in the player's image. A loss gets a painted screen too.

The one-line argument: *the game currently ends with a number crossing 0.8. It should end with a walk.*

### 1.2 The beats

| # | Beat | What the player sees | Sim state |
|---|---|---|---|
| E0 | **Genesis** | A dark column on the horizon, rendered even in unrevealed fog (LANDMARKS §6 rule 1). Multi-tile grey structure beneath it once revealed. | `temple_pos` rolled at genesis under placement constraints (§1.4) |
| E1 | **Mid-game** | Storm is permanent above the temple; the Grief Front fires as today, but its fog now *issues from* the temple and crawls to the target rather than materialising on it | Front mechanics unchanged or re-tuned (variants, §2.3) |
| E2 | **Hold complete** | Storm thins over ~1 sleep and lifts. Sky clears above the temple for the first time. No text. | Win check passes → enters new `WIN_PENDING` state instead of terminating. Loss check keeps running (it can still flip — measured 1/20 coasting brinks, intended) |
| E3 | **The walk** | Player crosses the map to the temple. World stays live. Temple steps are the only tiles where the unification overlay (grass / ember) stops. | Walk is the existing verb; no new input |
| E4 | **Inside** | Painted interior (`make_temple_scene.py`, already built, pole-colour-bleed assertion passing). Seated figure ~200px vs ~26px avatar. Player walks toward him. | Scene overlay; WASD only |
| E5 | **The dust** | Figure dissolves bottom-up into grey particles that fall, not rise. The room's only warm thing is still the player's flame, and now its light reaches the far wall. | Terminal fires here, not at E2 |
| E6 | **The world remade** | Full-screen painting + a short text card. **Hope:** the cave-mirror `hope` composition scaled up — joined hands, grass to the horizon, green sky. **Fear:** `fear` composition — the lunge, ember fields, red sky. Both end on the wordmark. | `RUN_ENDED: WIN_HOPE / WIN_FEAR` |
| L | **Game over** | The `grey` cave-mirror: both mouths grey, figures standing still, not touching. A text card. Storm over the temple never lifted; the screen shows it still standing. | `RUN_ENDED: LOSS` |

### 1.3 Why this is consistent with canon (and where it is not)

**Consistent:**

- *"Grief is not a pole — it is the gravity."* A temple that takes no colour (the painter's `POLE-COLOUR BLEED: none` assertion) and a storm that wears only the winner's colour when it goes out both survive. The win screens are pole-coloured because they are *after* grief, not inside it.
- LANDMARKS §4 already argues scale and silhouette for exactly this room. E4–E5 is that scene with one animation added.
- NICE #2, "wordless endscreen," is the next item in the fixed NICE order. This is that item, larger.

**Conflicts the bench has to rule on** (each is UPHOLD / AMEND / DEFER — no fourth option, CANON-process #1):

| # | Canon line | Conflict | My recommendation |
|---|---|---|---|
| R1 | `spawn_at: largest_dominant_pole_tribe_position` (Run 23b salvage, "no dead-air centroid misses, no player-steerable aim") | Fog issuing from a fixed temple is geographic again — the thing 23b was built to kill. LANDMARKS §7 called this "a real design tradeoff, not a free upgrade." | **AMEND, variant-gated.** Keep 23b's *target* (front still lands on the largest tribe); change only its *origin* and travel. If the harness shows siege-aiming comes back, drop to presentation-only (storm is a sprite, front logic untouched). |
| R2 | CANON #5: *"the words end permanently at the first sleep"* | E6 and L have text. | **AMEND** with precedent: `sonder-telling-surface` was amended on 2026-08-21 to allow tellings at conversions. Propose a second named surface, `terminal-card-surface`: one card, after the terminal, ≤ 40 words, Critic-gated, register-gated. Or UPHOLD and make E6/L wordless except the wordmark — the paintings can carry it. Decide before the Writer runs. |
| R3 | Win = unification hold, checked every tick, terminal immediately | Win now *arms* at the hold and *fires* at E5. | **AMEND.** Two-phase terminal. The Red-Teamer must attack the gap: can a player lose during the walk? (Yes, by design — the loss check never stops.) Can a player farm the pending state? (Stamina floor ~5 still applies; nothing new to farm.) |
| R4 | Temple at fixed `[24,6]` (LANDMARKS §8 Q1, never ruled) | You want random spawn. | **AMEND to random with constraints** (§1.4). Random costs the "map you can hold in your head" spine; the horizon silhouette gives most of it back. |
| R5 | Stop rule: NICE #2–5 frozen *until criterion 6 has been asked* (a stranger has lost and said what they'd do differently) | 0 of 6 tested. This is NICE #2. | **Honest answer: run one stranger test first** (it's on the ship checklist anyway). If you won't, AMEND the stop rule explicitly on the bench rather than quietly. |
| R6 | CUT tier: "all final art and audio" until the loop is proven fun | Four new paintings. | Presentation-only work has been allowed all along (cave, temple scene). Log as PASS-2 surface, not final art. |

### 1.4 Temple placement — constraints for the random roll

So the Mechanic Designer has something to design against rather than "random":

- ≥ 14 tiles from the cave `[24,24]` (never in the opening's reveal radius)
- ≥ 6 tiles from every beacon basin and from map edge (multi-tile footprint must fit)
- Not inside any tribe's genesis position
- Seeded from the run seed, so bots and harness replays are deterministic

### 1.5 The storm and the Front — what "sits above it" means mechanically

Three candidates, which is what the Designer is asked for anyway:

- **A — Presentation only.** Storm is a permanent render over the temple; the Front is exactly v3.9.1. Zero sim change, zero harness debt. Cheapest, and honestly probably the right first cut.
- **B — Origin change.** Front spawns at the temple and crawls to the largest dominant tribe at `move_tiles_per_sleep` (needs a higher step than 1 or it never arrives — that's the tuning question). Duration counts from arrival.
- **C — Apathy well.** Temple radius has elevated passive decay (LANDMARKS §7 hook #1). Makes the walk in E3 cost something. Most interesting, most dangerous; interacts with the front and needs the full ~40-arm treatment.

Recommend the crew builds all three and the harness decides — that's the pipeline's job.

---

## Part 2 — The interactive start menu

Presentation-only, no rulings needed beyond the standing ones (wordmark is gated to the opening; the cave is a place, not a menu).

**Concept: the menu *is* the cave wall.** You already have the Plato's-cave title painting and the rule that meaning arrives as silhouette. Make that interactive before the player has picked a mouth:

- The white flame follows the cursor (or WASD). The three-light model re-renders the wall in real time — the shadow-play stretches and slides as the light moves. This is the beacon SHADOW ALIGNMENT minigame (LANDMARKS §5.1) used as a menu, so the code gets built once and reused.
- Menu choices are *places on the wall*, not buttons: walk the flame toward the red mouth and the fighting shadows resolve; toward the green and the tending ones do. **Start** is walking out — which is already how the cave opening works, so the menu and the opening become the same screen.
- Secondary items (continue / sound / credits) are carvings low on the wall that only become legible when the flame is near them. Sound starts **off**; the carving for it is a bell.
- On Start the title rises and blurs into the game underneath (`BACKLOG-later.md` #1 — the transition is ~10 lines of CSS).
- Stronger art: render the painter at native 680 or 1020 instead of 2× nearest (BACKLOG note), keep the ~38-colour family and Bayer dither so the revisit variants stay in sync.

The class-13 checks this satisfies: title screen present, controls taught by doing, one sentence of "why am I here" (the A4 n1 line), sound starts quiet.

---

## Part 3 — The process: how to run this through the crew

The crew has six pipelines and one bench. This feature touches all of them, in this order. Each step's output is the next step's input; don't skip the bench.

### Step 0 — Land this document on the blackboard

`blackboard/gdd/` alongside the GDD, as a proposal. The Keeper retrieves by chunk; if it isn't on the blackboard, the agents can't see it.

### Step 1 — The bench first (canon/CANON-BIBLE.html via the console `/bible`)

Rule R1–R6 above. Every AMEND appends an AMEND-tagged line to CANON's delta and a `## Ruling` block; the audit invariant (AMEND lines = AMEND rulings) has been 0 = 0 since July — this is the first feature that will make it count. Save the ruling → `canon/CANON-RULING.json`. Every pipeline run after this records the law in force.

Do R5 honestly. If it's "run the stranger test first," the rest of this waits a week and that's fine.

### Step 2 — Sim rules: the A3 crew (`run_crew.py`)

This is the only pipeline allowed to change a number in the sim.

```bat
python run_crew.py --selftest
python run_crew.py --version-tag v3.10 --run-id temple-grief ^
  --goal "Give grief a home: a Temple spawns at genesis under placement constraints; the Grief Front issues from it. Win arms at the unification hold and fires when the player enters the temple. Loss unchanged." ^
  --questions "Does a fixed origin re-enable siege aiming (23b)? Can the walk from hold to temple be lost, farmed, or made trivial? Does variant C's apathy well brick Hope runs? Median added sleeps per variant?"
```

What comes out: Keeper B1 packet → `rules-v3.10-{A,B,C}.json` + rationale → validation gate → `attacks-v6.md` + `attacks.json` → `metrics-v3.10.md` from real harness runs → `contradictions-run24.md` with the blank `## Ruling`. You fill the ruling. Expect the Keeper to raise `CONTRADICTS-LOCKED` on R1 and R3 — that's the flag class finally firing against an agent output for the first time (CANON-process #2 defect 3), which is a good thing.

Also closes CANON-process #7 if you commit the report: nothing has been written since run 19.

### Step 3 — Keeper transcription

AMEND lines into `CANON.md` (keep it under 900 words — move prose to CANON-process), GDD bump to v0.9.11: §2 antagonist paragraph, §2.7 tier table (NICE #2 → built-in-progress), §2.8 unchanged. Ratify one ruleset file; `rules/` gets exactly one new file (CANON-process #6: a generation is a committed file).

### Step 4 — Words: content → GER → style

Only if R2 is AMEND. Beats for the Writer: `e6_hope`, `e6_fear`, `loss`. The standing retrieval rule applies — each beat pulls §2.5 (experience) and the win/loss row.

```bat
python run_content.py --beats e6_hope,e6_fear,loss --candidates 6 --run-id temple-cards
python run_ger.py --run-id temple-cards-register
python run_style.py --run-id temple-cards-style
```

Critic clears lore/tone, GER clears register (the CONTRADICTS-CHUNK citing machinery from A6), Style scores against `style/STYLEGUIDE.md` T1–T4 / V1–V4 / F1–F5. Fill the Director selection block. Three short lines should survive, or the screens go wordless and R2 flips to UPHOLD.

### Step 5 — Art (deterministic painters, then the visual audit)

No LLM in this step; the painters are Python and the audit is code.

| asset | source | status |
|---|---|---|
| Temple interior + seated Uhtcearu | `art/make_temple_scene.py` | built; add the dust-dissolve as a frame sequence or a runtime particle over the still |
| Temple top-down sprite, multi-tile, grey, no patina | `art/make_sprites.py` (it packs both atlases itself — `ASSETS.md` is stale on this) | not built |
| Storm column sprite / shader over the temple tile | new, in the slice's fog renderer | not built |
| Win-Hope, Win-Fear, Loss screens | `art/make_title_scene.py hope / fear / grey` at native res, wordmark gated back on for terminals | cave-mirror modes built; scale-up + composition pass needed |
| Start-menu wall, live three-light render | port `glow()` / `sil_layer()` to JS | not built |

Then `python style/make_visual_guide.py` — the palette audit reports % of pixels outside the locked COL family. Anything over tolerance is a finding, not a judgment; you decide.

### Step 6 — Build: the A5 builder, then the probe

Add the feature to `builder/features.py` (it ranks from the GDD tier table, so Step 3's GDD edit is what makes it visible — the builder is not allowed to read the answer). Then:

```bat
python run_builder.py --selftest
python run_builder.py --feature temple-endgame --run-id temple-build
```

Output is a patched `uhta-slice.html` in `out/`, never in place. Acceptance before it's promoted to `blackboard/build/`:

- Self-test grows checks: **G15** temple placed under constraints and deterministic per seed; **G16** win arms, does not terminate, at the hold; **G17** terminal fires only on temple entry; **G18** loss still fires during the walk; **G19** storm render absent after arm.
- `tools/mg_probe.js` win-bot extended to the full arc: cave → wake → hold → walk → temple → dust → card. Today it stops at WON in ~11 s; it needs to stop at E6.
- Zero page errors headless; 10/10 green on the probe.

Start menu goes in the same patch or its own — its own is safer; it has no sim surface.

### Step 7 — The stranger (again)

This is R5's debt paid. The checklist protocol: silent observation, one question per sleep boundary, and one new one at the end — *"what was in the temple?"* If they can't say, E4–E5 isn't reading and the painting needs the scale argument pushed harder.

### What not to do

- Don't hand-edit `rules-v3.9.1-C.json`. A number that changed without a harness run is the one failure mode the whole crew exists to prevent.
- Don't let the builder touch the sim. It patches presentation and wiring; the rules file it reads is the one Step 2 ratified.
- Don't mark anything "passing" before a stranger has produced it (CANON-process #4).
