# Variant rationale table

## Hypotheses

**Variant A:** Longer cooldown (3 sleeps) buys legibility through clearer on/off rhythm without reducing total wear — lower duty cycle (~0.50 vs ~0.65) makes each front arrival more attributable while preserving late-game pressure.

**Variant B:** Shorter duration (2 sleeps) with unchanged cooldown reduces straggler wear by ~17% (5 ticks → 6 ticks to grey an unheld v=5 NPC) through lower cumulative exposure while keeping the stall identity intact.

**Variant C:** Reduced radius (5 tiles) with longer cooldown (3 sleeps) creates sharper camp/loner distinction — tighter stall zone forces closer shepherding while lower duty cycle gives stragglers more breathing room between fronts.

## Parameter changes

| Parameter | §/§6 ref | Baseline | A | B | C | Reasoning |
|-----------|----------|----------|---|---|---|-----------|
| `cooldown_sleeps_after_expiry` | §6 Q2 | 2 | 3 | 2 | 3 | Cooldown is the only dial that changes duty cycle without touching in-sphere stall or per-tick wear rate |
| `duration_sleeps` | §6 Q1 | 3 | 3 | 2 | 3 | Duration directly controls cumulative exposure; 2-sleep reduces total wear by 33% per front cycle |
| `radius_tiles` | §6 Q1 | 6 | 6 | 6 | 5 | Radius defines the shepherding requirement; smaller = tighter camps, more exposed stragglers |

## Arithmetic blocks

### Variant A (cooldown 3, duration 3, radius 6)

**Contest** (player pressure vs zealot pull vs decay):
- In-sphere: zealot pull 2.0/tick = front decay 2.0/tick → net 0.000/sleep (stall preserved)
- Out-of-sphere straggler at v=5: decay 0.4/tick base × (1 + 4.0) = 2.0/tick → saturates step cap at −1/tick → 5 ticks to grey (unchanged from baseline)
- Duty cycle: 3-on / 3-off = 0.50 uptime (vs baseline 0.65)

**Traversal** (stamina budget vs map distance):
- Front moves 1 tile/sleep × 3 sleeps = 3 tiles per cycle
- Cooldown 3 gives 3 sleeps to reposition before next spawn
- Unchanged from baseline in per-cycle terms; lower frequency reduces total repositioning pressure

**Burnout headroom** (stacked same-pole pressure vs Y):
- Unchanged — front affects only dominant pole, no burnout interaction

**Growth race** (births vs casualties vs conversion):
- Lower duty cycle (0.50 vs 0.65) reduces late-game straggler attrition by ~23% (fewer front-ticks per 100 sleeps)
- Trigger threshold 0.55 unchanged — still fires at same dominance point
- Trailing window 3 unchanged — no hover-sprint re-opening

### Variant B (cooldown 2, duration 2, radius 6)

**Contest** (player pressure vs zealot pull vs decay):
- In-sphere: zealot pull 2.0/tick = front decay 2.0/tick → net 0.000/sleep (stall preserved)
- Out-of-sphere straggler at v=5: 2 sleeps × 2.0/tick = 4.0 total wear per front (vs 6.0 at duration 3) → ~6 ticks to grey (vs 5 at baseline)
- Duty cycle: 2-on / 2-off = 0.50 uptime (vs baseline 0.65)

**Traversal** (stamina budget vs map distance):
- Front moves 1 tile/sleep × 2 sleeps = 2 tiles per cycle (vs 3 at baseline)
- Shorter duration reduces total front displacement, easier to stay ahead

**Burnout headroom** (stacked same-pole pressure vs Y):
- Unchanged — front affects only dominant pole, no burnout interaction

**Growth race** (births vs casualties vs conversion):
- Reduced cumulative wear per cycle: 2 sleeps × 2.0/tick = 4.0 total (vs 6.0 baseline) → 33% less wear per front
- Combined with lower duty cycle (0.50 vs 0.65): total late-game straggler attrition reduced by ~50%
- Trigger threshold 0.55 unchanged — still fires at same dominance point
- Trailing window 3 unchanged — no hover-sprint re-opening

### Variant C (cooldown 3, duration 3, radius 5)

**Contest** (player pressure vs zealot pull vs decay):
- In-sphere: zealot pull 2.0/tick = front decay 2.0/tick → net 0.000/sleep (stall preserved)
- Smaller radius (5 vs 6) means fewer NPCs covered per front — more stragglers exposed
- Out-of-sphere straggler at v=5: decay 2.0/tick → saturates step cap at −1/tick → 5 ticks to grey (unchanged rate)
- Duty cycle: 3-on / 3-off = 0.50 uptime → fewer total front-ticks, but tighter coverage requirement

**Traversal** (stamina budget vs map distance):
- Smaller radius requires tighter clustering to keep NPCs in-sphere
- Front moves 1 tile/sleep × 3 sleeps = 3 tiles per cycle
- Cooldown 3 gives 3 sleeps to reposition

**Burnout headroom** (stacked same-pole pressure vs Y):
- Unchanged — front affects only dominant pole, no burnout interaction

**Growth race** (births vs casualties vs conversion):
- Smaller radius increases shepherding difficulty — more NPCs fall outside protection
- Lower duty cycle (0.50 vs 0.65) reduces total front exposure by ~23%
- Net effect: sharper camp/loner distinction — tight camps stall, loose formations grey faster
- Trigger threshold 0.55 unchanged — still fires at same dominance point
- Trailing window 3 unchanged — no hover-sprint re-opening

---

# Variant A — Longer cooldown for legibility


_(variant JSON emitted to its own file)_


# Variant B — Shorter duration reduces cumulative wear


_(variant JSON emitted to its own file)_


# Variant C — Tighter radius with longer cooldown


_(variant JSON emitted to its own file)_


---

# Expected-shape notes

## Variant A — Longer cooldown for legibility

- **Predicted run length:** 35–45 sleeps (unchanged from baseline; lower duty cycle does not extend game length, only changes rhythm)
- **Do-nothing softlock:** PASS — genesis still forms, terminal grace still lifts, front still triggers at 0.55 dominance
- **Tyrant burst:** PASS — front spawn anchor unchanged (largest dominant tribe), no hover-sprint re-opening
- **Campaign (Hope/Fear):** Hope 20–22/25 (−1 to −2 from baseline 21/25 due to lower late-game pressure), Fear 15–17/20 (−1 from baseline 16/20, same reason)
- **Frontal siege:** PASS — trailing window 3 unchanged, no GF5 re-opening; spawn anchor unchanged, no GF6 re-opening
- **Self-burn:** PASS — affects_dominant_pole_only unchanged, no cleanup-assist re-opening
- **Red-Team vulnerability:** **Rumour antagonist** — 0.50 duty cycle (3-on/3-off) risks front feeling absent in short games or low-dominance runs; if player never crosses 0.55 or crosses briefly, front may fire 0–2 times total
- **Playtester measurement:** (1) Count front spawns per game; (2) measure player-reported "I knew the fog was coming" vs "the fog surprised me"; (3) compare straggler grey-rate to baseline (should be unchanged at ~5 ticks for unheld v=5 NPC)

## Variant B — Shorter duration reduces cumulative wear

- **Predicted run length:** 35–45 sleeps (unchanged from baseline)
- **Do-nothing softlock:** PASS — genesis still forms, terminal grace still lifts, front still triggers at 0.55 dominance
- **Tyrant burst:** PASS — front spawn anchor unchanged (largest dominant tribe), no hover-sprint re-opening
- **Campaign (Hope/Fear):** Hope 22–24/25 (+1 to +3 from baseline 21/25 due to reduced straggler attrition), Fear 17–19/20 (+1 to +3 from baseline 16/20, same reason)
- **Frontal siege:** PASS — trailing window 3 unchanged, no GF5 re-opening; spawn anchor unchanged, no GF6 re-opening
- **Self-burn:** PASS — affects_dominant_pole_only unchanged, no cleanup-assist re-opening
- **Red-Team vulnerability:** **Toothless antagonist** — 33% less wear per front cycle + 0.50 duty cycle = ~50% total reduction in late-game straggler pressure; front may feel like a visual effect rather than a threat
- **Playtester measurement:** (1) Measure straggler grey-rate (should be ~6 ticks for unheld v=5 NPC, vs 5 at baseline); (2) count late-game grey conversions (should drop ~50%); (3) player-reported "the fog hurt" vs "the fog was ignorable"

## Variant C — Tighter radius with longer cooldown

- **Predicted run length:** 35–45 sleeps (unchanged from baseline)
- **Do-nothing softlock:** PASS — genesis still forms, terminal grace still lifts, front still triggers at 0.55 dominance
- **Tyrant burst:** PASS — front spawn anchor unchanged (largest dominant tribe), no hover-sprint re-opening
- **Campaign (Hope/Fear):** Hope 20–22/25 (−1 to −2 from baseline 21/25; tighter radius increases shepherding difficulty, offsetting lower duty cycle), Fear 15–17/20 (−1 from baseline 16/20, same reason)
- **Frontal siege:** PASS — trailing window 3 unchanged, no GF5 re-opening; spawn anchor unchanged, no GF6 re-opening
- **Self-burn:** PASS — affects_dominant_pole_only unchanged, no cleanup-assist re-opening
- **Red-Team vulnerability:** **Micro-tax** — radius 5 (vs 6 baseline) requires tighter clustering; player must position more precisely to keep NPCs in-sphere, increasing APM demand and punishing loose formations
- **Playtester measurement:** (1) Measure average NPC distance from player during fronts (should be lower than baseline); (2) count NPCs greyed while player is within 6 tiles of tribe center (should be higher than baseline, indicating radius matters); (3) player-reported "I had to bunch up" vs "I could spread out"

---

# Canon friction

None. All three variants preserve:
- Grief canon (CANON ruling 6): front wears dominant pole only, never recruits for opposite
- In-sphere stall identity: front_strength 4.0 → inside-front decay 2.0/tick = zealot pull 2.0/tick
- Run 23b closures: spawn anchor (largest dominant tribe position), trailing window (no hover-sprint), affects_dominant_pole_only (no cleanup-assist)
- Zealot immunity
- Legacy equivalence when `enabled: false` (no changes to non-front systems)

---

# Assumptions

[ASSUMPTION] **The step cap (−1/tick maximum NPC movement) is a locked substrate parameter** — it appears in no `rules-*.json` file and is implemented as a sim constant. Treating it as immovable; if it is tunable, that opens a different design space than the one this packet assumes.

[ASSUMPTION] **"Straggler wear below step-cap saturation" means reducing the effective decay rate experienced by unshepherded NPCs to < 1.0/tick** — i.e., an unheld NPC at v=5 takes > 5 ticks to grey, vs. the current exactly-5-tick measured behavior. Variant B achieves this through reduced cumulative exposure (2 sleeps × 2.0/tick = 4.0 total wear per front, vs 3 sleeps × 2.0/tick = 6.0 at baseline), not through per-tick rate reduction.

[ASSUMPTION] **"Legibility" in question 2 refers to player perception of the front as a recurring, attributable antagonist** — i.e., a longer cooldown trades lower uptime for clearer on/off rhythm, making each front arrival more noticeable rather than blending into continuous pressure. Variant A tests this at cooldown 3 (0.50 duty cycle vs baseline 0.65).

[ASSUMPTION] **The dominance term in `uhtcearu_damping_formula` is the same player-pole fraction the live damping formula reads** (CANON v17 meta note on v3.9), and `outside_dominance_scale` (not present in baseline) would multiply that term for NPCs outside the front radius while inside-front NPCs have dominance replaced entirely per `inside_replaces_dominance_with_strength: true`. Since no variant proposes adding `outside_dominance_scale`, this assumption does not affect the submitted designs.

[ASSUMPTION] **Front movement (`move_tiles_per_sleep: 1`) is locked** — no question in the Director's set opens it, and changing it would alter the traversal arithmetic in ways orthogonal to the straggler-wear / legibility trade space this run explores.

[ASSUMPTION] **The 96% "fronts do real work" metric (metrics-v3.9.1 §F) measures fronts that spawn at dominance ≥ 0.55** — i.e., the trailing-window trigger is functioning as intended. None of the proposed changes touch `trigger_dominance_min` or `trigger_trailing_window_sleeps`, so this metric should remain stable across all variants.
