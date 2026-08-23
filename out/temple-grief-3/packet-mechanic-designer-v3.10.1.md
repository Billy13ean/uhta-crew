# Context packet — mechanic-designer — v25 | for run: Temple endgame (GDD §9)

## CANON digest (verbatim)

# CANON.md — v18 | 2026-08-21 | gates [G1–G21 · Runs 17–22 · review-board closeout (v0.9.1/v0.9.2) · Run 23/23b SALVAGE — rules-v3.9.1-C ratified · A1-feedback closeout (v0.9.7) · the tellings ruled (v0.9.10)]

> **Process canon lives in `CANON-process.md`** (Keeper escalation, build order, Definition of Playable, roster, RAG corpus, report-discipline defect). This file is the always-on digest, capped at **900 words** (`prompts/keeper.md` Mode A); the split is what brought it back under.

**Open, promoted to top of queue:** the loop has never been tested by anyone but the Director. Thirteen ruleset generations verified, zero external playtests, 0 of 6 Playability criteria tested.

## Delta from v17 — the tellings (v0.9.10, ruled 2026-08-21)
**One text after the dawn.** `CONTRADICTS-LOCKED` against §1 Tone, raised by the A8 Sonder engine; **ruled AMEND** (`canon/CANON-RULING.json`, rule `sonder-telling-surface`): a banked *telling* — third person, gated, ending on a question — may be shown **at a conversion** as a paused card over the held world, colour-matched, once per conversion with ≥1 Sleep between, never in the sleep-0 cycle, never on the overworld or HUD. The pillar stands everywhere else. Three 2026-08-19 presentation proposals (HUD / instructions / repeats) remain **open**. Hook in the slice: next commit.

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

1. **GRIEF CANON (ruling 6):** "grief is not a pole — it is the *gravity*" — the temple as grief's home is a geographic expression of this principle; catastrophes wear the dominant pole toward 0 and never recruit for the opposite (§2.6).

2. **Run 23b salvage — `spawn_at largest_dominant_pole_tribe_position`:** the fog condenses ON the winner's largest tribe; kills centroid-steered siege aiming. **This run's variant B changes spawn_at to `temple_position`**, which re-opens the centroid-steering attack vector (attacks-v5 A6) that Run 23b closed. The Red-Teamer must verify whether geographic spawn + travel restores the exploit or whether the trailing-window trigger (also Run 23b) is sufficient defense.

3. **Run 23b salvage — `front_strength 4.0`:** inside-front decay 2.0/tick exactly equals zealot pull, a true STALL. **Variant C adds a second decay zone** (temple local_decay) that may stack with or replace the Front's decay; the interaction must be specified and the stall property re-verified.

4. **Win terminal — "checked every tick, terminal immediately" (§2.2, ruling 4 tie-priority context):** the two-phase terminal (arm on hold complete, fire on temple entry) changes *when* the win evaluates, not *what* it evaluates. The loss check remains live while armed; tie_priority still applies.

5. **The §3 stop rule:** "nothing new is built below the CORE/PASS-1 line until the Definition of Playable passes with an external player — except work required to unblock a Definition-of-Playable criterion." The temple endgame is NICE #2 (wordless endscreen) and is gated on the stranger test; **this proposal run does not violate the stop rule** because it produces `rules-*.json` variants for harness measurement, not a build.

## Relevant specification excerpts (cite §)

### §2.2 — Win/loss terminals (current ratified state, rules-v3.9.1-C)

**WIN:** your pole holds ≥0.8 of the population for 6 ticks spanning a generation, with **no living opposing zealot**, and only while you are acting. You win by doing, never by drifting.

**LOSS:** grey + burned ≥0.8 of the population. The loss check always runs, and **a same-tick tie resolves to the loss** — your excess feeds the sky. The counts are disjoint, so a completed win-hold can never flip; a coasting brink can (measured 1 run in 20 — intended).

**Intent measure (rules-v3.9.1-C):** `player_pole = sign(S), where S = signed sum of player-delivered valence pressure (witnessed Flame/Roar/Raze pushes plus own sleep and beacon aura ticks) over the trailing 1 sleep; the win check evaluates only on ticks where abs(S) >= 3, otherwise it is skipped that tick (the loss check always runs); no carry-over of a previous pole under any condition; before the first player action the win check is skipped`.

### §9 — Proposal: the Temple endgame (2026-08-21, pre-ruling)

**Status: PROPOSED, not canon.** Director pitch for a game-balance run; every number below is a hypothesis for the Mechanic Designer to vary and the harness to measure.

**The change in one line.** The antagonist gets a fixed location on the map. A **Temple** structure is placed at a random site at genesis; a permanent fog column is rendered above it; the Grief Front event originates from the temple rather than appearing at its target; and the win terminal becomes two-phase — it *arms* when the unification hold completes and *fires* when the player avatar reaches the temple tile. The loss terminal is unchanged.

**Placement constraints for the random roll.** ≥14 tiles from the cave `[24,24]`; ≥6 tiles from every beacon basin (`[[7,7],[41,7],[7,41],[41,41],[24,44]]`) and from the map edge (multi-tile footprint must fit); never inside a tribe's genesis position; drawn from the run seed so harness replays are deterministic.

**Variants requested — all three, harness decides.**

- **A — presentation only.** Temple and fog column are render-layer only; the Front is exactly `rules-v3.9.1-C`. Zero sim change. The control arm.
- **B — origin change.** Front spawns at the temple position and travels to `largest_dominant_pole_tribe_position`; `duration_sleeps` counts from arrival; `move_tiles_per_sleep` must rise above 1 or it never arrives on a 48×48 map — that is the tuning question. The *target* is unchanged from Run 23b; only origin and travel change.
- **C — local decay zone.** Elevated passive decay within a radius of the temple (the `LANDMARKS` §7 hook), so the walk from the hold to the temple costs something. Interacts with the Front; needs the full arm treatment.

**Two-phase terminal (all variants).** WIN: the existing hold (≥0.8, 6 ticks spanning a generation, no living opposing zealot, |S| ≥ 3) sets a `win_armed` flag; the terminal fires on temple entry. LOSS: unchanged, always live, including while `win_armed` — a same-tick tie still resolves to the loss. The stamina floor (~5 actions) is unchanged, so the armed state has nothing new to farm. The win/loss *definitions* are locked canon and do not change; only the moment the win terminal is evaluated moves.

**Known canon contact, for the Keeper.** B and C touch the Run 23b `spawn_at` salvage (origin becomes geographic again; target does not). The two-phase terminal touches "checked every tick, terminal immediately." The fixed `[24,6]` temple coordinate in `art/LANDMARKS.md` was proposed, never ruled. The §3 stop rule gates the *build* of this (NICE #2), not this proposal run.

**Questions for this run.** Does a fixed origin re-enable the centroid-steering attack that Run 23b closed? Can the hold-to-temple walk be lost, farmed, or trivialised? Does variant C make Hope runs unwinnable? Median added sleeps per variant against v3.9.1? Can any variant make the Front fire in a do-nothing run?

### §2.6 — The antagonist: the Grief Front (ratified state)

**The antagonist — the Grief Front.** Grief has no position on the scale, because grief is not a pole — **it is the gravity**. The passive decay toward 0 *is* Uhtcearu, and apathy is what he leaves behind. His active form is on screen: past 0.55 dominance a desaturating fog bank condenses **on the winner's largest tribe** for three sleeps. Inside it, grief exactly cancels a zealot's pull — the shepherded **stall**, never flipped or killed, while unshepherded believers grey quickly. It wears only the dominant pole's colors and cannot fire in a do-nothing run. *Grief takes the stragglers; the shepherded stand.*

### §4.2 — RAG corpus and packet sizing (GDD)

Chunk = one GDD `###` subsection; index = the blackboard file list; selection = Keeper Mode B1 with its exclusion list; packets target ≤15K tokens; `CANON.md` is the always-on digest under a 900-word cap.

## The baseline ruleset and what may move

**Baseline:** `rules-v3.10-C.json` (schema 3.10, pre-ruling control). This file is **behaviourally identical** to `rules-v3.9.1-C` (parity-tested); it exists so the Mechanic Designer has dials to vary. Every new block defaults to `enabled: false`.

**Schema 3.10 additions (all default-off in the baseline):**

1. **`world.temple`** — placement, footprint, local_decay zone (variant C).
   - `enabled: false` (variant A control)
   - `placement: "random_constrained"` with constraints per §9
   - `fixed_position: [24, 6]` — proposed, never ruled; used only if `placement: "fixed"`
   - `cave: [24, 24]`, `beacon_sites: [[7,7],[41,7],[7,41],[41,41],[24,44]]`
   - `min_dist_cave: 14`, `min_dist_sites: 6`, `min_dist_edge: 6`, `min_dist_tribes: 6`
   - `placement_tries: 500`, `footprint_radius_tiles: 2`
   - `local_decay.enabled: false` (variant C only)
   - `local_decay.radius_tiles: 8`, `local_decay.strength: 1.0`, `local_decay.affects_dominant_pole_only: true`

2. **`world.uhtcearu_events.grief_front`** — new spawn/travel fields (variant B).
   - `spawn_at: "largest_dominant_pole_tribe_position"` (v3.9.1 ratified) | `"temple_position"` (variant B)
   - `duration_counts_from: "spawn"` (v3.9.1) | `"arrival"` (variant B option)
   - `arrival_radius_tiles: 1`, `max_travel_sleeps: 6` (variant B only, if `duration_counts_from: "arrival"`)
   - `move_tiles_per_sleep: 1` (v3.9.1; variant B must tune this ≥2 for 48×48 arrival)

3. **`win_loss.terminal_fires_on`** — two-phase win (all variants).
   - `"hold_complete"` (v3.9.1) | `"temple_entry"` (all temple variants)
   - `temple_entry.harness_pilgrim_tiles_per_sleep: 6` — scripted bot walk toward temple while armed; 0 = bot must walk itself
   - `temple_entry.disarm_if_hold_breaks: false` — whether a broken hold after arming reverts to unarmed

**What may NOT move (locked canon):**

- Win/loss definitions: ≥0.8 threshold, 6-tick hold spanning generation, no living opposing zealot, |S| ≥ 3 intent measure, tie_priority loss (ruling 4).
- Front mechanics: `front_strength: 4.0` (stall property), `trigger_trailing_window_sleeps: 3`, `affects_dominant_pole_only: true`, `cooldown_sleeps_after_expiry: 2`, `zealots_immune: true` (all Run 23b salvage).
- Grief canon: catastrophes wear the dominant pole toward 0, never recruit for the opposite (ruling 6).

**What the Designer MUST vary:**

- **Variant A:** `world.temple.enabled: false`, `win_loss.terminal_fires_on: "hold_complete"` — the control, bit-identical to v3.9.1-C.
- **Variant B:** `world.temple.enabled: true`, `world.temple.local_decay.enabled: false`, `world.uhtcearu_events.grief_front.spawn_at: "temple_position"`, `win_loss.terminal_fires_on: "temple_entry"`. Tune `move_tiles_per_sleep` (≥2 for arrival) and choose `duration_counts_from` (`"spawn"` or `"arrival"`).
- **Variant C:** `world.temple.enabled: true`, `world.temple.local_decay.enabled: true`, `win_loss.terminal_fires_on: "temple_entry"`. Tune `local_decay.radius_tiles` and `local_decay.strength`. Front spawn may be `temple_position` or `largest_dominant_pole_tribe_position` — Designer's call.

## Open questions in scope for this run

1. **Does `spawn_at: "temple_position"` re-enable the centroid-steering attack (attacks-v5 A6) that Run 23b's `spawn_at: "largest_dominant_pole_tribe_position"` closed?** The trailing-window trigger may be sufficient defense even with geographic spawn; the Red-Teamer must verify.

2. **Can the hold-to-temple walk be lost, farmed, or trivialised?** The stamina floor (~5 actions) is unchanged, but the armed state is a new game phase. Can a player arm the win, then lose the hold and be unable to re-arm? Can they farm the armed state indefinitely? Does `harness_pilgrim_tiles_per_sleep: 6` trivialise the walk (bot reaches temple in ≤2 sleeps from any corner)?

3. **Does variant C (local_decay) make Hope runs unwinnable?** Elevated decay near the temple may exhaust Hope believers during the walk; the Designer must tune `radius_tiles` and `strength` to preserve Hope viability. The difficulty stance (Fear easy, Hope hard) is intent, but "hard" ≠ "impossible."

4. **Median added sleeps per variant vs. the v3.9.1 control?** The two-phase terminal delays the win by the walk time; variant B's travel time adds further delay. Measure the distribution, not just the median.

5. **Can any variant make the Front fire in a do-nothing run?** The Front requires dominance ≥0.55; a do-nothing run should never reach that threshold (genesis is symmetric 1F/1H). If any variant fires the Front without player action, the trigger is broken.

6. **Variant B: `duration_counts_from: "spawn"` or `"arrival"`?** If `"spawn"`, a temple-origin Front ages during travel and may expire before reaching its target on a 48×48 map. If `"arrival"`, it does not age until within `arrival_radius_tiles`, capped at `max_travel_sleeps`. Which preserves the Run 23b stall property and the "grief takes the stragglers" identity?

7. **Variant C: does local_decay stack with or replace the Front's decay when both overlap an NPC?** The schema note says "an active grief front inside its own radius takes precedence (no NPC under both)" — the Designer must implement this precedence rule and verify no double-punishment.

## Excluded from this packet (item — one-line reason)

- **§1 Summary, Tone** — no mechanical contact; the temple is a sim structure, not a narrative beat.
- **§2.2 Player verbs table, Encounters, The tellings** — verb costs/effects are locked in the baseline; encounters are unbuilt and out of scope; tellings are a presentation surface with no sim impact.
- **§2.2 Systems that respond (Burnout, Genesis, Settling, Schism, Faction fights, Zealot fate, Ascension, Worship)** — all ratified in v3.9.1-C and unchanged by the temple proposal; the baseline inherits them verbatim.
- **§3 Build order, §4 Definition of Playable** — process canon; the stop rule is cited under "Canon lines this run touches" because it gates the *build*, not this run.
- **§5 AI Architecture, §6 Technical Strategy, §7 Revision & Growth** — pipeline and tooling; no mechanical specification.
- **§8 Logic Gaps and Open Questions (resolved items)** — the temple proposal is the only open question in scope; all resolved items (worship, scale, roar, antagonist philosophy) are already ratified in the baseline.
- **CANON-process.md** — retrieved because §9 cites the stop rule, but only the stop rule excerpt is included; Keeper escalation, report discipline, and roster are out of scope.
- **CANON.md deltas from v16 (A1-feedback closeout)** — process rulings (Keeper contract, build order, Definition of Playable, roster, artifact counts, report discipline); no sim rules or tuning values changed at that gate.
- **GDD v0.9.10 delta (the tellings)** — cited under "Canon lines this run touches" because the Sonder ruling established the paused-card presentation class; the telling content and Sonder engine are out of scope for a sim-facing run.

## Assumptions

[ASSUMPTION] The `world.temple.placement: "random_constrained"` algorithm draws from the run seed (deterministic harness replays), but the seed-derivation method is not specified in §9 or the baseline schema. The Designer may implement any deterministic method; the Playtester will verify replay stability.

[ASSUMPTION] The `win_loss.temple_entry.harness_pilgrim_tiles_per_sleep: 6` dial is a harness-only behavior (scripted bot walk toward temple while armed); the production build does not auto-walk the player. The Designer implements this as a harness hook, not a core sim rule.

[ASSUMPTION] The schema 3.10 `world.temple.fixed_position: [24, 6]` coordinate was proposed in `art/LANDMARKS.md` but never ruled (§9 "Known canon contact"). The Designer uses this value only if `placement: "fixed"`; the default `placement: "random_constrained"` ignores it.

[ASSUMPTION] The `world.temple.local_decay` precedence rule ("an active grief front inside its own radius takes precedence") means: if an NPC is inside both the temple's local_decay radius AND an active Front's radius, only the Front's decay applies (no stacking). The Designer must implement this as an explicit check, not an additive formula.
