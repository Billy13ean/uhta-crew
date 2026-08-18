# A6 pipeline #2 (mini-game) submission runbook

Companion to `Rouke-uhta-A6-SUBMISSION-RUNBOOK.md` (pipeline #1). Same
deadline, same repo, same commit — this covers only what pipeline #2 adds.

---

## Phase 0 — land the drop

`a6-minigame-drop.tar.gz` was delivered in the chat (and extracted directly
into the repo if the desktop bridge was connected — check first):

```powershell
cd C:\dev\uhta-crew
git status --short   # if minigame/ files already show as ??, skip the tar
tar -xzf $env:USERPROFILE\Downloads\a6-minigame-drop.tar.gz
```

It unpacks ONLY new files:

```
minigame/{__init__,spec,checks,corpus,agents,builder_stage,pipeline,assemble,fixtures}.py
prompts/{minigame-designer,minigame-judge,minigame-refiner,minigame-programmer}.md
run_minigame.py
tests/fixtures/minigame/{designs,refiner,judge,programmer}.json + README.md
blackboard/research/minigame-patterns.md
Rouke-uhta-A6-MINIGAME-README.md
Rouke-uhta-A6-MINIGAME-RUNBOOK.md
```

## Phase 1 — verify, no API

```powershell
python run_minigame.py --selftest      # SELFTEST PASSED — 38 assertions
python run_ger.py --selftest           # still green (nothing imports minigame/)
python run_content.py --selftest       # still green
```

## Phase 2 — the full orchestration, no API

```powershell
python run_minigame.py --mock-llm --run-id mock-demo-mg
python run_minigame.py --mock-llm --build --select first-contact-hope --from-run mock-demo-mg --run-id mock-build-mg
python run_minigame.py --mock-llm --build --select holding-fear --from-run mock-demo-mg
```

Expect: propose exit 0 with `MG-ESCALATED.md` present (holding-fear
escalates by script); build exit 0 with `uhta-slice.minigame.patched.html`
and all post-checks green; the third command **exit 1** — selecting an
escalated design is refused, which is the human gate demonstrated at the
command line.

## Phase 3 — live propose (~$1, 5–10 min)

```powershell
python run_minigame.py --run-id mg-live
```

Read `out\mg-live\MINIGAME-CANDIDATES.md`. This is YOUR gate: pick the one
design you'd actually want in the game (the accepted-ids line at the bottom
lists what is selectable). Fill in the selection block — that written ruling
is submission evidence.

## Phase 4 — live build of your selection

*(Build v2/v3: the build phase runs Instructor → Presenter → Programmer
under the FIVE-anchor contract — the encounter lives in the per-frame
seat, owns the pointer while active, displays a first-use narration line
on sleep 0, dims the world when it begins, and **opening the file with
`#mg` in the URL force-arms it** for verification. The current evidence
run is `out\mg-live-build-v3`.)*

Fastest verification, straight from the terminal (no copying needed — the
patched file is self-contained):

```powershell
start "" "file:///C:/dev/uhta-crew/out/mg-live-build-v3/uhta-slice.minigame.patched.html#mg"
```

Click a path on the title screen; the encounter arms immediately. If the
`#mg` fragment is lost, add it in the address bar and press **F5** (a hash
change alone does not reload).

```powershell
python run_minigame.py --build --select <your-pick> --from-run mg-live --run-id mg-live-build
```

1–2 large Programmer calls. If it halts after the repair round, `FAILED.md`
carries both rounds of checker errors — re-running is safe, and an honest
"the Programmer could not satisfy the contract tonight" plus the propose run
is still a complete GER submission (the mock build proves the contract).

Then apply and verify (this stays out of the canonical build unless you rule
otherwise — the stop rule is yours):

```powershell
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\mg-live-build\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open it: every G-assertion AND the new M-assertion(s) green; play to the
encounter; judge it with the MINIGAME-BUILD.md checklist. Restore
`uhta-slice.pre-mg.html` afterwards if you don't want the encounter in the
submitted A6 build — the patched file in `out\mg-live-build\` is the
evidence either way.

## Phase 5 — commit (merged with pipeline #1's Phase 5)

```powershell
git add minigame/ run_minigame.py prompts/minigame-*.md tests/fixtures/minigame/
git add blackboard/research/minigame-patterns.md
git add Rouke-uhta-A6-MINIGAME-README.md Rouke-uhta-A6-MINIGAME-RUNBOOK.md
git add -f out/mg-live/ out/mg-live-build/ out/mock-demo-mg/ out/mock-build-mg/
```

Then the single A6 commit/tag/push from the pipeline #1 runbook covers both.

## Phase 6 — submit

Two pipelines, two tags on the same commit: `assignment-6-ger` and
`assignment-6-minigame` — submit each pipeline with its own tag URL + README
(`Rouke-uhta-A6-README.md`, `Rouke-uhta-A6-MINIGAME-README.md`). Each README
carries its own Pre-Build Declaration in §0.

## Known gaps, stated rather than hidden

- The live Programmer patch may need its repair round or may fail twice;
  the contract makes that loud, not silent.
- The mock build's patch is a hand-authored fixture proving the CONTRACT,
  not a designed game — its banner and README say so.
- Applying any encounter to the canonical slice remains gated on the GDD
  §3 stop rule / stranger test. This pipeline moves design and build behind
  human gates; it does not move the shipping decision.

## The Director's dashboard (submission centerpiece)

Every propose run now emits **`MINIGAME-DASHBOARD.html`** — the human gate
as an interactive checklist. Open it in a browser: one card per candidate
with THE RULES and THE VISUALS (drop-in for the render layer), the Judge's
cited verdict, and a BUILT badge where a playable exists. Check what you
approve → **Generate Director's ruling** → the page produces the signed
selection block plus the exact `run_minigame.py --build --select ...`
command per approved item, downloadable as `DIRECTOR-SELECTION.md`. The
gate stays structural: the dashboard writes the command; a human runs it.
The mg-live dashboard is at `out\mg-live\MINIGAME-DASHBOARD.html`.
