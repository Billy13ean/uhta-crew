# Contract: Orchestrator — v1 (crew port)

> **This agent has no LLM prompt, and that is the point.**
> Role: dispatch only. GDD §3.1, seated 0.9.7; CANON-process.md ruling 5.
> Implementation: `crew/orchestrator.py`. Deterministic Python, zero API calls.
> Version: v1 | No prior version (the role did not exist before GDD 0.9.7).

---

## Why this file has no `## SYSTEM` block

The Orchestrator's canon contract is **dispatch-only — never gates, never
authors, never tunes** (GDD §3.1). An LLM-backed orchestrator can do all three by
accident: asked to "route sensibly", a model will happily decide a variant looks
good, skip a stage it judges redundant, or paraphrase a packet on the way past.
The gates are what make this pipeline trustworthy, and an autonomous layer that
could approve anything would dissolve them.

So the Orchestrator is code. It cannot form an opinion about a ruleset because it
never reads one as text — it only checks that a file exists, parses, and hashes.
This is the narrowest possible reading of the contract, and it is deliberate.

## Contract

**Input:** the Director's goal + the blackboard state.
**Output:** `manifest.json`, the dispatch sequence, artifact verification, `RUN-LOG.md`.
**Definition of done** (GDD §3.1): the named artifact exists and the Director has
it stapled to its Keeper diff.

## The dispatch sequence

| # | Stage | Agent | Requires (halts naming this agent if absent) | Produces |
|---|---|---|---|---|
| 1 | `keeper_b1` | Keeper (Mode B1) | seeded blackboard | `packet-mechanic-designer-vN.md` |
| 2 | `mechanic_designer` | Mechanic Designer | the packet — **Keeper B1** | `rules-vN-{A,B,C}.json`, `designer-rationale.md` |
| 3 | `validation_gate` | *(deterministic, no agent)* | the variants — **Mechanic Designer** | `validation.json` |
| 4 | `red_teamer` | Red-Teamer | packet + a validated variant — **Keeper B1**, **Mechanic Designer** | `attacks-vN.md`, `attacks.json` |
| 5 | `playtester` | Playtester | variants + `attacks.json` — **Mechanic Designer**, **Red-Teamer** | `metrics-vN.md`, `execution-log.json` |
| 6 | `keeper_b2` | Keeper (Mode B2) | selected variant + metrics — **Mechanic Designer**, **Playtester** | `contradictions-runN.md` |
| 7 | `director_gate` | *(human — outside this crew)* | all of the above | a `## Ruling` block |

## Rules the Orchestrator enforces

1. **Sequential, never parallel.** Each stage's input is the previous stage's
   file. There is nothing to parallelise; a crew that fans out here would be
   fanning out over an empty blackboard.
2. **Artifact verification after every stage.** The named artifact must exist and
   be non-empty. If it is not, the run halts and `FAILED.md` names the agent, the
   stage, and the error.
3. **No fallbacks.** A missing upstream artifact halts the pipeline. It never
   degrades to "run the baseline instead" — a metrics file built from baseline
   numbers while claiming to measure a variant is exactly the failure mode the
   gates exist to prevent.
4. **Selection is a stand-in, and says so.** The Director selects the variant
   (GDD §3.3: `MD -->|2-3 variants| D`, `D -->|selects| RT`). This crew runs
   unattended, so the Orchestrator applies a documented deterministic rule — the
   first variant to clear the validation gate, in emitted order — records it in
   `manifest.json` as `selection.by = "orchestrator-standin"`, and sets
   `director_gate: "PENDING"`. It is a placeholder for a human decision, not a
   decision.
5. **It never reads an artifact's meaning.** Existence, size, parse, hash. That
   is the whole of its access.
6. **`manifest.json` records** model, prompt versions, seed list, per-stage status
   and duration, the full blackboard read/write ledger, and a SHA-256 of every
   artifact — so any output traces to the exact prompt and ruleset that produced
   it (GDD §3.3).

## What the player ever notices (GDD §3.4)

Nothing directly — "and that is the test it has to keep passing. Its only
player-facing consequence is *ordering*. If it ever changes what the player sees,
it has exceeded its contract and should be unseated."
