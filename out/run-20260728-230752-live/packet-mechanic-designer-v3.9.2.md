# Context packet — mechanic-designer — v17 | for run: Front feel (straggler wear softening)

## CANON digest (verbatim)

# CANON.md — v17 | 2026-07-28 | gates [G1–G21 · Runs 17–22 · review-board closeout (v0.9.1/v0.9.2) · Run 23/23b SALVAGE — rules-v3.9.1-C ratified · A1-feedback closeout (v0.9.7)]

> **Process canon lives in `CANON-process.md`** (Keeper escalation, build order, Definition of Playable, roster, RAG corpus, report-discipline defect). This file is the always-on digest, capped at **900 words** (`prompts/keeper.md` Mode A); the split is what brought it back under.

**Open, promoted to top of queue:** the loop has never been tested by anyone but the Director. Thirteen ruleset generations verified, zero external playtests, 0 of 6 Playability criteria tested.

## Delta from v15

### Runs 20–22 — the living world, now canon (was WIP at v15)
**Genesis (v3.6):** the world self-forms — grey nomad loners (55) + symmetric founding zealots (1F/1H) that gather, settle (min 5 followers at devout average), colonize. Terminal grace until formed (aligned ≥ 0.4 or first settle). genesis-off reproduces legacy exactly. **Schism (v3.7):** full+devout settlements fission same-pole daughter colonies (pop cap 16, fission radius 10, max 6 tribes) — the world grows by spreading, not ballooning. **Road allegiance (v3.7.1):** roads carry pole+strength; enemies crossing erode toward grey (then detach re-recruitable) and wear the road; enemy zealots damped on your color. **Rebalance (v3.7.3, Director):** difficulty is **asymmetric by design — Fear easy, Hope hard** (bot proxy at that gate: FEAR ~22/25, HOPE ~20/25 — **superseded, do not read as current**; at v3.9.1 the arms measure hope 21/25 / fear 16/20, and the genesis bots invert the OFF baseline. The stance is intent; re-benchmark before reading direction). hope_trade DISABLED (revisit as visible trader agents). **Ascension (v3.8):** follower-driven power tiers 0–3 (beacons 1→4, flame/aura radius, stamina cap 10→24), recomputed each sleep; the kaiju scales with the flock. **Peer contagion (v3.8.1):** belief spreads NPC-to-NPC (~0.1/neighbor, cap 0.7, r2); apathy spreads too.

### Review-board closeout — Director rulings (GDD v0.9.1, v0.9.2)
1. **Flame tint:** the cave choice sets only the starting tint; alignment is fully re-tintable through play. Identity is emergent.
2. **Counterpoint:** musical sense — a second, undetermined voice against Uhtcearu's theme, not a hope-predisposed opposite. Reconciles purpose-born with blank-slate.
3. **Document intent:** academic/portfolio piece; experience comps only (Journey/Gris; Reus/Black & White); no commercial claim.
4. **Win-vs-loss tie → LOSS.** *Discovery at implementation (Run 23):* the v3.7 sim silently gave the WIN the tie; `win_loss.tie_priority: "loss"` now enforced data-driven. No organic tie observed in ~420 runs; synthetic tie verified loss-first. **(v17 note: this is the canonical worked example of the §3.2 escalation rule — a `CONTRADICTS-LOCKED` flag against this line, ruled UPHOLD.)**
5. **The opening is narrated (wordless after the first dawn):** a text narrator — the teacher — names each verb and its consequence during the genesis cycle only; the words end permanently at the first sleep. Teaching-text is instrumentation, not authorship; the endscreen question stays open (§6).
6. **GRIEF CANON:** grief is not a pole — it is the *gravity*. Long-term grief traps people in apathy; the per-tick decay toward 0 IS Uhtcearu's grief. Uhtcearu never fights for a color; he drowns the board in grey. Catastrophes therefore wear the dominant pole toward 0 and never recruit for the opposite.

### Run 23 → 23b — Uhtcearu active events: the GRIEF FRONT (rules-v3.9.1-C, ratified)
Run 23 proposed three antagonist philosophies (tide / judge / law); **Director selected A (Grief Front)**. attacks-v5 verdicted it **safe but half-dead as shipped** (in-sphere drift delta 0.000/sleep; centroid spawn and instantaneous trigger both dodgeable) with a data-only salvage set; **Director ruled salvage-as-antagonist.** Co-gated fix set (Run 23b):
- `front_strength 4.0` → inside-front decay 2.0/tick **exactly equals zealot pull**: a true STALL. Held believers neither deepen nor grey; the front can never flip (decay can't cross 0), burn (decay is not same-pole pressure), or kill. Stragglers bounded by the step cap at −1/tick.
- `spawn_at largest_dominant_pole_tribe_position` — the fog condenses ON the winner's largest tribe; kills centroid-steered siege aiming.
- `trigger_trailing_window_sleeps 3` — fires on trailing-max dominance ≥ 0.55; kills hover-then-sprint scheduling.
- `affects_dominant_pole_only true` — grief wears only the winner, never greys enemy holdouts.
- Cooldown held at 2 (3-on/2-off, ~0.65 late-game uptime).

**Verified (metrics-v3.9.1, ~40 arms):** 80/80 legacy equivalence; 0 assert violations; hope campaign 23→21/25 at unchanged median, fear 16/20 untouched; 96% of fronts do real work; no front-as-shield, no in-front haven, no high-dominance sandwich. Full numbers stay in `outputs/v2/metrics-v3.9.1.md` — this digest carries decisions, not evidence. **Antagonist identity confirmed: "grief takes the stragglers; the shepherded stand."**

### Pipeline status
GDD (**v0.9.7**) → Orchestrator dispatch → Keeper packet → Mechanic Designer → Director select → Red-Team → Director salvage ruling → Playtester (harness, ~40 arms) → ratify → build port; Writer → Critic → Director for content. **Thirteen ruleset generations** — one committed `rules-*.json` file each, `rules-v1-B` → `rules-v3.9.1-C`. Fifteen Keeper reports across runs 1–19. Reference sim: `sim/harness-v3.9.py` (supersedes sim/harness.py; grief front + tie priority, data-driven, absent-field = prior behavior).

### Remaining work — human-owned / post-gate
**The external playtest (top of queue).** Narrated teaching opening (blocks 1, 3); front-render legibility (blocks 5); Keeper report backlog runs 20–23; fun-tuning; spawn-position lever; miracle polarity; difficulty-proxy re-benchmark; endscreen question; deferred §2.6 systems; trader agents; **CrewAI port 7/28**; **content pipeline 7/30**; capstone 9/1.

## Open questions (delta from v16)
Resolved: living-world gate (runs 20–22); review-board quick fixes; wordless-teaching; grief scale position; Uhtcearu active events; Keeper flag destination, core-vs-nice ordering, the meaning of "playable", orchestrator deferral (all → `CANON-process.md`). Remain: front feel items; endscreen; miracle polarity; **difficulty-proxy hygiene — the Fear-easy/Hope-hard stance is intent, not a measured result (metrics-v3.9.1 §F reads hope-favored)**; fun-tuning envelope; deferred systems; trader agents; whether the six Playability criteria are the right six; narration and endscreen content, blocked behind the Writer + Critic pipeline.

## Canon lines this run touches

**CANON ruling 6 (grief canon):** "grief is not a pole — it is the *gravity*. Long-term grief traps people in apathy; the per-tick decay toward 0 IS Uhtcearu's grief. Uhtcearu never fights for a color; he drowns the board in grey. Catastrophes therefore wear the dominant pole toward 0 and never recruit for the opposite."

**Run 23b salvage block (all five lines):**
- `front_strength 4.0` → inside-front decay 2.0/tick exactly equals zealot pull
- `spawn_at largest_dominant_pole_tribe_position`
- `trigger_trailing_window_sleeps 3`
- `affects_dominant_pole_only true`
- Cooldown held at 2

**Antagonist identity (CANON v17):** "grief takes the stragglers; the shepherded stand."

**Verified constraints (metrics-v3.9.1):** 80/80 legacy equivalence; 0 assert violations; hope campaign 23→21/25 at unchanged median, fear 16/20 untouched; 96% of fronts do real work; no front-as-shield, no in-front haven, no high-dominance sandwich.

## Relevant specification excerpts (cite §)

### §2 — The antagonist (grief canon + Grief Front mechanics)

**GDD §2 (Key systems):**

> **The antagonist — grief canon + the Grief Front.** Grief has no position on the scale because grief is not a pole — **it is the gravity**: the passive decay toward 0 (0.4/tick, scaled by dominance and idle sleeps) *is* Uhtcearu, and apathy is what grief leaves behind. His active form is gated and live: past trailing-window dominance 0.55, a visible desaturating fog bank condenses **on the winner's largest tribe** for 3 sleeps (cooldown 2). Inside it, grief exactly cancels a zealot's pull (front decay 2.0/tick = pull 2.0/tick): the shepherded **stall** — never flipped, burned, or killed — while unshepherded believers grey quickly. It wears only the dominant pole (grief never helps anyone), and it cannot fire in a do-nothing run by construction. *Grief takes the stragglers; the shepherded stand.*

### §2 — Contagion pressure mechanics (the step cap and zealot pull)

**GDD §2 (Core mechanic):**

> Each tick an NPC sums the pressure on it and steps **at most 1**: its zealot's pull **2.0/tick**, overlapping spheres **0.8** (sphere radius 2 + floor(√group)), peer contagion **0.1/neighbor within r2, capped 0.7/tick** (apathy spreads too), and passive decay **0.4/tick** toward 0.

**The step cap (−1/tick maximum movement) is the binding constraint on straggler wear.** An NPC outside all spheres experiences only decay (0.4/tick base, scaled by dominance + idle) and front pressure if inside a front. At `front_strength 4.0`, inside-front decay = 0.4·(1 + 4.0) = 2.0/tick, which **saturates the step cap** for any NPC at |belief| ≥ 2 (metrics-v3.9.1 §E: an unheld convert at v=5 fully greys in 5 ticks, ~2.4× the pre-salvage rate).

### §2.8 — Definition of Playable, criterion 5

**GDD §2.8:**

> | 5 | Can point at the grey fog bank and say what it is doing to them | **Untested — predicted at risk.** The front stalls camps but erases loners at ~2.4× the pre-salvage rate; the render must sell both readings |

### §6 — Open questions (front feel)

**GDD §6:**

> Front feel (straggler wear saturates the step cap — ~2.4× pre-salvage; render must sell "stalls camps, erases loners")

## The baseline ruleset and what may move

**Baseline:** `rules-v3.9.1-C.json` (ratified Run 23b).

**Locked and out of scope (per Director question set):**
- The grief canon itself (CANON ruling 6)
- Zealot immunity (`"zealots_immune": true`)
- All `win_loss` parameters
- The scale and bands (`scale`, `bands`)
- `hope_trade` (stays `"enabled": false`)
- **`front_strength 4.0` as the in-sphere stall anchor** — inside-front decay must remain exactly 2.0/tick to preserve the shepherded-stand identity

**In scope for variation:**
- `cooldown_sleeps_after_expiry` (currently 2)
- `duration_sleeps` (currently 3)
- `radius_tiles` (currently 6)
- `trigger_dominance_min` (currently 0.55)
- `trigger_trailing_window_sleeps` (currently 3)
- `move_tiles_per_sleep` (currently 1)
- **Derived parameter:** `outside_dominance_scale` (currently 1.0) — scales the dominance term in the damping formula for NPCs outside the front but still subject to passive decay

**The constraint surface:**
- **In-sphere stall must remain net ~0.000/sleep** (front decay 2.0/tick = zealot pull 2.0/tick).
- **Straggler wear is bounded by the step cap at −1/tick** for any change that does not touch `front_strength` or the base damping formula.
- **The three Run-23b closures must not re-open:** spawn anchor (largest dominant tribe position), trailing-window trigger (no hover-sprint), dominant-pole-only wear (no cleanup-assist).
- **Legacy equivalence when `enabled: false`** must hold (80/80 terminal match to v3.7).

**Current measured behavior (metrics-v3.9.1 §E, §F):**
- In-sphere drift delta: 0.000/sleep (exact stall)
- Straggler wear: an unheld NPC at v=5 fully greys in 5 ticks (~2.4× pre-salvage rate of ~12 ticks)
- Late-game duty cycle at cooldown 2: ~0.65 uptime (3-on/2-off)
- 96% of fronts do real work (dominance ≥ 0.55 at spawn)
- Hope campaign: 21/25 wins (−2 from pre-front 23/25); Fear: 16/20 (unchanged)

## Open questions in scope for this run

**From the Director's question set:**

1. **Can straggler wear be brought below the step-cap saturation point while `front_strength 4.0` keeps inside-front decay exactly equal to zealot pull (2.0/tick)?** Which dial does it — front_strength, cooldown, duration, radius, or the trigger threshold — and what does each cost?

2. **What is the late-game front duty cycle at cooldown 2** (3-on/2-off, measured ~0.65 uptime, metrics-v3.9.1 §F), **and does a longer cooldown buy legibility without making the antagonist a rumour?**

3. **Does any proposed change re-open a closure the Run-23b salvage bought** — the GF6 siege engine (spawn anchor), the GF5 hover-sprint shadow (trailing window), or the cleanup-assist (affects_dominant_pole_only)?

4. **Locked and out of scope:** the grief canon itself (CANON ruling 6 — grief wears the dominant pole and never recruits for the opposite), zealot immunity, `win_loss` in all its parts, the scale and bands, and `hope_trade` (stays disabled).

**From GDD §6 and §2.8 criterion 5:**

- Front feel: the render must sell "stalls camps, erases loners" — one antagonist, not two.
- Playability criterion 5 (untested, predicted at risk): "Can point at the grey fog bank and say what it is doing to them."

## Excluded from this packet (item — one-line reason)

- **GDD §1 (Summary, Concept, Tone)** — no mechanical bearing on front tuning; identity and voice are locked.
- **GDD §2 verb table (Walk, Flame, Roar, Light beacon, Raze, Wait, Sleep)** — player verbs unchanged; front is NPC-affecting only.
- **GDD §2 Burnout, Genesis, Schism, Settling, Faction fights, Zealot fate, Ascension, Worship economy** — all locked systems orthogonal to front tuning.
- **GDD §2 Win/loss** — explicitly out of scope per Director question 4.
- **GDD §2.7 (Build order)** — process, not mechanics.
- **GDD §2.8 criteria 1–4, 6** — not blocked on this run; criterion 5 is the only playability line this touches.
- **GDD §3 (AI Architecture), §4 (Technical Strategy), §7 (Provenance)** — pipeline and process, no mechanical content.
- **GDD §5 (Identified Logic Gaps)** — all resolved or accepted; none touch front tuning.
- **CANON-process.md** — process canon only; no sim rules or tuning values.
- **Full `rules-v3.9.1-C.json` schema outside `world.uhtcearu_events.grief_front`** — the baseline is provided in full above; only the grief_front block is in scope for variation.

## Assumptions

[ASSUMPTION] **The step cap (−1/tick maximum NPC movement) is a locked substrate parameter** — it appears in no `rules-*.json` file and is implemented as a sim constant. Treating it as immovable; if it is tunable, that opens a different design space than the one this packet assumes.

[ASSUMPTION] **"Straggler wear below step-cap saturation" means reducing the effective decay rate experienced by unshepherded NPCs to < 1.0/tick** — i.e., an unheld NPC at v=5 takes > 5 ticks to grey, vs. the current exactly-5-tick measured behavior.

[ASSUMPTION] **"Legibility" in question 2 refers to player perception of the front as a recurring, attributable antagonist** — i.e., a longer cooldown trades lower uptime for clearer on/off rhythm, making each front arrival more noticeable rather than blending into continuous pressure.

[ASSUMPTION] **The dominance term in `uhtcearu_damping_formula` is the same player-pole fraction the live damping formula reads** (CANON v17 meta note on v3.9), and `outside_dominance_scale` would multiply that term for NPCs outside the front radius while inside-front NPCs have dominance replaced entirely per `inside_replaces_dominance_
