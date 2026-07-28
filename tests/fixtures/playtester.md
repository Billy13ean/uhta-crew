```markdown
## Reading the board

**This is a mock-LLM fixture, so this paragraph quotes no numbers — and that
absence is the honest thing about it.** In a live run the Playtester reads the
consolidated board printed directly above and names the values: which arms moved
between the baseline and variants A/B/C, by how much, and whether the movement is
larger than 8 seeds can distinguish. A fixture cannot do that, because the fixture
was written before the harness ran and the board above was generated *from* the
run. What a reader can verify without any model at all: the board and the raw
facts appendix in this document are machine-generated from `execution-log.json`,
which records one real subprocess execution of `blackboard/sim/harness.py` per
(arm × ruleset), and those numbers are as real in a mock run as in a live one.

The structural expectations the live reading would test: P5 (`bot_do_nothing`)
must show `losses == n` and zero fronts on every ruleset — the passive baseline is
the safety floor and is not negotiable. P4 (`run_selfburn`) must show
`median_selfburns` of 0 everywhere; a non-zero value there is an implementation
bug, not a balance finding. P1/P2a (`bot_throughput`) carry the actual question — whether A's
radius-and-cooldown cut moves `median_front_exposure` and
`median_fronts_spawned` — and P2b (`run_campaign_v3`) checks it did so without
moving `wins`.

## Regression + attack verdicts

*(Fixture: verdict lines below carry the invariant and the shape of the
judgement, with `<measured>` where a live run substitutes the number from the
board. A live Playtester writes the number; this one cannot and will not
invent one.)*

- P5 (A5) — invariant: "every seed still reaches the apathy loss (losses == n) and median_fronts_spawned is 0" | measured: `<from board>` | **PASS expected — check the board**
- P4 (A4) — invariant: "max_selfburns is exactly 0 in every arm" | measured: `<from board>` | **PASS expected — check the board**
- P1 (A1) — invariant: "median_front_exposure on variant A is materially below the baseline arm" | measured: `<from board>` | **verdict requires the number**
- P2a (A2) — invariant: "median_fronts_spawned falls on A relative to baseline" | measured: `<from board>` | **verdict requires the number**
- P2b (A2) — invariant: "wins on A stay within 1 of the baseline arm and median_terminal_sleep within 2 sleeps" | measured: `<from board>` | **verdict requires the number**
- P3 (A3) — invariant: "median_heads on A stays within 1 of the baseline arm" | measured: `<from board>` | **verdict requires the number**
- P6 (A6) — invariant: "median_final_wf and wins on A stay within the baseline arm's values" | measured: `<from board>` | **verdict requires the number**
- P7 (A7) — invariant: "median_max_wf and wins on every variant match the baseline arm" | measured: `<from board>` | **PASS expected — check the board.** Note this arm ran a crew shim (see the "Policy shims in force" table below); it measures the shimmed policy, not `bots.py::run_tyrant` as written.

## Open tuning lever(s)

**Cooldown.** CANON v17 parks it explicitly — "cooldown held at 2 pending
campaign-impact measurement" — and variants A (4) and B (3) are the measurement.
The sweep that answers it is the one on the board: campaign arms at cooldown
2/3/4 with everything else held, read on `median_fronts_spawned`,
`median_front_exposure` and `wins` together. Reading any one of the three alone
is how a cadence change gets mistaken for a balance change.

**Radius versus duration.** A and B buy relief by different mechanisms — area
against dwell — and the run cannot separate them at 8 seeds. That is a sample-size
statement, not a result.

## Conformance re-confirmed

**Verified this run:** that every validated variant loads into the reference sim
and completes its arms; that the passive-baseline and self-burn controls run on
every ruleset; that all four Run-23b closures (`spawn_at`,
`trigger_trailing_window_sleeps`, `affects_dominant_pole_only`, `front_strength`)
are byte-identical to the baseline in every variant, since no variant proposed
changing them.

**NOT verified this run, and a reader should hold these against the board:**

- **Seed count.** 8 seeds, against the uhta standard of 20 (metrics-v3.9.1 runs
  20–25 per arm). Anything smaller than about a 2-win swing is inside the noise.
- **Legacy equivalence.** No `enabled: false` arm ran, so the 80/80 bit-identity
  check that gated v3.9.1 has not been repeated here.
- **The in-sphere stall itself.** No isolated arithmetic probe ran. The stall is
  argued from the JSON (`front_strength` unchanged at 4.0) rather than measured.
- **`[ASSUMPTION]` H-1/H-2** (static positions, Chebyshev distances, roads as an
  adjacency count) are in force throughout, per the harness docstring ledger.
- **The combined exploit surface** (GDD §5.6) is still un-re-attacked. This run
  attacked one field group.
```
