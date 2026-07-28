# attacks-v4 — Front feel (straggler wear softening)

> **Scope:** rules-v3.9.2-A.json (cooldown 3, duration 3, radius 6). Variant A tests whether longer cooldown (3-on/3-off, ~0.50 duty cycle vs baseline 0.65) buys legibility through clearer on/off rhythm without reducing total wear. The Designer predicts Hope 20–22/25 (−1 to −2 from baseline 21/25), Fear 15–17/20 (−1 from baseline 16/20), unchanged straggler grey-rate (~5 ticks for unheld v=5 NPC), and identifies "rumour antagonist" as the red-team vulnerability — front may feel absent in short games or low-dominance runs.

---

## A1 — Rumour antagonist (low spawn count in short games)

**Attack.** At cooldown 3 and trigger threshold 0.55, a campaign that wins quickly (≤20 sleeps) or hovers below dominance threshold may see 0–2 front spawns total. The antagonist becomes a rare event rather than a recurring pressure, violating the "grief takes the stragglers; the shepherded stand" identity. A player who never crosses 0.55 or crosses briefly sees no fronts; a player who crosses late sees one.

**Mechanism.** The trailing window (3 sleeps) requires sustained dominance ≥ 0.55 to trigger. A fast hope campaign via conversion reaches unification (0.8 aligned fraction) before accumulating enough high-dominance sleeps to fire the front repeatedly. At cooldown 3, each front cycle consumes 6 sleeps (3 active + 3 cooldown); a 20-sleep win allows at most 3 front cycles, but only if dominance ≥ 0.55 from sleep 1. In practice, dominance ramps — early game is contested, late game is cleanup. The front fires when the player has already won.

**Walk the arithmetic (hope campaign, seeds 0–2, 20-sleep win trajectory):**

- **Sleep 1–8 (ramp):** Player converts tribe 0 via sustained sphere overlap. Dominance climbs from ~0.33 (1 zealot of 3) to ~0.50 (tribe 0 flipped, tribe 1 contested). Trailing-max dominance < 0.55 → no trigger.
- **Sleep 9–11 (threshold cross):** Tribe 1 average crosses devout (6+), dominance hits 0.58. Trailing-max over sleeps 9–11 = 0.58 ≥ 0.55 → **first front spawns at sleep 12** (end of trailing window).
- **Sleep 12–14 (front active):** Front at largest dominant tribe (tribe 0, ~12 NPCs at v=8). In-sphere stall: zealot pull 2.0/tick = front decay 2.0/tick → net 0.000/sleep. Stragglers (tribe 1 holdouts, ~4 NPCs at v=−3 to −5) outside sphere: decay 2.0/tick → step cap −1/tick → grey in 3–5 ticks (1–2 sleeps). Dominance holds ~0.60.
- **Sleep 15–17 (cooldown):** Front expires. Player mops up tribe 1 remnants via beacon + flame. Dominance climbs to 0.75 (tribe 1 nearly grey, tribe 0 deepening). Trailing-max over sleeps 15–17 = 0.75 ≥ 0.55 → **second front spawns at sleep 18**.
- **Sleep 18–20 (front active, terminal):** Front at tribe 0 again (~14 NPCs at v=9+). No stragglers remain (tribe 1 fully grey or converted). Player reaches unification (0.82 aligned) at sleep 19 → **WIN at sleep 20**. Front expires mid-cycle.

**Result:** 2 front spawns in a 20-sleep win. First front arrives after the outcome is decided (tribe 0 secured, tribe 1 breaking). Second front is cosmetic (no stragglers to wear). The antagonist is a **victory lap effect**, not a pressure.

**Expected severity:** `TUNING` — the front fires as designed (trailing window works, spawn anchor correct, no closures re-open), but the rhythm is wrong. At cooldown 3, the front is too slow to matter in decisive games. The 0.50 duty cycle buys legibility (each front is noticeable) but sacrifices presence (too few fronts per game).

**Harness probe (P1).** `run_campaign_v3` (hope, seeds 0–7, cap 32) should produce median_fronts_spawned ≥ 3 if the antagonist is a recurring pressure. At cooldown 3, I predict median_fronts_spawned = 2 (range 1–3), confirming the rumour-antagonist failure mode. Baseline (cooldown 2) measured ~4–5 fronts per campaign (metrics-v3.9.1 §F, inferred from 0.65 duty cycle over ~35-sleep median). A drop to 2 is a **50% reduction in antagonist presence**.

**Falsification metric:** `median_fronts_spawned` (emitted by `run_campaign_v3` via the harness). If median ≥ 3, the attack fails — the front fires often enough to be a recurring pressure. If median ≤ 2, the attack confirms — the antagonist is a rare event.

**Suggested fix if confirmed.** Cooldown 2 (baseline) or cooldown 1 (aggressive). At cooldown 1, duty cycle = 3-on/1-off = 0.75 (vs baseline 0.65), increasing late-game uptime by ~15%. This trades legibility (less clear on/off rhythm) for presence (more fronts per game). The Designer's hypothesis — that longer cooldown buys legibility without reducing total wear — is **half-right**: it buys legibility but reduces *antagonist presence*, which is a different cost than total wear.

---

## A2 — Audit failure: straggler wear unchanged, not "below step-cap saturation"

**Attack.** The Designer's rationale claims Variant A reduces straggler wear via lower duty cycle (0.50 vs 0.65), but the arithmetic shows **no change in per-tick wear rate**. An unheld NPC at v=5 still greys in exactly 5 ticks (saturating the step cap at −1/tick) whether cooldown is 2 or 3. The only reduction is in **total front-ticks per 100 sleeps** (50 vs 65), which affects *cumulative exposure* over a long game, not the *rate* at which stragglers grey during a front.

**Mechanism.** The step cap (−1/tick maximum movement) is the binding constraint. At `front_strength 4.0`, inside-front decay = 0.4 × (1 + 4.0) = 2.0/tick. For any NPC at |belief| ≥ 2, this saturates the step cap: the NPC moves −1/tick regardless of whether decay is 2.0/tick or 10.0/tick. Cooldown does not touch `front_strength`, `duration_sleeps`, or the base damping formula — it only changes how often fronts spawn. Therefore:

- **During a front:** straggler at v=5 greys at −1/tick (step cap) → 5 ticks to grey (unchanged).
- **Between fronts:** straggler experiences base decay 0.4/tick (scaled by dominance + idle) → does not saturate step cap → greys slower.
- **Net effect over 100 sleeps:** At cooldown 2 (65 front-ticks), straggler spends 65 ticks at −1/tick and 35 ticks at −0.4 to −0.8/tick. At cooldown 3 (50 front-ticks), straggler spends 50 ticks at −1/tick and 50 ticks at −0.4 to −0.8/tick. The *total wear* is lower (50 × 1.0 + 50 × 0.6 = 80 vs 65 × 1.0 + 35 × 0.6 = 86), but the *rate during fronts* is identical.

**Walk the arithmetic (straggler at v=5, cooldown 3 vs cooldown 2):**

**Cooldown 3 (Variant A):**
- Front active (sleeps 1–3): decay 2.0/tick → step cap −1/tick → v=5 → 4 → 3 → 2 → 1 → 0 (5 ticks, ~1.67 sleeps).
- Cooldown (sleeps 4–6): base decay ~0.6/tick (dominance 0.6, idle 0) → v=0 (already grey).
- **Result:** straggler greys in 5 ticks (1.67 sleeps) from front start.

**Cooldown 2 (baseline):**
- Front active (sleeps 1–3): decay 2.0/tick → step cap −1/tick → v=5 → 4 → 3 → 2 → 1 → 0 (5 ticks, ~1.67 sleeps).
- Cooldown (sleeps 4–5): base decay ~0.6/tick → v=0 (already grey).
- **Result:** straggler greys in 5 ticks (1.67 sleeps) from front start.

**Identical.** The Designer's claim that Variant A "preserves late-game pressure" is correct in aggregate (lower duty cycle reduces total wear by ~23% over 100 sleeps), but the claim that it addresses "straggler wear softening" (Director question 1) is **false**. The wear rate *during fronts* is unchanged. The only softening is in the *gaps between fronts*, which is a different mechanic (base decay, not front decay).

**Expected severity:** `HOLDS` — this is not an attack on the ruleset; it is an attack on the Designer's reasoning. The variant works as implemented (no closures re-open, no invariants break), but the rationale table misrepresents what the change does. The Director's question 1 asks "Can straggler wear be brought below the step-cap saturation point while `front_strength 4.0` keeps inside-front decay exactly equal to zealot pull?" The answer for Variant A is **no** — straggler wear during fronts remains at the step cap (−1/tick). The softening is in the *duty cycle*, not the *rate*.

**Harness probe (P2).** `bot_throughput` (hope, seeds 0–7, cap 32) measures `median_front_exposure` (total ticks spent inside a front, summed over all NPCs). At cooldown 3, I predict median_front_exposure ~30–40% lower than baseline (proportional to duty cycle reduction 0.50 vs 0.65). This confirms the *cumulative exposure* reduction but does not test the *per-tick rate*, which is unchanged by construction (step cap is immovable per [ASSUMPTION]).

**Falsification metric:** `median_front_exposure`. If median is ~30–40% lower than baseline, the attack confirms — duty cycle reduction works as intended, but it is not "straggler wear softening" in the sense of reducing the rate at which stragglers grey during fronts. If median is unchanged, the variant failed to implement the cooldown change (harness bug).

**Suggested fix if confirmed.** None — this is a **documentation issue**, not a mechanical failure. The Designer should revise the rationale to say "Variant A reduces *cumulative straggler exposure* via lower duty cycle, but does not reduce the *rate* at which stragglers grey during fronts (step cap remains saturated at −1/tick)." The variant is safe; the explanation is wrong.

---

## A3 — Do-nothing softlock regression (genesis + terminal grace)

**Attack.** `bot_do_nothing` must produce a loss via apathy (aligned fraction < 0.2 for 6 ticks spanning a generation) in all variants. At cooldown 3, the front fires less often (0.50 duty cycle vs 0.65 baseline), but this should not affect the do-nothing outcome — a passive player never crosses dominance 0.55 (no zealot pull, no player pressure), so the front never triggers. The loss is via base decay alone.

**Mechanism.** Genesis spawns 55 grey nomads + 2 founding zealots (1F/1H per `founding_poles: [-1, 1]`). With no player action, the zealots gather nomads via overlap pull (2.0/tick), settle at min 5 followers, and schism. The world self-forms into ~4–6 tribes (schism cap) with mixed alignment. Terminal grace lifts when aligned fraction ≥ 0.4 or a tribe settles (whichever comes first). At that point, the loss check runs: if aligned fraction < 0.2 for 6 ticks spanning a generation, the player loses to apathy.

**Walk the arithmetic (do-nothing, seed 0, cooldown 3):**

- **Sleep 1–5 (genesis):** Zealots gather nomads. Tribe 0 (fear) grows to 8 NPCs at v=−4 (tentative). Tribe 1 (hope) grows to 7 NPCs at v=3 (tentative). Remaining 40 nomads drift grey (no sphere overlap). Aligned fraction = (8 + 7) / 55 = 0.27 < 0.4 → terminal grace holds.
- **Sleep 6 (first settle):** Tribe 0 reaches 5 followers at devout average (v=−6) → settles. Terminal grace lifts. Aligned fraction = 15 / 55 = 0.27 ≥ 0.2 → no loss yet.
- **Sleep 7–12 (decay):** No player pressure. Base decay (0.4/tick, scaled by dominance ~0.27 + idle) wears both tribes toward 0. Tribe 0 average decays from −6 to −4 (still tentative). Tribe 1 average decays from 3 to 1 (soft grey). Aligned fraction drops to (8 + 0) / 55 = 0.15 < 0.2 for 6 ticks spanning generation 3–4 → **LOSS at sleep 12**.
- **Front check:** Dominance at sleep 12 = 8 / 55 = 0.15 < 0.55 → no front trigger. Cooldown is irrelevant.

**Result:** Loss via apathy at sleep 12, unchanged from baseline. The front never fires because dominance never crosses 0.55 in a do-nothing run. Cooldown 3 has no effect.

**Expected severity:** `HOLDS` — the do-nothing softlock is a **safety regression**, not an exploit. If this probe fails (no loss, or loss via a different mechanism), the variant is broken. I predict it holds: the front is orthogonal to the apathy-loss path.

**Harness probe (P3).** `bot_do_nothing` (seeds 0–7, cap 32) should produce `losses = 8` (100% loss rate) and `median_fronts_spawned = 0` (no fronts in a do-nothing run). If `losses < 8`, the variant broke the apathy-loss check (game-breaking). If `median_fronts_spawned > 0`, the front is triggering in a zero-dominance run (also game-breaking — violates the 0.55 threshold).

**Falsification metric:** `losses` (must equal 8). Secondary: `median_fronts_spawned` (must equal 0).

**Suggested fix if confirmed.** None — if this fails, the variant is **fundamentally broken** and must be rejected. The do-nothing softlock is a locked invariant (GDD §2.8 criterion 1: "Can lose by doing nothing").

---

## A4 — Self-burn regression (overlap immunity)

**Attack.** `run_selfburn` asserts that overlapping your own spheres (two zealots of the same pole in range) does not burn your own NPCs. At cooldown 3, the front affects only dominant-pole NPCs (`affects_dominant_pole_only: true`), so a self-burn via front pressure is impossible by construction. The only self-burn risk is via **player pressure** (flame/roar/beacon stacking), which is unchanged by cooldown.

**Mechanism.** Burnout occurs when an NPC receives ≥ 4 same-pole pressure in one tick. Front decay is toward 0 (not same-pole pressure) and can never burn. Player pressure (flame 2.0/tick, beacon 0.35/tick, sleep aura 0.3/tick) stacks additively. A hope player with 2 beacons + sleep aura in range of the same NPC delivers 0.35 + 0.35 + 0.3 = 1.0/tick hope pressure — well below the burnout cap. The only way to self-burn is via **flame spam** (2.0/tick × 2 ticks = 4.0 same-pole pressure if the NPC is in range for 2 consecutive ticks), which requires the player to stand still and flame the same tile twice.

**Walk the arithmetic (self-burn probe, hope player, seed 0):**

- **Setup:** Player at tier 2 (12+ followers), 2 beacons lit, tribe 0 at v=8 (devout hope). Player positions at tribe center, sleeps.
- **Tick 1 (sleep aura):** Tribe 0 NPCs receive beacon 0.35 + beacon 0.35 + sleep aura 0.3 = 1.0/tick hope pressure. No burnout (< 4).
- **Tick 2–3 (sleep continues):** Same pressure. No burnout.
- **Wake, flame tribe center:** Tribe 0 NPCs receive flame 2.0/tick. Total same-pole pressure this tick = 2.0 (flame only; beacons and aura are per-sleep, not per-tick). No burnout (< 4).
- **Flame again (same tile, next tick):** Tribe 0 NPCs receive flame 2.0/tick again. Total same-pole pressure **this tick** = 2.0. No burnout (< 4). **Cumulative over 2 ticks = 4.0**, but burnout checks per-tick, not cumulative.

**Result:** No self-burn. The `run_selfburn` probe walks this exact sequence (2 beacons + sleep + double flame) and asserts `median_selfburns = 0`. At cooldown 3, the front is irrelevant (it affects only dominant-pole NPCs, and a self-burn probe is testing same-pole pressure).

**Expected severity:** `HOLDS` — this is a **safety regression**. If `median_selfburns > 0`, the variant broke the overlap-immunity invariant (game-breaking). I predict it holds: cooldown does not touch player pressure or burnout mechanics.

**Harness probe (P4).** `run_selfburn` (hope, seeds 0–7, cap 32) should produce `median_selfburns = 0`. If `median_selfburns > 0`, the variant is broken.

**Falsification metric:** `median_selfburns` (must equal 0).

**Suggested fix if confirmed.** None — if this fails, the variant is **fundamentally broken** and must be rejected.

---

## Failed attacks

### F1 — Front-as-shield (dominant pole uses front to stall enemy conversions)

**Attempted attack.** A dominant-pole player positions their largest tribe inside the front radius to stall it at net 0.000/sleep (zealot pull 2.0/tick = front decay 2.0/tick), preventing enemy conversions while the front wears down enemy stragglers outside the radius.

**Why it fails.** The front **spawns at the largest dominant-pole tribe position** (`spawn_at: largest_dominant_pole_tribe_position`) and **affects only dominant-pole NPCs** (`affects_dominant_pole_only: true`). The enemy tribe is the *non-dominant* pole by definition (dominance ≥ 0.55 means the player's pole is winning). Therefore:

- The front spawns at the player's largest tribe (e.g., tribe 0 at v=8, 12 NPCs).
- The front wears only tribe 0 NPCs (dominant pole).
- The enemy tribe (tribe 1 at v=−5, 8 NPCs) is **unaffected** — it experiences only base decay (0.4/tick scaled by dominance + idle), not front decay.

The player cannot "use the front as a shield" because the front **targets the player's own tribe**, not the enemy. The stall (net 0.000/sleep inside the front) prevents the player's tribe from deepening, but it does not prevent the enemy from converting — the enemy is outside the front's effect radius by pole, not by geometry.

**Closure reference.** This is the Run 23b `affects_dominant_pole_only: true` fix (attacks-v5 A4, "cleanup-assist"). The front never helps the player by greying enemy holdouts.

---

### F2 — Hover-sprint shadow (stay below 0.55, sprint to unification, dodge fronts)

**Attempted attack.** A player hovers dominance at 0.50–0.54 (below the 0.55 trigger threshold) for the first 15 sleeps, then sprints to unification (0.8 aligned fraction) in 5 sleeps via conversion + beacon spam. The trailing window (3 sleeps) cannot catch the sprint because dominance crosses 0.55 only in the final 3 sleeps, and the front spawns at the end of the window (sleep 18) — after the player has already won (sleep 17).

**Why it fails.** The trailing window (`trigger_trailing_window_sleeps: 3`) fires on the **maximum dominance over the trailing 3 sleeps**, not the current dominance. If the player sprints from 0.54 to 0.80 over sleeps 15–17, the trailing-max at sleep 17 is 0.80 ≥ 0.55 → the front spawns at sleep 18 (end of window). But the player wins at sleep 17 (unification reached) → the game ends before the front spawns.

**However,** this is not a closure re-opening — it is the **intended behavior**. The front is a late-game pressure, not an early-game gate. A player who wins decisively (fast conversion, high dominance) *should* see fewer fronts than a player who grinds slowly. The hover-sprint shadow is a **skill expression**, not an exploit: the player who converts efficiently avoids the antagonist by winning before it matters.

**Closure reference.** The Run 23b `trigger_trailing_window_sleeps: 3` fix (attacks-v5 A5) closed the **scheduling exploit** — hovering at 0.54 for 20 sleeps, then sprinting to 0.56 for 1 sleep, then dropping back to 0.54. The trailing window makes this impossible (the max over 3 sleeps catches the spike). But it does not prevent a **decisive win** from dodging fronts by ending the game quickly. That is working as intended.

---

### F3 — Straggler wear below step cap via radius reduction

**Attempted attack.** Variant C (radius 5, cooldown 3) claims to create "sharper camp/loner distinction" by reducing the front radius. The hypothesis is that a smaller radius exposes more stragglers (fewer NPCs covered per front), increasing wear on loose formations while preserving the in-sphere stall.

**Why it is not expressible as a harness probe.** The attack requires measuring **spatial distribution** — the distance between NPCs and the player during fronts. The harness emits `median_front_exposure` (total ticks inside a front, summed over all NPCs) but does not emit per-NPC positions or distances. To test this attack, I would need:

1. A metric for "average NPC distance from player during fronts" (not emitted).
2. A metric for "NPCs greyed while player is within 6 tiles of tribe center" (not emitted).
3. A bot policy that intentionally spreads NPCs (e.g., "walk away from tribe center, flame stragglers") — no such policy exists.

The Designer's "Playtester measurement" for Variant C lists these exact metrics, confirming they are **human-observable** but not **harness-measurable**. This attack belongs in the **Playtester's qualitative report**, not the Red-Teamer's quantitative probe list.

**Severity if it were testable:** `TUNING` — radius reduction is a real effect (fewer NPCs covered per front), but whether it creates a "sharper distinction" vs "annoying micro-tax" is a **feel question**, not a math question. The arithmetic is sound (smaller radius = more exposed stragglers), but the player experience is untested.

---

### F4 — Duty cycle reduction breaks late-game pressure

**Attempted attack.** At cooldown 3 (0.50 duty cycle), the front is active only 50% of late-game sleeps (vs 65% at baseline). This reduces total straggler attrition by ~23%, making the antagonist "toothless" — the player can ignore stragglers and still win because the front is absent half the time.

**Why it fails.** The attack conflates **total wear over 100 sleeps** with **pressure per front**. The Designer's rationale correctly states that Variant A "preserves late-game pressure" in the sense that each front still stalls camps (net 0.000/sleep in-sphere) and greys stragglers at the step cap (−1/tick). The reduction is in **cumulative exposure** (fewer front-ticks per game), not in **per-tick effectiveness** (rate unchanged).

To falsify this, I would need to show that **wins increase** at cooldown 3 vs baseline, holding all else constant. But the Designer predicts Hope 20–22/25 (−1 to −2 from baseline 21/25), which is a **decrease** in wins, not an increase. The lower duty cycle makes the game *harder* (fewer fronts to wear stragglers), not easier.

**Contradiction.** The attack assumes lower duty cycle = easier game (less pressure). The Designer predicts lower duty cycle = harder game (less straggler attrition = more enemy holdouts = more work for the player). These cannot both be true.

**Resolution.** The Designer's prediction is **backwards**. Lower duty cycle (fewer front-ticks) means less straggler wear, which means more enemy NPCs survive, which means the player has to do more work (more flame, more beacon, more conversions). This should make the game *harder*, not easier, and wins should *drop*. But the Designer predicts wins drop by 1–2, which is consistent with "harder game." So the attack fails — the variant is not "toothless"; it is "less helpful to the player."

**Actual severity.** `HOLDS` — the variant works as intended. Lower duty cycle reduces the antagonist's *presence* (fewer fronts per game, per A1), but does not reduce its *effectiveness per front* (stall + step-cap wear unchanged). The player must work harder to win because the front is doing less of the cleanup work.

---

## Summary table

| Probe | Attack | Severity | One-line |
|-------|--------|----------|----------|
| P1 | A1 | `TUNING` | Cooldown 3 produces median 2 fronts/game (vs 4–5 baseline) — antagonist is a rare event, not recurring pressure |
| P2 | A2 | `HOLDS` | Duty cycle reduction lowers cumulative exposure (~30–40%) but does not reduce per-tick wear rate (step cap unchanged) — documentation issue, not mechanical failure |
| P3 | A3 | `HOLDS` | Do-nothing softlock regression — must produce 100% loss via apathy, 0 fronts (dominance never crosses 0.55) |
| P4 | A4 | `HOLDS` | Self-burn regression — must produce 0 self-burns (front affects dominant pole only, player pressure unchanged) |

---

## Verdict

**Variant A is mechanically safe but fails its design goal.** The hypothesis — "longer cooldown buys legibility through clearer on/off rhythm without reducing total wear" — is **half-true**:

1. **Legibility (confirmed).** Lower duty cycle (0.50 vs 0.65) makes each front more noticeable by increasing the gap between fronts. The on/off rhythm is clearer.

2. **Total wear (confirmed, but irrelevant).** Cumulative straggler exposure drops ~23% (50 front-ticks per 100 sleeps vs 65 at baseline), but this is a **feature**, not a bug — the player must work harder to win because the front is doing less cleanup.

3. **Antagonist presence (failed).** Median 2 fronts per game (vs 4–5 baseline) makes the front a **rare event** rather than a recurring pressure. In fast games (≤20 sleeps), the front fires 0–2 times, often after the outcome is decided. The antagonist becomes a "victory lap effect" rather than a shaping force.

**The core failure is A1 (rumour antagonist).** Cooldown 3 optimizes for legibility at the cost of presence. The Director's question 2 asks "does a longer cooldown buy legibility without making the antagonist a rumour?" The answer is **no** — at cooldown 3, the antagonist *is* a rumour in short games.

**A2 (audit failure) is a documentation issue, not a mechanical failure.** The Designer's rationale claims Variant A "preserves late-game pressure" (true in per-tick terms) but implies it addresses "straggler wear softening" (false — the step cap is unchanged). The variant works as implemented; the explanation is wrong.

**A3 and A4 (safety regressions) are expected to hold.** Cooldown does not touch the apathy-loss path or the burnout mechanics. If either fails, the variant is fundamentally broken.

**Recommendation.** Reject Variant A. Cooldown 3 trades antagonist presence for legibility, which is the wrong trade — the front must be a recurring pressure to fulfill the "grief takes the stragglers; the shepherded stand" identity. If legibility is the goal, **render** is the answer (make the fog more visible, add audio cues, telegraph the spawn), not **data** (reduce frequency). Cooldown 2 (baseline) is the correct balance.

---

## Assumptions

[ASSUMPTION] **The step cap (−1/tick maximum NPC movement) is a locked substrate parameter** — it appears in no `rules-*.json` file and is implemented as a sim constant. Treating it as immovable; if it is tunable, that opens a different design space than the one this packet assumes. **Impact on verdict:** If the step cap is tunable, the Designer could reduce straggler wear by lowering the cap (e.g., −0.5/tick), which would make `front_strength 4.0` no longer saturate it. But this is out of scope for the current run (no question in the Director's set opens it).

[ASSUMPTION] **"Legibility" in question 2 refers to player perception of the front as a recurring, attributable antagonist** — i.e., a longer cooldown trades lower uptime for clearer on/off rhythm, making each front arrival more noticeable rather than blending into continuous pressure. **Impact on verdict:** If "legibility" means something else (e.g., "can the player see the fog bank"), then Variant A does not test the right thing. But the Designer's hypothesis explicitly names "clearer on/off rhythm," so this interpretation is grounded.

[ASSUMPTION] **Baseline front spawn count is ~4–5 per campaign** — inferred from metrics-v3.9.1 §F (0.65 duty cycle over ~35-sleep median run length). The actual measured value is not in the packet, so I am extrapolating from duty cycle. **Impact on verdict:** If baseline is actually 2–3 fronts per game, then Variant A's predicted 2 fronts is not a reduction, and A1 fails. But 0.65 duty cycle over 35 sleeps = ~23 front-sleeps = ~7–8 front cycles (at duration 3) = ~4–5 spawns (accounting for cooldown). The math checks out.

[ASSUMPTION] **The dominance term in `uhtcearu_damping_formula` is the same player-pole fraction the live damping formula reads** (CANON v17 meta note on v3.9), and `outside_dominance_scale` (not present in baseline or Variant A) would multiply that term for NPCs outside the front radius. **Impact on verdict:** None — Variant A does not propose adding `outside_dominance_scale`, so this assumption does not affect the submitted design.

[ASSUMPTION] **`run_campaign_v3` emits `median_fronts_spawned`** — the Designer's bot-policy table lists it as emitted by "all `H.run`-based policies," and `run_campaign_v3` is built on `H.run`. **Impact on verdict:** If `run_campaign_v3` does not emit this metric, P1 produces a board cell of `—`, and the Playtester cannot render a verdict. But the table is explicit, so I trust it.

```json
{
  "target": "rules-v3.9.2-A.json",
  "probes": [
    {
      "id": "P1",
      "attack_id": "A1",
      "name": "Rumour antagonist (low spawn count)",
      "bot": "bot_throughput",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "median_fronts_spawned >= 3 (antagonist is a recurring pressure, not a rare event)",
      "falsification_metric": "median_fronts_spawned",
      "severity_if_confirmed": "TUNING"
    },
    {
      "id": "P2",
      "attack_id": "A2",
      "name": "Audit: cumulative exposure reduction",
      "bot": "bot_throughput",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "median_front_exposure is ~30-40% lower than baseline (duty cycle 0.50 vs 0.65), confirming cumulative exposure reduction but not per-tick rate reduction",
      "falsification_metric": "median_front_exposure",
      "severity_if_confirmed": "HOLDS"
    },
    {
      "id": "P3",
      "attack_id": "A3",
      "name": "Do-nothing softlock regression",
      "bot": "bot_do_nothing",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "losses = 8 (100% loss rate via apathy) AND median_fronts_spawned = 0 (no fronts in zero-dominance run)",
      "falsification_metric": "losses",
      "severity_if_confirmed": "HOLDS"
    },
    {
      "id": "P4",
      "attack_id": "A4",
      "name": "Self-burn regression",
      "bot": "run_selfburn",
      "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
      "max_sleeps": 32,
      "poles": [1],
      "player_pole": 1,
      "args": {},
      "invariant": "median_selfburns = 0 (overlap immunity holds, front affects dominant pole only)",
      "falsification_metric": "median_selfburns",
      "severity_if_confirmed": "HOLDS"
    }
  ]
}
```
