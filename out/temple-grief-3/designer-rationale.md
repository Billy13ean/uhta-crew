# VARIANT RATIONALE TABLE

## Hypotheses

**Variant A (control):** Temple as presentation-only preserves v3.9.1-C behavior exactly; zero mechanical delta, establishes baseline for walk-time measurement.

**Variant B (geographic origin):** Temple-origin Front with 3-tile/sleep travel restores geographic spawn without restoring centroid-steering exploit; trailing-window trigger remains sufficient defense; walk adds 2–4 sleeps median.

**Variant C (decay zone):** Temple local_decay at r=6, strength=0.8 creates meaningful walk cost without Hope-impossible threshold; stacks conceptually with Front (grief layering) but precedence rule prevents double-punishment; walk adds 3–6 sleeps median, Hope campaigns +2 sleeps vs Fear.

## Parameter spread

| Parameter | §/§6 ref | A | B | C | One-line reasoning for the spread |
|-----------|----------|---|---|---|-----------------------------------|
| `world.temple.enabled` | §9 variants | `false` | `true` | `true` | A is render-only control; B/C enable sim structure |
| `world.temple.placement` | §9 constraints | n/a | `"random_constrained"` | `"random_constrained"` | Deterministic from run seed, ≥14 from cave, ≥6 from beacons/edge/tribes |
| `world.temple.local_decay.enabled` | §9 variant C | n/a | `false` | `true` | C tests decay zone; B isolates travel mechanics |
| `world.temple.local_decay.radius_tiles` | §9 Q3 | n/a | n/a | `6` | Smaller than Front r=8; covers ~113 tiles; walk crosses in 1 sleep at speed 6 |
| `world.temple.local_decay.strength` | §9 Q3 | n/a | n/a | `0.8` | Below Front 2.0/tick; Hope believers decay −0.8/tick in zone, survivable with shepherding |
| `world.temple.local_decay.affects_dominant_pole_only` | §2.6 grief canon | n/a | n/a | `true` | Grief wears winner toward 0, never recruits opposite (ruling 6) |
| `world.uhtcearu_events.grief_front.spawn_at` | §9 variant B, Q1 | `"largest_dominant_pole_tribe_position"` | `"temple_position"` | `"largest_dominant_pole_tribe_position"` | B tests geographic origin; C keeps Run 23b target-spawn to isolate decay effect |
| `world.uhtcearu_events.grief_front.move_tiles_per_sleep` | §9 variant B | `1` | `3` | `1` | B needs ≥2 for 48×48 arrival; 3 gives 2–3 sleep travel from corners, preserves 3-sleep duration |
| `world.uhtcearu_events.grief_front.duration_counts_from` | §9 Q6 | `"spawn"` | `"arrival"` | `"spawn"` | B counts from arrival to preserve 3-sleep stall window; A/C unchanged |
| `world.uhtcearu_events.grief_front.arrival_radius_tiles` | §9 variant B | n/a | `2` | n/a | Matches temple footprint; Front "arrives" when within 2 tiles of target |
| `world.uhtcearu_events.grief_front.max_travel_sleeps` | §9 variant B | n/a | `6` | n/a | Safety cap; 48×48 diagonal is 68 tiles, at 3/sleep = 23 sleeps worst case, but trailing-window limits spawn distance |
| `win_loss.terminal_fires_on` | §9 two-phase | `"hold_complete"` | `"temple_entry"` | `"temple_entry"` | A is v3.9.1 immediate; B/C arm-then-walk |
| `win_loss.temple_entry.harness_pilgrim_tiles_per_sleep` | §9 Q2 | n/a | `6` | `6` | Harness bot walks 6 tiles/sleep (stamina floor ~5 actions = 5–6 tiles); production build player-controlled |
| `win_loss.temple_entry.disarm_if_hold_breaks` | §9 two-phase | n/a | `false` | `false` | Armed state persists through hold breaks; player can re-shepherd and walk |

## Variant A — four-ratio arithmetic

**Contest (inside Front, dominant-pole believer at 0.6 alignment):**
- Zealot pull: +2.0/tick (Run 23b stall anchor)
- Front decay: −2.0/tick (front_strength 4.0, affects_dominant_pole_only)
- Net: 0.0/tick (stall verified)

**Traversal (armed win to temple entry):**
- Map diagonal: 68 tiles (corner [0,0] to temple ~[24,6])
- Harness walk speed: 6 tiles/sleep
- Walk time: 0 sleeps (terminal fires immediately at hold_complete)

**Burnout headroom (stacked same-pole pressure, dominant believer at 0.6):**
- Baseline decay: −0.05/tick (passive toward 0)
- Zealot pull: +2.0/tick
- Burnout threshold: 0.95 (Y from baseline)
- Headroom: 0.35 alignment units, ~18 ticks at net +1.95/tick

**Growth race (mid-game, 40 NPCs, 0.6 dominance):**
- Births: ~0.8/sleep (baseline fertility)
- Casualties: ~0.2/sleep (baseline attrition)
- Conversion rate: ~1.2 NPCs/sleep (player Flame at 0.6 avg target)
- Net growth: +1.8 NPCs/sleep

## Variant B — four-ratio arithmetic

**Contest (inside Front, dominant-pole believer at 0.6 alignment):**
- Zealot pull: +2.0/tick (unchanged)
- Front decay: −2.0/tick (unchanged)
- Net: 0.0/tick (stall preserved)

**Traversal (armed win to temple entry):**
- Median temple distance from largest tribe: ~18 tiles (random_constrained, min_dist 14 from cave [24,24], tribes cluster near beacons)
- Harness walk speed: 6 tiles/sleep
- Walk time: 3 sleeps median (18/6), range 2–5 sleeps
- Front travel time (temple to target): 6 tiles median at 3 tiles/sleep = 2 sleeps, duration counts from arrival = 3-sleep stall window preserved

**Burnout headroom (stacked same-pole pressure, dominant believer at 0.6):**
- Unchanged from A: 0.35 alignment units, ~18 ticks

**Growth race (mid-game, 40 NPCs, 0.6 dominance):**
- Unchanged from A: +1.8 NPCs/sleep net

## Variant C — four-ratio arithmetic

**Contest (inside temple decay zone, NO Front active, dominant-pole believer at 0.6):**
- Baseline decay: −0.05/tick
- Temple local_decay: −0.8/tick (strength 0.8, affects_dominant_pole_only)
- Net decay: −0.85/tick (no zealot present in zone)
- With zealot shepherding: +2.0 (zealot) −0.85 (decay) = +1.15/tick (survivable)

**Contest (inside BOTH temple zone AND Front, dominant believer at 0.6):**
- Precedence rule: Front decay takes precedence (no stacking)
- Front decay: −2.0/tick
- Zealot pull: +2.0/tick
- Net: 0.0/tick (stall preserved, no double-punishment)

**Traversal (armed win to temple entry, crossing decay zone):**
- Temple decay radius: 6 tiles
- Zone diameter: 12 tiles
- Harness walk speed: 6 tiles/sleep
- Time in zone: 2 sleeps (12/6)
- Decay exposure: −0.85/tick × 10 ticks/sleep × 2 sleeps = −17 alignment-ticks (believer at 0.6 drops to ~0.43 if unshepherded, to ~0.83 if shepherded)
- Total walk time: 3 sleeps median (same as B, temple distance ~18 tiles)

**Burnout headroom (inside temple zone, stacked pressure):**
- Baseline decay: −0.05/tick
- Temple decay: −0.8/tick
- Zealot pull: +2.0/tick
- Net: +1.15/tick (reduced from +1.95 outside zone)
- Headroom to 0.95: 0.35 units, ~30 ticks at +1.15/tick (vs 18 ticks outside zone)

**Growth race (mid-game, 40 NPCs, 0.6 dominance):**
- Unchanged from A: +1.8 NPCs/sleep net (temple zone is local, does not affect global growth)

---

# RULE VARIANTS

## Variant A


_(variant JSON emitted to its own file)_


## Variant B


_(variant JSON emitted to its own file)_


## Variant C


_(variant JSON emitted to its own file)_


---

# EXPECTED-SHAPE NOTES

## Variant A (control)

- **Predicted run length:** 18–22 sleeps median (unchanged from v3.9.1-C baseline; Fear 16/20, Hope 21/25 per metrics-v3.9.1).
- **Do-nothing softlock:** PASS — symmetric genesis (1F/1H) never reaches 0.55 dominance, Front never fires, loss terminal at grey+burned ≥0.8 eventually triggers (verified v3.9.1).
- **Tyrant burst:** PASS — single-pole sprint to 0.8 in 8–10 sleeps, no opposing zealot, win fires immediately at hold_complete (v3.9.1 behavior).
- **Campaign per pole:** Fear 16/20, Hope 21/25 (metrics-v3.9.1 baseline; asymmetric difficulty is intent).
- **Frontal siege:** PASS — Front spawns at largest_dominant_pole_tribe_position, 3-sleep stall window, cooldown 2, trailing-window trigger prevents hover-then-sprint (Run 23b verified).
- **Self-burn:** PASS — stacked same-pole pressure at 0.6 alignment burns to 0.95 in ~18 ticks, loss terminal fires (v3.9.1 behavior).
- **Red-Team vulnerability:** None new; A is the ratified v3.9.1-C control.
- **Playtester measurement:** Walk time = 0 sleeps (terminal fires at hold_complete); verify bit-identical replay vs v3.9.1-C harness runs.

## Variant B (geographic origin)

- **Predicted run length:** 20–26 sleeps median (+2–4 sleeps vs A; walk adds 3 sleeps median, Front travel adds 0–2 sleeps depending on spawn-to-target distance).
- **Do-nothing softlock:** PASS — symmetric genesis never reaches 0.55 dominance, Front never fires (trailing-window trigger unchanged from Run 23b).
- **Tyrant burst:** PASS — single-pole sprint to 0.8 in 8–10 sleeps, arm win, walk 3 sleeps median to temple, total 11–13 sleeps (faster than A's 18-sleep median because no Front opposition in burst scenario).
- **Campaign per pole:** Fear 18/20 (+2 sleeps for walk), Hope 24/25 (+3 sleeps for walk + Hope's longer consolidation phase).
- **Frontal siege:** VERIFY — Front spawns at temple (geographic), travels 3 tiles/sleep to largest_dominant_pole_tribe_position, duration counts from arrival. **Red-Team must verify:** does geographic spawn + trailing-window trigger prevent centroid-steering (attacks-v5 A6)? If player can steer largest tribe to a corner, does Front travel time exceed max_travel_sleeps (6) and expire in transit? Hypothesis: trailing-window (3 sleeps at ≥0.55) limits spawn distance to ~18 tiles median, travel time 2 sleeps median, Front arrives with 3-sleep stall window intact.
- **Self-burn:** PASS — unchanged from A (temple zone disabled in B).
- **Red-Team vulnerability:** **Centroid-steering revival (attacks-v5 A6)** — if player can manipulate largest_dominant_pole_tribe_position to maximize temple-to-target distance, Front may expire in transit (travel >6 sleeps) or arrive with <1 sleep duration remaining. Trailing-window trigger (3 sleeps at ≥0.55) is the defense; Red-Team must verify it holds.
- **Playtester measurement:** Walk time distribution (median, p25, p75); Front travel time distribution; Front expiry-in-transit rate (should be 0%); centroid-steering exploit success rate (should be 0%).

## Variant C (decay zone)

- **Predicted run length:** 21–28 sleeps median (+3–6 sleeps vs A; walk adds 3 sleeps median, Hope campaigns add +2 sleeps due to decay-zone attrition during consolidation phase).
- **Do-nothing softlock:** PASS — symmetric genesis never reaches 0.55 dominance, Front never fires, temple decay affects no one (affects_dominant_pole_only, no dominant pole in do-nothing).
- **Tyrant burst:** PASS — single-pole sprint to 0.8 in 8–10 sleeps, arm win, walk 3 sleeps crossing decay zone (2 sleeps in-zone at 6 tiles/sleep, believers drop from 0.6 to ~0.43 if unshepherded, to ~0.83 if shepherded), total 11–13 sleeps. **Verify:** does unshepherded walk break the hold (drop below 0.8 population)? Hypothesis: no, because armed state persists (disarm_if_hold_breaks: false) and player can re-shepherd after zone exit.
- **Campaign per pole:** Fear 19/20 (+3 sleeps for walk + zone crossing), Hope 26/25 (+5 sleeps for walk + zone attrition + Hope's longer consolidation). **CRITICAL:** does Hope hit the unwinnable threshold? Hypothesis: no, because local_decay strength 0.8 < Front strength 2.0, and shepherded believers survive zone crossing (+1.15/tick net inside zone with zealot).
- **Frontal siege:** PASS — Front spawns at largest_dominant_pole_tribe_position (unchanged from A), precedence rule ensures no double-punishment when Front overlaps temple zone.
- **Self-burn:** MODIFIED — inside temple zone, stacked same-pole pressure burns to 0.95 in ~30 ticks (vs 18 ticks outside zone), because net pressure drops from +1.95/tick to +1.15/tick. Burnout is slower inside the zone, not faster (decay opposes same-pole pressure).
- **Red-Team vulnerability:** **Hope-impossible threshold (§9 Q3)** — if local_decay strength is too high or radius too large, Hope campaigns may be unable to cross the zone without losing the hold. Hypothesis: strength 0.8, radius 6 is survivable with shepherding; Red-Team must verify Hope 26/25 success rate ≥80% (current Hope baseline is 21/25 = 84%).
- **Playtester measurement:** Walk time distribution; Hope campaign success rate (target ≥80%); believer alignment distribution after zone crossing (shepherded vs unshepherded); precedence rule verification (no NPC under both Front and temple zone shows double-punishment).

---

# CANON FRICTION

**None.** All three variants operate within locked canon:

1. **Grief canon (ruling 6):** Temple local_decay (variant C) wears the dominant pole toward 0 (`affects_dominant_pole_only: true`), never recruits for the opposite — satisfies "grief is the gravity."
2. **Run 23b salvage:** Front `front_strength: 4.0`, `trigger_trailing_window_sleeps: 3`, `affects_dominant_pole_only: true`, `cooldown_sleeps_after_expiry: 2` are unchanged in all variants; variant B's `spawn_at: "temple_position"` changes origin but preserves the stall property (duration counts from arrival, not spawn).
3. **Win/loss definitions (ruling 4):** The two-phase terminal (variants B/C) changes *when* the win evaluates (hold_complete → temple_entry), not *what* it evaluates (≥0.8, 6 ticks, no opposing zealot, |S| ≥ 3, tie_priority loss). The loss check remains live while armed, and a same-tick tie still resolves to loss.
4. **§3 stop rule:** This proposal run produces `rules-*.json` variants for harness measurement, not a build; does not violate the stop rule (NICE #2 is gated on external playtest, but the *proposal* is not).

**One clarification request (not friction):** The precedence rule for variant C ("an active grief front inside its own radius takes precedence") is stated in the schema note but not in the ratified canon. The Designer implements it as specified (Front decay replaces temple decay when both overlap an NPC), but the Red-Teamer should verify this interpretation matches the Director's intent for "grief layering."

---

# ASSUMPTIONS

1. **[ASSUMPTION]** The `world.temple.placement: "random_constrained"` algorithm draws from the run seed using a deterministic PRNG (e.g., seed → hash → x,y candidate → constraint check → retry or accept). The Designer does not specify the hash function; the Playtester will verify replay stability (same seed → same temple position across harness runs).

2. **[ASSUMPTION]** The `win_loss.temple_entry.harness_pilgrim_tiles_per_sleep: 6` dial is a harness-only behavior: the scripted bot walks toward the temple at 6 tiles/sleep while `win_armed: true`. The production build does not auto-walk the player; the player must manually navigate to the temple. The Designer implements this as a harness hook (e.g., `if win_armed and harness_mode: move_toward(temple_position, speed=6)`), not a core sim rule.

3. **[ASSUMPTION]** The `world.temple.fixed_position: [24, 6]` coordinate (proposed in `art/LANDMARKS.md`, never ruled) is used only if `placement: "fixed"`. The default `placement: "random_constrained"` ignores this field. Variants B and C use `"random_constrained"`, so `[24, 6]` is not active in any variant.

4. **[ASSUMPTION]** The `world.temple.local_decay` precedence rule ("an active grief front inside its own radius takes precedence") means: if an NPC is inside both the temple's local_decay radius (r=6) AND an active Front's radius (r=8, from baseline), only the Front's decay (−2.0/tick) applies to that NPC. The temple's decay (−0.8/tick) does not stack. The Designer implements this as an explicit check in the decay calculation: `if inside_front_radius: apply_front_decay; elif inside_temple_radius: apply_temple_decay; else: apply_baseline_decay`. No NPC receives both simultaneously.

5. **[ASSUMPTION]** The `world.uhtcearu_events.grief_front.duration_counts_from: "arrival"` (variant B) means: the Front's 3-sleep duration (`duration_sleeps: 3` from baseline) begins counting when the Front reaches `arrival_radius_tiles: 2` of its target (`largest_dominant_pole_tribe_position`), not when it spawns at the temple. If the Front travels for 2 sleeps (temple → target at 3 tiles/sleep), it remains active for 3 sleeps after arrival, then expires. Total Front lifespan = travel_time + 3 sleeps. If travel exceeds `max_travel_sleeps: 6`, the Front expires in transit (never arrives).

6. **[ASSUMPTION]** The `win_loss.temple_entry.disarm_if_hold_breaks: false` (variants B/C) means: once `win_armed: true` (hold completes), the armed state persists even if the population drops below 0.8 or an opposing zealot spawns. The player can lose believers during the walk, re-shepherd them, and still fire the win terminal upon temple entry. The loss terminal remains live (checked every tick), so a same-tick tie (win entry + loss threshold) resolves to loss (ruling 4).

7. **[ASSUMPTION]** The `world.temple.min_dist_tribes: 6` constraint (§9 placement constraints) means: the temple must be ≥6 tiles from every NPC's position at the moment of temple placement (genesis, before any NPC movement). After genesis, NPCs may move closer to the temple (e.g., a tribe settles within 6 tiles); the constraint applies only at placement time, not dynamically.
