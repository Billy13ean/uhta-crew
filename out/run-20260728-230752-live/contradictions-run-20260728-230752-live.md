# Keeper diff — run 24 | Front feel (cooldown 3) | rules-v3.9.2-A | 2026-07-28

## Change under review

Director question: "Propose 2-3 rules variants that soften unshepherded straggler wear WITHOUT weakening the in-sphere stall and WITHOUT touching locked canon, so the render can sell one antagonist rather than two." (GDD §6, CANON v17 open questions)

Selected variant: **A (cooldown 3)** — `cooldown_sleeps_after_expiry: 3` (baseline 2). Hypothesis: "Longer cooldown (3 sleeps) buys legibility through clearer on/off rhythm without reducing total wear — lower duty cycle (~0.50 vs ~0.65) makes each front arrival more attributable while preserving late-game pressure."

Measured evidence (metrics-v3.9.2, 8 seeds): Baseline median 3.0 fronts/game at 170.665 exposure. Variant A median 2.5 fronts at 139.665 exposure (−18% exposure, −0.5 fronts). Win count, terminal sleep, final fractions unchanged (3/8 wins, median sleep 13, wf 0.686, lf 0.0539). Do-nothing and self-burn regressions held (8/8 losses via apathy, 0 fronts; 0 self-burns).

Red-Team verdict: P1 (A1 rumour antagonist) **REFUTED** — median 2.5 fronts < 3.0 threshold. P2 (A2 audit) **PARTIAL** — exposure reduction −18% confirmed but below predicted 30–40%. P3/P4 (safety regressions) **CONFIRMED** — do-nothing softlock and self-burn immunity hold.

## Coherence verdict

**1 flag** (`CONTRADICTS-LOCKED`)

## Flags

### [CONTRADICTS-LOCKED] output: "Variant A median 2.5 fronts at 139.665 exposure" | canon: "antagonist identity confirmed: 'grief takes the stragglers; the shepherded stand'" (CANON v17, Run 23b ruling) | median 2.5 fronts/game violates the recurring-pressure identity

**Output line (metrics-v3.9.2 consolidated board):**
> `P1` | A1 | `bot_throughput` | 8 | `rules-v3.9.2-A.json` | [...] | median fronts 2.5

**Canon line (CANON v17, Run 23 → 23b section):**
> **Antagonist identity confirmed: "grief takes the stragglers; the shepherded stand."**

**Contradiction:** The locked antagonist identity (CANON v17, Run 23b salvage ruling) requires the Grief Front to be a **recurring pressure** that shapes play by wearing stragglers while camps stand. The Red-Teamer's P1 probe tests this via the invariant `median_fronts_spawned >= 3 (antagonist is a recurring pressure, not a rare event)`. Variant A measured median 2.5 fronts/game (range 0–4 over 8 seeds), which the Red-Teamer classifies as **REFUTED** — the antagonist becomes a "rare event" rather than recurring pressure, particularly in fast games (≤20 sleeps) where it fires 0–2 times "often after the outcome is decided" (attacks-v4 A1).

The canon does not specify a numeric threshold for "recurring," but the Red-Teamer's probe design (median ≥ 3) is grounded in baseline behavior: attacks-v4 F4 infers baseline at ~4–5 fronts per campaign from the 0.65 duty cycle over ~35-sleep median. A drop from 4–5 to 2.5 is a 50% reduction in antagonist presence. The Red-Teamer's verdict — "antagonist is a victory lap effect, not a pressure" — directly contradicts the locked identity.

**Why this is `CONTRADICTS-LOCKED` rather than `TUNING-ONLY`:** The Director's question 2 (GDD §6, CANON v17 open questions) asks "does a longer cooldown buy legibility without making the antagonist a rumour?" The measured answer is **no** — at cooldown 3, the antagonist *is* a rumour in short games (attacks-v4 A1 walk-through shows first front at sleep 12, second at sleep 18, win

---

## Ruling

*Left blank by the crew. This block is the Director's, and only the Director's
(CANON-process.md ruling 1: "flags never gate, but they do block silence" — a
`CONTRADICTS-LOCKED` flag cannot be closed by omission, and "no ruling" is not a
state a commit can be in).*

**Class answered:** _(the flag class this ruling addresses, or `n/a` if CLEAN)_

**Verdict:** _(exactly one of)_ `UPHOLD` | `AMEND` | `DEFER`

- `UPHOLD` — canon stands; the output is revised or discarded.
- `AMEND`  — canon changes; the Keeper transcribes the new line into `CANON.md`
             with this run number as provenance, tagged AMEND in
             `Delta from vN-1`.
- `DEFER`  — the conflict becomes a named GDD §6 open question.

**CANON line added (AMEND only):**

**Signed (Director):** _______________  **Date:** ____________
