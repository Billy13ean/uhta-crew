```markdown
# attacks-v3.9.2 — front-feel sweep (rules-v3.9.2-A, r4 / cooldown 4)

> Run artifact | target: `world.uhtcearu_events.grief_front` under variant A
> (radius 4, cooldown 4; `front_strength` 4.0 and all four Run-23b closures
> untouched) | probes P1–P6 specified for the Playtester in `attacks.json`.

Scope: the front's geometry and cadence only. Prior surfaces (v3.3 wander, v3.4
death/roads/loners, v3.5 battle pressure, v3.6–3.8 genesis/schism/ascension) are
assumed at their gated verdicts — with the standing caveat from GDD §5.6 that the
combined genesis + schism + road-allegiance surface has never been re-attacked as
a whole, which this pass does not fix.

**Arithmetic used throughout (live values, variant A).** Baseline sleep decay at
the 0.55 trigger = 0.4 × (1 + 0.55) = **0.62/tick**. Inside the front = 0.4 ×
(1 + 4.0) = **2.0/tick**, dominance-independent. Zealot pull 2.0/tick. `dv` is
clamped to ±1 *after* summing, so a held member nets clamp(2.0 − 2.0) =
**0.000/tick** and an unheld one nets clamp(0 − 2.0) = **−1.0/tick**. Decay is
sleep-only, 3 ticks/sleep. Decay is not same-pole pressure and cannot burn; it
moves toward 0 and cannot cross it.

---

### A1 — The radius cut is a coverage cut, not a relief cut

**Attack.** Variant A buys its straggler relief by shrinking the fog from r6 to
r4. But the NPCs it stops covering are the ones at the *edge* of the old
footprint — and the salvage anchors the spawn on the largest dominant tribe,
which is exactly where the shepherded (immune, stalled) sit. So A may remove
coverage from precisely the population that was already taking 0.000/tick, while
leaving the unheld converts near the tribe core still fully exposed. The relief
would then be arithmetic on the exposure metric and invisible in play.

**Mechanism.** r6 covers 13×13 = 169 tiles; r4 covers 9×9 = 81 — a 52% cut by
area. But a settled tribe's member footprint is ±2 tiles from centre (25 tiles),
entirely inside r4. Every held member stays covered and stays stalled. What
leaves the footprint is the annulus between 5 and 6 tiles out, which is where
loners drifting toward the tribe sit — i.e. the relief lands on the *straggler*
class after all, but for a geometric reason the rationale table does not state.
The attack fails on its own terms; the finding is that the Designer got the right
answer from the wrong sentence.

**Expected severity.** HOLDS (the mechanism works) / audit note against the
rationale (hard rule 7).

**Harness probe (P1).** `bot_throughput`, seeds 0–7, cap 25, hope — chosen over
the campaign bot deliberately: `run_campaign_v3` builds its own return dict in
`bots.py` and does not carry the front counters, so an exposure question asked of
it comes back `—`. Read `median_front_exposure` on A against the baseline arm.
**Accept the relief if** A's median exposure is materially below baseline.
**Reject if** exposure is flat — that would mean the annulus was empty and the
radius cut bought nothing.

**Suggested fix if confirmed.** None. Correct the rationale's stated reason.

---

### A2 — Cooldown 4 halves the metronome, and that is the risk, not the benefit

**Attack.** attacks-v5 A9 found the front fires on a fixed 5-sleep metronome once
dominance sticks above the trigger, and called a recurring dramatic fog with no
mechanical content "worse for trust in the world than no antagonist at all."
Variant A stretches the cycle to 3-on/4-off — 7 sleeps — which cuts the announce
rate but also cuts total pressure. If the campaign win rate is unchanged, A has
made the antagonist rarer without making it more legible: the same null, less
often.

**Mechanism.** Duty cycle falls from 3/5 = 0.60 to 3/7 = 0.43. Against a campaign
that runs ~20 sleeps post-formation, that is roughly 3 fronts instead of 4. Each
front's *internal* arithmetic is unchanged, so the only measurable effect is
total exposure and any downstream win-rate shift.

**Expected severity.** TUNING.

**Harness probe (P2).** Two arms, because the question spans two metric
families. **P2a** `bot_throughput`, seeds 0–7, cap 25 — `median_fronts_spawned`
(the campaign bot does not emit it). **P2b** `run_campaign_v3`, seeds 0–7, cap 32
— `wins` and `median_terminal_sleep`, the outcome the cadence change is supposed
to be free against. **Flag as content-free if** fronts drop on P2a while P2b's
wins and median sleep are identical.

**Suggested fix if confirmed.** Data-only, and a Director call, not mine: if the
cadence change costs nothing it should be reverted rather than kept, since
canon parked cooldown at 2 pending exactly this measurement.

---

### A3 — Geometry null, re-opened: r4 + 3 tiles of crawl is 7 tiles of reach

**Attack.** The v3.9 A3 finding was that centroid spawn plus 9 tiles of total
reach could not find its target in the spread world schism produces. The salvage
closed it by anchoring the spawn on the target. Variant A shrinks the radius to 4
without touching the crawl, giving total reach 4 + 3 = 7 tiles. If the anchor
tribe *moves* during the front's life — an unsettled tribe drifts 1 tile/sleep,
and a routed one recoils `sphere + 2..4` — the fog can be left behind by a target
that was never rooted.

**Mechanism.** Settled tribes are rooted and cannot move, so the modal case is
safe. The exposure is unsettled dominant tribes, which is the early-to-mid game,
and routed tribes, which move `rb + 2` or `rb + 4` in a single sleep — a jump of
7–9 tiles, beyond a 1-tile-per-sleep crawl at any radius. A r4 front loses contact
one sleep sooner than an r6 one.

**Expected severity.** TUNING (a pre-existing hole, marginally widened).

**Harness probe (P3).** `run_siege` with `roads: true`, seeds 0–7 — the arm that
reliably produces contact and rout. Compare `median_heads` on A vs baseline
(`run_siege` carries the siege metrics but not the front counters, so exposure is
P1's job, not this arm's). **Confirm the widening if** A's converted heads fall
against baseline.

**Suggested fix if confirmed.** Data-only: raise `move_tiles_per_sleep` with the
radius cut, as variant C does independently. Co-gate them rather than shipping A
alone.

---

### A4 — Front-as-shield, re-probed under a smaller footprint

**Attack.** attacks-v5 C1 closed front-as-shield on mechanism: the overdose check
sums same-pole *pressure entries*, and `decay_term` is computed after the burnout
branch, so front decay can neither absorb nor trigger overdose. Shrinking the
radius cannot re-open a closure that lives in the order of two code branches — but
a smaller front concentrated on a tribe core is the densest same-pole environment
in the game, so the negative control is worth re-running rather than assumed.

**Mechanism.** None available. The claim is structural.

**Expected severity.** HOLDS expected.

**Harness probe (P4).** `run_selfburn`, seeds 0–3. **Accept if** `max_selfburns`
is 0. **Any non-zero value is GAME-BREAKING** and an implementation bug, not a
balance finding.

---

### A5 — Passive-baseline regression: the front must still be unreachable by doing nothing

**Attack.** Not an exploit — the safety floor. Canon: the front "cannot fire in a
do-nothing run by construction," and metrics-v3.9.1 §B measured 19/20 seeds with
zero fronts. A radius or cadence change must not disturb the apathy loss.

**Mechanism.** A do-nothing world never reaches dominance 0.55 for the player's
pole, so the trigger is never armed. Radius and cooldown are downstream of the
trigger and cannot reach back through it.

**Expected severity.** HOLDS expected.

**Harness probe (P5).** `bot_do_nothing`, seeds 0–7, cap 40. **Accept if** every
seed still reaches the apathy loss and `median_fronts_spawned` is 0. **A ruleset
that breaks the passive baseline is broken regardless of how it handles clever
play.**

---

### A6 — Fear burst: the fear pole must not be quietly advantaged by a smaller fog

**Attack.** `affects_dominant_pole_only` means the front wears whoever is winning.
A fast fear burst reaches dominance early, so it eats fronts early — and a
*smaller* front is a smaller tax on exactly that line. If A improves the tyrant
arm while leaving the hope campaign flat, the variant has moved the pole balance
under cover of a feel change, against a stance canon already flags as unmeasured.

**Mechanism.** The fear-burst arm runs at cap 15 and is the shortest in the
roster; it typically terminates before many front cycles. The effect, if real,
should be small and should show in `median_max_wf` rather than in wins.

**Expected severity.** TUNING (pole-balance drift).

**Harness probe (P6).** `make_flamer` at `{"tribe": 0, "pole": -1}` with
`player_pole: -1`, seeds 0–7, cap 15 — a fear-pole burst against the fear founding
tribe. (`run_tyrant` is the canonical arm for this and is unusable here: it
hard-codes tribe index 2, which does not exist under the genesis start's two
founding tribes, so it raises on every seed. That is a defect in the vendored bot
suite, recorded rather than worked around.) Compare
A vs baseline on `median_final_wf` and `wins` (`make_flamer` runs through `H.run`
and so carries the front counters too; `median_max_wf` is a `run_tyrant`-only
metric and is not available here). **Flag if** A's fear-burst numbers rise while
the hope arms are unchanged.

---

### A7 — Tyrant regression: the fear-pole control must not move

**Attack.** Not an exploit — the second safety floor, and the pole-balance
counterpart to A5. `run_tyrant` is the canonical naive fear burst. A front-feel
change is supposed to be free against it: the tyrant terminates around sleep 14-15,
fronts fire late if at all, and the arm's job is to sit still. If a radius or
cadence change moves the tyrant's `max_wf`, the variant has moved pole balance
under cover of a legibility fix — against a stance canon already flags as intent
rather than measurement (CANON v17, "re-benchmark before reading direction").

**Mechanism.** The burst reaches dominance early and so eats fronts early; a
smaller or rarer fog is a smaller tax on exactly that line. The effect, if real,
should show in `median_max_wf` before it shows in `wins`.

**Note on the policy.** `run_tyrant` runs through `crew/policy_shims.py`, not
through `bots.py` — upstream hard-codes tribe index 2, which does not exist under
the genesis start, and raised on every seed. The shim resolves the target once at
t0 as the first tribe opposing the player's pole. Recorded here because a shimmed
arm's provenance belongs in the attack that names it, not only in the runner's
log. See `FINDINGS.md` #1.

**Expected severity.** HOLDS expected.

**Harness probe (P7).** `run_tyrant`, seeds 0-7. **Accept if** `median_max_wf` and
`wins` on every variant match the baseline arm.

---

## Failed attacks

- **Flip-the-stall.** Attempted: use the smaller radius to place the front so a
  held member sits at the edge and takes partial decay. Fails — the front applies
  a single decay coefficient inside `cheb <= radius` with no falloff, so there is
  no edge to exploit. Not harness-expressible; no probe.
- **Burn a camp with grief.** Fails on the same branch order as A4. Decay is not a
  pressure entry. Recorded so a future reader does not re-attempt it.
- **Cooldown-riding.** Attempted: time the win hold to land in a cooldown window.
  Fails against `trigger_trailing_window_sleeps 3`, which A leaves at its gated
  value — the same closure that killed hover-sprint in attacks-v5 A5.

## Summary table

| Probe | Severity | One-line |
|---|---|---|
| P1 (A1) | HOLDS + audit note | The radius cut does buy straggler relief, for a geometric reason the rationale states wrongly |
| P2a/P2b (A2) | TUNING | Cooldown 4 halves the metronome; if wins are unchanged it bought rarity, not legibility |
| P3 (A3) | TUNING | r4 + 1-tile crawl loses a routed target a sleep sooner than r6 did |
| P4 (A4) | HOLDS expected | Front-as-shield stays closed by branch order; run the control anyway |
| P5 (A5) | HOLDS expected | Passive baseline must be untouched — the safety floor |
| P6 (A6) | TUNING | A smaller fog is a smaller tax on whoever reaches dominance fastest (fear-burst arm; `run_tyrant` is genesis-incompatible) |

| P7 (A7) | HOLDS expected | Tyrant fear-pole control; runs via the crew shim (FINDINGS.md #1) |

## Verdict

**No GAME-BREAKING finding, and no DOMINANT-STRATEGY.** Variant A does what it
says: it cuts exposure without touching the stall arithmetic, and all four Run-23b
closures are left at their gated values, so nothing the salvage bought is
re-opened. The two live questions are both TUNING and both for the Director: A2
(does the cadence change buy anything a player could notice, or only a lower
number?) and A6 (does a smaller fog quietly favour the pole that reaches dominance
first, on a balance stance canon already marks as intent rather than measurement?).
A3 is a pre-existing hole marginally widened and argues for co-gating A's radius
cut with C's faster crawl rather than shipping A alone.

## Assumptions

- `[ASSUMPTION]` That `front_exposure` (NPC-sleeps) is a faithful proxy for
  "straggler wear". It counts every front-decayed sleeping tick including
  *stalled* members, who take the decay but net zero movement — so exposure
  overstates wear wherever the shepherded are numerous. Flagged because P1's
  verdict rests on it.
- `[ASSUMPTION]` That 8 seeds is enough to separate these arms. It is not, for
  anything subtle; the uhta standard is 20 and the Playtester must say so.
```

```json
{
  "target": "rules-v3.9.2-A.json",
  "probes": [
    {
      "id": "P1",
      "attack_id": "A1",
      "name": "front exposure \u2014 does the radius cut actually relieve stragglers",
      "bot": "bot_throughput",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 25,
      "poles": [
        -1,
        1
      ],
      "player_pole": 1,
      "args": {},
      "invariant": "median_front_exposure on variant A is materially below the baseline arm; if it is flat, the radius cut bought nothing",
      "falsification_metric": "median_front_exposure",
      "severity_if_confirmed": "HOLDS"
    },
    {
      "id": "P2a",
      "attack_id": "A2",
      "name": "metronome rate \u2014 how often the fog announces itself",
      "bot": "bot_throughput",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 25,
      "poles": [
        -1,
        1
      ],
      "player_pole": 1,
      "args": {},
      "invariant": "median_fronts_spawned falls on A relative to baseline; if it does not, the cooldown stretch is not reaching the scheduler at all",
      "falsification_metric": "median_fronts_spawned",
      "severity_if_confirmed": "TUNING"
    },
    {
      "id": "P2b",
      "attack_id": "A2",
      "name": "campaign outcome \u2014 is the cadence change free",
      "bot": "run_campaign_v3",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 32,
      "poles": [
        -1,
        1
      ],
      "player_pole": 1,
      "args": {},
      "invariant": "wins on A stay within 1 of the baseline arm and median_terminal_sleep within 2 sleeps \u2014 a cadence change that moves the outcome is a balance change wearing a feel change's clothes",
      "falsification_metric": "wins",
      "severity_if_confirmed": "TUNING"
    },
    {
      "id": "P3",
      "attack_id": "A3",
      "name": "roads siege \u2014 target-loss under a 7-tile reach",
      "bot": "run_siege",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 20,
      "poles": [
        -1,
        -1,
        1
      ],
      "player_pole": 1,
      "args": {
        "use_roar": false,
        "roads": true
      },
      "invariant": "median_heads on A stays within 1 of the baseline arm; a larger drop means the smaller front is losing contact with a moving target",
      "falsification_metric": "median_heads",
      "severity_if_confirmed": "TUNING"
    },
    {
      "id": "P4",
      "attack_id": "A4",
      "name": "front-as-shield negative control",
      "bot": "run_selfburn",
      "seeds": [
        0,
        1,
        2,
        3
      ],
      "max_sleeps": 8,
      "poles": [
        1,
        1,
        -1
      ],
      "player_pole": 1,
      "args": {},
      "invariant": "max_selfburns is exactly 0 in every arm; any non-zero value is GAME-BREAKING and an implementation bug",
      "falsification_metric": "median_selfburns",
      "severity_if_confirmed": "GAME-BREAKING"
    },
    {
      "id": "P5",
      "attack_id": "A5",
      "name": "passive baseline \u2014 the safety floor",
      "bot": "bot_do_nothing",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 40,
      "poles": [
        -1,
        1
      ],
      "player_pole": 1,
      "args": {},
      "invariant": "every seed still reaches the apathy loss (losses == n) and median_fronts_spawned is 0 \u2014 the front cannot fire in a do-nothing run by construction",
      "falsification_metric": "losses",
      "severity_if_confirmed": "GAME-BREAKING"
    },
    {
      "id": "P6",
      "attack_id": "A6",
      "name": "fear-pole burst \u2014 pole-balance drift under a smaller fog",
      "bot": "make_flamer",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 15,
      "poles": [
        -1,
        1
      ],
      "player_pole": -1,
      "args": {
        "tribe": 0,
        "pole": -1
      },
      "invariant": "median_final_wf and wins on A stay within the baseline arm's values; a rise in both while the hope arms are flat indicates pole-balance drift",
      "falsification_metric": "median_final_wf",
      "severity_if_confirmed": "TUNING"
    },
    {
      "id": "P7",
      "attack_id": "A7",
      "name": "tyrant fear-pole regression control (shimmed policy)",
      "bot": "run_tyrant",
      "seeds": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_sleeps": 15,
      "poles": [
        -1,
        1
      ],
      "player_pole": -1,
      "args": {},
      "invariant": "median_max_wf and wins on every variant match the baseline arm; a move means a front-feel change has shifted pole balance",
      "falsification_metric": "median_max_wf",
      "severity_if_confirmed": "TUNING"
    }
  ]
}
```
