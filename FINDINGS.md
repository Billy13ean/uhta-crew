# FINDINGS — defects this crew surfaced in the uhta game repo

Things the crew found by running against the real blackboard, for the Director's
work queue. Each entry names what it is, how it surfaced, what the crew does
about it now, and what the fix in the **game repo** would be.

The crew never edits `blackboard/sim/` — those files are vendored byte-identical
from the game repo, and the Playtester owns them (GDD §3.1). A crew that quietly
rewrote the reference suite to make its own arms pass would be manufacturing the
evidence it then reports. So every workaround lives in crew-side code, is
labelled as a workaround, and is logged every time it runs.

---

## 1. `run_tyrant` is genesis-incompatible — hard-coded tribe index

**What it is.** `sim/bots.py::run_tyrant` calls `make_flamer(2, -1)`, targeting
tribe index 2. That index is correct for the **legacy** start
(`zealot_poles=(-1,-1,1)`, three pre-clustered tribes) where index 2 is the hope
tribe — the one opposing the fear player. The ratified baseline
`rules-v3.9.1-C.json` enables `world.genesis` with `founding_poles: [-1, 1]`, so
the world begins with **two** tribes and grows by schism. `w.tribes[2]` raises
`IndexError` on the first wake.

**How it was found.** A `--mock-llm` crew run whose fixture attack list named
`run_tyrant` as a pole-balance probe. Every seed raised; the arm produced nothing.
It has presumably been silently unusable since the Run-20 genesis gate — the
canonical tyrant regression from `metrics-v2`/`v3.x` cannot have been re-run
against any genesis-enabled ruleset.

**Blast radius.** `run_tyrant` is one of the Playtester's baseline roster arms
(`prompts/v2/playtester.md`, hard rule 4). Any metrics file claiming a tyrant
result on a genesis ruleset is either stale or was not actually run.

**What the crew does about it.** `crew/policy_shims.py` provides a genesis-safe
`run_tyrant` and `crew/probe_runner.py` routes the policy name there instead of
to `bots.py`. The shim reproduces the policy's *intent* rather than its literal
index: resolve the target **once, at t0**, as the first tribe whose pole opposes
the player's — which is what index 2 meant in the world the policy was written
for. Resolving once (not per-wake) matters, because schism grows the tribe list
mid-run and re-picking would be a different policy under the same name. Pole,
15-sleep cap and the acting bot (`bots.make_flamer`) are unchanged.

Every shimmed arm is stamped: a `SHIM:` line in `RUN-LOG.md` per arm, and a
declared **"Policy shims in force"** table in `metrics-vN.md` above the raw-facts
appendix. A shimmed number is never presented as a measurement of the upstream
policy as written.

**Measured after the shim** — `rules-v3.9.1-C`, seeds 0–7, cap 15, fear pole:

| metric | value |
|---|---|
| seed errors | **0** (was 8/8 `IndexError`) |
| wins | 1/8 (seed 7, at sleep 14) |
| `max_wf` per seed | 0.372, 0.398, 0.529, 0.552, 0.823, 0.667, 0.496, 0.938 (median 0.540) |
| `fronts_spawned` per seed | 0, 0, 0, 0, 2, 1, 0, 2 |

A live arm with a real spread, not a crash converted into noise. One honest
caveat: at 8 seeds the **medians** are identical across `rules-v3.9.1-C` and the
v3.9.2 fixture variants — only per-seed front counts move (seed 7: 2→1 under
variant A; seed 4: 2→1 under variant C). Read it as a fear-pole *regression
control* that should stay flat, where a move is the signal — not as a
discriminator between small data changes.

**The fix in the game repo.** One line in `sim/bots.py`:

```python
def run_tyrant(seed):
    w = World(seed); w.player_pole = -1
    target = next((t.idx for t in w.tribes if t.pole == 1), w.tribes[-1].idx)
    bot = make_flamer(target, -1)
    ...
```

Once that lands, delete the entry from `crew/policy_shims.py::SHIMS` — the shim
is designed to be removable, and the registry is the list of things the game repo
still owes.

---

## 2. Composite bots do not carry the grief-front counters

**What it is.** `harness.run()` returns a stat dict including `fronts_spawned`,
`front_exposure`, `final_lf` and `pop`. The composite policies in `bots.py` —
`run_campaign_v3`, `run_siege`, `run_selfburn` — do not go through
`harness.run()`; each builds its own return dict from a subset of world state, and
none of them includes the grief-front counters. So the campaign bot, which the
project treats as the canonical winning line, **cannot answer any question about
the antagonist.**

**How it was found.** A crew run whose attack list asked for
`median_front_exposure` on a `run_campaign_v3` arm. The probe executed fine and
the metric came back empty; the board rendered `—`. Nothing crashed, which is
exactly why it is worth writing down — this one fails silently.

**Blast radius.** Any front-feel question routed to the campaign or siege arms
returns nothing. In practice it means grief-front tuning has to be measured on
`bot_throughput` or `make_flamer`, which are naive policies, while the
sophisticated policy stays blind to the mechanic the project is currently tuning.

**What the crew does about it.** Nothing — and deliberately. This is a real
limitation of the reference suite, not a bug to wrap: a shim here would have to
invent a return contract for three policies, which is a design decision the
Playtester and the Director own. Instead `prompts/red-teamer.md` carries a
policy→metric table, so the Red-Teamer picks a policy that emits the metric its
invariant names rather than spending an arm to learn it. The Playtester is
required to say "not measured this run" instead of filling the gap.

**The fix in the game repo.** Have the composite bots return a superset — either
by folding the same end-of-run block `harness.run()` uses into each one, or by
factoring that block into a `harness.summarize(world)` helper the composites call.
Mechanical, no behaviour change, and it would make the campaign arm usable for
antagonist work.

---

*Both entries were produced by running the crew, not by reading the code. That is
the argument for the pipeline: the validation gate and the real-execution
Playtester are what turn "the suite looks fine" into "arm P6 raised on 8 of 8
seeds, here is the exception."*
