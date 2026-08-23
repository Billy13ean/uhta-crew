# Keeper diff — run 24 | Temple endgame variant A (control) | rules-v3.10.2-A | 2026-08-21

## Change under review

Temple endgame schema 3.10, variant A (control): two-phase terminal (`win_loss.terminal_fires_on: "temple_entry"`, `world.temple.enabled: true`), presentation structure only, zero mechanical delta from v3.9.1-C except terminal timing. Hypothesis: "Temple and two-phase terminal add presentation structure with zero mechanical cost — median sleep count unchanged, no new failure modes."

## Coherence verdict

1 flag.

## Flags

### `CONTRADICTS-LOCKED`

**Output:** "The baseline (v3.10-C) and all three temple variants produce **identical campaign outcomes** across 20 seeds: 16 wins, 1 loss, 3 timeouts, median terminal sleep 13–15."

**Canon:** "difficulty is **asymmetric by design — Fear easy, Hope hard** (bot proxy at that gate: FEAR ~22/25, HOPE ~20/25 — **superseded, do not read as current**; at v3.9.1 the arms measure hope 21/25 / fear 16/20, and the genesis bots invert the OFF baseline. The stance is intent; re-benchmark before reading direction)." (CANON.md v18, Delta from v15, Runs 20–22 rebalance note)

**Note:** The Playtester reports identical win rates for Hope and Fear campaigns (both 16/20 across all variants), contradicting the locked asymmetry. The canon states Fear campaigns should win ~16/20 and Hope ~21/25 at v3.9.1-C. The measured 16/20 Hope rate is 5 wins below the v3.9.1 baseline, and the measured 16/20 Fear rate matches Hope exactly, erasing the asymmetry. The Playtester's prose acknowledges this ("same win rate as Hope due to `player_pole` not affecting bot policy in this harness configuration"), attributing it to harness configuration rather than ruleset change, but the canon asymmetry is a locked design intent that the measurement contradicts. The Red-Teamer's attack A6 sets the invariant as `wins >= 19` (Hope) and `wins >= 14` (Fear), both of which the measured data refutes (Hope 16 < 19, Fear 16 > 14 but equal to Hope).

## Cross-file impact

None. The flag is confined to the metrics report and does not propagate to the selected ruleset JSON (which is data-only and contains no win-rate claims) or the Red-Team attack surface (which correctly predicts the asymmetry based on canon).

## Loose ends flagged

1. **Harness configuration vs. ruleset asymmetry.** The Playtester attributes the erased asymmetry to "`player_pole` not affecting bot policy in this harness configuration," implying the harness is running both poles with the same bot policy. If true, this is a harness defect (the bot should implement pole-specific strategies to reproduce the asymmetry), not a ruleset defect. However, the canon does not specify that the asymmetry is bot-policy-dependent; it states the asymmetry is measured at the ruleset level ("the arms measure hope 21/25 / fear 16/20"). The Keeper cannot resolve whether the contradiction is a harness bug or a ruleset regression without the Director clarifying the source of the asymmetry.

2. **Hope win rate 5 below baseline.** The measured Hope campaign wins 16/20 (median terminal sleep 13–15 across variants), compared to the v3.9.1 baseline of 21/25. The Red-Teamer's attack A6 predicts `wins >= 19` (allowing 2-loss variance); the measured 16 is 3 losses beyond variance. The Playtester does not flag this as a regression, instead treating 16/20 as within expected range. The canon does not define a variance threshold for campaign regressions, so the Keeper cannot classify this as a locked contradiction, but it is a loose end requiring Director attention.

3. **Variant C do-nothing median shift.** The Playtester reports variant C (local decay zone) produces `median_terminal_sleep = 23.5` in the do-nothing baseline (P4), compared to 24.0 for the control and variants A/B. The Red-Teamer's attack A4 sets the invariant as `median_terminal_sleep == 24`, which variant C violates by 0.5 sleeps. The Playtester marks this as "PARTIAL" (C violates median, A/B hold) but does not escalate it as a coherence issue. The canon locks the do-nothing baseline at 24 sleeps (CANON.md v18, "difficulty-proxy re-benchmark" open question references the 24-sleep baseline as the anchor). A 0.5-sleep shift is small but non-zero, indicating variant C introduces a mechanical side effect. The Keeper flags this as a loose end because the contradiction is against variant C (not the selected variant A), but it suggests the schema 3.10 temple mechanics are not fully isolated.

## Coherence recommendation

**Hold.** The measured Hope win rate (16/20) contradicts the locked asymmetry baseline (21/25 Hope, 16/20 Fear) by 5 wins, and the measured Fear win rate (16/20) erases the asymmetry entirely. The Playtester attributes this to harness configuration, but the canon does not ground the asymmetry in bot policy — it states the asymmetry is measured at the ruleset level. The Director must rule whether the contradiction is a harness defect (UPHOLD canon, fix harness) or a ruleset regression (AMEND canon to reflect the new measured baseline, or reject the variant). The Keeper cannot recommend ratification while a locked design intent is contradicted by the evidence.

---

## Ruling

**Class answered:** `CONTRADICTS-LOCKED` (Hope/Fear campaign asymmetry, Red-Team A6 / Playtester P6–P7)

**Verdict:** `UPHOLD`

Canon stands; the output is revised. The flag is a probe artifact, not a ruleset regression, on three grounds:

1. `run_campaign_v3` is hope-only by construction (`w.player_pole = 1` inside `bots.py`); P7's "Fear campaign" re-measured Hope. No Fear campaign was run, so no asymmetry was erased — none was measured.
2. The control `rules-v3.10-C.json` measured the same 16/20 as every variant, and the 3.10 harness is parity-tested bit-identical to 3.9.1. A number the control shares cannot be a variant's regression.
3. 16/20 (80%) against CANON's 21/25 (84%) is one seed on different seed counts; CANON itself says "re-benchmark before reading direction." The campaign line's 20-seed baseline is recorded as 16/20 from here (a measurement, not a rule).

**Loose ends, ruled:**

- Variant C's do-nothing 23.5 vs 24.0 is the local decay zone doing what it says (apathy slightly faster near the temple); within the "self-limiting" intent of grief canon; noted, not a contradiction.
- Variant B's front geometry was **not measured** this run: five of seven probes used `run_campaign_v3`, which cannot see the front counters (the Red-Teamer's own prompt says so). A shim `run_campaign_v3_audit` now reports the full stat dict; B re-runs with it.
- The `harness_pilgrim_tiles_per_sleep` sweep was requested and not run (the Designer must vary it as a dial; it is not a bot arg). Carried to run 26.

**Variant ratified:** `rules-v3.10.2-A.json` → committed as `rules/rules-v3.10.2-A.json`, the fifteenth generation. It is the minimum the build needs (temple placed, two-phase terminal) and it is clean: +2 sleeps median for the walk, no change to win/loss counts, 16/16 armed campaign runs reached the temple in 1–4 sleeps, 0 lost while armed (shim smoke, 20 seeds). B and C remain proposals on the 3.10 dials, gated on run 26.

**CANON line added (AMEND only):** n/a — but the Keeper transcribes the ratification: *"Ruleset v3.10.2-A (Run 25): the Temple is placed at genesis (seeded, constrained); the unification hold ARMS the win and entering the temple FIRES it; the loss check is untouched and live while armed (H-9 pilgrimage assumption in the harness). Grief Front origin (B) and the local decay zone (C) are proposals, unratified."*

**Signed (Director):** Nicholas Rouke  **Date:** 2026-08-23
