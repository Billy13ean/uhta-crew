# Assignment 9 — Adversarial QA Agent · *uhta*

> Nicholas Rouke · ELVTR Multi-Agent AI for Game Development · due 27 Aug 2026

**Game:** *uhta* — the vertical slice at `blackboard/build/uhta-slice.html` (Phaser, single HTML file, on-load self-test 13/13).
**Agent:** `tools/chaos_probe.js` — a seeded chaos agent that drives the real build in headless Chromium via Playwright and actively tries to break it.
**Reports:** `out/a9-chaos/chaos-report-seed7.json`, `-seed23.json`, `-idle.json` (headless), and `live-run.json` (headed, human-paced — the run that found F02).

## What "broken" means (the agent's strategy)

The agent does not look for anything vague. Ten invariants are declared up front, and a finding exists only when one is violated:

I1 zero page/console errors, ever · I2 the avatar stays inside the 48×48 map · I3 no NPC ever holds NaN state and |v| never exceeds the zealot pin (±12) · I4 population never hits 0 or runs away · I5 the stamina ledger never goes NaN, the budget never goes negative · I6 a terminal, once fired, never changes (a win cannot become a loss) · I7 the phase machine holds only known states and input after a terminal is inert-safe · I8 camera zoom stays inside its clamp under wheel abuse · I9 the build's own 13-check self-test still fully passes *after* an entire chaos run · I10 the world is never stuck — real input during play advances the tick counter, and when it doesn't, the agent diagnoses *why* before calling it a freeze.

Everything else the agent does is pressure applied to make one of those break: hammering the title screen, marching into all four map edges, 120 random keys including ones the game never bound, 80-click storms, extreme scroll-zoom in both directions, right-click roars aimed off the map, spamming beacon/raze/art-pass toggles, draining the entire wake budget and then poking every verb, riding forty real generations to a terminal, mashing input after the run has ended, viewport resizes mid-play, and five rapid `newGame()` replays. Runs are seeded (`--seed`), so every finding reproduces.

## What the agent found

**F01 — `ZERO_STAMINA_NO_FEEDBACK` · stamina economy / input feedback · medium.** When the wake budget is exhausted, walk, flame, roar, beacon, and raze all silently do nothing — `moveStep()` and `tryAct()` bail with a bare `return` — the tick counter holds still, and the tip line never changes. Wait and Sleep still function (Wait costs 0 by design), but nothing on screen tells the player that Sleep is now the only meaningful verb. Reproduces on every seed tested (7 and 23; full game context with input tail in the reports, e.g. seed 7: sleep 3, tick 41, pos [20,21]). A first-time player who spends their budget in the opening minute experiences this as "the game stopped responding" — exactly the first-30-seconds bounce Class 13 warned about. Suggested fix is one line: `setTip('You are spent. Sleep (space) brings the next generation.')` in the early-return path.

**What did *not* break, which is the other half of the result.** Across all three runs: zero page errors (I1), the position clamp held at all four edges (I2), no NaN or over-pin NPC state ever appeared (I3), population stayed bounded through generation churn (I4), the terminal never mutated once fired (I6), zoom respected its 0.55–2.2 clamp under ±12,000-unit wheel deltas (I8), the do-nothing control arm reached its apathy loss rather than idling forever, five rapid replays leaked nothing into the fresh run, and the build's own 13-check self-test was still fully green after every chaos session (I9).

**F02 — `NO_ENDING_FOR_IDLE_RUN` · win/loss check (apathy loss) / ambient contagion · medium — found only by the live headed run.** Run at full headless speed, an idle run reaches its apathy loss (the do-nothing control arm ends, matching the reference harness's sleep-24 baseline). Run headed with `--slow 120` — human pacing — the same seed idles through **40 generations with no ending** (`out/a9-chaos/live-run.json`: sleep 47, tick 194, no terminal). The cause is a design-boundary leak: the slice's ambient peer-contagion beat fires on a **wall-clock timer** (every 1.05 s), decoupled from sim ticks, and it mutates NPC belief — so a slow player gets many more alignment beats per generation than a fast one, and grey never claims 0.8. The beat was labeled "presentation — the Sim core is untouched," but it is a sim force the reference harness never models and the self-test cannot see (it compares fresh Worlds, not the live one). The fix is a design decision (tie the beat to ticks, cap its per-generation effect, or re-tune the loss), so per this project's own process it is logged as an open question for the crew (`BACKLOG-later.md` #2), not quietly patched.

**Status: F01 fixed and re-verified; F02 open by design.** The finding shipped: `moveStep()`'s and `tryAct()`'s early-return paths now call `spentTip()` — *"You are spent. Sleep — space — brings the next generation."* — before bailing. After the fix, the build's self-test is still 13/13 and the same probe on the same seed (`--seed 7`) reports zero findings: the agent that found the bug is the agent that verified the repair. The committed reports in `out/a9-chaos/` are the pre-fix runs, kept as the evidence.

## Was I surprised?

Three times. The third and best: the finding my agent could only make **at human speed**. Every headless run said an idle player gets their ending; the first headed run at `--slow 120` proved they don't, because a wall-clock game system behaves differently under a slow hand than a fast script. An adversarial agent that only runs at machine speed is blind to an entire class of bug — the ones that live in the difference between how bots play and how people do. That one finding justified building the `--headed`/`--slow` mode.

First, by how little broke: this build has survived thirteen harness-verified ruleset generations and six director playtest iterations, and it shows — the chaos agent's whole arsenal produced one finding, and it's a feedback gap, not a crash. Second, by my own agent's first misdiagnosis: its stuck-detector initially reported `WORLD_STUCK` (tick frozen despite movement input), and the truth was the stamina system working as designed with no one telling the player. The agent had reproduced *the player's experience of the bug* rather than the bug — which is what convinced me the finding is real and worth fixing, and taught the agent to diagnose the cause (it now checks whether Sleep still works and reads the remaining budget before it cries freeze).

## Reproduce

```
node tools/chaos_probe.js blackboard/build/uhta-slice.html --seed 7  --out out/a9-chaos/chaos-report-seed7.json
node tools/chaos_probe.js blackboard/build/uhta-slice.html --seed 23 --out out/a9-chaos/chaos-report-seed23.json
node tools/chaos_probe.js blackboard/build/uhta-slice.html --seed 11 --arm idle --out out/a9-chaos/chaos-report-idle.json
```

Requires the `playwright` package (same dependency as `tools/mg_probe.js`, the A6 play-probe this agent descends from). Each run prints and writes one JSON report: invariants, behaviors run, whether a terminal was reached, self-test status after chaos, and findings with the required fields — location (mechanic/system), error type, and game context (seed, phase, sleep, tick, position, pole, population, terminal, and the last twelve raw inputs before the finding).
