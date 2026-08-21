# A7 submission runbook

Counterpart to the A3–A6 runbooks. **Due 20 Aug, 11:59 PM ET.**

Deliverables: (1) the style guide (`style/STYLEGUIDE.md`), (2) the loop code
(`style/` + `run_style.py`), (3) before/after demos (the live run's
`BEFORE-AFTER.md`), (4) the pipeline sentence (README §0).

---

## Phase 0 — land the drop

```bat
cd C:\dev\uhta-crew
tar -xzf %USERPROFILE%\Downloads\a7-drop.tar.gz
git status --short
```

It unpacks ONLY new files — nothing overwrites:

```
style/{__init__,spec,checks,llm,agents,pipeline,fixtures}.py
style/STYLEGUIDE.md
prompts/{style-generator,style-evaluator,style-refiner}.md
run_style.py
Rouke-uhta-A7-README.md
Rouke-uhta-A7-SUBMISSION-RUNBOOK.md
```

Everything should be `??` (untracked). If anything shows `M`, stop and read
the diff before continuing.

## Phase 1 — verify, before any API call

```bat
python run_style.py --selftest
```

Expect **`SELFTEST PASSED — 38 assertions`**, exit 0. No key, no calls.
Then confirm nothing regressed (`style/` imports nothing from `crew/`,
`content/`, `builder/` or `ger/`; nothing imports `style/`):

```bat
python run_crew.py --selftest
python run_content.py --selftest
python run_builder.py --selftest
python run_ger.py --selftest
```

All four must still print `SELFTEST PASSED` and exit 0. (Not verifiable in
the cloud — this machine proves them, same as every assignment.)

## Phase 2 — the orchestration, without spending anything

```bat
python run_style.py --mock-llm --run-id mock-demo-a7
```

Exit 0, artifacts in `out\mock-demo-a7\`. The fixture script deliberately
walks every path: **era-nomad / era-village** accepted round 0;
**demo-tone / demo-vocab / demo-format** each caught with a low SCORE +
REASON and repaired to 10/10 (the rubric's three classes; live acceptance
is ≥9, see README "Live calibration");
**era-victorian ESCALATED** by the breaker, so `ESCALATED.md` exists in a
completed run. Every artifact is banner-stamped as fixture output.

Optional, 30 seconds — the breaker trip:

```bat
python run_style.py --mock-llm --run-id mock-trip-a7 --escalation-limit 1
```

Expect **exit 1** and `FAILED.md` naming `circuit-breaker`.

## Phase 3 — the live run

```bat
python run_style.py --run-id a7-live
```

~15–30 calls (6 generations, 6+ evaluations, refine/re-eval pairs per
failure), well under $1, a few minutes. Needs `ANTHROPIC_API_KEY` in `.env`.

What to check:

1. **`out\a7-live\BEFORE-AFTER.md`** — the submission's centerpiece. All
   three sabotage items should score low with rule-citing REASONs and come
   back repaired. If a sabotage line somehow scores high, that is a weaker
   but honest result — say so rather than re-rolling until it fails.
2. **`out\a7-live\STYLE-LOG.md`** — every round; each sub-10 score must
   carry a REASON citing rule IDs.
3. **`out\a7-live\candidates.md`** — era candidates, ending at the unfilled
   Director selection block. Fill it after review (or in a console run room
   once a `style` card is added — optional, post-submission).
4. **`ESCALATED.md`** if present is evidence, not embarrassment.

## Phase 3b — regenerate the visual guide from YOUR current art

The drop ships the generator only — no pre-rendered HTML. The `art/`
scripts were restored into the repo from the project snapshots (they were
missing from the working tree), so the citable page is built on your
machine from exactly what is committed:

```bat
python art\make_sprites.py
python art\make_scene.py
python art\make_temple_scene.py
python art\make_title_scene.py
python style\make_visual_guide.py --no-inspiration
```

(`--no-inspiration` keeps local reference screenshots out of the committed
page; drop the flag for your own reference render.)

Open `style\VISUAL-GUIDE.html` and check: the palette swatches, the era
characters, the avatar veins/vines, the three scenes, and the palette-audit
table (sprites near 0%% off-palette; scenes may drift — reported, not
failed). If your current scripts output to a different folder, point at it:
`python style\make_visual_guide.py --assets <path>`. Anything in
`style\inspiration\` gets absorbed on the same run.

## Phase 4 — commit

The gitignore trap, same as every assignment — force-add the runs:

```bat
git add style/ prompts/style-generator.md prompts/style-evaluator.md prompts/style-refiner.md
git add style/VISUAL-GUIDE.html style/inspiration/README.md
git add run_style.py Rouke-uhta-A7-README.md Rouke-uhta-A7-SUBMISSION-RUNBOOK.md
git add art/ Dockerfile.style docker-compose.yml
git add -f out/a7-live/ out/a7-live-1/
git add -f out/mock-demo-a7/ out/mock-trip-a7/
git status --short
git commit -m "Assignment 7: Style Guide Agent (score+reason evaluator, refiner loop, three-class before/after), with committed live + mock runs"
git tag assignment-7
git push origin main --tags
```

## Phase 5 — submit

1. Repo/tag: `https://github.com/Billy13ean/uhta-crew/tree/assignment-7`
2. `Rouke-uhta-A7-README.md` — stands alone: style guide location, loop
   contract, the three demos, and the pipeline sentence in §0.

## Known gaps, stated rather than hidden

- Live sabotage scores are the model's, not guaranteed; the mock run is the
  only run guaranteed to demonstrate all three catches.
- Register B length limits are stated policy, not GDD constants.
- No console card for the style pipeline yet — launch from the terminal;
  adding a sixth card to `run_console.py` is a two-line follow-up if wanted.
