# Assignment 7 — the Style Guide Agent for *uhta*

> Nicholas Rouke · ELVTR Multi-Agent AI for Game Development · due 20 Aug
> The pipeline: `run_style.py` + `style/` — the fifth pipeline in `uhta-crew`,
> alongside `run_crew.py` (A3, the game's numbers), `run_content.py` (A4, the
> game's words in bulk), `run_builder.py` (A5, the goal-oriented coder) and
> `run_ger.py` (A6, the first-use narration loop).

## 0. The pipeline sentence (deliverable 04)

This Style Guide Agent runs inside the content pipeline immediately after the
Writer emits era-flavor and epilogue candidates and before the Director's
selection gate, scoring every candidate 1–10 against the uhta style guide
(mournful register, canonical Uhtcearu/flame vocabulary, narration length
limits) and auto-refining any sub-10 candidate before it reaches the
selection block.

## 1. The capstone-anchored style guide (deliverable 01)

`style/STYLEGUIDE.md` — thirteen rules across **three constraint types**
(TONE T1–T4, VOCABULARY & LORE V1–V4, FORMAT & LENGTH F1–F5), every rule
cited to a GDD section or a prior-assignment artifact, with a provenance
table. It is machine-read: `style/spec.py` hashes it into every run manifest
and the selftest asserts no rule ID in the spec is missing from the prose —
the artifact the grader reads and the spec the loop enforces cannot drift
apart silently.

The specificity test the rubric threatens ("if a stranger can't tell exactly
what game the rules are for, 0") is answered by the rules themselves:
Uhtcearu, the white flame, the closed Hope/Fear/Apathy vocabulary, the
nomad → village → Victorian era nouns with clocktowers and smoking
factories, the "reads identically in a Hope run" test from the GDD's own
worked example — none of it survives transplantation to another game.

## 2. The Evaluator & Refiner loop (deliverable 02)

Generator → Evaluator → Refiner, breaker-guarded, no human anywhere in the
loop (the Director gate is after it, unfilled, as in every pipeline here):

- **Evaluator** — strictly `SCORE: [X/10]` + `REASON: ...`, never binary
  (the contract parser rejects PASS/FAIL). Two layers, kept from A6: a
  deterministic format gate (`style/checks.py`, rules F1–F5 plus V-evidence)
  runs first and **caps the score at 6 in code** when any F-finding exists —
  the model argues the reason, the code enforces the floor. The Evaluator
  **cannot repair**: a REWRITE/SUGGESTION field in its reply halts the run.
- **Refiner** — receives the original line, the SCORE, the REASON verbatim,
  and the gate findings; rewrites toward acceptance (≥9/10, §3 anchors).
  A no-op rewrite halts the run.
- **Breaker** — 2 refinements per item then ESCALATED with full history;
  3 escalations trip the run (exit 1, `FAILED.md` names `circuit-breaker`).
  Escalated items ship nothing — the pipeline never silently substitutes.

## 3. Before/after demonstration (deliverable 03)

Three sabotage items are part of every run's item set: the Generator is
*instructed to produce wrong content* in a named class (per the assignment's
step 4), then the loop must catch and fix it unaided — TONE (a triumphant
level-up toast), VOCAB/LORE ("the old gods", "mana", "press E"), and
FORMAT ("After 14 sleeps you have built 3 factories…"). Every run writes
`BEFORE-AFTER.md`: Before / SCORE + REASON / After, one section per class.
The live run's version is the citable one; the mock run's is scripted and
banner-stamped as such (though its gate findings are real — the gate is
code, and the seeded lines genuinely contain the digits and second person
it catches).

## 4. What the genuine content is, and one honest canon note

The non-sabotage items target the GDD §4.2 named gap: **era-transition
flavor across three eras**. One wrinkle the style guide states rather than
hides: under the wordless pillar (§1 Tone, ruled v0.9.2), Register B lines
have **no mid-run surface** — they are banked candidates for the endscreen
epilogue (Narrative F5, open) and for era cards pending a Director ruling.
The loop polices candidates; where words appear is a gate it deliberately
does not own.

## 4b. The visual half — VISUAL-GUIDE.html

`style/make_visual_guide.py` renders `style/VISUAL-GUIDE.html`: a single
self-contained page showing the aesthetic canon as pixels — the locked COL
palette as named swatches, the avatar and all three flames, every character
across the three eras (grey → tentative → devout per pole), the era-invariant
mythic constants, settlements, roads (compacted → cobble → paved, per
allegiance), beacons, verb FX, and the three composed scenes. Every image is
rendered by the **real art pipeline** (`art/make_sprites.py` + scene
generators), never mocked. Two things make it a style *guide* rather than a
gallery: a **deterministic palette audit** (fraction of opaque pixels beyond
tolerance from the nearest locked color — code measures, does not judge;
scenes are expected to drift and the drift is reported, not failed), and the
**written guide's hash and rule index embedded in the header**, so one
artifact carries both halves of the canon. Drop reference images into
`style/inspiration/` and re-run to grow a mood-board section. Regenerate:
`python art/make_sprites.py && python art/make_scene.py && python
art/make_temple_scene.py && python art/make_title_scene.py && python
style/make_visual_guide.py`.

Provenance note: at A7 time the `art/` generators were not present in the
crew repo's working tree; they were restored from the project-knowledge
snapshots (`make_sprites.py` art pass 3b, 2026-07-23; scene painters
2026-08-05) and committed under `art/` with this assignment, so the
regeneration command above runs from a clean checkout. The committed
`VISUAL-GUIDE.html` was rendered from those restored scripts on the
submitting machine, against the guide hash shown in its header.

## 5. Run modes and evidence

```
python3 run_style.py --selftest    # 38 assertions, no key, no calls
python3 run_style.py --mock-llm    # full loop on fixtures walking EVERY
                                   # path: two round-0 accepts, all three
                                   # class catches + repairs, and one
                                   # ESCALATION (era-victorian)
python3 run_style.py               # live (~15–30 calls, < $1)
```

Every run writes to `out/<run-id>/`: `RUN-LOG.md` (every stage, byte count +
sha), `STYLE-LOG.md` (every round of every item), `BEFORE-AFTER.md`,
`candidates.md` (ends at an unfilled `## Director selection` block),
`ESCALATED.md` when the breaker fired, `manifest.json` (with the style
guide's hash — a run is reproducible against the exact guide it enforced).

## 5b. Live calibration — what the first live run taught

The first live run (`out/a7-live-1`, kept) tripped the breaker with zero
rule violations. The acceptance bar was 10/10 and the Evaluator prompt said
"be stingy with it" — so a live model did exactly that: every gate-clean era
line scored 8 or 9 with only a *craft note* in the REASON ("metaphor
slightly stacked", "T4 only implied"), the Refiner was sent after lines that
had nothing to fix, and twice it repaired a craft note by *adding* words and
ran the line past 160 characters, so the deterministic gate capped it at 6.
Three escalations, breaker, `FAILED.md`. The mock fixtures never showed this
because their canned Evaluator hands out 10s.

Two changes, both in the artifact the pipeline enforces rather than in
scattered code: STYLEGUIDE §3 now has score anchors (10 = nothing to note,
9 = rules honored + craft note, 8 = a rule strained, ≤7 = violated) and
**accepts at 9**, with `spec.ACCEPT_SCORE` following the prose; and the
Refiner is told length is a hard gate and that fixing F1 means *cutting*.
The selftest and mock run are unchanged (fixtures still score 10). This is
the evaluator-calibration finding the rubric asks a pipeline to surface,
found the only way it can be: by running it live.

## 6. Honest limits

- **Register B's numbers are mine.** ≤2 sentences / ≤160 chars is stated
  policy calibrated to sit near the A6 narration limits, not a GDD constant
  — same honesty class as A6's 120/24.
- **The breaker thresholds are budget policy,** carried from A6 unmeasured.
- **A mock run proves orchestration, not judgment.** Its verdicts are canned
  and every artifact says so; only the gate findings inside it are real.
- **Sabotage items withhold the style guide from the Generator** (and only
  from the Generator, and only for those items) so the wrong content is
  genuinely wrong rather than a model politely pretending — stated here
  because it is the one place the pipeline's two run kinds differ.
- **The style guide can score text; it cannot rule on surfaces.** Whether
  era flavor ever appears in the wordless game is a Director question the
  loop leaves unfilled by design.
