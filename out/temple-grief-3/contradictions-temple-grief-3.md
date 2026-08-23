# Keeper diff — run 24 | Temple endgame variant A (control) | rules-v3.10-A.json | 2026-08-21

## Change under review

Temple endgame schema 3.10, variant A: presentation-only temple placement (`world.temple.enabled: false`), terminal fires at `hold_complete` (v3.9.1 behavior), zero mechanical delta from `rules-v3.9.1-C.json`. Harness-verified bit-identical outcomes across all four probes (P1–P4) on 16 arms.

## Coherence verdict

**1 flag** — `CONTRADICTS-LOCKED` on the do-nothing terminal sleep prediction.

## Flags

### [CONTRADICTS-LOCKED] output: "median_terminal_sleep in [18, 22] (matches v3.9.1 baseline)" (Red-Team A1 invariant, Playtester P1 invariant) | canon: "Do-nothing softlock: symmetric genesis never fires Front, apathy loss at median sleep 24" (implicit in metrics-v3.9.1 §F, not explicitly stated but derivable from the v3.9.1 campaign baseline) | Measured 24 sleeps (all four variants), predicted 18–22 sleeps — a +2 sleep delta outside the Designer's stated range

**Detail:** The Red-Teamer's A1 invariant and the Playtester's P1 probe both predict `median_terminal_sleep in [18, 22]` for the do-nothing softlock, citing "matches v3.9.1 baseline." The measured facts show median 24.0 sleeps (baseline), 24.0 (A), 24.0 (B), 23.5 (C) — all outside the [18, 22] range. The Playtester flags this as "PARTIAL — Front and loss counts hold; terminal sleep 24 vs. predicted [18, 22] is +2 sleeps outside range, consistent across all variants" and suggests "A re-benchmark of `bot_do_nothing` on `rules-v3.9.1-C.json` (not run this session) would confirm whether the +2 delta is a harness change, a seed-selection artifact, or a Designer prediction error."

**Canon conflict:** CANON.md v18 does not explicitly state a do-nothing terminal sleep number for v3.9.1-C. The metrics-v3.9.1 report (referenced in CANON.md but not in this packet) is the authoritative source for v3.9.1 baseline numbers. The Designer's [18, 22] prediction appears in the Red-Team and Playtester outputs for this run (run 24), not in prior canon. However, the Playtester's verdict ("PARTIAL") and the Red-Teamer's severity ("HOLDS") both treat the +2 delta as a **regression from a known baseline**, implying the [18, 22] range was previously measured or predicted. If the v3.9.1 baseline was never 18–22 sleeps, the prediction is ungrounded. If it was, the +2 delta is a real regression.

**Trace failure:** I cannot trace the [18, 22] prediction to a CANON.md line or a prior metrics report in this packet. The closest reference is CANON.md v18 § "Delta from v15" → "Runs 20–22" → "Rebalance (v3.7.3, Director): difficulty is **asymmetric by design — Fear easy, Hope hard** (bot proxy at that gate: FEAR ~22/25, HOPE ~20/25 — **superseded, do not read as current**; at v3.9.1 the arms measure hope 21/25 / fear 16/20…)." This gives campaign win rates, not do-nothing terminal sleeps. The do-nothing softlock is a **safety gate** (P1, A1), not a campaign metric, and its baseline is not recorded in CANON.md v18.

**Classification rationale:** If the [18, 22] range is a Designer prediction error (the v3.9.1 baseline was always ~24 sleeps, and the Designer misremembered it as 18–22), this is `UNGROUNDED` (the Designer introduced a number not in canon). If the [18, 22] range was measured at v3.9.1 and the +2 delta is a real regression (e.g., a harness change between v3.9.1 and v3.10 added 2 sleeps to the do-nothing path), this is `CONTRADICTS-LOCKED` (the output claims "matches v3.9.1 baseline" but the measured outcome does not match). The Playtester's language ("PARTIAL — … +2 sleeps outside range, consistent across all variants") and the Red-Teamer's verdict ("HOLDS") both treat this as a **known delta, not a contradiction**, which suggests the [18, 22] prediction was never locked canon. However, the Playtester also writes "this is a +2 sleep regression from the Designer's v3.9.1 baseline prediction," which implies the Designer claimed [18, 22] as a v3.9.1 fact.

**Final classification:** `CONTRADICTS-LOCKED` — the output claims the measured outcome "matches v3.9.1 baseline," but the measured 24 sleeps does not match the predicted [18, 22] range. The Playtester flags this as "PARTIAL" (not CONFIRMED), and the Red-Teamer's severity is "HOLDS" (not GAME-BREAKING), but both acknowledge the delta. The contradiction is between the **claim of equivalence** ("matches v3.9.1 baseline") and the **measured fact** (24 vs. 18–22). If the Director rules this is a prediction error (the baseline was always 24), the output should be revised to remove the [18, 22] claim. If the Director rules this is a real regression (the baseline was 18–22 and the harness changed), the output should note the delta and defer the root cause to a GDD §6 open question.

## Cross-file impact

None. The temple schema 3.10 additions (`world.temple`, `win_loss.temple_entry`) are isolated to the `rules-v3.10-*.json` files and do not touch CANON.md, GDD, or prior rulesets. The measured bit-identical outcomes (all four variants produce identical P1–P4 results) confirm that `enabled: false` and `terminal_fires_on: "hold_complete"` correctly reproduce v3.9.1-C behavior, modulo the +2 sleep delta flagged above.

## Loose ends flagged

1. **Do-nothing terminal sleep baseline unknown.** CANON.md v18 does not record a do-nothing terminal sleep number for v3.9.1-C. The Playtester suggests "A re-benchmark of `bot_do_nothing` on `rules-v3.9.1-C.json` (not run this session) would confirm whether the +2 delta is a harness change, a seed-selection artifact, or a Designer prediction error." This is a **measurement gap**, not a contradiction — the baseline was never locked, so the +2 delta cannot contradict it. However, the output **claims** the measured outcome "matches v3.9.1 baseline," which is unverifiable without the baseline number.

2. **Variant A is not the control.** The Playtester writes "**The surprising finding:** variant A is not the control — all four rulesets behave identically, suggesting the temple/travel/decay mechanics are either disabled or non-functional in the harness." This contradicts the Designer's claim that variant A is "the v3.9.1-C behavioral control; zero mechanical delta." If all four variants are bit-identical, then variants B and C (which have `enabled: true` for temple placement and travel) are **also** controls, and the Designer's three-variant design (A = control, B = travel, C = decay) collapses. The Playtester flags this as an **assumption** ("I assume the harness reads `world.temple.enabled: false` and skips all temple-related logic") and defers the root cause to the Director. This is not a coherence flag (the output does not contradict canon), but it is a **design-intent flag** (the output does not match the Designer's stated goal).

3. **Front exposure delta (variant B).** The Playtester measures median front exposure 170.665 (baseline/A), 78.0 (B), 176.665 (C) and writes "variant B's median exposure drops to 78.0 (vs. 170.665 baseline) — if `spawn_at: "temple_position"` + `move_tiles_per_sleep: 3` causes the Front to arrive late or miss high-density windows, a sweep of `move_tiles_per_sleep` [1, 2, 3, 4, 6] would find the arrival-timing sweet spot." This is a **tuning lever**, not a contradiction. The Playtester does not flag it as a failure (P3 verdict is CONFIRMED for all variants), but notes it as an open tuning question. This belongs in GDD §6 if the Director wants to pursue it.

4. **Campaign win-rate delta (variant C).** The Playtester measures 16/20 wins (baseline/A/B), 17/20 (C) and writes "variant C at 17/20 is +1 win, still inside ±2" tolerance. The Red-Teamer's A2 invariant is "Fear wins 16/20 ± 2, Hope wins 21/25 ± 2," so 17/20 is within tolerance. However, the Playtester also writes "The Director's question 'Does variant C make Hope runs unwinnable?' cannot be answered from this data" because the board does not separate Fear/Hope outcomes (it reports only total wins, not per-pole). This is a **measurement gap**, not a contradiction. If the Director wants a per-pole breakdown, the Playtester must re-run P2 with separate Fear/Hope arms.

## Coherence recommendation

**Hold** — one `CONTRADICTS-LOCKED` flag on the do-nothing terminal sleep prediction requires a Director ruling (UPHOLD / AMEND / DEFER) before this run can land. The measured 24 sleeps contradicts the claimed [18, 22] baseline match. If the Director rules the [18, 22] prediction was never locked canon (it was a Designer error), the output should be revised to remove the claim. If the Director rules the [18, 22] range was the v3.9.1 baseline and the +2 delta is a real regression, the output should note the delta and defer the root cause to GDD §6.

The bit-identical outcomes across all four variants (P1–P4 results identical for baseline/A/B/C) are **coherent with the Designer's claim that variant A is a control**, but they also suggest variants B and C are non-functional (the temple/travel/decay mechanics produce no measurable delta). The Playtester flags this as a design-intent question, not a coherence contradiction. The Director must decide whether to accept variant A as the control (and investigate why B/C are inert) or reject all four variants and re-design the temple mechanics.

---

## Assumptions

1. **[ASSUMPTION]** The [18, 22] do-nothing terminal sleep range is a Designer prediction, not a locked canon number. CANON.md v18 does not record a do-nothing baseline for v3.9.1-C. The Playtester treats the +2 delta as a regression ("this is a +2 sleep regression from the Designer's v3.9.1 baseline prediction"), but I cannot trace the [18, 22] range to a prior metrics report or CANON line in this packet. If the Director has access to the full metrics-v3.9.1 report (referenced in CANON.md but not in this packet), the [18, 22] range may be verified or refuted there.

2. **[ASSUMPTION]** The Playtester's "bit-identical" claim (all four variants produce identical P1–P4 results) is based on the consolidated board, which shows identical medians for all metrics across all variants. The raw facts appendix confirms this: every probe × ruleset pair has identical `wins`, `losses`, `none`, `median_terminal_sleep`, `median_final_wf`, `median_final_lf`, `median_selfburns`, `median_fronts_spawned`, and `median_front_exposure` values, except for minor variance in P2 terminal sleep (13 baseline/A, 15 B/C) and P3 front exposure (170.665 baseline/A, 78.0 B, 176.665 C). The Playtester interprets this as "the temple/travel/decay mechanics are either disabled or non-functional in the harness," but does not provide a root-cause diagnosis. I assume the harness correctly reads `enabled: false` and skips temple logic, but I cannot verify this without the harness source code.

3. **[ASSUMPTION]** The Red-Teamer's "HOLDS" verdict for A1 (do-nothing softlock) means "the audit passes" (the Designer's arithmetic is sound), not "the measured outcome matches the prediction." The Red-Teamer writes "Expected severity: HOLDS (the audit passes) or TUNING (notation ambiguity in burnout headroom)" and concludes "No new vulnerabilities found in variant A." This suggests the Red-Teamer treats the +2 sleep delta as a **known variance**, not a contradiction. However, the Playtester's "PARTIAL" verdict and the flag I raised above treat the +2 delta as a **regression**. The Director must reconcile these two interpretations.

---

## Ruling

**Class answered:** `CONTRADICTS-LOCKED` (do-nothing terminal sleep, Red-Team A1 / Playtester P1)

**Verdict:** `UPHOLD`

Canon stands; the output is revised. The `[18, 22]` do-nothing terminal-sleep range is not a canon line and was never measured at v3.9.1 — it is an ungrounded Designer prediction that the Red-Teamer and Playtester repeated as if it were a baseline. The measured 24 sleeps is the same on the ratified baseline and on every variant, and `tools/parity_schema310.py` shows the 3.10 harness bit-identical to the 3.9.1 harness across 30 arms, so there is no regression to explain. The claim "matches v3.9.1 baseline" is struck; 24 sleeps is recorded as the do-nothing baseline for v3.9.1-C / v3.10-C going forward (a measurement, not a rule — no CANON line).

**Loose ends, ruled:**

1. *Variant A is the control* — because the Designer emitted A as a zero-key delta, not as "temple + temple_entry." That is a Designer error, not a finding about the mechanics: B and C do differ from the baseline (P2 terminal sleep 15 vs 13 — the walk; P3 front exposure 78 vs 171 — the travel). The Playtester's "all four bit-identical" reading is wrong on its own appendix. The Keeper diffed A, which is why the diff found nothing.
2. The Playtester could not see the arming at all: the probe runner did not surface the schema-3.10 audit stats. Fixed in `crew/probe_runner.py` (armed_runs, lost_while_armed, armed→terminal, pilgrim tiles, well exposure, front travel).
3. Front exposure under B (78 vs 171) and the Hope/Fear split for C are measurement gaps, not contradictions — they go into run 25's question set, not §6.

**Variant ratified:** none. This run lands as evidence (first `CONTRADICTS-LOCKED` raised against an agent output — CANON-process #2 defect 3 closed; report discipline #7 resumes at run 24). Run 25 re-asks with A stated unambiguously.

**CANON line added (AMEND only):** n/a

**Signed (Director):** Nicholas Rouke  **Date:** 2026-08-23
