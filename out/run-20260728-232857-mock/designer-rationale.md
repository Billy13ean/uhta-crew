> **MOCK-LLM FIXTURE — NOT REAL DESIGN WORK.** This document was replayed verbatim from `tests/fixtures/` by `--mock-llm`, a no-API-key test mode whose only purpose is to prove the orchestration executes end to end. No model saw the packet; no judgement was exercised; nothing here is evidence about uhta. Harness NUMBERS in this run are still real (the Playtester always executes the simulator) — the PROSE around them is a fixture.

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


_(variant JSON emitted to its own file)_



_(variant JSON emitted to its own file)_



_(variant JSON emitted to its own file)_



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
