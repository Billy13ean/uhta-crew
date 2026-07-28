```markdown
# Context packet — mechanic-designer — v3.9.2 | for run: front feel — soften unshepherded straggler wear without weakening the in-sphere stall

## CANON digest (verbatim)

*(In a live run this section carries `blackboard/CANON.md` reproduced verbatim,
~900 words, per the Mode-A cap. It is omitted from this fixture only because a
fixture that duplicated the digest would be 6 KB of text no one reads twice; the
live Keeper does not omit it, and `crew/agents/keeper.py` passes it the real
file.)*

The load-bearing lines for this run:

- **CANON ruling 6 — GRIEF CANON.** "Grief is not a pole — it is the *gravity*.
  Long-term grief traps people in apathy; the per-tick decay toward 0 IS
  Uhtcearu's grief. Uhtcearu never fights for a color; he drowns the board in
  grey. Catastrophes therefore wear the dominant pole toward 0 and never recruit
  for the opposite." **Locked.**
- **Run 23b salvage block, all five bullets.** `front_strength 4.0` → inside-front
  decay 2.0/tick exactly equals zealot pull: a true STALL, and "the front can
  never flip (decay can't cross 0), burn (decay is not same-pole pressure), or
  kill. Stragglers bounded by the step cap at −1/tick." `spawn_at
  largest_dominant_pole_tribe_position`. `trigger_trailing_window_sleeps 3`.
  `affects_dominant_pole_only true`. **"Cooldown held at 2 (3-on/2-off, ~0.65
  late-game uptime)."**
- **Verified band.** "hope campaign 23→21/25 at unchanged median, fear 16/20
  untouched; 96% of fronts do real work; no front-as-shield, no in-front haven,
  no high-dominance sandwich."
- **Open questions, first item:** "front feel items."

## Canon lines this run touches

This is the mechanism correction the Run-23 tie-bug miss bought (GDD §3.2): a
packet must name the canon *lines*, not just the GDD sections.

| Canon line | Status for this run | Why it is named |
|---|---|---|
| CANON v17 ruling 6 (grief canon) | **LOCKED — may not move** | Any variant that made the front recruit, flip, or help the loser contradicts it directly. |
| Run-23b bullet 1, `front_strength 4.0` | **LOCKED by gate** | It is the stall. The question set forbids weakening it, and the arithmetic 0.4 × (1+4.0) = 2.0 = zealot pull is the whole claim. |
| Run-23b bullet 2, `spawn_at` | **LOCKED by gate** | Closes the GF6 siege engine at the spawn gate. |
| Run-23b bullet 3, `trigger_trailing_window_sleeps 3` | **LOCKED by gate** | Closes the GF5 hover-sprint shadow. `trigger_dominance_min` is a *separate* field and is not locked by this bullet. |
| Run-23b bullet 4, `affects_dominant_pole_only` | **LOCKED by gate** | Closes the cleanup-assist. |
| Run-23b bullet 5, cooldown 2 | **EXPLICITLY OPEN** — "held at 2 **pending campaign-impact measurement**" | This is the dial canon parked. It is the natural centre of this run. |
| CANON open questions, "front feel items" | **OPEN (§6)** | The authority for the run existing at all. |
| `win_loss` in all its parts, `scale`, `bands` | **LOCKED — out of scope** | Not touched by front feel. |
| `hope_trade` | **LOCKED disabled** (Runs 20–22) | Named so a variant does not "tidy" it back on. |

## Relevant specification excerpts (cite §)

**§2, the antagonist.** "Grief has no position on the scale because grief is not a
pole — **it is the gravity** … past trailing-window dominance 0.55, a visible
desaturating fog bank condenses **on the winner's largest tribe** for 3 sleeps
(cooldown 2). Inside it, grief exactly cancels a zealot's pull (front decay
2.0/tick = pull 2.0/tick): the shepherded **stall** — never flipped, burned, or
killed — while unshepherded believers grey quickly. It wears only the dominant
pole (grief never helps anyone), and it cannot fire in a do-nothing run by
construction. *Grief takes the stragglers; the shepherded stand.*"

**§2, contagion arithmetic.** "Each tick an NPC sums the pressure on it and steps
**at most 1**: its zealot's pull **2.0/tick**, overlapping spheres **0.8** (sphere
radius 2 + floor(√group)), peer contagion **0.1/neighbor within r2, capped
0.7/tick** (apathy spreads too), and passive decay **0.4/tick** toward 0."

**§2.8, criterion 5 — the reason this run exists.** "Can point at the grey fog
bank and say what it is doing to them. **Untested — predicted at risk.** The
front stalls camps but erases loners at ~2.4× the pre-salvage rate; the render
must sell both readings."

**§6, open questions.** "Front feel (straggler wear saturates the step cap —
~2.4× pre-salvage; render must sell 'stalls camps, erases loners')."

**§3.5, verification layers.** "Validation happens before anything is compiled or
imported." Note for the Designer: a deterministic gate derives its required key
set from the baseline file and will reject any variant missing a path. Emit
complete rules files.

## The baseline ruleset and what may move

The ratified baseline is `rules-v3.9.1-C.json` (schema 3.9.1). *(The live packet
carries it verbatim; `crew/agents/keeper.py` passes the real file.)*

**May move** — `world.uhtcearu_events.grief_front`: `radius_tiles`,
`duration_sleeps`, `cooldown_sleeps_after_expiry`, `trigger_dominance_min`,
`move_tiles_per_sleep`.

**May not move** — `front_strength`, `spawn_at`, `move_toward`,
`trigger_trailing_window_sleeps`, `affects_dominant_pole_only`, `zealots_immune`,
`inside_replaces_dominance_term`, `outside_dominance_scale`,
`max_concurrent_fronts`; and everything outside `grief_front`.

## Open questions in scope for this run

1. Front feel — straggler wear saturating the ±1 step cap (§6, the top item).
2. Cooldown duty cycle at 2 — the value CANON parked pending measurement.
3. Whether relief is better bought geometrically (radius), temporally (duration),
   or by cadence (cooldown / trigger). This run's whole job is to separate them.

## Excluded from this packet (item — one-line reason)

- **GDD §2.7 build order and §2.8 rows 1–4, 6** — a data-only tuning change builds
  nothing, so the stop rule and the other playability criteria do not bind it;
  criterion 5 is included because it is the criterion this run serves.
- **§3.1 roster, §3.2 Keeper contract, §3.4 player-facing table** — process canon;
  the Designer's job is numbers, and roster detail is context it would have to
  ignore.
- **§4.2 RAG corpus and the Writer/Critic pipeline** — a different pipeline
  entirely (the 7/30 deliverable); no overlap with the ruleset.
- **§4.3 budgets, §7 provenance** — history and cost, not constraints on a dial.
- **§5 items 1–4, 7, 8** — resolved or non-mechanical. Item 6 (the un-re-attacked
  combined exploit surface) is *not* excluded and is flagged to the Red-Teamer.
- **`sim/harness.py` source** — the Designer proposes data, never code (hard rule
  2). The Playtester reads the harness; the Designer does not.
- **`zealot_fate`, `schism`, `road_allegiance`, `faction_fight` blocks** — real
  canon, but untouched by front feel. Excluding them keeps the packet under the
  15K target and keeps the Designer's hands where the question is.

## Assumptions

- `[ASSUMPTION]` That "soften straggler wear" means reduce total exposure
  (NPC-sleeps inside a front), not reduce per-tick decay — because per-tick decay
  is `front_strength`, which the question set locks. The Designer should state if
  it reads the brief otherwise.
- `[ASSUMPTION]` That `trigger_dominance_min` is separable from
  `trigger_trailing_window_sleeps`. The Run-23b bullet locks the *window*; the
  threshold is a distinct field. If the Director intended both locked, this
  packet has cut wrongly and the exclusion list is where that becomes visible.
```
