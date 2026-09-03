# Pipeline Audit & Cost Analysis — *uhta* (1 page)

**Nicholas Rouke · Assignment 10 · Complete AI Dev Pipeline**
All figures below are measured from run manifests in `out/*/manifest.json` (each live run
records `llm_calls` and `llm_tokens`), priced at claude-sonnet-4-5 API rates ($3/M input,
$15/M output). Nothing is projected unless labeled as a projection.

## 01 — Pipeline Production & Functionality

**a. What the pipeline produced (present in the playable build).** (1) The tuned ruleset:
every number the game plays on — contagion, burnout, stamina economy, road allegiance,
schism, the Grief Front (variant A, run 23b), and the temple-endgame dials — was emitted as
`rules-vN.json` variants by the Mechanic Designer, attacked by the Red-Teamer, measured by
the Playtester against the reference harness, contradiction-checked by the Keeper, and
ratified by Director ruling; `rules-v3.10.2-A.json` is the 15th-generation baseline of that
loop. (2) The narrative layer: the SONDER engine's style-gated story bank (13 tellings with
lineage-locked heirlooms) is inlined verbatim into the build and surfaces as the night's
story cards. (3) QA-driven fixes shipped in the build: the adversarial agent's findings
(zero-stamina feedback F01; the win-seal class caught after a human report) each became a
patched build plus a permanent probe invariant (I1–I11) and self-test (19/19).

**b. Manual steps remaining.** One friction point: promoting a ratified `rules-vN.json`
into the embedded `RULES` literal of the single-file HTML is a hand-merge. Two process
steps are human **by design**, not friction: the Director ruling on every contradiction,
and commits. (Honest note: Keeper transcription of rulings into `CANON.md` has lagged the
runs — a discipline gap, not an automation gap.)

**c. To eliminate it.** A build-time injection step: the builder stamps the ratified JSON
over a template marker in the HTML at package time (the sonder bank already ships this
way), plus a post-ruling hook appending each `RULING.md` to `CANON.md`. The verification
half is already automated (deterministic validation gate, harness batteries, parity check,
chaos probe, terrain win-gate — all scripted, exit-code CI-able). 100% automation of the
*gate* is deliberately not wanted; 100% automation of everything around it is one script.

## 02 — Architectural Reflection

**a. Decision I would change.** Maintaining **two reference simulators** — the python
harness (`sim/harness.py`) and the JS World inside the playable slice — under a
"baseline is the schema" parity contract. Every new mechanic (temple, schema 3.10; wild
terrain, 3.11) must be written twice before the crew can tune it, and parity
(`tools/parity_schema310.py`) is a standing tax paid on every change.

**b. Specific alternative.** Single-source the sim: run the slice's own `World` headless
under Node as *the* reference harness, with the python layer reduced to orchestration
calling it. This is proven in-repo — `tools/winprobe_terrain.js` already extracts the
build's World and runs seeded bot policies against it; the terrain feature was tuned and
regression-gated that way in one afternoon, with zero parity debt.

## 03 — Cost Analysis (measured)

**a. Total actual run cost:** **$0.75** for `a10-video-3` — the full pipeline run
recorded in the submission video (5 agent calls; 127,287 input + 24,769 output tokens,
claude-sonnet-4-5; its manifest, with these token counts, appears on screen). The prior
ratifying run `temple-grief-4` measured $0.85 (140,732 / 28,222). Pipeline-to-date across
every live run including all failures: 1,801,237 input + 379,685 output ≈ **$11.10**.

**b. Most expensive step:** the **Mechanic Designer** variant-emission step — 71K tokens
actual against 19K projected (4–6×), because it verifies its own output against harness
batteries; art-direction passes (85–135K, run outside the crew) were the only larger
category in the project.

**c. Solo sustainability: yes.** A full design → attack → measure → ruling cycle costs
under a dollar; the entire crew history costs less than lunch. The binding constraint is
Director review time, not tokens — the pipeline paces on human gate decisions.

## 04 — Mid-Project Cost-Reduction Change

**a. Strategy/prompting — Before:** Mechanic Designer prompt v3 asked for **the complete
rules file per variant**. The Designer re-typed ~15 baseline values from memory; one
(`growth: 0.15`, a float where the sim casts int) crashed the harness on all variants and
the whole run was lost. **After:** prompt v4 asks for a **delta only** — just the changed
keys, nested as in the baseline — and the deterministic gate merges it onto the canonical
baseline before validation. The baseline can no longer be mis-copied, by construction.

**b. Token/API cost — Before:** 30,915 output tokens for the Designer step alone, on a run
that then **failed** (`temple-grief-2`: $0.57 spent, nothing ratified). **After:** the
entire six-call pipeline — Designer, Red-Teamer, Playtester, Keeper — completes in 28,222
output tokens (`temple-grief-4`: $0.85, ratified). Less output than the old broken step,
for the whole crew, with the failure class deleted.
