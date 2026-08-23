# Context packet — mechanic-designer — v25 | for run: Temple endgame, GDD §9, schema 3.10 dials

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

1. **CANON ruling 6 (GRIEF CANON):** grief is the gravity; catastrophes wear the dominant pole toward 0, never recruit for the opposite. Temple placement gives grief a geographic home; local decay zone (variant C) is a passive grief effect.

2. **Run 23b salvage — `spawn_at largest_dominant_pole_tribe_position`:** the Front condenses ON its target. Variant B changes this to `temple_position` (geographic origin) while keeping the same target for movement — reverses the Run-23b centroid-steering fix. Red-Team must verify the attack stays closed.

3. **Run 23b salvage — `trigger_trailing_window_sleeps 3`:** fires on trailing-max dominance. Unchanged in all variants; listed because the temple walk adds sleeps and the trigger window is a sleep count.

4. **Run 23b salvage — `affects_dominant_pole_only true`:** grief wears only the winner. Variant C's local decay zone must honor this (if enabled).

5. **Review-board ruling 4 (tie priority):** `win_loss.tie_priority: "loss"` — a same-tick tie resolves to the loss. The two-phase terminal (hold arms, temple entry fires) keeps this rule live while armed.

6. **Win/loss check (CANON §2, GDD §2):** WIN = ≥0.8 unification for 6 ticks spanning a generation, no living opposing zealot, only while acting (|S| ≥ 3). LOSS = grey+burned ≥0.8, always live. The two-phase change moves *when* the win fires, not *what* the win is.

7. **Genesis placement (v3.6):** grey nomads scattered + founding zealots. Temple placement must not collide with tribe genesis positions (constraint in §9).

8. **Map size and beacon basins (GDD §2, art/LANDMARKS.md):** 48×48 map, five beacon sites at `[[7,7],[41,7],[7,41],[41,41],[24,44]]`, cave at `[24,24]`. Temple placement constraints reference these as exclusion zones.

## Relevant specification excerpts (cite §)

### GDD §2 — Win/loss terminals (verbatim relevant subsection)

**Win state / lose state** — both are unification events, checked every tick.

- **WIN:** your pole holds ≥0.8 of the population for 6 ticks spanning a generation, with **no living opposing zealot**, and only while you are acting. You win by doing, never by drifting.
- **LOSS:** grey + burned ≥0.8 of the population. The loss check always runs, and **a same-tick tie resolves to the loss** — your excess feeds the sky. The counts are disjoint, so a completed win-hold can never flip; a coasting brink can (measured 1 run in 20 — intended).

### GDD §9 — Proposal: the Temple endgame (verbatim, full section)

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

### GDD §3 — Build order (stop rule only)

**Stop rule: nothing new is built below the CORE/PASS-1 line until the Definition of Playable passes with an external player** — **except** work required to unblock a Definition-of-Playable criterion, which is not "new," it is the gate. Permitted and required: NICE #1 (narrated opening) and front-render legibility. Frozen: NICE #2–5 and everything else below the line, until criterion 6 has been asked.

### GDD §4 — Definition of Playable (status only)

**Tally: 0 of 6 tested.** Thirteen ruleset generations of verified mechanics, and the loop has never been played by anyone but me.

### GDD §2 — Player verbs (stamina floor reference)

| Verb | Cost |
|---|---|
| **Walk** | 0.5/tile (0.4 roaded) |
| **Flame** | 2.5 |
| **Roar** | ½ walk cost of distance |
| **Beacon** | 3 |
| **Raze** | 4 + 0.5·devout |
| **Wait** | 0 |
| **Sleep** | ends cycle |

**Stamina floor (GDD §2, §9 reference):** `stamina.floor_actions: 5` — a losing player always has moves left. The armed state has nothing new to farm because the floor is unchanged.

## The baseline ruleset and what may move

**Baseline:** `rules-v3.10-C.json` (schema 3.10) — behaviourally identical to `rules-v3.9.1-C` with every new block default-off. This file exists so the Designer has dials to vary; no value here is ratified.

**What MUST NOT change (locked canon):**
- `scale`, `bands`, `contagion`, `player_pressure`, `burnout`, `settling`, `zealot_fate`, `stamina`, `raze` — untouched.
- `world.map_size: 48`, `world.tribes`, `world.tribe_size_initial`, `world.growth_per_tribe_per_sleep`, `world.apathy_decay_per_tick`, `world.zealot_pull_per_tick`, `world.uhtcearu_damping_formula`, `world.generation_ticks_per_sleep` — untouched.
- `world.genesis`, `world.schism`, `world.road_allegiance`, `world.faction_fight`, `world.settlement_exile`, `world.contagion_spread` — untouched (the living world is ratified).
- `world.uhtcearu_events.grief_front.trigger_dominance_min: 0.55`, `max_concurrent_fronts: 1`, `cooldown_sleeps_after_expiry: 2`, `radius_tiles: 6`, `inside_replaces_dominance_term: true`, `front_strength: 4.0`, `outside_dominance_scale: 1.0`, `zealots_immune: true`, `trigger_trailing_window_sleeps: 3`, `affects_dominant_pole_only: true` — Run 23b salvage, locked.
- `ascension` — untouched.
- `win_loss.check_after_every_tick: true`, `hold_window_ticks: 6`, `hold_must_span_generation: true`, `hold_continuity: "skipped_pauses_failed_resets"`, `requires_no_living_opposing_zealot: true`, `win_count_bands`, `loss_count_states`, `unification_threshold_fraction: 0.8`, `intent_measure` (the |S| ≥ 3 rule), `tie_priority: "loss"` — locked.

**What MUST change (the run's mandate):**

**Variant A (control):**
- `world.temple.enabled: true`
- `win_loss.terminal_fires_on: "temple_entry"`
- All other `world.temple.*` fields remain default (placement will occur, but no other temple mechanics active).
- `world.uhtcearu_events.grief_front.*` unchanged from v3.9.1-C (spawn_at, duration_counts_from, move_tiles_per_sleep all at salvage values).

**Variant B (origin + travel):**
- `world.temple.enabled: true`
- `win_loss.terminal_fires_on: "temple_entry"`
- `world.uhtcearu_events.grief_front.spawn_at: "temple_position"`
- `world.uhtcearu_events.grief_front.duration_counts_from: "arrival"`
- `world.uhtcearu_events.grief_front.move_tiles_per_sleep` — **TUNING QUESTION:** must be >1 to reach target on 48×48 map; sweep required.
- `world.uhtcearu_events.grief_front.arrival_radius_tiles` and `max_travel_sleeps` — set per schema, tune if needed.
- `world.temple.local_decay.enabled: false`

**Variant C (local decay zone):**
- `world.temple.enabled: true`
- `win_loss.terminal_fires_on: "temple_entry"`
- `world.temple.local_decay.enabled: true`
- `world.temple.local_decay.radius_tiles` — **TUNING QUESTION:** how large?
- `world.temple.local_decay.strength` — **TUNING QUESTION:** how strong? (adds to damping formula's dominance term)
- `world.temple.local_decay.affects_dominant_pole_only: true` (honors Run 23b salvage)
- `world.uhtcearu_events.grief_front.*` unchanged from v3.9.1-C (no origin change in C).

**Temple placement (all variants):**
- `world.temple.placement: "random_constrained"` (the default; `fixed_position` is a fallback if random fails).
- Constraints per §9: `min_dist_cave: 14`, `min_dist_sites: 6`, `min_dist_edge: 6`, `min_dist_tribes: 6`, `placement_tries: 500`, `footprint_radius_tiles: 2`.
- Reference coordinates: `cave: [24,24]`, `beacon_sites: [[7,7],[41,7],[7,41],[41,41],[24,44]]`.

**Harness bot behavior (all variants):**
- `win_loss.temple_entry.harness_pilgrim_tiles_per_sleep` — **TUNING QUESTION for the sweep:** scripted walk toward temple while armed. Sweep `[3, 6, 12]` per Director question set. `0` means the bot must walk itself (uncosted movement disabled).
- `win_loss.temple_entry.disarm_if_hold_breaks: false` (locked per schema).

## Open questions in scope for this run

**From Director question set (verbatim):**
1. How many sleeps does the armed-to-terminal walk add, and how sensitive is it to `harness_pilgrim_tiles_per_sleep` (sweep 3, 6, 12)?
2. Are any runs lost while armed?
3. Does `spawn_at: temple_position` re-enable centroid steering (Run 23b attack A6) — and why does B halve front exposure?
4. Split Hope and Fear for C: does either pole become unwinnable?
5. Do-nothing baseline is 24 sleeps — does any variant change it?

**From GDD §9 (verbatim):**
1. Does a fixed origin re-enable the centroid-steering attack that Run 23b closed?
2. Can the hold-to-temple walk be lost, farmed, or trivialised?
3. Does variant C make Hope runs unwinnable?
4. Median added sleeps per variant against v3.9.1?
5. Can any variant make the Front fire in a do-nothing run?

**Tuning questions (Designer's scope):**
- Variant B: `move_tiles_per_sleep` value that reaches target without trivializing or stalling.
- Variant C: `local_decay.radius_tiles` and `local_decay.strength` that cost the walk without making Hope unwinnable.
- All variants: `harness_pilgrim_tiles_per_sleep` sweep `[3, 6, 12]` — measure sleep-count sensitivity.

## Excluded from this packet (item — one-line reason)

- **GDD §1 (Summary, Tone)** — no mechanical contact; temple is a sim structure, not a narrative beat.
- **GDD §2 (Encounters, The tellings)** — unbuilt; temple does not interact with encounter mini-games or Sonder bank.
- **GDD §2 (Contagion, Burnout, Settling, Zealot fate, Ascension, Road allegiance, Faction fights, Genesis, Schism)** — ratified mechanics unchanged by this run; baseline ruleset carries them verbatim.
- **GDD §5 (AI Architecture)** — crew roster and data flow; no relevance to ruleset variant design.
- **GDD §6 (Technical Strategy)** — pipeline and token budget; Designer produces JSON, not commits.
- **GDD §7 (Revision & Growth)** — Avery's notes and their resolutions; historical context only.
- **GDD §8 (Logic Gaps and Open Questions) — full section** — extracted relevant open questions only (difficulty-proxy hygiene, front feel, endscreen); the rest (Keeper report backlog, content pipeline, CrewAI port) are out of scope.
- **CANON-process.md (full file)** — process canon (Keeper escalation, build order, roster, RAG corpus); no sim-rule contact. Retrieved because the run brief mentions the §3 stop rule, but only that excerpt is included above.
- **CANON v15 deltas (Runs 20–22 mechanics detail)** — summarized in digest; full tick-by-tick behavior is in the baseline ruleset, not re-specified here.
- **CANON pipeline status detail** — thirteen ruleset generations, fifteen reports; historical accounting, no design input.
- **CANON remaining work detail** — playtest queue, content pipeline, port dates; post-gate human work, not Designer scope.
- **Baseline ruleset meta fields** — `meta.variant`, `meta.hypothesis`, `meta.gdd_version`, `meta.schema`, `meta.patches`, `meta.gate`, `meta.*_note` fields are provenance and explanation; Designer sets them per output variant, but they are not constraints.
- **Baseline ruleset `world.hope_trade`** — `enabled: false`, deferred to trader agents (GDD §3 NICE #3); untouched.
- **Baseline ruleset `world.temple` render/presentation fields** — `fixed_position`, `cave`, `beacon_sites` are reference coordinates for placement constraints, not tunable; fog column rendering is build-layer, not sim.
- **art/LANDMARKS.md** — referenced in §9 as containing a proposed fixed temple coordinate `[24,6]`; that proposal was never ruled, and this run uses `random_constrained` placement, so the file is not retrieved.
- **CONCEPT-temple-endgame-and-start-menu.md** — presentation design (interior scene, terminal paintings, start menu); explicitly out of scope per GDD §9.

## Assumptions

[ASSUMPTION] Temple placement occurs at genesis (before tribes settle) so `min_dist_tribes` can be enforced against genesis positions. Schema 3.10 does not specify the placement timing; inferred from "never inside a tribe's genesis position" constraint and the fact that settled tribes are not genesis-positioned.

[ASSUMPTION] `world.temple.local_decay` (variant C) ADDS `strength` to the damping formula's dominance term for NPCs within `radius_tiles` of the temple, rather than replacing it. Schema says "elevated passive decay" and "ADDS strength"; the grief_front precedent is `inside_replaces_dominance_term`, which this does not set.

[ASSUMPTION] An active grief front's `inside_replaces_dominance_term` takes precedence over `local_decay` for NPCs under both effects (no double-punishment). Inferred from "Interacts with the Front" in §9 and the Run 23b "no double-punishment" principle.

[ASSUMPTION] `harness_pilgrim_tiles_per_sleep` is uncosted movement (does not spend stamina). Schema says "scripted bots know nothing about the temple; while armed the harness walks the avatar this many tiles toward it at each sleep boundary, uncosted." The word "uncosted" is explicit.

[ASSUMPTION] The do-nothing baseline (24 sleeps, GDD §9 question 5) refers to a harness run with no player actions and `world.uhtcearu_events.enabled: false`, measured against v3.9.1-C. This is the only configuration that produces a deterministic sleep count independent of player behavior.

[ASSUMPTION] "Median added sleeps" (§9 question 4) means the difference in median terminal sleep count between each variant and v3.9.1-C, measured across the same harness campaign (same bot policies, same seed set).

[ASSUMPTION] The centroid-steering attack (§9 question 1, Run 23b attack A6) refers to the player steering the dominant-pole NPC centroid away from their own position to delay or avoid the Front. Variant B's `spawn_at: temple_position` makes origin fixed, but `move_toward: largest_dominant_pole_tribe_position` is unchanged, so the *target* is still player-influenceable.

[ASSUMPTION] "Why does B halve front exposure?" (Director question 3) refers to an expected or observed reduction in front uptime or effectiveness in variant B compared to A or v3.9.1-C. The question implies a measured or predicted phenomenon; the Designer's task is to produce the variant so the harness can measure it.

[ASSUMPTION] `win_loss.temple_entry.disarm_if_hold_breaks: false` means the armed state persists even if the unification hold drops below threshold after arming. The loss check remains live, so a
