```markdown
# Keeper diff — run v3.9.2 (crew) | front-feel sweep: radius / duration / cadence | rules-v3.9.2-A | mock fixture

## Change under review

The Director's goal, quoted back: *"Front feel (GDD §6, CANON v17 open questions).
metrics-v3.9.1 §E records that the Grief Front's straggler wear now saturates the
±1 step cap … Propose 2-3 rules variants that soften unshepherded straggler wear
WITHOUT weakening the in-sphere stall and WITHOUT touching locked canon, so the
render can sell one antagonist rather than two."*

Under review: `rules-v3.9.2-A`, which changes exactly two fields against the
ratified baseline — `world.uhtcearu_events.grief_front.radius_tiles` 6 → 4 and
`.cooldown_sleeps_after_expiry` 2 → 4 — together with its Red-Team surface
(`attacks-v3.9.2.md`, probes P1–P6) and the Playtester's measured board.

## Coherence verdict

CLEAN — 0 canon contradictions.

## Flags

None.

Three checks that could have produced a flag and did not:

- **`front_strength` is 4.0 in all three variants**, byte-identical to the
  baseline. Had it moved, that would be `CONTRADICTS-LOCKED` against the Run-23b
  salvage line ("front_strength 4.0 → inside-front decay 2.0/tick **exactly
  equals zealot pull**: a true STALL") and against the question set's own
  exclusion. It did not move.
- **The four Run-23b closures are untouched** — `spawn_at`,
  `move_toward`, `trigger_trailing_window_sleeps`, `affects_dominant_pole_only`.
  Variant C moves `trigger_dominance_min`, which is a *different* field from the
  trailing window; the packet flagged that separation as an `[ASSUMPTION]` and it
  is the right place for it to have been flagged.
- **The grief canon holds** (CANON ruling 6). Nothing in any variant lets the
  front recruit for the opposite pole, help the loser, or act on a non-dominant
  NPC. `affects_dominant_pole_only` remains `true` in all three.

One item that would be `TUNING-ONLY` if a reader wanted it recorded as a flag
rather than as a loose end: `cooldown_sleeps_after_expiry` is a §6 open question
by canon's own words ("held at 2 pending campaign-impact measurement"). Touching
it is legal and is the point of the run. Recorded below rather than as a flag.

## Cross-file impact

| File | Impact |
|---|---|
| `rules/rules-v3.9.2-{A,B,C}.json` | New. Three candidates; none ratified. `rules-v3.9.1-C.json` remains the ratified baseline until the Director gates. |
| `CANON.md` | **No change unless the Director rules AMEND.** If a variant is ratified, the Run-23b bullet "Cooldown held at 2 pending campaign-impact measurement" becomes stale and must be rewritten with the measurement that retired it. |
| `CANON-process.md` | None. No process decision is touched. |
| `sim/harness.py` | **None — and this is the load-bearing fact.** Every changed field is already read by the existing scheduler (`GF.get('radius_tiles')`, `GF.get('cooldown_sleeps_after_expiry')`, `GF.get('trigger_dominance_min')`, `GF.get('move_tiles_per_sleep')`). This is a data change, not a code change, which is why it can be measured before it is decided. |
| `build/uhta-slice.html` | Inline `RULES` block would need the same values on port, plus a render pass: r4 is a visibly smaller fog bank, and §2.8 criterion 5 is about whether the player can read it. |
| `outputs/v2/metrics-v3.9.2.md` | New. |
| `reports/contradictions-*.md` | This file. |
| GDD §6 | The "front feel" bullet is the question this run answers; it does not close until a Director ruling lands. |

## Loose ends flagged

*Not contradictions — dials and orderings.*

1. **The measurement canon asked for is not the measurement it got.** Run 23b
   parked cooldown "pending campaign-impact measurement" at 20–25 seeds per arm.
   This run measured 8. The Playtester says so in its Conformance section; canon
   should not treat an 8-seed sweep as having discharged that debt.
2. **A3 argues against shipping A alone.** The Red-Teamer's finding is that r4
   with a 1-tile crawl loses a routed target a sleep sooner than r6 did, and
   recommends co-gating A's radius cut with C's faster crawl. Co-gating is
   precisely the shape the Run-23b salvage took ("the three must ship and be
   re-probed together"), so there is precedent for the Director to follow.
3. **The exposure metric may flatter the result.** The Red-Teamer's own
   `[ASSUMPTION]` block notes `front_exposure` counts stalled members, who take
   the decay and net zero movement — so it overstates wear wherever the shepherded
   are numerous, which is exactly where the spawn anchor puts the fog. A relief
   measured only in exposure is weaker evidence than it looks.
4. **Ordering.** §2.8 criterion 5 is a *render* criterion. Whatever value ships,
   the front-render legibility work is still what closes it, and it is permitted
   under the §2.7 stop rule's carve-out. Tuning the number does not substitute for
   drawing it.
5. **The report-discipline defect** (CANON-process ruling 7) is not addressed by
   this run. The backlog for runs 20–23 remains open.

## Coherence recommendation

`ratify-for-coherence` — with the loose ends above attached.

The three variants are internally consistent with canon, touch only fields canon
leaves open, and preserve every value the Run-23b gate locked. This is a coherence
verdict only and carries no weight on approval, which is the Director's alone. In
particular it is **not** a statement that variant A is the right answer, that 8
seeds is enough evidence, or that anything should ship: those are the three
questions the loose ends exist to put in front of the Director.
```
