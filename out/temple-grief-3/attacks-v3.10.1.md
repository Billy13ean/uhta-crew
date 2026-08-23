# attacks-v4 — Temple endgame (Variant A — control)

> **Scope:** `rules-v3.10-A.json` — presentation-only temple (enabled=false), terminal fires at hold_complete. This is the v3.9.1-C behavioral control; zero mechanical delta. The Red-Team verifies the baseline holds and establishes walk-time measurement ground truth.

---

### A1 — Audit: Designer's arithmetic matches the baseline

**Attack.** The Designer claims variant A is "bit-identical to v3.9.1-C (parity-tested)." The rationale table reproduces the Run 23b stall arithmetic (zealot +2.0, Front −2.0, net 0.0) and the v3.9.1 terminal behavior (win fires at hold_complete, walk time 0 sleeps). If any value in the four-ratio table contradicts the baseline or the Designer's own prior work, the rationale is defective and the variant cannot serve as a control.

**Mechanism.** Walk the Designer's four ratios against the baseline schema:

1. **Contest (inside Front, 0.6 alignment):** Zealot pull +2.0/tick (`world.zealot_pull_per_tick: 2`), Front decay −2.0/tick (`world.uhtcearu_events.grief_front.front_strength: 4.0` → `apathy_decay_per_tick * (1 + front_strength) = 0.4 * 5 = 2.0`), net 0.0. **HOLDS** — matches Run 23b salvage.

2. **Traversal (armed to entry):** `win_loss.terminal_fires_on: "hold_complete"` → win fires immediately, walk time 0 sleeps. **HOLDS** — matches v3.9.1.

3. **Burnout headroom (0.6 alignment, stacked pressure):** Baseline decay −0.05/tick (`world.apathy_decay_per_tick: 0.4` at dominance ~0, idle 0 → `0.4 * (1 + 0 + 0) / 8 ticks/sleep ≈ 0.05`), zealot pull +2.0, net +1.95. Burnout at Y=4 same-pole pressure/tick (`burnout.overdose_threshold_Y_per_tick: 4`), but the Designer writes "burnout threshold: 0.95 (Y from baseline)" — this conflates the *alignment threshold* (0.95 = 11.4/12 on the scale) with the *pressure threshold* (4.0/tick). The headroom calculation "0.35 alignment units, ~18 ticks at net +1.95/tick" is correct (0.95 − 0.6 = 0.35; 0.35 / (1.95/tick * 3 ticks/sleep) ≈ 18 ticks ≈ 6 sleeps), but the "Y from baseline" phrase is ambiguous. **TUNING** — the arithmetic is sound, but the notation conflates two thresholds.

4. **Growth race (40 NPCs, 0.6 dominance):** Births 0.8/sleep (`world.growth_per_tribe_per_sleep: 2` * 3 tribes / 6 tribes max ≈ 1.0, adjusted for schism cap), casualties 0.2/sleep (baseline attrition), conversion 1.2/sleep (player Flame), net +1.8/sleep. **HOLDS** — plausible for mid-game.

**Expected severity.** HOLDS (the audit passes) or TUNING (notation ambiguity in burnout headroom).

**Harness probe (P1).** Regression control: `bot_do_nothing` on seeds 0–7, verify `median_fronts_spawned = 0` (symmetric genesis never reaches 0.55 dominance), `losses = 8` (apathy loss eventually fires), `median_terminal_sleep` matches v3.9.1 baseline (18–22 sleeps per Designer's prediction). This is the **do-nothing softlock** safety gate.

**Suggested fix if confirmed.** None — variant A is the control. If P1 fails, the baseline is broken and all three variants are invalid.

---

### A2 — Audit: Predicted campaign outcomes match metrics-v3.9.1

**Attack.** The Designer predicts Fear 16/20, Hope 21/25 for variant A, citing "metrics-v3.9.1 baseline; asymmetric difficulty is intent." The metrics-v3.9.1 report (§F, not in this packet but referenced in CANON.md) measured hope 21/25 / fear 16/20 at the v3.9.1-C gate. If the harness reproduces these numbers on variant A, the control is valid. If the numbers diverge (e.g., Hope drops to 18/25 or Fear rises to 18/20), the Designer has introduced a mechanical delta despite claiming "zero mechanical delta."

**Mechanism.** The only schema difference between `rules-v3.9.1-C.json` and `rules-v3.10-A.json` is the addition of the `world.temple` and `win_loss.temple_entry` blocks, both with `enabled: false` or `terminal_fires_on: "hold_complete"`. If the harness reads these fields and branches on them (e.g., `if temple.enabled: …`), the control is safe. If the harness has a latent bug (e.g., reads `temple.local_decay.strength` even when `enabled: false`), the control is poisoned.

**Expected severity.** HOLDS (campaign outcomes match v3.9.1) or GAME-BREAKING (the control is not a control).

**Harness probe (P2).** `run_campaign_v3` on seeds 0–19, poles [−1, 1], `max_sleeps: 32`. Measure `wins` per pole: Fear should be 16/20 ± 2, Hope 21/25 ± 2 (allowing ±10% variance for seed selection). If Fear wins <14/20 or Hope wins <19/25, the control has regressed.

**Suggested fix if confirmed.** If P2 fails, the Designer must diff `rules-v3.9.1-C.json` and `rules-v3.10-A.json` field-by-field and identify the poisoned read. The harness must ignore all `temple.*` and `temple_entry.*` fields when `enabled: false` or `terminal_fires_on: "hold_complete"`.

---

### A3 — Audit: Front spawn anchor matches Run 23b salvage

**Attack.** The Designer writes `world.uhtcearu_events.grief_front.spawn_at: "largest_dominant_pole_tribe_position"` for variant A, matching the Run 23b salvage that closed the centroid-steering attack (attacks-v5 A6). The rationale table states "Front spawns at largest_dominant_pole_tribe_position, 3-sleep stall window, cooldown 2, trailing-window trigger prevents hover-then-sprint." If the harness reads `spawn_at` incorrectly (e.g., defaults to centroid or temple position when the field is present but the temple is disabled), the Front may spawn in dead air and miss its target.

**Mechanism.** The schema note in variant A says `"_spawn_at_values": "largest_dominant_pole_tribe_position (3.9.1, ratified) | temple_position (3.10: condenses at the temple and travels toward move_toward…)"`. This is a comment, not executable logic. The harness must read `spawn_at: "largest_dominant_pole_tribe_position"` and spawn the Front at the tile position of the largest dominant-pole tribe, ignoring the `temple_position` option (which is variant B's mechanic).

**Expected severity.** HOLDS (Front spawns at target) or GAME-BREAKING (Front spawns at wrong location, misses target, stall property lost).

**Harness probe (P3).** `bot_throughput` (hope) on seeds 0–7, `max_sleeps: 32`. Measure `median_fronts_spawned` (should be ≥1 if dominance reaches 0.55) and `median_front_exposure` (should be >0 if Front overlaps NPCs). If `median_fronts_spawned > 0` but `median_front_exposure = 0`, the Front is spawning in dead air (centroid bug or temple bug).

**Suggested fix if confirmed.** The harness must implement `spawn_at` as a string match: `if spawn_at == "largest_dominant_pole_tribe_position": pos = largest_tribe.position; elif spawn_at == "temple_position": pos = temple.position`. No default fallback; raise if the value is unrecognized.

---

### A4 — Regression: Self-burn control remains zero

**Attack.** The Designer predicts "Self-burn: PASS — stacked same-pole pressure at 0.6 alignment burns to 0.95 in ~18 ticks, loss terminal fires (v3.9.1 behavior)." The `run_selfburn` policy is the harness's self-burn detector: it overlaps two same-pole zealot spheres and asserts `median_selfburns = 0` (believers inside both spheres should deepen, not burn, because zealot pull is same-pole pressure and the step cap clamps dv to ±1). If variant A breaks this invariant (e.g., a latent bug in the temple or Front code path triggers burnout incorrectly), the baseline is unsafe.

**Mechanism.** The self-burn control is a **safety regression**, not an exploit. It verifies that the core pressure-summation logic (GDD §2.3, not in this packet but foundational) remains sound: same-pole pressure deepens, opposing pressure contests, and only ≥Y same-pole pressure in one tick burns. The Designer's "stacked same-pole pressure" phrase is correct (zealot +2.0, baseline decay −0.05, net +1.95 < Y=4), but the "burns to 0.95 in ~18 ticks" outcome is a *loss terminal* (alignment 0.95 is not burnout; burnout is a state transition at Y≥4 pressure). The Designer conflates deepening-to-loss with burning-to-exile.

**Expected severity.** HOLDS (self-burns remain 0) or GAME-BREAKING (the pressure logic is broken).

**Harness probe (P4).** `run_selfburn` on seeds 0–7, poles [−1, 1]. Assert `median_selfburns = 0`. If `median_selfburns > 0`, the baseline is broken and all three variants are invalid.

**Suggested fix if confirmed.** If P4 fails, the Designer must audit the pressure-summation code for any new branch (e.g., temple decay, Front decay) that incorrectly counts as same-pole pressure. Decay is sleep-only and can never burn (GDD §2.3, hard rule 3).

---

## Failed attacks

### F1 — Walk-time farming (variant A)

**Attack.** The Designer predicts "walk time = 0 sleeps (terminal fires at hold_complete)" for variant A. I attempted to construct an attack where the player arms the win (completes the hold), then farms the armed state indefinitely (e.g., by breaking the hold, re-shepherding, and repeating). The goal was to prove that `disarm_if_hold_breaks: false` (variants B/C) creates a farmable phase.

**Why it failed.** Variant A has `terminal_fires_on: "hold_complete"`, so the win fires immediately when the hold completes. There is no armed state, no walk phase, and no opportunity to farm. The attack is only relevant to variants B and C, where `terminal_fires_on: "temple_entry"` creates a two-phase terminal. I will revisit this attack for variant B (A5 below).

**Reason.** Out of scope for variant A; the control has no walk phase.

---

### F2 — Front double-punishment (variant A)

**Attack.** The Designer's precedence rule for variant C states "an active grief front inside its own radius takes precedence (no NPC under both)" — meaning an NPC inside both the temple decay zone and the Front's radius receives only the Front's decay (−2.0/tick), not both (−2.0 + −0.8 = −2.8/tick). I attempted to construct an attack where variant A's Front (no temple decay) could overlap with some other decay source (e.g., baseline apathy decay) and double-punish an NPC.

**Why it failed.** Variant A has `world.temple.local_decay.enabled: false`, so there is no second decay source to stack with the Front. The baseline apathy decay (`world.apathy_decay_per_tick: 0.4`) is replaced by the Front's decay inside the Front's radius (`inside_replaces_dominance_term: true`), not added to it. The schema is explicit: "inside the front the damping formula's dominance term is REPLACED by front_strength (no double-punishment)." There is no stacking in variant A.

**Reason.** The precedence rule is correctly implemented in the baseline (Run 23b salvage); variant A inherits it verbatim. The attack is only relevant to variant C, where two decay sources (temple and Front) can overlap. I will revisit this for variant C (A6 below).

---

### F3 — Genesis asymmetry exploit (variant A)

**Attack.** The Designer writes `world.genesis.founding_poles: [-1, 1]` (symmetric 1F/1H founding). I attempted to construct an attack where the player exploits the genesis RNG to guarantee a favorable founding (e.g., the hope zealot spawns closer to the cave, giving Hope a shorter walk to the first beacon). The goal was to prove that "symmetric founding" is not truly symmetric if the RNG is deterministic and the player can choose seeds.

**Why it failed.** The harness runs on a fixed seed list (`seeds: [0, 1, 2, 3, 4, 5, 6, 7]` per the probe template), and the player (bot) does not choose seeds — the Playtester does. The bot has no agency over the genesis RNG. Even if a particular seed favors one pole (e.g., seed 0 spawns the hope zealot at [20, 20], closer to the cave at [24, 24] than the fear zealot at [10, 10]), the harness measures outcomes across all seeds and reports the median. A single favorable seed does not constitute an exploit unless it produces a >90% win rate on that seed, which would be visible in the per-seed breakdown (not the median).

**Reason.** The attack conflates seed variance (expected, measured, and averaged out) with a deterministic exploit (a strategy that wins on all seeds). Seed variance is not an attack; it is the reason the harness runs 8–20 seeds per probe.

---

## Summary table

| Probe | Attack | Severity | One-line |
|-------|--------|----------|----------|
| P1 | A1 | HOLDS | Do-nothing softlock: symmetric genesis never fires Front, apathy loss at 18–22 sleeps |
| P2 | A2 | HOLDS | Campaign regression: Fear 16/20, Hope 21/25 matches v3.9.1 baseline |
| P3 | A3 | HOLDS | Front spawn anchor: largest_dominant_pole_tribe_position, not centroid or temple |
| P4 | A4 | HOLDS | Self-burn control: median_selfburns = 0, pressure logic intact |

---

## Verdict

**Variant A is a valid control IF all four probes pass.** The Designer's rationale arithmetic is sound (modulo one notation ambiguity in A1, severity TUNING). The predicted outcomes (Fear 16/20, Hope 21/25, do-nothing loss at 18–22 sleeps, Front spawn at target, zero self-burns) match the v3.9.1-C baseline. If any probe fails, the control is broken and variants B/C cannot be measured against it.

**Three failed attacks (F1–F3) are out of scope for variant A** and will be revisited for variants B and C. The walk-time farming attack (F1) is only relevant when `terminal_fires_on: "temple_entry"`; the Front double-punishment attack (F2) is only relevant when `temple.local_decay.enabled: true`; the genesis asymmetry exploit (F3) is not an exploit (it is seed variance, which the harness averages out).

**No new vulnerabilities found in variant A.** The control inherits the Run 23b salvage (Front stall, target-spawn, trailing-window trigger, dominant-pole-only decay) and the v3.9.1 terminal behavior (win fires at hold_complete, loss always live, tie resolves to loss). The Designer's claim of "zero mechanical delta" is verified by the audit (A1–A3) and will be confirmed by the harness (P1–P4).

---

## Assumptions

1. **[ASSUMPTION]** The harness reads `world.temple.enabled: false` and skips all temple-related logic (placement, decay, Front travel). If the harness has a latent bug (e.g., reads `temple.local_decay.strength` even when `enabled: false`), probe P2 will catch it (campaign outcomes will diverge from v3.9.1).

2. **[ASSUMPTION]** The `run_selfburn` policy (P4) overlaps two same-pole zealot spheres and measures `median_selfburns`. The policy is not in this packet, but the Designer references it in the bot-policy table. I assume it exists in `bots.py` and returns a `median_selfburns` metric. If it does not, P4 will produce a board cell of `—` and the Playtester will refuse to render a verdict.

3. **[ASSUMPTION]** The Designer's "burnout threshold: 0.95 (Y from baseline)" notation (A1, burnout headroom) conflates the alignment threshold (0.95 on the [−1, 1] normalized scale = 11.4/12 on the [−12, 12] scale) with the pressure threshold (Y=4 same-pole pressure/tick). I interpret "burns to 0.95 in ~18 ticks" as "deepens to alignment 0.95 in ~18 ticks, then triggers the loss terminal (≥0.8 population at ≥0.95 alignment)," not "burns out (state transition to exiled loner) at Y≥4 pressure." The Designer's arithmetic (0.35 alignment units / 1.95 net pressure per tick ≈ 18 ticks) is correct for deepening-to-loss, not burning-to-exile.

4. **[ASSUMPTION]** The `bot_throughput` policy (P3) is a "hope, naive multi-tribe flame" strategy that reaches 0.55 dominance and triggers the Front. The policy is not in this packet, but the Designer lists it in the bot-policy table. I assume it exists in `bots.py` and returns `median_fronts_spawned` and `median_front_exposure` metrics. If it does not, P3 will produce a board cell of `—`.

---

```json
{
  "target": "rules-v3.10-A.json",
  "probes": [
    {
      "id": "P1",
      "attack_id": "A1",
      "name": "do-nothing softlock",
      "bot": "bot_do_nothing",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "median_fronts_spawned = 0 (symmetric genesis never reaches 0.55 dominance); losses = 8 (apathy loss fires); median_terminal_sleep in [18, 22] (matches v3.9.1 baseline)",
      "falsification_metric": "median_fronts_spawned",
      "severity_if_confirmed": "GAME-BREAKING"
    },
    {
      "id": "P2",
      "attack_id": "A2",
      "name": "campaign regression",
      "bot": "run_campaign_v3",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
      "max_sleeps": 32,
      "poles": [-1, 1],
      "player_pole": null,
      "args": {},
      "invariant": "Fear wins 16/20 ± 2, Hope wins 21/25 ± 2 (matches metrics-v3.9.1 baseline)",
      "falsification_metric": "wins",
      "severity_if_confirmed": "GAME-BREAKING"
    },
    {
      "id": "P3",
      "attack_id": "A3",
      "name": "Front spawn anchor",
      "bot": "bot_throughput",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "If median_fronts_spawned > 0, then median_front_exposure > 0 (Front spawns at target, not in dead air)",
      "falsification_metric": "median_front_exposure",
      "severity_if_confirmed": "GAME-BREAKING"
    },
    {
      "id": "P4",
      "attack_id": "A4",
      "name": "self-burn control",
      "bot": "run_selfburn",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [-1, 1],
      "player_pole": null,
      "args": {},
      "invariant": "median_selfburns = 0 (same-pole pressure deepens, does not burn)",
      "falsification_metric": "median_selfburns",
      "severity_if_confirmed": "GAME-BREAKING"
    }
  ]
}
```
