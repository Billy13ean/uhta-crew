# attacks-v4 — Temple endgame, Variant A (control)

> **Scope:** `rules-v3.10.2-A.json` — two-phase terminal (arm on hold, fire on temple entry), temple render only, zero mechanical delta from v3.9.1-C except terminal timing. Red-Team verdict on whether presentation structure introduces failure modes.

---

### A1 — Armed-state farming (stamina accumulation across sleep cycles)

**Attack.** If the unification hold completes but the player delays temple entry, they can farm stamina across multiple sleep cycles while `win_armed: true`, accumulating resources with no loss risk if the hold remains stable. A player could arm at sleep 10, idle until sleep 20, and enter the temple with 10× the normal stamina budget.

**Mechanism.** `win_loss.terminal_fires_on: "temple_entry"` decouples hold completion from terminal evaluation. `disarm_if_hold_breaks: false` keeps the armed state even if the hold drops below 0.8, but the loss check (`grey+burned >= 0.8`) remains live. If the hold *stays* above 0.8, the player can sleep repeatedly without triggering either terminal, and `stamina.worship_to_stamina_formula` recomputes each wake, capping at tier-based `stamina_cap` (10–24). The floor is 5 actions; the cap is 10–24 depending on follower count. A stable 0.8+ hold at tier 3 (40+ followers, cap 24) allows 24 stamina per wake.

**Arithmetic (3 generations, seed 0, Hope campaign):**
- **Sleep 10 (hold completes, arms):** `wf = 0.82`, `pop = 96`, tier 2 (24 followers), `stamina_cap = 18`. Player has 18 stamina, spends 0, sleeps. `win_armed = true`.
- **Sleep 11 (idle wake):** `wf = 0.83` (hold stable, no player action), tier 2, cap 18. Stamina recomputed: `5 + 0.35×24 + 1.5×2 = 16.4 → 16`. Player sleeps again.
- **Sleep 12 (idle wake):** `wf = 0.84`, tier 2, cap 18, stamina 16. Player sleeps again.
- **Sleep 13 (temple entry):** Player walks 12 tiles (median temple distance per Designer's expected-shape) at 0.5/tile = 6 stamina, enters temple with 10 stamina remaining. Terminal fires, WIN.

**Expected delta vs immediate entry:** +3 sleeps (3 idle wakes), +48 stamina accumulated (16×3), but stamina is capped and unused stamina does not carry over. The attack *works* (player can delay indefinitely while armed) but is **self-limiting**: stamina caps at tier-based max, and a stable hold requires continued player pressure (the `intent_measure` |S| >= 3 rule means the win check skips on idle ticks, but the *hold* was already completed before arming, so skipped checks don't break it). The loss check is live, so if the hold breaks to grey+burned >= 0.8, the run loses even while armed.

**Falsification metric:** `median_terminal_sleep` in the campaign arm. If A > v3.9.1-C by >5 sleeps, farming is occurring. If `losses > 0` in the campaign arm with `win_armed` logged, the loss-check mitigation failed.

**Expected severity:** **TUNING** — the attack works but is bounded by stamina caps and loss-check liveness. A player can delay 3–5 sleeps to bank stamina, but cannot delay indefinitely without risking hold erosion. The Designer's "+2 sleeps" prediction (one to arm, one to walk) assumes immediate entry; measured campaigns will show whether players naturally delay or rush.

**Harness probe (P1).** `run_campaign_v3`, seeds 0–19, both poles, `max_sleeps: 40` (extended to allow farming). Invariant: `median_terminal_sleep <= 24` (v3.9.1-C median ~22, +2 for two-phase = 24; >24 indicates farming). Falsification metric: `median_terminal_sleep`.

**Suggested fix if confirmed.** Data-only: `win_loss.temple_entry.max_armed_sleeps: 5` — if armed for >5 sleeps without terminal, force-fire the win (player had their window). Alternatively, `disarm_if_hold_breaks: true` — if the hold drops below 0.8 after arming, disarm and require re-hold (punishes farming that erodes the hold). Both are schema-legal; neither is in the current variant.

---

### A2 — Temple placement collision with dominant tribe (zero-distance walk)

**Attack.** If the temple spawns within `footprint_radius_tiles: 2` of the player's dominant tribe position at the moment the hold completes, the armed-to-terminal walk is zero distance, and the terminal fires the same sleep as arming. The Designer's "+2 sleeps" prediction assumes a walk; a collision makes it +0.

**Mechanism.** Temple placement is `random_constrained` at genesis with `min_dist_tribes: 6` enforced against *genesis* tribe positions. Tribes wander (`world.wander.step_tiles_per_sleep: 1`, `home_box_tiles: 9`) and settle (`settling.settle_hold_generations: 1`). A settled tribe anchors, but its genesis position is not its settled position. If a tribe settles within 6 tiles of the temple (allowed, because `min_dist_tribes` only gates genesis positions), and that tribe becomes the player's dominant tribe (largest aligned population), the player's likely position (near their dominant tribe to maintain the hold) is near the temple. At `harness_pilgrim_tiles_per_sleep: 6`, a 6-tile walk is 1 sleep; a 0-tile walk (player already on temple footprint) is 0 sleeps.

**Arithmetic (hypothetical seed, Hope campaign):**
- **Genesis (sleep 0):** Temple placed at `[30, 30]`, tribe 0 (Hope founding zealot) at `[24, 24]` (cave), tribe 1 (Fear) at `[10, 10]`. `min_dist_tribes: 6` satisfied (distance 8.5 tiles).
- **Sleep 5:** Tribe 0 wanders to `[28, 28]` (within home box), gathers 12 followers, settles. Distance to temple: 2.8 tiles.
- **Sleep 10:** Player (Hope) has converted tribe 0 to `wf = 0.85`, hold completes. Player position: `[28, 28]` (at tribe). Temple position: `[30, 30]`. Distance: 2.8 tiles, within `footprint_radius_tiles: 2`. `win_armed = true`, player is already on temple footprint, terminal fires immediately. Total sleeps: 10 (same as if terminal fired on hold completion).

**Expected delta vs median:** −2 sleeps (Designer predicted +2, collision makes it +0). Probability: low (requires dominant tribe to settle near temple, and player to be at tribe when hold completes). Measured across 20 seeds, expect 0–2 collisions.

**Falsification metric:** `min(terminal_sleep)` in the campaign arm. If `min < 20` (v3.9.1-C floor ~18, +2 = 20), a collision occurred. Alternatively, log `temple_walk_distance` per run and check for `distance < 3` in winning runs.

**Expected severity:** **TUNING** — the attack works but is rare and does not break the game. A zero-distance walk is a lucky spawn, not an exploit. The two-phase terminal still functions (hold must complete before terminal fires); the walk is just trivial.

**Harness probe (P2).** `run_campaign_v3`, seeds 0–19, Hope only (Fear campaigns are shorter and less likely to have dominant tribes settle), `max_sleeps: 32`. Invariant: `min(terminal_sleep) >= 20` (no collision-induced early terminal). Falsification metric: `median_terminal_sleep` (if median < 22, collisions are common enough to shift the distribution).

**Suggested fix if confirmed.** Data-only: `world.temple.min_dist_settled_tribes: 10` — re-check temple placement constraints against settled tribe positions at the moment the hold completes, and if violated, move the temple to the nearest valid position. Requires schema extension (not in 3.10). Alternatively, accept the variance (collisions are rare and not exploitable).

---

### A3 — Loss while armed (hold breaks during temple walk)

**Attack.** If the player arms at a fragile hold (e.g., `wf = 0.81`, just above threshold) and the hold erodes to `grey+burned >= 0.8` during the temple walk, the loss terminal fires while `win_armed: true`. The Designer's expected-shape notes this as a vulnerability; the question is whether it occurs in practice.

**Mechanism.** `disarm_if_hold_breaks: false` keeps the armed state even if `wf` drops below 0.8 after arming. The loss check (`grey+burned >= 0.8`) is always live. During the temple walk, the player is moving (not flaming/roaring), so no new pressure is applied. Apathy decay (`world.apathy_decay_per_tick: 0.4`, scaled by dominance and idle sleeps) erodes alignment toward 0. If the walk takes 2 sleeps (12 tiles at 6 tiles/sleep) and the hold was marginal, decay can push `wf` below 0.8 and `grey` above 0.8.

**Arithmetic (3 generations, seed 0, Hope campaign, fragile hold):**
- **Sleep 10 (hold completes, arms):** `wf = 0.81`, `lf = 0.10`, `grey = 0.09`, `pop = 96`. Dominance `= 0.81` (Hope-aligned fraction). Damping formula: `0.4 × (1 + 1×0.81 + 0) = 0.72/tick`. Player is at `[10, 10]`, temple at `[35, 35]` (distance 35 tiles). `win_armed = true`.
- **Sleep 11 (walk toward temple):** Player walks 6 tiles (harness pilgrim), now at `[13, 13]`. No flame/roar, so no new pressure. Apathy decay: 3 ticks/generation × 0.72/tick = 2.16 per generation. Over 1 sleep (3 generations = 9 ticks), decay = 6.48 total across 96 NPCs = 0.0675/NPC. Hope-aligned NPCs (78) each lose 0.0675 alignment; new `wf = 0.81 - 0.0675 = 0.7425`. `grey = 0.09 + 0.0675 = 0.1575`. Loss check: `grey + burned = 0.1575 + 0 = 0.1575 < 0.8`, no loss.
- **Sleep 12 (continue walk):** Player walks 6 more tiles, now at `[16, 16]`. Decay continues: `wf = 0.7425 - 0.0675 = 0.675`. `grey = 0.1575 + 0.0675 = 0.225`. Still no loss.
- **Sleep 13 (continue walk):** `wf = 0.675 - 0.0675 = 0.6075`. `grey = 0.225 + 0.0675 = 0.2925`. Still no loss.
- **Sleep 14 (continue walk):** `wf = 0.6075 - 0.0675 = 0.54`. `grey = 0.2925 + 0.0675 = 0.36`. Still no loss.
- **Sleep 15 (continue walk):** `wf = 0.54 - 0.0675 = 0.4725`. `grey = 0.36 + 0.0675 = 0.4275`. Still no loss.
- **Sleep 16 (arrive at temple):** Player enters temple footprint. `wf = 0.4725`, `grey = 0.4275`, `grey+burned = 0.4275 < 0.8`. Terminal fires: **WIN** (armed state persists, loss threshold not reached).

**Revised arithmetic (faster decay, higher dominance):** If dominance were 0.9 (stronger hold), damping = `0.4 × (1 + 0.9) = 0.76/tick`, and decay/sleep = 6.84. Over 6 sleeps (35-tile walk at 6 tiles/sleep), total decay = 41.04 across 96 NPCs = 0.428/NPC. Starting `wf = 0.81`, final `wf = 0.81 - 0.428 = 0.382`, `grey = 0.09 + 0.428 = 0.518`. Still no loss.

**Corrected arithmetic (loss threshold is grey+burned >= 0.8, not wf < 0.8):** The loss check is `(grey + burned) / pop >= 0.8`, not `wf < 0.8`. If `wf = 0.81` and `grey = 0.09`, then `aligned = 0.81×96 = 78`, `grey_count = 0.09×96 = 9`, `burned = 0`. For loss, need `grey + burned >= 0.8×96 = 77`. Starting with 9 grey, need to convert 68 aligned NPCs to grey. At 0.0675/NPC/sleep, that takes 68 / 0.0675 = 1007 sleeps. **The attack does not work** — decay is too slow to trigger loss during a realistic temple walk.

**Re-examining the mechanism:** The Designer's expected-shape says "any run lost while `win_armed: true`" is a measurement target, implying it *could* happen. Under what conditions? If the hold is marginal (`wf = 0.81`) and an **active Grief Front** spawns during the walk, the Front's `front_strength: 4.0` replaces the dominance term, making inside-front decay = `0.4 × (1 + 4.0) = 2.0/tick`. Over 3 sleeps (Front duration), decay = 18/tick × 9 ticks = 162 total across 96 NPCs = 1.69/NPC. If 78 aligned NPCs each lose 1.69, new `wf = 0.81 - 1.69 = −0.88` (impossible; clamped to 0). All 78 NPCs grey out, `grey = 87/96 = 0.906 > 0.8`. **LOSS while armed.**

**Revised attack:** Loss while armed requires a Grief Front to spawn during the temple walk. Front trigger: `dominance >= 0.55`, `cooldown_sleeps_after_expiry: 2`, `trigger_trailing_window_sleeps: 3`. If the player arms at sleep 10 with `dominance = 0.81`, the Front can trigger at sleep 11, 12, or 13 (trailing window). If it spawns at sleep 11 and the player is walking (not flaming), the Front stalls the hold for 3 sleeps, eroding it to grey. By sleep 14, `grey >= 0.8`, loss fires.

**Falsification metric:** `losses` in the campaign arm, filtered for runs where `win_armed: true` was logged. If `losses > 0` in armed runs, the attack confirmed.

**Expected severity:** **TUNING** — the attack works but requires a Front to spawn during the walk, which requires the walk to take >=3 sleeps (18+ tiles) and the Front trigger to fire. Probability: low (median temple distance ~12 tiles = 2 sleeps, Front trigger is trailing-window so may fire before arming). Measured across 20 seeds, expect 0–2 armed losses.

**Harness probe (P3).** `run_campaign_v3`, seeds 0–19, both poles, `max_sleeps: 40`. Invariant: `losses == 0` in runs where `win_armed: true` (no loss while armed). Falsification metric: `losses` (if >0, check logs for armed-state losses).

**Suggested fix if confirmed.** Data-only: `win_loss.temple_entry.suppress_front_while_armed: true` — disable Grief Front spawns while `win_armed: true`, so the walk cannot be interrupted. Alternatively, `disarm_if_hold_breaks: true` — if the hold drops below 0.8, disarm and require re-hold (player must stabilize before walking).

---

### A4 — Do-nothing regression (softlock baseline)

**Attack.** The do-nothing baseline (no player actions, `world.uhtcearu_events.enabled: false`) should produce a deterministic 24-sleep loss via grey threshold, unchanged from v3.9.1-C. If Variant A changes this, the two-phase terminal or temple placement has introduced a mechanical side effect.

**Mechanism.** With no player actions, no tribes settle (no pressure to cross `settling.settle_band_threshold_abs: 6`), no conversions occur, and apathy decay (`world.apathy_decay_per_tick: 0.4`) erodes all NPCs toward 0. At `pop = 36` (3 tribes × 12 initial), `growth_per_tribe_per_sleep: 2` adds 6 NPCs/sleep. By sleep 24, `pop = 36 + 24×6 = 180`. Apathy decay over 24 sleeps (72 generations, 216 ticks) at 0.4/tick = 86.4 total decay. Starting NPCs (36) at `initial_state.regular_start_value_abs: 2` (tentative band) decay to 0 by tick 5, then remain at 0. New births (144) spawn at 0 (grey). By sleep 24, `grey = 180/180 = 1.0 > 0.8`, loss fires.

**Expected result:** `median_terminal_sleep = 24`, `losses = 8/8`, `wins = 0`, `median_final_wf = 0.0`, `median_final_lf = 0.0`. Any deviation indicates a mechanical change.

**Falsification metric:** `median_terminal_sleep`. If ≠ 24, the baseline is broken.

**Expected severity:** **GAME-BREAKING** if changed — the do-nothing baseline is the invariant anchor. If it moves, the ruleset is not behaviourally identical to v3.9.1-C.

**Harness probe (P4).** `bot_do_nothing`, seeds 0–7, `player_pole: 1` (arbitrary), `max_sleeps: 30`, `args: {}`. Invariant: `median_terminal_sleep == 24` and `losses == 8`. Falsification metric: `median_terminal_sleep`.

---

### A5 — Self-burn regression (overlap immunity)

**Attack.** The self-burn control (`run_selfburn`) asserts that overlapping same-pole spheres do not burn each other (zealots are immune to same-pole pressure, and non-zealots under same-pole pull deepen rather than burn). If Variant A changes this, the two-phase terminal or temple mechanics have introduced a burnout vector.

**Mechanism.** `run_selfburn` (from `bots.py`) places two same-pole zealots at overlapping positions and measures `selfburns` (burnout events where the burned NPC was under same-pole pressure). Expected: `median_selfburns = 0` across all seeds. Any `selfburns > 0` indicates a rule violation.

**Expected result:** `median_selfburns = 0`, `wins = 0`, `losses = 8/8` (self-burn runs are short and lose to apathy).

**Falsification metric:** `median_selfburns`. If > 0, the attack confirmed.

**Expected severity:** **GAME-BREAKING** — same-pole immunity is a locked invariant (GDD §2, burnout is `>= Y same-pole pressure in one tick`; decay is not same-pole pressure).

**Harness probe (P5).** `run_selfburn`, seeds 0–7, `player_pole: 1`, `max_sleeps: 20`, `args: {}`. Invariant: `median_selfburns == 0`. Falsification metric: `median_selfburns`.

---

### A6 — Campaign regression (win rate and terminal sleep)

**Attack.** The campaign bot (`run_campaign_v3`) should win ~21/25 Hope, ~16/20 Fear against v3.9.1-C (per Designer's expected-shape). Variant A predicts +2 sleeps (one to arm, one to walk). If measured results deviate by >2 sleeps or win rate drops by >2, the two-phase terminal has introduced a mechanical cost beyond the walk.

**Mechanism.** `run_campaign_v3` is the fate-aware Hope campaign with `max_sleeps: 32`. It should arm at sleep ~20 (hold completes), walk 1–2 sleeps (median temple distance ~12 tiles at 6 tiles/sleep), and terminal at sleep ~22. If the walk is longer (temple spawned far) or the hold breaks during the walk (Front interference), terminal sleep increases. If the armed state allows farming (A1) or the walk is trivial (A2), terminal sleep decreases.

**Expected result (Hope):** `wins >= 19/20` (allowing 1 loss for variance), `median_terminal_sleep = 22` (v3.9.1-C ~20, +2 for two-phase). `median_final_wf >= 0.8` (hold maintained). `median_fronts_spawned` unchanged from v3.9.1-C (~1.5/run).

**Expected result (Fear):** `wins >= 14/20` (Fear is harder, per asymmetry), `median_terminal_sleep = 18` (Fear campaigns are shorter). `median_final_lf >= 0.8`.

**Falsification metric:** `median_terminal_sleep` (Hope), `wins` (both poles). If Hope `median > 24` or `wins < 19`, the two-phase terminal is costly. If Hope `median < 20`, collisions (A2) or farming (A1) are common.

**Expected severity:** **TUNING** if terminal sleep moves by >2; **HOLDS** if within ±2.

**Harness probe (P6).** `run_campaign_v3`, seeds 0–19, both poles, `max_sleeps: 32`. Invariant: `median_terminal_sleep <= 24` (Hope), `wins >= 19` (Hope). Falsification metric: `median_terminal_sleep`, `wins`.

---

## Failed attacks

**F1 — Temple placement determinism break.** Hypothesis: enabling `world.temple.enabled: true` perturbs the RNG stream and changes tribe genesis positions, breaking deterministic replay. **Why it failed:** The Designer's rationale states "Placement draws from its own rng stream, so enabling it perturbs nothing else." Schema 3.10 does not specify this, but the Designer's claim is testable: if `bot_do_nothing` produces `median_terminal_sleep = 24` (P4), the RNG stream is isolated. If P4 fails, this attack is confirmed; if P4 holds, this attack is closed.

**F2 — Harness pilgrim speed as exploit vector.** Hypothesis: `harness_pilgrim_tiles_per_sleep: 6` is fast enough that the player can outrun a Grief Front (Front moves 1 tile/sleep, player moves 6), trivializing the walk. **Why it failed:** The Front spawns at `largest_dominant_pole_tribe_position` (the player's likely location to maintain the hold), not at the player's position. The player must walk *toward* the temple, not away from the Front. The Front's target is the dominant tribe, which the player must stay near to maintain the hold. The player cannot outrun the Front without abandoning the hold, which disarms the win (loss check is live). The attack requires the player to maintain the hold *and* flee the Front, which are contradictory.

**F3 — Temple footprint blocks tribe movement.** Hypothesis: the temple's `footprint_radius_tiles: 2` creates a no-go zone that blocks wandering tribes, causing them to cluster at the footprint edge and creating unintended high-density pressure zones. **Why it failed:** Schema 3.10 does not specify that the temple footprint blocks movement; it only defines the footprint for terminal-entry detection. Tribes wander via `world.wander.step_tiles_per_sleep: 1` with `home_box_tiles: 9`, and there is no collision detection in the movement rules. The temple is a render-layer structure (per GDD §9 "presentation only" for Variant A); it does not interact with NPC pathfinding. If the footprint *did* block movement, it would be a schema-level mechanic, not a Variant A side effect.

**F4 — Armed state persists across multiple holds.** Hypothesis: if the player arms at sleep 10, the hold breaks at sleep 12, and the player re-establishes a hold at sleep 15, the armed state persists from sleep 10 (never disarmed), allowing the player to enter the temple at sleep 16 without re-holding for 6 ticks. **Why it failed:** `disarm_if_hold_breaks: false` means the armed state does not disarm when the hold drops below 0.8, but the **loss check is always live**. If the hold breaks to `grey+burned >= 0.8`, the loss terminal fires immediately, ending the run. The player cannot "re-establish" a hold after a loss. If the hold breaks but stays above the loss threshold (e.g., `wf = 0.75`, `grey = 0.20`), the armed state persists, but the player has no incentive to re-hold (the terminal is already armed). The attack assumes the player can lose the hold, survive, and re-hold, but the loss check prevents this.

---

## Summary table

| Probe | Attack | Severity | One-line |
|---|---|---|---|
| P1 | A1 | TUNING | Armed-state farming allows 3–5 idle sleeps to bank stamina, bounded by caps and loss-check liveness |
| P2 | A2 | TUNING | Temple collision with dominant tribe makes walk zero-distance, rare but not exploitable |
| P3 | A3 | TUNING | Loss while armed if Grief Front spawns during walk, low probability |
| P4 | A4 | GAME-BREAKING if fails | Do-nothing baseline must remain 24 sleeps; any change breaks v3.9.1-C parity |
| P5 | A5 | GAME-BREAKING if fails | Self-burn control must remain 0; any selfburns break same-pole immunity |
| P6 | A6 | TUNING / HOLDS | Campaign win rate and terminal sleep must stay within ±2 of v3.9.1-C + walk cost |

---

## Verdict

**Variant A is SAFE with minor tuning risk.** The two-phase terminal introduces three low-probability failure modes (armed-state farming, temple collision, loss while armed) and two regression controls (do-nothing, self-burn). The Designer's hypothesis ("zero mechanical cost") is **optimistic but testable**: if P4 and P5 hold and P6 stays within ±2 sleeps, the variant is behaviourally identical to v3.9.1-C except for terminal timing. If P1 or P3 confirm (farming or armed losses occur), the severity is TUNING (bounded effects, not game-breaking). If P4 or P5 fail, the variant is GAME-BREAKING (baseline invariants violated).

**Expected Playtester outcome:** P4 and P5 hold (do-nothing and self-burn are isolated from temple mechanics), P6 shows `median_terminal_sleep = 22` (Hope) and `wins = 19–20/20` (within variance), P1 shows `median_terminal_sleep = 23–24` (1–2 sleeps of farming, not 10), P2 shows `min(terminal_sleep) = 20–21` (no collision-induced early terminals), P3 shows `losses = 0` in armed runs (no Front interference during walk). **Verdict: HOLDS** with a measured +2 sleep cost and no new failure modes.

**If the Playtester finds otherwise:** P1 `median > 25` → farming is common, recommend `max_armed_sleeps: 5`. P3 `losses > 0` → Front interference during walk, recommend `suppress_front_while_armed: true`. P4 `median ≠ 24` → RNG stream not isolated, **GAME-BREAKING**, reject variant. P5 `median > 0` → same-pole immunity broken, **GAME-BREAKING**, reject variant. P6 `wins < 17` (Hope) → two-phase terminal is costly, recommend reverting to `terminal_fires_on: "hold_complete"`.

---

## Assumptions

[ASSUMPTION] The harness logs `win_armed: true` when the hold completes and the armed state is set, allowing P3 to filter for armed-state losses. If the harness does not log this, P3 cannot distinguish armed losses from pre-armed losses.

[ASSUMPTION] The harness computes `temple_walk_distance` as the Euclidean distance from the player's position at the moment `win_armed: true` to the temple position, allowing P2 to measure collision probability. If the harness does not log this, P2 must infer collisions from `min(terminal_sleep)`.

[ASSUMPTION] `run_campaign_v3` does not emit `median_fronts_spawned` or `median_front_exposure` (per the bot policy table), so P6 cannot measure Front cadence changes. If Front metrics are needed, use `bot_throughput` or `make_flamer` instead.

[ASSUMPTION] The Designer's "median temple distance ~12 tiles" is based on the constrained random placement (≥14 from cave, ≥6 from beacons/edge) and assumes the player's dominant tribe is near the cave or a beacon. Actual distances will vary by seed; the 12-tile estimate is a central tendency, not a guarantee.

[ASSUMPTION] `disarm_if_hold_breaks: false` means the armed state persists even if `wf < 0.8`, but the loss check (`grey+burned >= 0.8`) is independent and always live. The Designer's expected-shape confirms this ("loss check remains live while armed"), so the assumption is grounded.

[ASSUMPTION] The Grief Front's `spawn_at: largest_dominant_pole_tribe_position` in Variant A is unchanged from v3.9.1-C (target-spawn, not temple-spawn). The Designer's parameter table confirms this; Variant B changes it to `temple_position`, but A does not.

[ASSUMPTION] The do-nothing baseline (`bot_do_nothing`) with `world.uhtcearu_events.enabled: false` is the correct configuration for P4. The Designer's expected-shape references "do-nothing baseline (24 sleeps, GDD §9 question 5)" and specifies "no Front fires," confirming this.

[ASSUMPTION] The self-burn control (`run_selfburn`) is unchanged from v3.9.1-C and tests same-pole immunity. The bot policy table confirms `run_selfburn` is available; the Designer's expected-shape does not mention it, but it is a standard regression control per attacks-v2/v5 precedent.

[ASSUMPTION] The campaign bot (`run_campaign_v3`) is the correct policy for P6 (win rate and terminal sleep regression). The Designer's expected-shape references "Hope 21/25, Fear 16/20" as the v3.9.1-C baseline, and `run_campaign_v3` is the fate-aware Hope campaign that produces these results.

[ASSUMPTION] The harness sweep `[3, 6, 12]` for `harness_pilgrim_tiles_per_sleep` is a harness configuration parameter, not a ruleset parameter, so the Red-Teamer does not probe it. The Designer's parameter table sets the baseline at 6; the sweep is the Playtester's job (Director question 1).
