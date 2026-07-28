## 1. Variant rationale table

**A — tighten the fog, not the physics.** Tighten the fog, not the physics: a smaller radius and a longer cooldown cut total straggler exposure while the in-sphere stall arithmetic (front_strength 4.0 -> 2.0/tick = zealot pull) is left exactly alone.

**B — shorten the breath.** Shorten the breath: a 2-sleep front on a 3-sleep cooldown halves the dwell a single unheld convert can take before the fog lifts, trading peak bite for recoverability.

**C — fire later, move faster.** Fire later, move faster: raising the trigger to 0.65 and doubling crawl speed makes the front a late-game punctuation over the leader's core rather than mid-game weather over its edges.

| Parameter | §/§6 ref | A | B | C | One-line reasoning for the spread |
|---|---|---|---|---|---|
| `grief_front.radius_tiles` | §2 antagonist / §6 front feel | **4** | 6 | 6 | A buys the straggler relief geometrically: r4 covers 81 tiles vs r6's 169, so ~52% fewer unheld NPCs are ever inside the fog at all, at zero cost to the arithmetic inside it. |
| `grief_front.duration_sleeps` | §6 front feel | 3 | **2** | 3 | B caps the dwell instead of the footprint: a v=5 convert greys in 5 ticks (metrics-v3.9.1 §E), and 2 sleeps is 6 ticks — still lethal to the fully unheld, but it stops erasing anyone the player reaches in time. |
| `grief_front.cooldown_sleeps_after_expiry` | §6 front feel, CANON Run-23b ("cooldown held at 2 pending campaign-impact measurement") | **4** | **3** | 2 | The one dial CANON explicitly parked. A and B both stretch it; C leaves it, so the sweep separates duty-cycle effects from geometry effects. |
| `grief_front.trigger_dominance_min` | §2 antagonist | 0.55 | 0.55 | **0.65** | C moves the antagonist out of the midgame entirely. The trailing-window closure (GF5) is untouched, so this is a threshold change, not a scheduling hole. |
| `grief_front.move_tiles_per_sleep` | §2 antagonist | 1 | 1 | **2** | Pairs with the raised trigger: a later front must reach its target inside its life, or C reintroduces the A3 geometry null the salvage closed. |
| `grief_front.front_strength` | CANON Run-23b (locked-by-gate) | 4.0 | 4.0 | 4.0 | **Untouched in all three.** 0.4 x (1 + 4.0) = 2.0/tick exactly cancels zealot pull. Moving it is the one change that would weaken the stall, which the question set forbids. |

### Four-ratio arithmetic

**Contest.** Unchanged in all three: flame 2.0 vs zealot pull 2.0 vs decay 0.4 x (1 + dominance). Inside a front, decay 2.0/tick; a held member nets 2.0 - 2.0 = **0.000/tick** (the stall) in A, B and C alike. An unheld convert nets 0 - 2.0, clamped by `step_per_tick_max` to **-1.0/tick** in all three — the per-tick bite is *not* what any of these variants change. What changes is how many ticks of it exist: A cuts who is inside (r4 vs r6), B cuts how long (2 sleeps = 6 ticks vs 9), C cuts how often (trigger 0.65).

**Traversal.** Untouched. Walk 0.5/tile, roaded 0.4, stamina floor 5, cap by tier 10/14/18/24. C's faster crawl (2 tiles/sleep) means a fleeing unsettled tribe at `wander.step_tiles_per_sleep` 1 can no longer outrun the fog, which is a real cost of C and is the thing to measure.

**Burnout headroom.** Untouched and structurally safe in all three: Y = 4 sums *same-pole pressure entries only*, and `decay_term` is computed after the burnout branch. Front decay cannot enter the sum at any radius, duration or cadence. Predicted self-burns: 0 in every arm, as in metrics-v3.9.1 §C.

**Growth race.** Births +2/tribe/sleep up to `schism.pop_cap` 16; casualties `casualty_rate` 0.2, below regrowth. None of the three touches these, so any change in run length is front-attributable rather than demographic — which is what makes this sweep readable.

```json
{
 "meta": {
  "variant": "A",
  "hypothesis": "Tighten the fog, not the physics: a smaller radius and a longer cooldown cut total straggler exposure while the in-sphere stall arithmetic (front_strength 4.0 -> 2.0/tick = zealot pull) is left exactly alone.",
  "gdd_version": "0.8.1",
  "schema": "3.9.2",
  "patches": "rules-v3.9.1-C | MOCK-FIXTURE run (crew v3.9.2, variant A) - front-feel sweep, NOT a Director-gated change.",
  "gate": "G20 2026-07-20 \u2014 conversion redesigned reachable (defer + breath-hold, integer-state averaging), Director-ruled option 1, four calibration cycles harness-verified; declared asymmetry: Hope converts (fear-zealot targets, bars 8.0/8.0), Fear breaks (hope-zealot targets expel-only \u2014 measured check-3 ceiling 6.67; knife-edge bars rejected). hold_continuity enumerated skipped_pauses_failed_resets (A11/R1). | Run 18 2026-07-20 \u2014 Director rulings: fights=real casualties+rout, burnout-exile=lone wanderer, road-follow=strong bias. | Run 19 2026-07-20 \u2014 Director ruling: battle pressure (extended fighting exhausts hope to middle, breaks fear to burnout; deep hope resists & performs slightly better). Death rate kept below regrowth. | Run 20 2026-07-20 \u2014 Director: GENESIS start (grey nomads + 3 lone founding zealots that gather, settle, and are found via roads). Balance preserved (2F/1H emergent). | Run 21 2026-07-21 \u2014 Director: SCHISM (capped-count symmetric colony fission) to bound settlements + spread the world; roads gain allegiance (erode-then-recruit). | Run 23 2026-07-23 - Director: UHTCEARU ACTIVE EVENTS, Variant A (Grief Front) selected from mechanic-designer-run23; tie_priority=loss ratified (GDD v0.9.1). | Run 23b 2026-07-23 - Director: SALVAGE-AS-ANTAGONIST ruled. Fix set shipped as a co-gated unit per attacks-v5: front_strength 4.0 (front stalls faith inside spheres to net ~0; still cannot flip or burn), spawn anchor = largest dominant tribe (closes A3 geometry null + deletes A6 centroid-steering), trailing-window trigger over 3 sleeps (closes A5 hover-sprint shadow), decay restricted to dominant-pole NPCs (grief never helps anyone - closes the cleanup-assist). Cooldown held at 2 pending campaign-impact measurement.",
  "wander_note": "v3.3 adds world.wander: cohesive, regionally-bounded nomadic drift for UNSETTLED tribes (settled anchor). Belief-neutral by construction (tribe moves as a body; box keeps tribes from colliding unaided) \u2014 harness-verified identical terminals to v3.2-C. Player-led tribe collisions remain deferred (a future belief-affecting mechanic needing its own harness pass).",
  "v34_note": "v3.4 adds three BELIEF-AFFECTING nomad systems (harness-gated, not raw engine edits): (1) strong road-following \u2014 unsettled tribes steer onto/along player-laid roads (leaving the home box when on a road), making roads a leash to lead tribes to spheres/beacons; (2) faction fights \u2014 when rival-pole spheres overlap, real casualties accrue each sleep (weakest-first, zealots immune), the outnumbered UNSETTLED tribe routs, settled tribes stand; (3) settlement exile \u2014 settling roots a tribe (it no longer wanders and cannot be led out); the ONLY exit is burnout, which detaches the broken NPC as a lone wanderer that drifts (road-biased) and can be re-adopted by any sphere that pulls it to |I|>=2. Substrate: a real World.roads tile set (mirrors the build). Autonomous world (no player roads, no forced collisions) must reduce to v3.3 terminals.",
  "v35_note": "v3.5 layers BELIEF battle-pressure onto v3.4 faction fights (harness-gated). Each fight-sleep, contested combatants take pressure in addition to weakest-first casualties: FEAR combatants deepen toward -SPAN and burn out at the regular cap (Fear breaks); HOPE combatants are exhausted toward 0/middle, reduced by their depth (Hope bends; deep hope resists). Strong opposing hope deepens fear faster (fear_deepen_hope_bonus). Counterplay to a pin: deep-hope defenders burn the attacker out while barely eroding. Casualty_rate unchanged (below regrowth); battle burnout adds no population removal (burned recover per timer).",
  "v36_note": "v3.6 replaces the pre-clustered 3x12 start with a GENESIS: grey_nomads(40) unaligned loners scattered on the map + 3 founding zealots (2F 1H) each with a small seed following, wandering. Zealots gather nearby nomads (overlap pull -> re-adoption), grow, and settle once they hold >= min_settle_members followers at devout average; leftover nomads find settlements via roads. Two genesis-only safety gates, both no-ops for the legacy start: min_settle_members (a lone/tiny zealot cannot settle on its own zealot-inflated average) and terminal_grace_until_formed (win/loss suppressed until the world takes shape -> aligned fraction >= formed_aligned_fraction OR a tribe settles; otherwise a ~all-grey genesis would trip the apathy loss instantly). genesis.enabled=false reproduces v3.5 exactly.",
  "v37_note": "v3.7 adds SCHISM: a settled tribe at pop_cap with a deep (|avg|>=devout_threshold) conviction births a same-pole daughter zealot, hands it daughter_takes_fraction of the flock, migrates the colony >= fission_radius tiles away and settles it. Symmetric (both poles colonize) but total tribe count capped at max_tribes. This bounds every settlement to a convertible size and grows the world by spreading rather than ballooning \u2014 the fix for genesis unbounded births. Road allegiance (erode-then-recruit) layered next.",
  "founding_note": "v3.7.1: living-world rebalance \u2014 symmetric 1F/1H founding (fair spreading contest), max_tribes 5, road_allegiance (erode-then-recruit + enemy-zealot damping).",
  "balance_note": "v3.7.3: living world winnable & roughly balanced with symmetric 1F1H founding + max_tribes 5 (bot proxy: HOPE ~20/25, FEAR ~22/25 -> asymmetric, fear-favored as intended). hope_trade DISABLED (road-refresh design misguides movement + churns; revisit traders as discrete visible agents that double as live-movement).",
  "ascension_note": "v3.8: follower-driven ASCENSION (shifting power scale). Your power tier = f(your-pole believer count), recomputed at each sleep (level-up). Higher tiers unlock more beacons (1->4), bigger flame radius (+0..+2), bigger sleep aura, and a larger stamina cap (10->24). Gives Hope a snowball, adds beacon-placement agency, and the avatar (kaiju) scales with the flock. Legacy (no tiers) = tier0 = unchanged.",
  "contagion_note": "v3.8.1: PEER CONTAGION \u2014 each tick every NPC also feels its neighbours: hope neighbours pull you hope, fear pull fear, grey (apathy) drag you toward 0. Belief now spreads NPC-to-NPC like a contagion (not just from zealots); apathy spreads too (stakes). The kai.ju/beacons tip the local balance. Small per-neighbour strength so it enriches rather than dominates the zealot economy.",
  "v39_note": "v3.9 adds world.uhtcearu_events variant A_grief_front (Run 23, GDD v0.9.2 grief canon: grief is the gravity, not a pole - catastrophes wear the dominant pole toward 0, never recruit for the opposite). At each sleep boundary, if dominance >= trigger and no front is active and cooldown elapsed, a grief front (radius 6) condenses at the tile centroid of dominant-pole NPCs and crawls 1 tile/sleep toward the largest dominant-pole tribe for 3 sleeps. Inside the front the damping formula's dominance term is REPLACED by front_strength (no double-punishment; outside is exactly the live formula). Zealots immune. Render: a visible desaturating fog bank, sky darkest above it. enabled=false reproduces v3.7 bit-for-bit. Dominance source rebound per packet [ASSUMPTION]: the same player-pole fraction the live damping formula reads.",
  "v391_note": "v3.9.1 SALVAGE (Run 23b): the as-shipped 1.6 front was harness-proven safe but half-dead (in-sphere drift delta 0.000/sleep - zealot pull + step cap swallow it; attacks-v5 A1/A2/A3/A5). Salvage set, co-gated per the red-team verdict: (1) front_strength 4.0 -> inside-front decay 0.4*(1+4.0)=2.0/tick = zealot pull: the front STALLS deepening inside spheres to net ~0 without ever flipping (decay cannot cross 0) or burning (decay is not same-pole pressure); step cap bounds unsupported NPCs at -1/tick as before, so no overkill vs stragglers. (2) spawn_at largest_dominant_tribe_position: the front condenses ON its target - no dead-air centroid misses, no player-steerable aim. (3) trigger_trailing_window_sleeps 3: fires on the MAX dominance over the trailing window, so hovering below threshold then sprinting cannot schedule the antagonist away. (4) affects_dominant_pole_only true: grief wears down only the winner - it never greys enemy holdouts for you (cleanup-assist closed). Zealot immunity unchanged; enabled:false still reproduces v3.7 bit-for-bit."
 },
 "scale": {
  "min": -12,
  "max": 12,
  "zealot_value": 12
 },
 "bands": {
  "tentative": [
   1,
   5
  ],
  "devout": [
   6,
   11
  ],
  "zealot": 12
 },
 "contagion": {
  "step_per_tick_max": 1,
  "sphere_base_radius_tiles": 2,
  "sphere_growth_formula": "sphere_base_radius_tiles + floor(sqrt(group_size))",
  "overlap_pull_strength": 0.8,
  "awake_pull_multiplier": 0.3,
  "zero_value_membership": {
   "spawn_state": "in",
   "window_ticks_at_zero_cumulative": 6,
   "reset_on_stable_adoption_abs_gte": 2,
   "after_window": "out"
  }
 },
 "player_pressure": {
  "flame_push_base": 2.0,
  "flame_radius_tiles": 3,
  "alignment_strength_multiplier_formula": "1",
  "roar_fear_push": 2.8,
  "roar_witness_radius_R_tiles": 6,
  "wait_apathy_push": 0.5,
  "wait_witness_radius_tiles": 1,
  "sleep_tick_push": 0.3,
  "sleep_radius_tiles": 3,
  "beacon_tick_push": 0.35,
  "beacon_radius_tiles": 4
 },
 "burnout": {
  "overdose_threshold_Y_per_tick": 4,
  "timer_X_sleeps": 3,
  "save_penalty_fraction": 0.75
 },
 "settling": {
  "settle_band_threshold_abs": 6,
  "settle_hold_generations": 1,
  "unsettle_hold_generations": 1,
  "resistance_opposing_multiplier": 0.3,
  "road_erosion_per_adjacent_tile": 0.2,
  "resistance_floor": 0.2
 },
 "zealot_fate": {
  "trigger_tribe_average_opposite_min_abs": 6,
  "trigger_hold_generations": 2,
  "convert_eval": {
   "averaging": "integer_states",
   "at_check2_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "defer_to_check3_if_check2_avg_abs_gte": 7.0,
   "at_check3_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "deferred_generation_state": "settled_equivalent_resistance",
   "else_outcome": "expel",
   "_declared_asymmetry": "Conversion is Hope's pole: hope converts (fear_zealot targets), fear breaks (hope_zealot targets are expel-only; measured deferred-generation ceiling 6.67 makes any legal bar a knife-edge - declared, not accidental)."
  },
  "average_excludes_window_zeros": true,
  "converted_zealot": {
   "value": "opposing_pole_max",
   "keeps": "immunities_pull_sphere_wincount_worship"
  },
  "expelled_zealot": {
   "npc": "removed_from_all_counts",
   "slot": "empty_for_run",
   "sphere": "dissolves",
   "tribe": "zealotless_drift_per_2_3"
  }
 },
 "stamina": {
  "floor_actions": 5,
  "worship_to_stamina_formula": "min(14, floor_actions + 0.35 * pop_aligned_weighted + per_beacon_bonus * beacons_lit)",
  "worship_band_weights": {
   "tentative": 0.5,
   "devout": 1.0,
   "zealot": 2.0
  },
  "per_beacon_bonus": 1.5,
  "costs": {
   "walk_per_tile_base": 0.5,
   "road_tier1_discount": 0.4,
   "flame": 2.5,
   "roar_per_tile_fraction_of_walk": 0.5,
   "roar_distance_base": "projection",
   "light_beacon": 3,
   "wait": 0
  }
 },
 "raze": {
  "included": true,
  "burn_capable": false,
  "cost_devotion_formula": "4 + 0.5 * target_devout_count",
  "fear_push_per_witness": 2.5,
  "witness_radius_tiles": 5
 },
 "world": {
  "map_size": 48,
  "tribes": 3,
  "tribe_size_initial": 12,
  "growth_per_tribe_per_sleep": 2,
  "initial_state": {
   "regular_start_band": "tentative",
   "regular_start_value_abs": 2,
   "zealot_pole_mix": "2_fear_1_hope"
  },
  "apathy_decay_per_tick": 0.4,
  "zealot_pull_per_tick": 2,
  "uhtcearu_damping_formula": "apathy_decay_per_tick * (1 + 1 * dominance + 0.4 * max(0, idle_sleeps - 1))",
  "generation_ticks_per_sleep": 3,
  "wander": {
   "enabled": true,
   "step_tiles_per_sleep": 1,
   "home_box_tiles": 9,
   "road_follow": {
    "enabled": true,
    "road_sight_tiles": 6,
    "leave_box_on_road": true
   }
  },
  "faction_fight": {
   "enabled": true,
   "trigger": "rival_pole_spheres_overlap",
   "casualty_rate": 0.2,
   "min_casualty_per_side": 1,
   "kill_order": "weakest_first",
   "zealots_immune_in_melee": true,
   "rout_if_contested_strength_ratio_below": 0.5,
   "settled_tribes_stand": true,
   "battle_pressure": {
    "enabled": true,
    "note": "Fear breaks / Hope bends: extended fighting deepens fear combatants toward burnout and exhausts hope combatants toward the middle (0); deep hope resists exhaustion AND drives fear to burnout harder (\"high hope fighters perform slightly better\").",
    "hope_exhaust_per_sleep": 2.5,
    "hope_depth_resist": 0.5,
    "fear_deepen_per_sleep": 1.5,
    "fear_deepen_hope_bonus": 0.5,
    "fear_burnout_at_regular_cap": true
   }
  },
  "settlement_exile": {
   "enabled": true,
   "detach_on_burnout_if_settled": true,
   "loner_tribe_id": -1,
   "loner_step_tiles_per_sleep": 1,
   "loner_follows_roads": true,
   "readopt_on_stable_adoption_abs": 2
  },
  "genesis": {
   "enabled": true,
   "grey_nomads": 55,
   "zealot_seeds_each": 3,
   "min_settle_members": 5,
   "terminal_grace_until_formed": true,
   "formed_aligned_fraction": 0.4,
   "founding_poles": [
    -1,
    1
   ]
  },
  "schism": {
   "enabled": true,
   "pop_cap": 16,
   "devout_threshold_abs": 8,
   "daughter_takes_fraction": 0.5,
   "fission_radius_tiles": 10,
   "max_tribes": 6
  },
  "road_allegiance": {
   "enabled": true,
   "initial_strength": 3,
   "erode_per_sleep": 1.0,
   "wear_per_crossing": 1,
   "detach_to_loner_on_zero": true,
   "zealot_pull_damp_on_enemy_road": 0.5
  },
  "hope_trade": {
   "enabled": false,
   "min_colonies": 2,
   "connect_radius_tiles": 28,
   "refresh_strength": 3
  },
  "contagion_spread": {
   "enabled": true,
   "radius_tiles": 2,
   "strength_per_neighbor": 0.1,
   "max_push": 0.7,
   "apathy_spreads": true
  },
  "uhtcearu_events": {
   "enabled": true,
   "variant": "A_grief_front",
   "check_at": "sleep_boundary",
   "dominance_source": "uhtcearu_damping_formula_input",
   "grief_front": {
    "trigger_dominance_min": 0.55,
    "max_concurrent_fronts": 1,
    "cooldown_sleeps_after_expiry": 4,
    "spawn_at": "largest_dominant_pole_tribe_position",
    "radius_tiles": 4,
    "duration_sleeps": 3,
    "move_tiles_per_sleep": 1,
    "move_toward": "largest_dominant_pole_tribe_position",
    "inside_replaces_dominance_term": true,
    "front_strength": 4.0,
    "outside_dominance_scale": 1.0,
    "zealots_immune": true,
    "trigger_trailing_window_sleeps": 3,
    "affects_dominant_pole_only": true
   }
  }
 },
 "ascension": {
  "enabled": true,
  "scale_by": "followers",
  "stamina_per_follower": 0.35,
  "tiers": [
   {
    "min_followers": 0,
    "beacons": 1,
    "flame_radius_bonus": 0,
    "aura_radius_bonus": 0,
    "stamina_cap": 10
   },
   {
    "min_followers": 12,
    "beacons": 2,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 0,
    "stamina_cap": 14
   },
   {
    "min_followers": 24,
    "beacons": 3,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 1,
    "stamina_cap": 18
   },
   {
    "min_followers": 40,
    "beacons": 4,
    "flame_radius_bonus": 2,
    "aura_radius_bonus": 1,
    "stamina_cap": 24
   }
  ],
  "beacon_cap_t1": 1
 },
 "win_loss": {
  "check_after_every_tick": true,
  "hold_window_ticks": 6,
  "hold_must_span_generation": true,
  "hold_continuity": "skipped_pauses_failed_resets",
  "requires_no_living_opposing_zealot": true,
  "win_count_bands": [
   "tentative",
   "devout",
   "zealot"
  ],
  "loss_count_states": [
   "soft_grey_0",
   "burned"
  ],
  "unification_threshold_fraction": 0.8,
  "intent_measure": "player_pole = sign(S), where S = signed sum of player-delivered valence pressure (witnessed Flame/Roar/Raze pushes plus own sleep and beacon aura ticks) over the trailing 1 sleep; the win check evaluates only on ticks where abs(S) >= 3, otherwise it is skipped that tick (the loss check always runs); no carry-over of a previous pole under any condition; before the first player action the win check is skipped",
  "tie_priority": "loss"
 }
}
```

```json
{
 "meta": {
  "variant": "B",
  "hypothesis": "Shorten the breath: a 2-sleep front on a 3-sleep cooldown halves the dwell a single unheld convert can take before the fog lifts, trading peak bite for recoverability.",
  "gdd_version": "0.8.1",
  "schema": "3.9.2",
  "patches": "rules-v3.9.1-C | MOCK-FIXTURE run (crew v3.9.2, variant B) - front-feel sweep, NOT a Director-gated change.",
  "gate": "G20 2026-07-20 \u2014 conversion redesigned reachable (defer + breath-hold, integer-state averaging), Director-ruled option 1, four calibration cycles harness-verified; declared asymmetry: Hope converts (fear-zealot targets, bars 8.0/8.0), Fear breaks (hope-zealot targets expel-only \u2014 measured check-3 ceiling 6.67; knife-edge bars rejected). hold_continuity enumerated skipped_pauses_failed_resets (A11/R1). | Run 18 2026-07-20 \u2014 Director rulings: fights=real casualties+rout, burnout-exile=lone wanderer, road-follow=strong bias. | Run 19 2026-07-20 \u2014 Director ruling: battle pressure (extended fighting exhausts hope to middle, breaks fear to burnout; deep hope resists & performs slightly better). Death rate kept below regrowth. | Run 20 2026-07-20 \u2014 Director: GENESIS start (grey nomads + 3 lone founding zealots that gather, settle, and are found via roads). Balance preserved (2F/1H emergent). | Run 21 2026-07-21 \u2014 Director: SCHISM (capped-count symmetric colony fission) to bound settlements + spread the world; roads gain allegiance (erode-then-recruit). | Run 23 2026-07-23 - Director: UHTCEARU ACTIVE EVENTS, Variant A (Grief Front) selected from mechanic-designer-run23; tie_priority=loss ratified (GDD v0.9.1). | Run 23b 2026-07-23 - Director: SALVAGE-AS-ANTAGONIST ruled. Fix set shipped as a co-gated unit per attacks-v5: front_strength 4.0 (front stalls faith inside spheres to net ~0; still cannot flip or burn), spawn anchor = largest dominant tribe (closes A3 geometry null + deletes A6 centroid-steering), trailing-window trigger over 3 sleeps (closes A5 hover-sprint shadow), decay restricted to dominant-pole NPCs (grief never helps anyone - closes the cleanup-assist). Cooldown held at 2 pending campaign-impact measurement.",
  "wander_note": "v3.3 adds world.wander: cohesive, regionally-bounded nomadic drift for UNSETTLED tribes (settled anchor). Belief-neutral by construction (tribe moves as a body; box keeps tribes from colliding unaided) \u2014 harness-verified identical terminals to v3.2-C. Player-led tribe collisions remain deferred (a future belief-affecting mechanic needing its own harness pass).",
  "v34_note": "v3.4 adds three BELIEF-AFFECTING nomad systems (harness-gated, not raw engine edits): (1) strong road-following \u2014 unsettled tribes steer onto/along player-laid roads (leaving the home box when on a road), making roads a leash to lead tribes to spheres/beacons; (2) faction fights \u2014 when rival-pole spheres overlap, real casualties accrue each sleep (weakest-first, zealots immune), the outnumbered UNSETTLED tribe routs, settled tribes stand; (3) settlement exile \u2014 settling roots a tribe (it no longer wanders and cannot be led out); the ONLY exit is burnout, which detaches the broken NPC as a lone wanderer that drifts (road-biased) and can be re-adopted by any sphere that pulls it to |I|>=2. Substrate: a real World.roads tile set (mirrors the build). Autonomous world (no player roads, no forced collisions) must reduce to v3.3 terminals.",
  "v35_note": "v3.5 layers BELIEF battle-pressure onto v3.4 faction fights (harness-gated). Each fight-sleep, contested combatants take pressure in addition to weakest-first casualties: FEAR combatants deepen toward -SPAN and burn out at the regular cap (Fear breaks); HOPE combatants are exhausted toward 0/middle, reduced by their depth (Hope bends; deep hope resists). Strong opposing hope deepens fear faster (fear_deepen_hope_bonus). Counterplay to a pin: deep-hope defenders burn the attacker out while barely eroding. Casualty_rate unchanged (below regrowth); battle burnout adds no population removal (burned recover per timer).",
  "v36_note": "v3.6 replaces the pre-clustered 3x12 start with a GENESIS: grey_nomads(40) unaligned loners scattered on the map + 3 founding zealots (2F 1H) each with a small seed following, wandering. Zealots gather nearby nomads (overlap pull -> re-adoption), grow, and settle once they hold >= min_settle_members followers at devout average; leftover nomads find settlements via roads. Two genesis-only safety gates, both no-ops for the legacy start: min_settle_members (a lone/tiny zealot cannot settle on its own zealot-inflated average) and terminal_grace_until_formed (win/loss suppressed until the world takes shape -> aligned fraction >= formed_aligned_fraction OR a tribe settles; otherwise a ~all-grey genesis would trip the apathy loss instantly). genesis.enabled=false reproduces v3.5 exactly.",
  "v37_note": "v3.7 adds SCHISM: a settled tribe at pop_cap with a deep (|avg|>=devout_threshold) conviction births a same-pole daughter zealot, hands it daughter_takes_fraction of the flock, migrates the colony >= fission_radius tiles away and settles it. Symmetric (both poles colonize) but total tribe count capped at max_tribes. This bounds every settlement to a convertible size and grows the world by spreading rather than ballooning \u2014 the fix for genesis unbounded births. Road allegiance (erode-then-recruit) layered next.",
  "founding_note": "v3.7.1: living-world rebalance \u2014 symmetric 1F/1H founding (fair spreading contest), max_tribes 5, road_allegiance (erode-then-recruit + enemy-zealot damping).",
  "balance_note": "v3.7.3: living world winnable & roughly balanced with symmetric 1F1H founding + max_tribes 5 (bot proxy: HOPE ~20/25, FEAR ~22/25 -> asymmetric, fear-favored as intended). hope_trade DISABLED (road-refresh design misguides movement + churns; revisit traders as discrete visible agents that double as live-movement).",
  "ascension_note": "v3.8: follower-driven ASCENSION (shifting power scale). Your power tier = f(your-pole believer count), recomputed at each sleep (level-up). Higher tiers unlock more beacons (1->4), bigger flame radius (+0..+2), bigger sleep aura, and a larger stamina cap (10->24). Gives Hope a snowball, adds beacon-placement agency, and the avatar (kaiju) scales with the flock. Legacy (no tiers) = tier0 = unchanged.",
  "contagion_note": "v3.8.1: PEER CONTAGION \u2014 each tick every NPC also feels its neighbours: hope neighbours pull you hope, fear pull fear, grey (apathy) drag you toward 0. Belief now spreads NPC-to-NPC like a contagion (not just from zealots); apathy spreads too (stakes). The kai.ju/beacons tip the local balance. Small per-neighbour strength so it enriches rather than dominates the zealot economy.",
  "v39_note": "v3.9 adds world.uhtcearu_events variant A_grief_front (Run 23, GDD v0.9.2 grief canon: grief is the gravity, not a pole - catastrophes wear the dominant pole toward 0, never recruit for the opposite). At each sleep boundary, if dominance >= trigger and no front is active and cooldown elapsed, a grief front (radius 6) condenses at the tile centroid of dominant-pole NPCs and crawls 1 tile/sleep toward the largest dominant-pole tribe for 3 sleeps. Inside the front the damping formula's dominance term is REPLACED by front_strength (no double-punishment; outside is exactly the live formula). Zealots immune. Render: a visible desaturating fog bank, sky darkest above it. enabled=false reproduces v3.7 bit-for-bit. Dominance source rebound per packet [ASSUMPTION]: the same player-pole fraction the live damping formula reads.",
  "v391_note": "v3.9.1 SALVAGE (Run 23b): the as-shipped 1.6 front was harness-proven safe but half-dead (in-sphere drift delta 0.000/sleep - zealot pull + step cap swallow it; attacks-v5 A1/A2/A3/A5). Salvage set, co-gated per the red-team verdict: (1) front_strength 4.0 -> inside-front decay 0.4*(1+4.0)=2.0/tick = zealot pull: the front STALLS deepening inside spheres to net ~0 without ever flipping (decay cannot cross 0) or burning (decay is not same-pole pressure); step cap bounds unsupported NPCs at -1/tick as before, so no overkill vs stragglers. (2) spawn_at largest_dominant_tribe_position: the front condenses ON its target - no dead-air centroid misses, no player-steerable aim. (3) trigger_trailing_window_sleeps 3: fires on the MAX dominance over the trailing window, so hovering below threshold then sprinting cannot schedule the antagonist away. (4) affects_dominant_pole_only true: grief wears down only the winner - it never greys enemy holdouts for you (cleanup-assist closed). Zealot immunity unchanged; enabled:false still reproduces v3.7 bit-for-bit."
 },
 "scale": {
  "min": -12,
  "max": 12,
  "zealot_value": 12
 },
 "bands": {
  "tentative": [
   1,
   5
  ],
  "devout": [
   6,
   11
  ],
  "zealot": 12
 },
 "contagion": {
  "step_per_tick_max": 1,
  "sphere_base_radius_tiles": 2,
  "sphere_growth_formula": "sphere_base_radius_tiles + floor(sqrt(group_size))",
  "overlap_pull_strength": 0.8,
  "awake_pull_multiplier": 0.3,
  "zero_value_membership": {
   "spawn_state": "in",
   "window_ticks_at_zero_cumulative": 6,
   "reset_on_stable_adoption_abs_gte": 2,
   "after_window": "out"
  }
 },
 "player_pressure": {
  "flame_push_base": 2.0,
  "flame_radius_tiles": 3,
  "alignment_strength_multiplier_formula": "1",
  "roar_fear_push": 2.8,
  "roar_witness_radius_R_tiles": 6,
  "wait_apathy_push": 0.5,
  "wait_witness_radius_tiles": 1,
  "sleep_tick_push": 0.3,
  "sleep_radius_tiles": 3,
  "beacon_tick_push": 0.35,
  "beacon_radius_tiles": 4
 },
 "burnout": {
  "overdose_threshold_Y_per_tick": 4,
  "timer_X_sleeps": 3,
  "save_penalty_fraction": 0.75
 },
 "settling": {
  "settle_band_threshold_abs": 6,
  "settle_hold_generations": 1,
  "unsettle_hold_generations": 1,
  "resistance_opposing_multiplier": 0.3,
  "road_erosion_per_adjacent_tile": 0.2,
  "resistance_floor": 0.2
 },
 "zealot_fate": {
  "trigger_tribe_average_opposite_min_abs": 6,
  "trigger_hold_generations": 2,
  "convert_eval": {
   "averaging": "integer_states",
   "at_check2_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "defer_to_check3_if_check2_avg_abs_gte": 7.0,
   "at_check3_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "deferred_generation_state": "settled_equivalent_resistance",
   "else_outcome": "expel",
   "_declared_asymmetry": "Conversion is Hope's pole: hope converts (fear_zealot targets), fear breaks (hope_zealot targets are expel-only; measured deferred-generation ceiling 6.67 makes any legal bar a knife-edge - declared, not accidental)."
  },
  "average_excludes_window_zeros": true,
  "converted_zealot": {
   "value": "opposing_pole_max",
   "keeps": "immunities_pull_sphere_wincount_worship"
  },
  "expelled_zealot": {
   "npc": "removed_from_all_counts",
   "slot": "empty_for_run",
   "sphere": "dissolves",
   "tribe": "zealotless_drift_per_2_3"
  }
 },
 "stamina": {
  "floor_actions": 5,
  "worship_to_stamina_formula": "min(14, floor_actions + 0.35 * pop_aligned_weighted + per_beacon_bonus * beacons_lit)",
  "worship_band_weights": {
   "tentative": 0.5,
   "devout": 1.0,
   "zealot": 2.0
  },
  "per_beacon_bonus": 1.5,
  "costs": {
   "walk_per_tile_base": 0.5,
   "road_tier1_discount": 0.4,
   "flame": 2.5,
   "roar_per_tile_fraction_of_walk": 0.5,
   "roar_distance_base": "projection",
   "light_beacon": 3,
   "wait": 0
  }
 },
 "raze": {
  "included": true,
  "burn_capable": false,
  "cost_devotion_formula": "4 + 0.5 * target_devout_count",
  "fear_push_per_witness": 2.5,
  "witness_radius_tiles": 5
 },
 "world": {
  "map_size": 48,
  "tribes": 3,
  "tribe_size_initial": 12,
  "growth_per_tribe_per_sleep": 2,
  "initial_state": {
   "regular_start_band": "tentative",
   "regular_start_value_abs": 2,
   "zealot_pole_mix": "2_fear_1_hope"
  },
  "apathy_decay_per_tick": 0.4,
  "zealot_pull_per_tick": 2,
  "uhtcearu_damping_formula": "apathy_decay_per_tick * (1 + 1 * dominance + 0.4 * max(0, idle_sleeps - 1))",
  "generation_ticks_per_sleep": 3,
  "wander": {
   "enabled": true,
   "step_tiles_per_sleep": 1,
   "home_box_tiles": 9,
   "road_follow": {
    "enabled": true,
    "road_sight_tiles": 6,
    "leave_box_on_road": true
   }
  },
  "faction_fight": {
   "enabled": true,
   "trigger": "rival_pole_spheres_overlap",
   "casualty_rate": 0.2,
   "min_casualty_per_side": 1,
   "kill_order": "weakest_first",
   "zealots_immune_in_melee": true,
   "rout_if_contested_strength_ratio_below": 0.5,
   "settled_tribes_stand": true,
   "battle_pressure": {
    "enabled": true,
    "note": "Fear breaks / Hope bends: extended fighting deepens fear combatants toward burnout and exhausts hope combatants toward the middle (0); deep hope resists exhaustion AND drives fear to burnout harder (\"high hope fighters perform slightly better\").",
    "hope_exhaust_per_sleep": 2.5,
    "hope_depth_resist": 0.5,
    "fear_deepen_per_sleep": 1.5,
    "fear_deepen_hope_bonus": 0.5,
    "fear_burnout_at_regular_cap": true
   }
  },
  "settlement_exile": {
   "enabled": true,
   "detach_on_burnout_if_settled": true,
   "loner_tribe_id": -1,
   "loner_step_tiles_per_sleep": 1,
   "loner_follows_roads": true,
   "readopt_on_stable_adoption_abs": 2
  },
  "genesis": {
   "enabled": true,
   "grey_nomads": 55,
   "zealot_seeds_each": 3,
   "min_settle_members": 5,
   "terminal_grace_until_formed": true,
   "formed_aligned_fraction": 0.4,
   "founding_poles": [
    -1,
    1
   ]
  },
  "schism": {
   "enabled": true,
   "pop_cap": 16,
   "devout_threshold_abs": 8,
   "daughter_takes_fraction": 0.5,
   "fission_radius_tiles": 10,
   "max_tribes": 6
  },
  "road_allegiance": {
   "enabled": true,
   "initial_strength": 3,
   "erode_per_sleep": 1.0,
   "wear_per_crossing": 1,
   "detach_to_loner_on_zero": true,
   "zealot_pull_damp_on_enemy_road": 0.5
  },
  "hope_trade": {
   "enabled": false,
   "min_colonies": 2,
   "connect_radius_tiles": 28,
   "refresh_strength": 3
  },
  "contagion_spread": {
   "enabled": true,
   "radius_tiles": 2,
   "strength_per_neighbor": 0.1,
   "max_push": 0.7,
   "apathy_spreads": true
  },
  "uhtcearu_events": {
   "enabled": true,
   "variant": "A_grief_front",
   "check_at": "sleep_boundary",
   "dominance_source": "uhtcearu_damping_formula_input",
   "grief_front": {
    "trigger_dominance_min": 0.55,
    "max_concurrent_fronts": 1,
    "cooldown_sleeps_after_expiry": 3,
    "spawn_at": "largest_dominant_pole_tribe_position",
    "radius_tiles": 6,
    "duration_sleeps": 2,
    "move_tiles_per_sleep": 1,
    "move_toward": "largest_dominant_pole_tribe_position",
    "inside_replaces_dominance_term": true,
    "front_strength": 4.0,
    "outside_dominance_scale": 1.0,
    "zealots_immune": true,
    "trigger_trailing_window_sleeps": 3,
    "affects_dominant_pole_only": true
   }
  }
 },
 "ascension": {
  "enabled": true,
  "scale_by": "followers",
  "stamina_per_follower": 0.35,
  "tiers": [
   {
    "min_followers": 0,
    "beacons": 1,
    "flame_radius_bonus": 0,
    "aura_radius_bonus": 0,
    "stamina_cap": 10
   },
   {
    "min_followers": 12,
    "beacons": 2,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 0,
    "stamina_cap": 14
   },
   {
    "min_followers": 24,
    "beacons": 3,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 1,
    "stamina_cap": 18
   },
   {
    "min_followers": 40,
    "beacons": 4,
    "flame_radius_bonus": 2,
    "aura_radius_bonus": 1,
    "stamina_cap": 24
   }
  ],
  "beacon_cap_t1": 1
 },
 "win_loss": {
  "check_after_every_tick": true,
  "hold_window_ticks": 6,
  "hold_must_span_generation": true,
  "hold_continuity": "skipped_pauses_failed_resets",
  "requires_no_living_opposing_zealot": true,
  "win_count_bands": [
   "tentative",
   "devout",
   "zealot"
  ],
  "loss_count_states": [
   "soft_grey_0",
   "burned"
  ],
  "unification_threshold_fraction": 0.8,
  "intent_measure": "player_pole = sign(S), where S = signed sum of player-delivered valence pressure (witnessed Flame/Roar/Raze pushes plus own sleep and beacon aura ticks) over the trailing 1 sleep; the win check evaluates only on ticks where abs(S) >= 3, otherwise it is skipped that tick (the loss check always runs); no carry-over of a previous pole under any condition; before the first player action the win check is skipped",
  "tie_priority": "loss"
 }
}
```

```json
{
 "meta": {
  "variant": "C",
  "hypothesis": "Fire later, move faster: raising the trigger to 0.65 and doubling crawl speed makes the front a late-game punctuation over the leader's core rather than mid-game weather over its edges.",
  "gdd_version": "0.8.1",
  "schema": "3.9.2",
  "patches": "rules-v3.9.1-C | MOCK-FIXTURE run (crew v3.9.2, variant C) - front-feel sweep, NOT a Director-gated change.",
  "gate": "G20 2026-07-20 \u2014 conversion redesigned reachable (defer + breath-hold, integer-state averaging), Director-ruled option 1, four calibration cycles harness-verified; declared asymmetry: Hope converts (fear-zealot targets, bars 8.0/8.0), Fear breaks (hope-zealot targets expel-only \u2014 measured check-3 ceiling 6.67; knife-edge bars rejected). hold_continuity enumerated skipped_pauses_failed_resets (A11/R1). | Run 18 2026-07-20 \u2014 Director rulings: fights=real casualties+rout, burnout-exile=lone wanderer, road-follow=strong bias. | Run 19 2026-07-20 \u2014 Director ruling: battle pressure (extended fighting exhausts hope to middle, breaks fear to burnout; deep hope resists & performs slightly better). Death rate kept below regrowth. | Run 20 2026-07-20 \u2014 Director: GENESIS start (grey nomads + 3 lone founding zealots that gather, settle, and are found via roads). Balance preserved (2F/1H emergent). | Run 21 2026-07-21 \u2014 Director: SCHISM (capped-count symmetric colony fission) to bound settlements + spread the world; roads gain allegiance (erode-then-recruit). | Run 23 2026-07-23 - Director: UHTCEARU ACTIVE EVENTS, Variant A (Grief Front) selected from mechanic-designer-run23; tie_priority=loss ratified (GDD v0.9.1). | Run 23b 2026-07-23 - Director: SALVAGE-AS-ANTAGONIST ruled. Fix set shipped as a co-gated unit per attacks-v5: front_strength 4.0 (front stalls faith inside spheres to net ~0; still cannot flip or burn), spawn anchor = largest dominant tribe (closes A3 geometry null + deletes A6 centroid-steering), trailing-window trigger over 3 sleeps (closes A5 hover-sprint shadow), decay restricted to dominant-pole NPCs (grief never helps anyone - closes the cleanup-assist). Cooldown held at 2 pending campaign-impact measurement.",
  "wander_note": "v3.3 adds world.wander: cohesive, regionally-bounded nomadic drift for UNSETTLED tribes (settled anchor). Belief-neutral by construction (tribe moves as a body; box keeps tribes from colliding unaided) \u2014 harness-verified identical terminals to v3.2-C. Player-led tribe collisions remain deferred (a future belief-affecting mechanic needing its own harness pass).",
  "v34_note": "v3.4 adds three BELIEF-AFFECTING nomad systems (harness-gated, not raw engine edits): (1) strong road-following \u2014 unsettled tribes steer onto/along player-laid roads (leaving the home box when on a road), making roads a leash to lead tribes to spheres/beacons; (2) faction fights \u2014 when rival-pole spheres overlap, real casualties accrue each sleep (weakest-first, zealots immune), the outnumbered UNSETTLED tribe routs, settled tribes stand; (3) settlement exile \u2014 settling roots a tribe (it no longer wanders and cannot be led out); the ONLY exit is burnout, which detaches the broken NPC as a lone wanderer that drifts (road-biased) and can be re-adopted by any sphere that pulls it to |I|>=2. Substrate: a real World.roads tile set (mirrors the build). Autonomous world (no player roads, no forced collisions) must reduce to v3.3 terminals.",
  "v35_note": "v3.5 layers BELIEF battle-pressure onto v3.4 faction fights (harness-gated). Each fight-sleep, contested combatants take pressure in addition to weakest-first casualties: FEAR combatants deepen toward -SPAN and burn out at the regular cap (Fear breaks); HOPE combatants are exhausted toward 0/middle, reduced by their depth (Hope bends; deep hope resists). Strong opposing hope deepens fear faster (fear_deepen_hope_bonus). Counterplay to a pin: deep-hope defenders burn the attacker out while barely eroding. Casualty_rate unchanged (below regrowth); battle burnout adds no population removal (burned recover per timer).",
  "v36_note": "v3.6 replaces the pre-clustered 3x12 start with a GENESIS: grey_nomads(40) unaligned loners scattered on the map + 3 founding zealots (2F 1H) each with a small seed following, wandering. Zealots gather nearby nomads (overlap pull -> re-adoption), grow, and settle once they hold >= min_settle_members followers at devout average; leftover nomads find settlements via roads. Two genesis-only safety gates, both no-ops for the legacy start: min_settle_members (a lone/tiny zealot cannot settle on its own zealot-inflated average) and terminal_grace_until_formed (win/loss suppressed until the world takes shape -> aligned fraction >= formed_aligned_fraction OR a tribe settles; otherwise a ~all-grey genesis would trip the apathy loss instantly). genesis.enabled=false reproduces v3.5 exactly.",
  "v37_note": "v3.7 adds SCHISM: a settled tribe at pop_cap with a deep (|avg|>=devout_threshold) conviction births a same-pole daughter zealot, hands it daughter_takes_fraction of the flock, migrates the colony >= fission_radius tiles away and settles it. Symmetric (both poles colonize) but total tribe count capped at max_tribes. This bounds every settlement to a convertible size and grows the world by spreading rather than ballooning \u2014 the fix for genesis unbounded births. Road allegiance (erode-then-recruit) layered next.",
  "founding_note": "v3.7.1: living-world rebalance \u2014 symmetric 1F/1H founding (fair spreading contest), max_tribes 5, road_allegiance (erode-then-recruit + enemy-zealot damping).",
  "balance_note": "v3.7.3: living world winnable & roughly balanced with symmetric 1F1H founding + max_tribes 5 (bot proxy: HOPE ~20/25, FEAR ~22/25 -> asymmetric, fear-favored as intended). hope_trade DISABLED (road-refresh design misguides movement + churns; revisit traders as discrete visible agents that double as live-movement).",
  "ascension_note": "v3.8: follower-driven ASCENSION (shifting power scale). Your power tier = f(your-pole believer count), recomputed at each sleep (level-up). Higher tiers unlock more beacons (1->4), bigger flame radius (+0..+2), bigger sleep aura, and a larger stamina cap (10->24). Gives Hope a snowball, adds beacon-placement agency, and the avatar (kaiju) scales with the flock. Legacy (no tiers) = tier0 = unchanged.",
  "contagion_note": "v3.8.1: PEER CONTAGION \u2014 each tick every NPC also feels its neighbours: hope neighbours pull you hope, fear pull fear, grey (apathy) drag you toward 0. Belief now spreads NPC-to-NPC like a contagion (not just from zealots); apathy spreads too (stakes). The kai.ju/beacons tip the local balance. Small per-neighbour strength so it enriches rather than dominates the zealot economy.",
  "v39_note": "v3.9 adds world.uhtcearu_events variant A_grief_front (Run 23, GDD v0.9.2 grief canon: grief is the gravity, not a pole - catastrophes wear the dominant pole toward 0, never recruit for the opposite). At each sleep boundary, if dominance >= trigger and no front is active and cooldown elapsed, a grief front (radius 6) condenses at the tile centroid of dominant-pole NPCs and crawls 1 tile/sleep toward the largest dominant-pole tribe for 3 sleeps. Inside the front the damping formula's dominance term is REPLACED by front_strength (no double-punishment; outside is exactly the live formula). Zealots immune. Render: a visible desaturating fog bank, sky darkest above it. enabled=false reproduces v3.7 bit-for-bit. Dominance source rebound per packet [ASSUMPTION]: the same player-pole fraction the live damping formula reads.",
  "v391_note": "v3.9.1 SALVAGE (Run 23b): the as-shipped 1.6 front was harness-proven safe but half-dead (in-sphere drift delta 0.000/sleep - zealot pull + step cap swallow it; attacks-v5 A1/A2/A3/A5). Salvage set, co-gated per the red-team verdict: (1) front_strength 4.0 -> inside-front decay 0.4*(1+4.0)=2.0/tick = zealot pull: the front STALLS deepening inside spheres to net ~0 without ever flipping (decay cannot cross 0) or burning (decay is not same-pole pressure); step cap bounds unsupported NPCs at -1/tick as before, so no overkill vs stragglers. (2) spawn_at largest_dominant_tribe_position: the front condenses ON its target - no dead-air centroid misses, no player-steerable aim. (3) trigger_trailing_window_sleeps 3: fires on the MAX dominance over the trailing window, so hovering below threshold then sprinting cannot schedule the antagonist away. (4) affects_dominant_pole_only true: grief wears down only the winner - it never greys enemy holdouts for you (cleanup-assist closed). Zealot immunity unchanged; enabled:false still reproduces v3.7 bit-for-bit."
 },
 "scale": {
  "min": -12,
  "max": 12,
  "zealot_value": 12
 },
 "bands": {
  "tentative": [
   1,
   5
  ],
  "devout": [
   6,
   11
  ],
  "zealot": 12
 },
 "contagion": {
  "step_per_tick_max": 1,
  "sphere_base_radius_tiles": 2,
  "sphere_growth_formula": "sphere_base_radius_tiles + floor(sqrt(group_size))",
  "overlap_pull_strength": 0.8,
  "awake_pull_multiplier": 0.3,
  "zero_value_membership": {
   "spawn_state": "in",
   "window_ticks_at_zero_cumulative": 6,
   "reset_on_stable_adoption_abs_gte": 2,
   "after_window": "out"
  }
 },
 "player_pressure": {
  "flame_push_base": 2.0,
  "flame_radius_tiles": 3,
  "alignment_strength_multiplier_formula": "1",
  "roar_fear_push": 2.8,
  "roar_witness_radius_R_tiles": 6,
  "wait_apathy_push": 0.5,
  "wait_witness_radius_tiles": 1,
  "sleep_tick_push": 0.3,
  "sleep_radius_tiles": 3,
  "beacon_tick_push": 0.35,
  "beacon_radius_tiles": 4
 },
 "burnout": {
  "overdose_threshold_Y_per_tick": 4,
  "timer_X_sleeps": 3,
  "save_penalty_fraction": 0.75
 },
 "settling": {
  "settle_band_threshold_abs": 6,
  "settle_hold_generations": 1,
  "unsettle_hold_generations": 1,
  "resistance_opposing_multiplier": 0.3,
  "road_erosion_per_adjacent_tile": 0.2,
  "resistance_floor": 0.2
 },
 "zealot_fate": {
  "trigger_tribe_average_opposite_min_abs": 6,
  "trigger_hold_generations": 2,
  "convert_eval": {
   "averaging": "integer_states",
   "at_check2_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "defer_to_check3_if_check2_avg_abs_gte": 7.0,
   "at_check3_if_avg_abs_gte": {
    "fear_zealot": 8.0,
    "hope_zealot": null
   },
   "deferred_generation_state": "settled_equivalent_resistance",
   "else_outcome": "expel",
   "_declared_asymmetry": "Conversion is Hope's pole: hope converts (fear_zealot targets), fear breaks (hope_zealot targets are expel-only; measured deferred-generation ceiling 6.67 makes any legal bar a knife-edge - declared, not accidental)."
  },
  "average_excludes_window_zeros": true,
  "converted_zealot": {
   "value": "opposing_pole_max",
   "keeps": "immunities_pull_sphere_wincount_worship"
  },
  "expelled_zealot": {
   "npc": "removed_from_all_counts",
   "slot": "empty_for_run",
   "sphere": "dissolves",
   "tribe": "zealotless_drift_per_2_3"
  }
 },
 "stamina": {
  "floor_actions": 5,
  "worship_to_stamina_formula": "min(14, floor_actions + 0.35 * pop_aligned_weighted + per_beacon_bonus * beacons_lit)",
  "worship_band_weights": {
   "tentative": 0.5,
   "devout": 1.0,
   "zealot": 2.0
  },
  "per_beacon_bonus": 1.5,
  "costs": {
   "walk_per_tile_base": 0.5,
   "road_tier1_discount": 0.4,
   "flame": 2.5,
   "roar_per_tile_fraction_of_walk": 0.5,
   "roar_distance_base": "projection",
   "light_beacon": 3,
   "wait": 0
  }
 },
 "raze": {
  "included": true,
  "burn_capable": false,
  "cost_devotion_formula": "4 + 0.5 * target_devout_count",
  "fear_push_per_witness": 2.5,
  "witness_radius_tiles": 5
 },
 "world": {
  "map_size": 48,
  "tribes": 3,
  "tribe_size_initial": 12,
  "growth_per_tribe_per_sleep": 2,
  "initial_state": {
   "regular_start_band": "tentative",
   "regular_start_value_abs": 2,
   "zealot_pole_mix": "2_fear_1_hope"
  },
  "apathy_decay_per_tick": 0.4,
  "zealot_pull_per_tick": 2,
  "uhtcearu_damping_formula": "apathy_decay_per_tick * (1 + 1 * dominance + 0.4 * max(0, idle_sleeps - 1))",
  "generation_ticks_per_sleep": 3,
  "wander": {
   "enabled": true,
   "step_tiles_per_sleep": 1,
   "home_box_tiles": 9,
   "road_follow": {
    "enabled": true,
    "road_sight_tiles": 6,
    "leave_box_on_road": true
   }
  },
  "faction_fight": {
   "enabled": true,
   "trigger": "rival_pole_spheres_overlap",
   "casualty_rate": 0.2,
   "min_casualty_per_side": 1,
   "kill_order": "weakest_first",
   "zealots_immune_in_melee": true,
   "rout_if_contested_strength_ratio_below": 0.5,
   "settled_tribes_stand": true,
   "battle_pressure": {
    "enabled": true,
    "note": "Fear breaks / Hope bends: extended fighting deepens fear combatants toward burnout and exhausts hope combatants toward the middle (0); deep hope resists exhaustion AND drives fear to burnout harder (\"high hope fighters perform slightly better\").",
    "hope_exhaust_per_sleep": 2.5,
    "hope_depth_resist": 0.5,
    "fear_deepen_per_sleep": 1.5,
    "fear_deepen_hope_bonus": 0.5,
    "fear_burnout_at_regular_cap": true
   }
  },
  "settlement_exile": {
   "enabled": true,
   "detach_on_burnout_if_settled": true,
   "loner_tribe_id": -1,
   "loner_step_tiles_per_sleep": 1,
   "loner_follows_roads": true,
   "readopt_on_stable_adoption_abs": 2
  },
  "genesis": {
   "enabled": true,
   "grey_nomads": 55,
   "zealot_seeds_each": 3,
   "min_settle_members": 5,
   "terminal_grace_until_formed": true,
   "formed_aligned_fraction": 0.4,
   "founding_poles": [
    -1,
    1
   ]
  },
  "schism": {
   "enabled": true,
   "pop_cap": 16,
   "devout_threshold_abs": 8,
   "daughter_takes_fraction": 0.5,
   "fission_radius_tiles": 10,
   "max_tribes": 6
  },
  "road_allegiance": {
   "enabled": true,
   "initial_strength": 3,
   "erode_per_sleep": 1.0,
   "wear_per_crossing": 1,
   "detach_to_loner_on_zero": true,
   "zealot_pull_damp_on_enemy_road": 0.5
  },
  "hope_trade": {
   "enabled": false,
   "min_colonies": 2,
   "connect_radius_tiles": 28,
   "refresh_strength": 3
  },
  "contagion_spread": {
   "enabled": true,
   "radius_tiles": 2,
   "strength_per_neighbor": 0.1,
   "max_push": 0.7,
   "apathy_spreads": true
  },
  "uhtcearu_events": {
   "enabled": true,
   "variant": "A_grief_front",
   "check_at": "sleep_boundary",
   "dominance_source": "uhtcearu_damping_formula_input",
   "grief_front": {
    "trigger_dominance_min": 0.65,
    "max_concurrent_fronts": 1,
    "cooldown_sleeps_after_expiry": 2,
    "spawn_at": "largest_dominant_pole_tribe_position",
    "radius_tiles": 6,
    "duration_sleeps": 3,
    "move_tiles_per_sleep": 2,
    "move_toward": "largest_dominant_pole_tribe_position",
    "inside_replaces_dominance_term": true,
    "front_strength": 4.0,
    "outside_dominance_scale": 1.0,
    "zealots_immune": true,
    "trigger_trailing_window_sleeps": 3,
    "affects_dominant_pole_only": true
   }
  }
 },
 "ascension": {
  "enabled": true,
  "scale_by": "followers",
  "stamina_per_follower": 0.35,
  "tiers": [
   {
    "min_followers": 0,
    "beacons": 1,
    "flame_radius_bonus": 0,
    "aura_radius_bonus": 0,
    "stamina_cap": 10
   },
   {
    "min_followers": 12,
    "beacons": 2,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 0,
    "stamina_cap": 14
   },
   {
    "min_followers": 24,
    "beacons": 3,
    "flame_radius_bonus": 1,
    "aura_radius_bonus": 1,
    "stamina_cap": 18
   },
   {
    "min_followers": 40,
    "beacons": 4,
    "flame_radius_bonus": 2,
    "aura_radius_bonus": 1,
    "stamina_cap": 24
   }
  ],
  "beacon_cap_t1": 1
 },
 "win_loss": {
  "check_after_every_tick": true,
  "hold_window_ticks": 6,
  "hold_must_span_generation": true,
  "hold_continuity": "skipped_pauses_failed_resets",
  "requires_no_living_opposing_zealot": true,
  "win_count_bands": [
   "tentative",
   "devout",
   "zealot"
  ],
  "loss_count_states": [
   "soft_grey_0",
   "burned"
  ],
  "unification_threshold_fraction": 0.8,
  "intent_measure": "player_pole = sign(S), where S = signed sum of player-delivered valence pressure (witnessed Flame/Roar/Raze pushes plus own sleep and beacon aura ticks) over the trailing 1 sleep; the win check evaluates only on ticks where abs(S) >= 3, otherwise it is skipped that tick (the loss check always runs); no carry-over of a previous pole under any condition; before the first player action the win check is skipped",
  "tie_priority": "loss"
 }
}
```


## 3. Expected-shape notes

**A (r4, cooldown 4)**
- Run length: unchanged median; fronts per run should roughly halve against baseline.
- Regressions: do-nothing still 8/8 apathy loss (the trigger is never reached passively); tyrant unchanged; campaign within 1 win of baseline; frontal siege flip-identical; self-burns 0.
- Most vulnerable to: a re-opened A3 geometry null — r4 + 3 tiles of crawl is 7 tiles of reach, and schism daughters spawn 10 tiles out.
- Falsify by: `median_front_exposure` against baseline. If it does not drop materially, the radius is not where the exposure lives.

**B (duration 2, cooldown 3)**
- Run length: unchanged median; slightly more fronts than A, each shorter.
- Regressions: as A. Duty cycle drops from ~0.65 to ~0.40.
- Most vulnerable to: the metronome finding (attacks-v5 A9) — more frequent, weaker fronts is the worst case for "announces an antagonist that does nothing".
- Falsify by: `median_fronts_spawned` up while `median_front_exposure` is flat — that would mean B bought noise, not relief.

**C (trigger 0.65, crawl 2)**
- Run length: possibly longer at the tail — the front now lands during the hold window rather than before it.
- Regressions: do-nothing unaffected by construction; brink behaviour is the risk.
- Most vulnerable to: hold-denial (attacks-v5 A7). A front that only fires past 0.65 fires almost exclusively into the endgame.
- Falsify by: `wins` and `median_terminal_sleep` in the campaign arm against baseline.

## 4. Canon friction

None. `front_strength` is left at its gated value in all three variants; the grief canon (CANON ruling 6 — grief wears the dominant pole, never recruits for the opposite) is untouched, as is `affects_dominant_pole_only`. Cooldown is the dial CANON itself parked "pending campaign-impact measurement" (Run 23b), so moving it is the question this run was convened to ask.

## 5. Assumptions

- `[ASSUMPTION]` That straggler relief is worth measuring in `front_exposure` (NPC-sleeps) rather than in a per-NPC greying rate. The harness emits the former; the latter would need a new probe.
- `[ASSUMPTION]` That the Run-23b closures (spawn anchor, trailing window, dom-only) are independent of radius, duration and cadence. A, B and C all leave those four fields at their gated values, so this is testable rather than assumed away.
