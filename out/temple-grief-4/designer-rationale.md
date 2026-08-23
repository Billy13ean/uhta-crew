# VARIANT RATIONALE TABLE

## Hypotheses

**Variant A (control):** Temple and two-phase terminal add presentation structure with zero mechanical cost — median sleep count unchanged, no new failure modes.

**Variant B (origin + travel):** Geographic Front origin with moderate travel speed creates a visible approach window and mild sleep-count penalty without re-enabling centroid steering.

**Variant C (local decay zone):** A narrow, moderate-strength decay aura around the temple costs the armed walk without making Hope unwinnable, testing whether geographic grief pressure differentiates pole difficulty.

## Parameter table

| Parameter | §/§6 ref | A | B | C | One-line reasoning for the spread |
|-----------|----------|---|---|---|----------------------------------|
| `world.temple.enabled` | §9 mandate | `true` | `true` | `true` | All variants enable temple structure |
| `win_loss.terminal_fires_on` | §9 mandate | `"temple_entry"` | `"temple_entry"` | `"temple_entry"` | All variants use two-phase terminal |
| `world.uhtcearu_events.grief_front.spawn_at` | §9 B mandate | `"largest_dominant_pole_tribe_position"` | `"temple_position"` | `"largest_dominant_pole_tribe_position"` | B tests geographic origin; A/C preserve v3.9.1-C target-spawn |
| `world.uhtcearu_events.grief_front.duration_counts_from` | §9 B mandate | `"spawn"` | `"arrival"` | `"spawn"` | B delays duration start until Front reaches target |
| `world.uhtcearu_events.grief_front.move_tiles_per_sleep` | §9 B tuning | `0` | `4` | `0` | B needs >1 to traverse 48×48; 4 = ~6 sleeps worst-case diagonal |
| `world.uhtcearu_events.grief_front.arrival_radius_tiles` | §9 B schema | `0` | `3` | `0` | B defines "arrived" as within 3 tiles of target |
| `world.uhtcearu_events.grief_front.max_travel_sleeps` | §9 B schema | `0` | `15` | `0` | B caps travel at 15 sleeps (60 tiles = 1.25× diagonal) |
| `world.temple.local_decay.enabled` | §9 C mandate | `false` | `false` | `true` | C tests geographic decay zone |
| `world.temple.local_decay.radius_tiles` | §9 C tuning | `0` | `0` | `5` | C radius = 5 (smaller than Front r=6, larger than arrival r=3) |
| `world.temple.local_decay.strength` | §9 C tuning | `0.0` | `0.0` | `1.5` | C strength = 1.5 (half of front_strength 4.0, below zealot_pull 2.0) |
| `world.temple.local_decay.affects_dominant_pole_only` | §9 C / Run 23b | `false` | `false` | `true` | C honors grief-wears-winner canon |
| `win_loss.temple_entry.harness_pilgrim_tiles_per_sleep` | §9 tuning / Dir Q1 | `6` | `6` | `6` | Baseline 6 for all; sweep [3,6,12] is harness config, not ruleset |
| `world.temple.placement` | §9 all | `"random_constrained"` | `"random_constrained"` | `"random_constrained"` | All use random placement per §9 |
| `world.temple.min_dist_cave` | §9 constraint | `14` | `14` | `14` | Placement constraint: ≥14 from cave |
| `world.temple.min_dist_sites` | §9 constraint | `6` | `6` | `6` | Placement constraint: ≥6 from beacons |
| `world.temple.min_dist_edge` | §9 constraint | `6` | `6` | `6` | Placement constraint: ≥6 from edge |
| `world.temple.min_dist_tribes` | §9 constraint | `6` | `6` | `6` | Placement constraint: ≥6 from genesis tribes |
| `world.temple.placement_tries` | §9 schema | `500` | `500` | `500` | Retry budget for random placement |
| `world.temple.footprint_radius_tiles` | §9 schema | `2` | `2` | `2` | Temple occupies 2-tile radius |

## Arithmetic blocks

### Variant A — contest / traversal / burnout / growth

**Contest (pressure vs pull vs decay):**
- Player flame pressure: `2.0` (per §contagion, unchanged)
- Zealot pull (inside Front): `2.0` (front_strength 4.0 / 2, Run 23b salvage)
- Apathy decay (outside Front): `0.05` (world.apathy_decay_per_tick, unchanged)
- **Ratio:** flame 1.0× pull, 40× decay — Front stalls believers exactly, decay is negligible

**Traversal (stamina budget vs map distance):**
- Stamina floor actions: `5` (unchanged)
- Worst-case temple distance: `~34 tiles` (diagonal from corner beacon [7,7] to opposite corner [41,41])
- Walk cost: `0.5/tile` (0.4 roaded, but temple walk likely unroaded)
- **Ratio:** 5 actions = 10 tiles walked; 34-tile walk = 17 stamina = 3.4× floor budget — requires 2–3 sleep cycles if unassisted

**Burnout headroom (stacked pressure vs threshold):**
- Burnout threshold Y: `0.8` (bands.burnout.threshold, unchanged)
- Max stacked pressure: flame 2.0 + roar ~1.0 + beacon 1.5 = `4.5` (single-tick burst)
- Sustained pressure: flame 2.0 (spammable)
- **Ratio:** burst 5.6× threshold, sustained 2.5× — burnout risk unchanged from v3.9.1-C

**Growth race (births vs casualties vs conversion):**
- Births per sleep: `0.5` per tribe (world.growth_per_tribe_per_sleep, unchanged)
- Casualties (burnout): ~0–2 per sleep in late game (measured v3.9.1-C)
- Conversion rate: `2.0` per flame (player_pressure.flame, unchanged)
- **Ratio:** 6 tribes = 3 births/sleep; flame converts 2/action; burnout drains <1/sleep — conversion dominates

---

### Variant B — contest / traversal / burnout / growth

**Contest (pressure vs pull vs decay):**
- Player flame pressure: `2.0`
- Zealot pull (inside Front): `2.0` (unchanged from A)
- Apathy decay (outside Front): `0.05`
- Front travel: `4 tiles/sleep`, worst-case `~17 sleeps` to traverse diagonal
- **Ratio:** same as A during Front; travel window adds 0–17 sleeps of Front-free time before duration starts

**Traversal (stamina budget vs map distance):**
- Same as A: 5 actions = 10 tiles, 34-tile worst-case = 3.4× floor
- Front travel adds 0–17 sleeps to campaign length (not to player walk cost)
- **Ratio:** player walk cost unchanged; Front approach is observable but does not block player movement

**Burnout headroom:**
- Identical to A: burst 5.6×, sustained 2.5×

**Growth race:**
- Identical to A: 3 births/sleep, 2 converts/flame, <1 burnout/sleep
- Front travel window (0–17 sleeps) allows 0–51 births before Front duration starts
- **Ratio:** travel window = 17× growth rate vs Front uptime (~3 sleeps at 0.65 duty cycle)

---

### Variant C — contest / traversal / burnout / growth

**Contest (pressure vs pull vs decay):**
- Player flame pressure: `2.0`
- Zealot pull (inside Front): `2.0`
- Apathy decay (outside Front): `0.05`
- Local decay (inside temple r=5): `0.05 + 1.5 = 1.55` (adds strength to dominance term)
- **Ratio:** temple zone decay 31× baseline, 0.78× zealot pull — believers grey slowly inside zone, do not flip or burn

**Traversal (stamina budget vs map distance):**
- Same as A: 5 actions = 10 tiles, 34-tile worst-case = 3.4× floor
- Temple zone radius: `5 tiles` (10-tile diameter)
- Worst-case zone exposure: `10 tiles` (straight-line diameter crossing)
- Zone crossing time: `~2 sleeps` at 6 tiles/sleep pilgrim speed (harness baseline)
- **Ratio:** 2 sleeps in zone = 2× generation (12 ticks) = 12 ticks × 1.55 decay = 18.6 total decay per NPC

**Burnout headroom:**
- Identical to A: burst 5.6×, sustained 2.5×
- Local decay does not burn (decay moves toward 0, not past threshold)

**Growth race:**
- Identical to A: 3 births/sleep, 2 converts/flame, <1 burnout/sleep
- Temple zone crossing (2 sleeps) costs 6 births if player idles
- **Ratio:** zone crossing = 2× growth cycle; decay erodes ~0.15 alignment/NPC (18.6 / 120 NPCs in late game)

# RULE VARIANTS

## Variant A


_(variant JSON emitted to its own file)_


## Variant B


_(variant JSON emitted to its own file)_


## Variant C


_(variant JSON emitted to its own file)_


# EXPECTED-SHAPE NOTES

## Variant A (control)

- **Predicted run length:** Median +2 sleeps vs v3.9.1-C (one sleep to arm, one sleep temple walk at 6 tiles/sleep × ~12-tile median distance).
- **Do-nothing softlock:** 24 sleeps unchanged (no Front fires, no temple mechanics engage, loss at grey threshold).
- **Tyrant burst:** Unchanged (burnout threshold and pressure unchanged).
- **Campaign per pole:** Hope 21/25, Fear 16/20 unchanged (no mechanical delta from v3.9.1-C except terminal timing).
- **Frontal siege:** Unchanged (Front spawn/duration/strength all v3.9.1-C values).
- **Self-burn:** Unchanged (no new burnout vectors).
- **Red-Team vulnerability:** Attack B3 (armed-state farming) — if hold breaks slowly, player could farm stamina across multiple sleep cycles before terminal fires; mitigated by `disarm_if_hold_breaks: false` keeping loss check live.
- **Playtester measurement:** Median sleep count delta; any run lost while `win_armed: true`; temple walk stamina cost (should be ~6–12 stamina for median placement).

## Variant B (origin + travel)

- **Predicted run length:** Median +6 sleeps vs v3.9.1-C (+4 Front travel, +2 temple walk) — "halves front exposure" because duration starts at arrival, not spawn, reducing effective uptime.
- **Do-nothing softlock:** 24 sleeps unchanged (Front never triggers without dominance ≥0.55).
- **Tyrant burst:** Unchanged.
- **Campaign per pole:** Hope 21/25, Fear 15/20 (−1 Fear due to longer campaigns giving more burnout opportunities; Hope unchanged because Hope avoids burnout).
- **Frontal siege:** Front travel window (0–17 sleeps) is observable but does not block player; centroid steering CLOSED because target is still `largest_dominant_pole_tribe_position` (player cannot steer temple position, and travel happens regardless of player location).
- **Self-burn:** Unchanged.
- **Red-Team vulnerability:** Attack A6 variant (Front-dodging by staying near temple during travel) — if player camps temple, Front arrives at player's dominant tribe but player is elsewhere; mitigated by `move_toward: largest_dominant_pole_tribe_position` keeping Front on-target and player needing to return to dominant tribe to maintain hold.
- **Playtester measurement:** Front travel sleep count (should be 4–17 depending on temple-to-target distance); any run where Front never arrives (max_travel_sleeps cap hit); whether "halved exposure" = reduced front uptime or reduced effectiveness.

## Variant C (local decay zone)

- **Predicted run length:** Median +3 sleeps vs v3.9.1-C (+1 for zone-crossing caution, +2 temple walk).
- **Do-nothing softlock:** 24 sleeps unchanged (local decay does not trigger without player action).
- **Tyrant burst:** Unchanged (decay does not burn).
- **Campaign per pole:** Hope 19/25 (−2 due to zone-crossing erosion on Hope-aligned NPCs), Fear 16/20 unchanged (Fear benefits from zone eroding Hope holdouts).
- **Frontal siege:** Unchanged (Front mechanics identical to v3.9.1-C).
- **Self-burn:** Unchanged (zone decay moves toward 0, not past burnout threshold).
- **Red-Team vulnerability:** Attack C2 (Hope unwinnable) — if temple spawns far from Hope's dominant tribe and zone erosion breaks hold during walk; mitigated by `strength: 1.5` being below `zealot_pull: 2.0` (zone slows but does not flip believers) and `affects_dominant_pole_only: true` (zone does not help enemy).
- **Playtester measurement:** Hope win rate (target ≥19/25, failure = unwinnable); zone-crossing alignment delta (should be ~−0.15 per NPC over 2 sleeps); any run where hold breaks inside zone and re-arms (tests whether zone prevents hold maintenance).

# CANON FRICTION

**GDD §9 "the Front is exactly `rules-v3.9.1-C`" vs Variant B's origin change.** The brief says "A — presentation only… zero sim change. The control arm." and "B — origin change… The *target* is unchanged from Run 23b; only origin and travel change." This is internally consistent (B is not the control, A is), but the phrasing "exactly v3.9.1-C" in the A description could be read as applying to all variants. **Resolved by reading A as the control and B/C as the experimental arms.**

**GDD §9 "`move_tiles_per_sleep` must rise above 1" vs schema default `0`.** The brief states this as a requirement ("must rise"), but the baseline has `0` (stationary Front, v3.9.1-C behavior). **Resolved by treating the baseline as a template and the brief's "must" as a design constraint for Variant B only.**

**Run 23b salvage `spawn_at: largest_dominant_pole_tribe_position` vs Variant B `spawn_at: temple_position`.** The brief explicitly asks "Does a fixed origin re-enable the centroid-steering attack that Run 23b closed?" This acknowledges that B contradicts the Run 23b salvage decision. **Resolved by treating this as an intentional experimental reversal to test whether the attack re-emerges (Red-Team's job to verify it stays closed).**

# ASSUMPTIONS

[ASSUMPTION] Temple placement occurs at genesis (before tribes settle) so `min_dist_tribes` can be enforced against genesis positions. Schema 3.10 does not specify the placement timing; inferred from "never inside a tribe's genesis position" constraint and the fact that settled tribes are not genesis-positioned.

[ASSUMPTION] `world.temple.local_decay` (variant C) ADDS `strength` to the damping formula's dominance term for NPCs within `radius_tiles` of the temple, rather than replacing it. Schema says "elevated passive decay" and "ADDS strength"; the grief_front precedent is `inside_replaces_dominance_term`, which this does not set.

[ASSUMPTION] An active grief front's `inside_replaces_dominance_term` takes precedence over `local_decay` for NPCs under both effects (no double-punishment). Inferred from "Interacts with the Front" in §9 and the Run 23b "no double-punishment" principle.

[ASSUMPTION] `harness_pilgrim_tiles_per_sleep` is uncosted movement (does not spend stamina). Schema says "scripted bots know nothing about the temple; while armed the harness walks the avatar this many tiles toward it at each sleep boundary, uncosted." The word "uncosted" is explicit.

[ASSUMPTION] The do-nothing baseline (24 sleeps, GDD §9 question 5) refers to a harness run with no player actions and `world.uhtcearu_events.enabled: false`, measured against v3.9.1-C. This is the only configuration that produces a deterministic sleep count independent of player behavior.

[ASSUMPTION] "Median added sleeps" (§9 question 4) means the difference in median terminal sleep count between each variant and v3.9.1-C, measured across the same harness campaign (same bot policies, same seed set).

[ASSUMPTION] The centroid-steering attack (§9 question 1, Run 23b attack A6) refers to the player steering the dominant-pole NPC centroid away from their own position to delay or avoid the Front. Variant B's `spawn_at: temple_position` makes origin fixed, but `move_toward: largest_dominant_pole_tribe_position` is unchanged, so the *target* is still player-influenceable.

[ASSUMPTION] "Why does B halve front exposure?" (Director question 3) refers to an expected or observed reduction in front uptime or effectiveness in variant B compared to A or v3.9.1-C. The question implies a measured or predicted phenomenon; the Designer's task is to produce the variant so the harness can measure it. **Hypothesis: `duration_counts_from: "arrival"` delays the 3-sleep Front duration until the Front reaches its target, so a 6-sleep travel adds 6 sleeps to the campaign but only 3 sleeps of active Front pressure, halving the Front's duty cycle in that window.**

[ASSUMPTION] `win_loss.temple_entry.disarm_if_hold_breaks: false` means the armed state persists even if the unification hold drops below threshold after arming. The loss check remains live, so a broken hold can still lose; the flag only prevents disarming. This creates the "lost while armed" failure mode the Director asks about.

[ASSUMPTION] Variant C's `local_decay.strength: 1.5` is calibrated to be below `zealot_pull: 2.0` so that zealots inside the zone still pull believers toward their pole (net +0.5/tick), preventing zone-induced flips. Non-zealot believers inside the zone decay at 1.55/tick (0.05 baseline + 1.5 zone), which is 31× baseline but still slow enough that a 2-sleep crossing (~12 ticks) erodes ~18.6 alignment points across 120 NPCs = ~0.15/NPC, not enough to break a 0.8+ hold.

[ASSUMPTION] The harness sweep `[3, 6, 12]` for `harness_pilgrim_tiles_per_sleep` is a harness configuration parameter, not a ruleset parameter. The ruleset sets the baseline value (6), and the harness runs three campaigns per variant (one at each speed) to measure sensitivity. The Designer does not emit three sub-variants per variant.

[ASSUMPTION] `world.temple.cave`, `world.temple.beacon_sites` in the baseline schema are reference coordinates for placement constraint enforcement, not tunable parameters. The Designer does not change these values; they are world constants.

[ASSUMPTION] `max_travel_sleeps: 15` in Variant B is set to 1.25× the worst-case diagonal (48√2 ≈ 68 tiles / 4 tiles per sleep ≈ 17 sleeps), providing a safety margin. If the Front cannot reach its target in 15 sleeps, it expires without firing (a failure mode the Playtester should measure).

[ASSUMPTION] Variant C's `radius_tiles: 5` is chosen to be smaller than the Front's `radius_tiles: 6` (so the zone does not fully overlap a Front) but larger than Variant B's `arrival_radius_tiles: 3` (so the zone is a meaningful obstacle, not a pinprick). The 10-tile diameter is ~1/5 of the map width, making it a local hazard rather than a map-wide effect.
