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
