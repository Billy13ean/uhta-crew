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
