# A6 submission runbook

Counterpart to the A3/A4/A5 runbooks. **Due 18 Aug, 11:59 PM ET.**

Deliverables: (1) the pipeline code (Generator, Evaluator, Refiner, Circuit
Breaker), (2) the Pre-Build Declaration (submitted separately before the
build; also reproduced in the README §0), (3) the ReadMe
(`Rouke-uhta-A6-README.md`).

---

## Phase 0 — land the drop

The pipeline was built and verified in the cloud container against a staged
copy of this repo. `a6-drop.tar.gz` was delivered in the chat.

```bat
cd C:\dev\uhta-crew
tar -xzf %USERPROFILE%\Downloads\a6-drop.tar.gz
```

It unpacks ONLY new files — nothing overwrites:

```
ger/{__init__,spec,checks,generator,evaluator,refiner,breaker,pipeline,assemble,fixtures}.py
prompts/{ger-generator,ger-evaluator,ger-refiner}.md
run_ger.py
tests/fixtures/ger/{generator,refiner,evaluator}.json + README.md
Rouke-uhta-A6-README.md
Rouke-uhta-A6-SUBMISSION-RUNBOOK.md
```

Confirm:

```bat
git status --short
```

Everything should be `??` (untracked). If anything shows `M`, stop and read
the diff before continuing.

---

## Phase 1 — verify, before any API call

```bat
python run_ger.py --selftest
```

Expect **`SELFTEST PASSED — 38 assertions`**, exit 0. No key, no calls. Two
of those assertions run against the real build: the register gate must catch
the shipped `guide()` strings, and `TEACHING_TEXT` must extract exactly the
seven spec verbs.

Then confirm nothing regressed in the other three pipelines (`ger/` imports
`crew/` and `content/`; nothing imports `ger/`):

```bat
python run_crew.py --selftest
python run_content.py --selftest
python run_builder.py --selftest
```

All three must still print `SELFTEST PASSED` and exit 0. (Verified in the
cloud for `run_content.py`; `run_crew.py`/`run_builder.py` weren't staged
there, so this is the machine that proves them.)

---

## Phase 2 — the orchestration, without spending anything

```bat
python run_ger.py --mock-llm --run-id mock-demo-a6
```

Expect exit 0 and eight artifacts in `out\mock-demo-a6\`. The fixture script
deliberately walks every path: walk/wait/beacon/sleep accepted at round 0;
**roar** caught by the deterministic gate (`Press R`) and repaired; **flame**
caught by the (mock) judge as EXCEEDS-SCOPE ("the old gods") and repaired;
**raze** failing three different register checks and **ESCALATED** by the
circuit breaker — so `ESCALATED.md` exists in a completed run. Every
artifact is banner-stamped as fixture output.

Optional, 30 seconds: see the global breaker trip.

```bat
python run_ger.py --mock-llm --run-id mock-trip-a6 --escalation-limit 1
```

Expect **exit 1** and `FAILED.md` naming `circuit-breaker` — the halt is the
demo, same as A3's `--drop-agent`.

---

## Phase 3 — the live run

```bat
python run_ger.py --run-id a6-live
```

**Cost:** ~21–35 calls — 7 baseline judgments, 7 generations, 7+ evaluations,
plus refine/re-judge pairs per failure. About $1 and 5–10 minutes, same
envelope as the A4/A5 live runs. Needs `ANTHROPIC_API_KEY` in `.env`
(already there).

### What to check in the output

1. **`out\a6-live\BASELINE-AUDIT.md`** — the strongest page in the
   submission. All seven guide() strings should fail the register gate. Read
   what layer 2 ruled on the stub `roar` line: a CONTRADICTS-CHUNK citing the
   "unconditional Fear push … regardless of flame color" row is the catch the
   README predicts. If the judge PASSes it instead, that is a weaker but
   honest result — say so in the submission rather than re-rolling until it
   fails.
2. **`out\a6-live\GER-LOG.md`** — every round. At temp 0.9 expect roughly
   0–3 verbs to need a refinement; each FAIL must carry a quoted chunk.
3. **`out\a6-live\ESCALATED.md`** — probably absent in a live run (the mock
   run is where escalation is guaranteed demonstrated). If present, it is
   evidence, not embarrassment: that is the breaker doing its job.
4. **`out\a6-live\teaching-lines.md`** — the seven lines, ending at the
   unfilled Director selection block.

### If it halts

`FAILED.md` names the agent and the stage. An `AgentError` halt is a broken
contract (retry-able — runs are independent); a `BREAKER_TRIPPED` manifest
status means ≥3 verbs escalated and the prompts/spec need a look before
re-running.

---

## Phase 4 — put the words in the game

The pipeline modifies nothing in place. Two equivalent routes; the second is
one command:

```bat
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-a6.html
copy out\a6-live\uhta-slice.patched.html blackboard\build\uhta-slice.html
```

Open `blackboard\build\uhta-slice.html`, check the self-test panel (bottom
left) — **13/13 PASS**, including G12/G13 which gate this exact mechanism.
Play to the first Sleep: each verb narrated once, in the new lines, and the
words stop. Then fill in the `## Director selection` block in
`teaching-lines.md`.

If you'd rather apply by hand, `teaching-text.snippet.js` replaces the single
`const TEACHING_TEXT={...};` line.

---

## Phase 5 — commit

**The gitignore trap, same as every assignment.** `out/*` is ignored except
`.gitkeep`; force-add the run:

```bat
git add ger/ prompts/ger-generator.md prompts/ger-evaluator.md prompts/ger-refiner.md
git add run_ger.py tests/fixtures/ger/
git add Rouke-uhta-A6-README.md Rouke-uhta-A6-SUBMISSION-RUNBOOK.md
git add blackboard/build/uhta-slice.html
git add -f out/a6-live/
git add -f out/mock-demo-a6/
git status --short
```

`git status` must show `out/a6-live/BASELINE-AUDIT.md`, `GER-LOG.md`,
`teaching-lines.md`, `teaching-text.snippet.js`, `RUN-LOG.md`,
`manifest.json` (and `ESCALATED.md` if produced) as staged. The mock run is
worth committing too — it is the only run guaranteed to show the breaker.

```bat
git commit -m "Assignment 6: two GER pipelines (narration + mini-games), live runs, dashboard, play-probe"
git tag assignment-6-ger
git tag assignment-6-minigame
git push origin main --tags
```

---

## Phase 6 — submit

1. **Pipeline code** — the repo / tag:
   `https://github.com/Billy13ean/uhta-crew/tree/assignment-6-ger`
2. **Pre-Build Declaration** — already submitted before the build; §0 of the
   README reproduces it verbatim.
3. **ReadMe** — `Rouke-uhta-A6-README.md`. Stands alone if the grader wants a
   single document: it names the game, the content type, the GDD rule (with
   the two-layer enforcement table), and the baseline-audit catches.

## Known gaps, stated rather than hidden

- **The live baseline verdicts are the model's, not guaranteed.** The mock
  run's roar-stub catch is canned; the README says which is which, and the
  live `BASELINE-AUDIT.md` is the citable one.
- **The register gate's thresholds (120 chars / 24 words) and the breaker's
  (2 rounds, 3 escalations) are stated policy, not measured optima.**
- **Escalated verbs ship the old stub** in the patched build, marked in
  `teaching-lines.md` — the pipeline never silently substitutes.
- **run_crew / run_builder non-regression was not re-verifiable in the
  cloud** (not staged); Phase 1 on this machine is the check.
