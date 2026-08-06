# uhta — the rules-pipeline crew

**uhta** (*ūhta*, m., "the last part of the night, before dawn") is a browser
god-game about emotional contagion. You play a kaiju-scale being born as a
counterpoint to Uhtcearu, the world's grieving god, and the game asks one
question: *what will you make people feel, and what will that do to the world?*
NPCs sit on a −12..+12 emotion scale; every Sleep runs a generation of contagion
you cannot micromanage. The playable slice is `build/uhta-slice.html` in the game
repo. This repo is not the game — it is the five-agent crew that produces the
**data file the game boots from**.

*Assignment 3, ELVTR Multi-Agent AI for Game Development. Raw Python
orchestration — no CrewAI, no LangChain. Sole third-party dependency:
`anthropic`.*

*The repo now holds a **second pipeline**: `run_content.py` (Assignment 4, the
dynamic content pipeline) generates the game's **text** — the teacher's narration
lines, era and settlement flavor, endscreen candidates — against the same
blackboard, read as a RAG corpus. Same three run modes, same halt discipline, no
new dependency. See [Content pipeline](#the-second-pipeline--rag-content-generation)
below.*

\---

## What this crew produces, and why uhta needs it

Every number uhta feels like — how hard a flame pushes, how fast a tribe hardens,
how long you have to save someone from burnout, how the grief fog behaves — lives
in `rules-vN.json`, a data file the browser build loads at boot. Tuning stays in
data precisely so a change after a playtest reaches the player without a code
review (GDD §3.4). Thirteen generations of that file exist, `rules-v1-B` through
the ratified `rules-v3.9.1-C`.

This crew is the machinery that produces the next one. Given a Director goal, it
runs:

**a canon packet → 2–3 candidate rulesets → a deterministic validation gate → an
attack surface → real simulator measurements → a coherence diff → a human gate.**

The output is a proposal bundle the Director can rule on: the candidate rules
files, the attacks they must survive, the metrics that measure them, and the
Keeper diff stapled on top. **The crew does not ship anything.** It makes the
Director's decision cheap, evidenced, and traceable.

Concretely, what a run gives the game:

|Artifact|What it does for uhta|
|-|-|
|`rules-vN-{A,B,C}.json`|Candidates for the file the build loads at boot. Validated to load in the reference simulator before a human looks at them.|
|`attacks-vN.md` + `attacks.json`|The degenerate strategies each candidate must survive, expressed as executable probes. This is how "the frontal flame siege converts 0 heads" got found.|
|`metrics-vN.md`|Evidence, from real runs, that decides which candidate earns the Director's scarce playtest hours.|
|`contradictions-runN.md`|The coherence diff against `CANON.md`, with a blank `## Ruling` block. This is what stops a proposal reaching a commit without a verdict.|

Running the crew has also turned up two defects in the game repo's own reference
suite, written up for the Director in [**`FINDINGS.md`**](FINDINGS.md). Both were
found by executing the suite, not by reading it.

\---

## The crew

Five LLM-backed roles plus a deterministic Orchestrator, adapted from the prompts
in the game repo (`prompts/v1/keeper.md`, `prompts/v2/mechanic-designer.md`,
`prompts/v3/red-teamer.md`, `prompts/v2/playtester.md`) rather than written fresh.
Every prompt in `prompts/` carries a versioned header stating what changed from
its predecessor and why.

|#|Agent|Input|Output|
|-|-|-|-|
|—|**Orchestrator** `crew/orchestrator.py`|Director goal + blackboard state|`manifest.json`, the dispatch sequence, artifact verification after every stage, `RUN-LOG.md`|
|1|**Keeper (Mode B1)**|`CANON.md` + `CANON-process.md` + GDD sections + the run's question set|`packet-mechanic-designer-vN.md` — CANON digest verbatim, the canon *lines* the change touches, scoped excerpts, and an explicit **excluded and why** list|
|2|**Mechanic Designer**|The Keeper packet + the baseline rules JSON|2–3 complete `rules-vN-{A,B,C}.json` + `designer-rationale.md` (hypothesis per variant, parameter table, four-ratio arithmetic)|
|3|*Validation gate* (no LLM)|The variants + the baseline|`validation.json`. Parse, schema, harness-load. One repair round-trip on failure, then abort.|
|4|**Red-Teamer**|The packet + the selected variant + the rationale|`attacks-vN.md` **and** `attacks.json` — probes naming a bot policy, seeds, `max\_sleeps`, poles, and a falsifiable invariant|
|5|**Playtester**|The variants + `attacks.json`|`metrics-vN.md` built from **real harness execution**, plus `execution-log.json`|
|6|**Keeper (Mode B2)**|The selected variant + metrics + attacks|`contradictions-runN.md` in the GDD §3.2 six-heading schema, with the four flag classes and a blank `## Ruling` block|
|7|**Director** (human, outside this crew)|All of the above|`UPHOLD` / `AMEND` / `DEFER`, and the variant to ratify|

\---

## What breaks if you remove agent X

Not an assertion — a flag. `--drop-agent <name>` removes an agent from the
dispatch sequence, and the run is **expected to halt with exit 1**. A completed
run there would be the failure.

```bash
python3 run\_crew.py --mock-llm --drop-agent red-teamer   # halts, exit 1
```

|Remove|What breaks|Actual halt message|
|-|-|-|
|**Orchestrator**|Nothing is sequenced, nothing is verified, no manifest exists, and a failure surfaces as a traceback instead of a named stage. It is the only component that knows the run *is* a run.|*(it is the runner; removing it is removing the program)*|
|**Keeper B1**|The Designer has no view of canon at all — it never reads `CANON.md` directly, by design, so a wrong retrieval is a visible file rather than a silent omission.|`PIPELINE HALT: mechanic-designer requires the artifact '…/packet-mechanic-designer-v3.9.2.md', which is produced by the keeper-b1.`|
|**Mechanic Designer**|There is no candidate ruleset. The validation gate has nothing to validate and the Red-Teamer has nothing to attack.|`PIPELINE HALT: validation-gate requires the artifact '…/rules-v3.9.2-A.json', which is produced by the mechanic-designer.`|
|**Red-Teamer**|The Playtester has no arms. `attacks.json` **is** the arm list; there is no fallback to a baseline sweep, because a metrics file built from baseline numbers while claiming to measure a variant is exactly the failure the gates exist to prevent.|`PIPELINE HALT: playtester requires the artifact '…/attacks.json', which is produced by the red-teamer.`|
|**Playtester**|No numbers. Selection between variants becomes argument, and the Keeper has no evidence to diff against canon.|`PIPELINE HALT: keeper-b2 requires the artifact '…/metrics-v3.9.2.md', which is produced by the playtester.`|
|**Keeper B2**|A proposal reaches the Director with no diff stapled to it — which is precisely the state CANON-process ruling 1 forbids ("flags never gate, but they do block silence"). The Orchestrator verifies the gate bundle as a unit, so this halts too.|`PIPELINE HALT: director-gate requires the artifact '…/contradictions-<run>.md', which is produced by the keeper-b2.`|

\---

## Quickstart

### Docker (recommended)

```bash
cp .env.example .env          # add your key for the live mode
docker compose build          # the build RUNS --selftest; it fails if the sim can't run
docker compose run --rm crew --selftest      # deterministic half, no key needed
docker compose run --rm crew --mock-llm      # full pipeline, no key needed
docker compose run --rm crew                 # LIVE — needs ANTHROPIC\_API\_KEY
```

Artifacts land in `./out/<run-id>/` on the host (bind-mounted).

Useful live invocations:

```bash
# a real run at the uhta project's standard 20 seeds per arm
docker compose run --rm crew --seeds 20

# your own Director goal
docker compose run --rm crew --goal "Burnout headroom: Y=4 vs the innocent stack…"

# a different model
CREW\_MODEL=claude-opus-4-1 docker compose run --rm crew
```

### Bare Python

```bash
python3 -m venv .venv \&\& source .venv/bin/activate
pip install -r requirements.txt          # not needed for --selftest / --mock-llm
export ANTHROPIC\_API\_KEY=sk-ant-...      # live mode only
python3 run\_crew.py --selftest
python3 run\_crew.py --mock-llm
python3 run\_crew.py
```

Python 3.11.

\---

## The three run modes

|Mode|API calls|What it proves|
|-|-|-|
|**default (live)**|yes|The whole thing. Model from `$CREW\_MODEL` (default `claude-sonnet-4-5`), key from `$ANTHROPIC\_API\_KEY`.|
|**`--selftest`**|**none**|That the deterministic half works with no key: the blackboard round-trips and halts by name on a missing artifact; the validation gate accepts the baseline and rejects three distinct kinds of breakage; and the reference simulator **really executes** and returns real statistics. Exits 0.|
|**`--mock-llm`**|**none**|That the orchestration executes end to end with no key.|

### Read this before you look at a `--mock-llm` run

> \*\*`--mock-llm` is a test fixture. It produces no real design work.\*\*
>
> Every agent response in a mock run is replayed verbatim from `tests/fixtures/`.
> No model sees the packet. No judgement is exercised. Nothing in a mock run's
> `out/` directory is evidence about uhta, and the mock Playtester's prose
> deliberately refuses to state numbers it cannot know.
>
> Every artifact a mock run produces is stamped with that warning in its first
> lines, `RUN-LOG.md` says it, and `manifest.json` records
> `"llm\_backend": "mock"`.
>
> \*\*One part of a mock run is real: the harness numbers.\*\* The Playtester always
> executes the simulator — the same subprocesses, the same seeds, the same
> `RULES` bindings — because the orchestration cannot be tested end to end
> without it. So the consolidated board in a mock `metrics-vN.md` contains real
> measurements of the fixture's rulesets. The prose around them is canned.

\---

## A sample of real output

From `--selftest` (no key, no API calls, real simulator):

```
\[3/3] Reference simulator — REAL execution on the ratified baseline
  \[PASS] probe S1 (bot\_do\_nothing) executed in 1.25s over 8 seeds
         wins=0 losses=8 none=0 med\_terminal\_sleep=24.0 med\_final\_wf=0.0223
         med\_final\_lf=0.9208 med\_selfburns=0.0 med\_fronts=0.0
  \[PASS] probe S2 (run\_campaign\_v3) executed in 4.63s over 8 seeds
         wins=7 losses=0 none=1 med\_terminal\_sleep=20 med\_final\_wf=0.8121
  \[PASS] do-nothing reaches the apathy loss in every seed (G8/A11) — 8/8 losses
  \[PASS] self-burn control stays at 0 self-burns — max=0
```

From the consolidated board in a `metrics-v3.9.2.md` — machine-generated from
`execution-log.json`, no model involved:

|probe|attack|bot|n|ruleset|wins|losses|none|med sleep|med wf|med selfburn|med fronts|med expo|
|-|-|-|-|-|-|-|-|-|-|-|-|-|
|`P1`|A1|`bot\_throughput`|8|`rules-v3.9.1-C.json`|2|0|6|12.5|0.6244|0|2.5|94.165|
|`P1`|A1|`bot\_throughput`|8|`rules-v3.9.2-A.json`|2|0|6|12.5|0.6276|0|**1.5**|**77.335**|
|`P5`|A5|`bot\_do\_nothing`|8|`rules-v3.9.1-C.json`|0|8|0|24|0.0223|0|0|0|
|`P5`|A5|`bot\_do\_nothing`|8|`rules-v3.9.2-A.json`|0|8|0|24|0.0223|0|0|0|

That is the shape of the thing: variant A's smaller grief front measurably cuts
front count and exposure, and the passive-baseline safety floor is untouched. Real
numbers, from real runs, on a candidate ruleset that did not exist before the run
started.

\---

## Design notes worth knowing

**The Playtester really executes the harness.** `blackboard/sim/harness.py` is the
game repo's `sim/harness-v3.9.py`, vendored verbatim (it must be importable as
`harness`, because `bots.py` does `import harness as H`). For every probe × every
ruleset, `crew/agents/playtester.py` spawns `crew/probe\_runner.py` as a subprocess
with `RULES=<abs path to that variant>` and `cwd`/`PYTHONPATH` set to the sim
directory. One process per pair, because the harness reads `RULES` at import time.
The consolidated board and the raw-facts appendix in `metrics-vN.md` are generated
by code from `execution-log.json`; the model writes only the interpretation
between them, and is told in its prompt that the numbers are facts it may not
alter. **A hallucinated number cannot reach the board, because the board is not
generated from the model's output.**

**The validation gate derives its schema from the baseline.** `crew/validate.py`
walks `rules-v3.9.1-C.json` at runtime to produce the required key-path set — 203
paths in the current file — rather than carrying a hand-typed schema that would go
stale the moment the Director ratifies a new baseline. Two documented exclusions,
both applied programmatically: everything under `meta.` (provenance prose the
harness never reads) and any path with a `\_`-prefixed segment (the baseline's own
annotation convention). Then check (c): the harness imports the candidate and
ticks it. A ruleset can be schema-complete and still unloadable, and check (c) is
the only thing standing between that and the Red-Teamer.

**The blackboard is the filesystem.** `crew/blackboard.py` is the only module that
touches disk. No agent receives another agent's live context. Every read and write
is appended to `RUN-LOG.md` with a byte count and a SHA-256 prefix as it happens.

**Two real defects in the vendored bot suite, found by running it — see**
[**`FINDINGS.md`**](FINDINGS.md)**.** `bots.py` predates the genesis start, and the crew
surfaced two consequences. (1) `run\_tyrant` hard-codes tribe index 2, which does
not exist under `founding\_poles: \[-1, 1]`; it raised on every seed. That one is
now handled by `crew/policy\_shims.py`, a crew-side wrapper that resolves the
target once at t0 as the first tribe opposing the player's pole — which is what
index 2 meant under the legacy start. **`blackboard/sim/bots.py` is not modified**
and stays byte-identical to the game repo: the Playtester owns that file, and a
crew that rewrote the reference suite to make its own arms pass would be
manufacturing the evidence it reports. Every shimmed arm is stamped in
`RUN-LOG.md` and in a declared "Policy shims in force" table in `metrics-vN.md`.
Measured after the shim, seeds 0–7: 0 seed errors (was 8/8), 1/8 wins, `max\_wf`
0.372–0.938. (2) The composite policies (`run\_campaign\_v3`, `run\_siege`,
`run\_selfburn`) build their own return dicts and so do not carry the grief-front
counters — a real limitation rather than a bug, left unwrapped and documented in
`prompts/red-teamer.md` with a policy→metric table. A probe that raises is
reported as an errored arm and the run is marked **incomplete**; it does not take
the crew down.

\---

## What this crew is *not*

* **It does not gate.** The human Director is the only gate and the only author of
canon (GDD §3.1). The Keeper flags and never rules; the Orchestrator dispatches
and never approves; the crew ends at a blank `## Ruling` block. When an
unattended run needs to hand the Red-Teamer a target, the Orchestrator applies a
documented stand-in — *first variant to clear the validation gate* — records it
as `selection.by: "orchestrator-standin"` with `director\_gate: "PENDING"`, and
expresses no preference between variants. That is a placeholder for a human
decision, not a decision.
* **It does not touch the render layer.** No sprites, no Phaser, no
`uhta-slice.html`. The Aesthetic Director and the Programmer are separate roles
in the GDD roster and are not in this crew.
* **It is not the content pipeline.** The Writer and Critic (GDD §4.2, the
Assignment-4 deliverable) generate the game's narration lines against the same
blackboard-as-RAG-corpus. Different agents, different artifacts, not here.
* **It does not judge fun.** The Playtester measures shape and is forbidden from
judging fun (GDD §3.1). No layer of this crew covers it — that is what §2.8's
stranger-at-the-keyboard test is for, and it has 0 of 6 criteria tested.
* **It is not a 20-seed run by default.** 8 seeds finishes in about ninety
seconds; the uhta standard is 20. Use `--seeds 20` for anything you intend to
rule on, and read the Playtester's Conformance section, which is required to
state what the run did *not* verify.

\---

## The second pipeline — RAG content generation

`run_content.py` is the **Assignment-4** deliverable: a separate program that
happens to share this repo's plumbing. `crew/blackboard.py`, `crew/llm.py` and
`crew.agents.AgentError` are reused verbatim, and **nothing in `crew/` imports
`content/`** — the dependency runs one way, which is why adding the content
pipeline could not change what a rules run does.

It answers a different question — not *what should the numbers be* but *what
should the game say* — and uhta has an unusually sharp version of that question,
because after the first dawn it says nothing at all.

| | rules crew (`run_crew.py`) | content pipeline (`run_content.py`) |
|---|---|---|
| Produces | `rules-vN.json` — the file the build boots from | the game's text: 8 narration lines, 5 era/settlement flavor beats, 3 endscreen candidates |
| Corpus | CANON + GDD sections, hand-cut by the Keeper | the same blackboard, **ranked by BM25** — scoped to game material: 24 chunks / 12,315 words in, 28 chunks / 13,311 words out with a reason each |
| Agents | Keeper ×2, Mechanic Designer, Red-Teamer, Playtester | Retriever (deterministic), Writer, Critic |
| Evidence | `metrics-vN.md` from real harness runs | `RAG-TRACE.md`, `CRITIC-LOG.md`, `VOICE-JUDGMENT.md`, `README-A4.md` — all generated from the run |
| Ends at | a blank `## Ruling` block | an unfilled `## Director selection` block |

```bash
python3 run_content.py --selftest      # no key: chunking, corpus policy, BM25, halt guards
python3 run_content.py --mock-llm      # no key: full pipeline on fixtures (NOT content)
python3 run_content.py --candidates 8  # LIVE — needs ANTHROPIC_API_KEY
```

**Retrieval is BM25 in pure Python** (`content/retriever.py`, k1=1.5, b=0.75,
non-negative IDF), because the assignment permits one third-party package and it
is already spent on `anthropic`. A chunk is one `###` subsection — the rule GDD
§4.5 had already fixed. Headings inside fenced code blocks are not headings: the
GDD embeds a Keeper report skeleton whose lines start with `##`, and treating
those as sections would shred §3.2 into nonsense. Selection then applies the
Keeper's Mode-B1 discipline to the scorer: a score threshold, a token budget,
duplicate-heading suppression, and **every cut recorded with its reason**.

**The corpus is scoped to game material** by a declared policy (`CORPUS_POLICY`).
The GDD is two documents in one binding — the design of uhta, and the design of
the pipeline that builds uhta — and only the first is a knowledge base for
writing the game's text. In: GDD §1, §2, §5, §6, Appendix A and `CANON.md`. Out:
§3, §4, §7, the front-matter changelogs and `CANON-process.md`, each recorded as
a corpus-level exclusion with a reason. The sharp case is **§4.5**, which
contains the Director's own hand-written worked example of a narration line —
indexed, it ranks near the top on a Roar query, and a Writer handed it is not
generating a line, it is handing the Director's back.

**Every beat retrieves twice.** GDD §4.5 records that the first hand-run
retrieved only the experience section and produced lines that would sit unchanged
in any god-game about hope and fear. So each beat carries two queries — the
mechanical consequence and the experience — and their cuts are unioned. `--ab`
runs one beat both ways and hands both candidate sets to the same Critic; that
comparison is in `VOICE-JUDGMENT.md`, which is the difference between a retrieval
tweak that is claimed and one that is measured.

**The Critic must catch *and* correct.** A `FAIL` verdict with no `correction`
raises `AgentError` and halts the run (`content/agents/critic.py`), as does a
flag class outside the four allowed and a FAIL that quotes no chunk. So
`CRITIC-LOG.md` cannot contain a rejection without a repair — the pipeline is
incapable of producing one.

**`--selftest` proves the retrieval half with no key.** 27 assertions, exit 0: a
Roar query must rank the §2.2 verb table **first** (bm25 30.12 vs 16.45 for the
runner-up); a burnout query must rank the §2.3 systems block first (12.80); two
deliberately off-topic control queries must score everything below threshold and
retrieve **nothing** (best 0.00 against a threshold of 8.0); the corpus policy
must have actually removed §3, §4, §7 and `CANON-process.md`; all sixteen beats
must retrieve two chunks; the A/B arms must genuinely differ; and every halt
guard must fire.

**What breaks if you remove the Writer or the Critic.** Same demonstration the
rules crew ships, applied here. `--drop-agent <name>` removes a role from the
dispatch sequence and the run is **expected to halt with exit 1**; a completed
run there would be the failure.

```bash
python3 run_content.py --mock-llm --drop-agent critic   # halts, exit 1
```

| Remove | What breaks | Actual halt |
|---|---|---|
| **Writer** | The Critic has nothing to judge, and the halt proves the handoff is an artifact rather than a variable. | `PIPELINE HALT: critic-n1 requires the artifact 'out/<run>/drafts/n1-draft.json', which is produced by the writer-n1.` |
| **Critic** | Assembly would build `CRITIC-LOG.md` around an unreviewed line set — a document that reads like evidence and is not. | `PIPELINE HALT: assemble requires the artifact 'out/<run>/verdicts/n1-verdict.json', which is produced by the critic-n1.` |

This is why the Orchestrator row in GDD §3.1 is honest. Its stated justification
is that *"the run manifest is what guarantees a generated line set reaches the
Critic before it reaches the build"* — so `content/orchestrator.py` writes the
Writer's candidates to `drafts/<beat>-draft.json` and the Critic **reads them
back off disk**. There is no in-memory handoff between the two roles, which is
what makes the halt above possible at all.

> **A note on run ids.** Both pipelines write to `out/<run-id>/`. The defaults do
> not collide (`run-…` vs `content-…`), but passing the same `--run-id` to both
> would interleave two runs in one directory. Don't.

---

## Repo layout

```
uhta-crew/
  README.md  ARCHITECTURE.md            # this file; roles + two rendered Mermaid diagrams
  FINDINGS.md                           # defects this crew surfaced in the game repo
  Dockerfile  docker-compose.yml  requirements.txt  .env.example  .gitignore
  run\_crew.py                           # rules pipeline: live | --selftest | --mock-llm | --drop-agent
  run\_content.py                        # content pipeline: live | --selftest | --mock-llm
  crew/
    orchestrator.py                     # dispatch, artifact verification, manifest — no LLM
    blackboard.py                       # the filesystem as shared memory; read/write ledger
    validate.py                         # the deterministic gate; schema derived from the baseline
    llm.py                              # Anthropic client (3 retries, backoff) + fixture stub
    probe\_runner.py                     # one process per arm × ruleset; real harness execution
    policy\_shims.py                     # crew-side fixes for broken upstream bot policies
    agents/{keeper,mechanic\_designer,red\_teamer,playtester}.py
  prompts/                              # one per role, versioned headers, adapted from the game repo
    keeper.md  mechanic-designer.md  red-teamer.md  playtester.md  orchestrator.md
    writer.md  critic.md                # the content pipeline's two roles
  content/                              # ASSIGNMENT 4 — the content pipeline
    retriever.py                        # chunking + CORPUS\_POLICY + BM25 + recorded exclusions
    beats.py                            # the 16 beats, their two queries each, their named gaps
    pipeline.py                         # stages, manifest, FAILED.md — no LLM
    assemble.py                         # every evidence document, generated from the run
    fixtures.py                         # --mock-llm backend (subclasses crew/llm.py MockLLM)
    agents/{writer,critic}.py
  blackboard/                           # seeded, read-mostly
    CANON.md  CANON-process.md
    gdd/uhta-gdd-v0.9.7-abridged.md
    gdd/uhta-gdd-v0.9.7-full.md         # added for the content pipeline's deeper corpus
    rules/rules-v3.9.1-C.json           # the ratified baseline AND the schema
    sim/harness.py  sim/bots.py         # vendored verbatim from the game repo
  diagrams/                             # flow.mmd, memory.mmd + rendered SVGs
  tests/fixtures/                       # canned artifacts for --mock-llm (rules crew)
  tests/fixtures/content/               # canned artifacts for --mock-llm (content pipeline)
  out/                                  # per-run artifacts (gitignored except .gitkeep)



\--

## Committed evidence

Two runs are committed to this repo so the crew can be assessed without an API
key and without re-running anything.

### `out/run-20260728-230752-live/` — a complete live run

All six agent stages executed against the Anthropic API, ending at the Director
gate. Thirteen artifacts:

|Artifact|Produced by|What it is|
|-|-|-|
|`packet-mechanic-designer-v3.9.2.md`|Keeper B1|the assembled canon packet (15,785 B)|
|`rules-v3.9.2-{A,B,C}.json`|Mechanic Designer|three candidate rulesets, each a complete file|
|`designer-rationale.md`|Mechanic Designer|hypothesis per variant + parameter table|
|`validation.json`|validation gate|parse / 203-key-path schema / harness load+smoke, per variant|
|`attacks-v3.9.2.md` + `attacks.json`|Red-Teamer|4 probes, expressed as executable arms|
|`execution-log.json`|Playtester|raw results of 16 real harness arms (4 probes × 4 rulesets)|
|`metrics-v3.9.2.md`|Playtester|consolidated board, generated from the execution log|
|`contradictions-run-20260728-230752-live.md`|Keeper B2|the coherence diff, with a blank `## Ruling` block|
|`RUN-LOG.md`|Orchestrator|every blackboard read and write, with byte counts and SHA-256|
|`manifest.json`|Orchestrator|model, prompt versions, per-stage status, artifact hashes|

`manifest.json` records `"llm\\\_backend": "live"`. The run ends, correctly, without
a decision: `Director gate: PENDING`.

### `out/run-20260728-232857-mock/` — the removability demonstration

```bash
docker compose run --rm crew --mock-llm --drop-agent red-teamer   # exit 1
```

The Orchestrator skips the Red-Teamer; the Playtester halts because
`attacks.json` has no producer. `FAILED.md` is the artifact:

```
PIPELINE HALT: playtester requires the artifact 'attacks.json',
which is produced by the red-teamer. It is not on the blackboard.
  -> This crew has no fallback for a missing upstream artifact: continuing
     would produce a downstream artifact that LOOKS real and is not.
```

This is the Role Clarity claim as a demonstration rather than an assertion. Each
of the five removable agents halts at a different, correctly-named consumer — see
the table in "What breaks if you remove agent X" above.

### Reproducing without a key

```bash
docker compose build                          # the build runs --selftest
docker compose run --rm crew --selftest       # no key: gate + real simulator
docker compose run --rm crew --mock-llm       # no key: full six-stage orchestration
```

\---

## What this run does *not* establish

Stated here rather than left for a reader to discover.

**The arms ran at 8 seeds, not 20.** The invocation was `--seeds 20`, and the
run header reports `Seeds: \\\[0..19]`, but every arm in `execution-log.json` shows
`n=8`. The Red-Teamer's `attacks.json` carries a per-probe seed count that takes
precedence over the CLI flag, and nothing reconciles the two. The header is
therefore misleading and the flag is not doing what its name implies. Logged as
finding 7 in [`FINDINGS.md`](FINDINGS.md).

**No variant separated from the baseline.** All four rulesets returned identical
win/loss/none counts on all four probes:

|probe|bot|baseline|A|B|C|
|-|-|-|-|-|-|
|P1|`bot\\\_throughput`|3/0/5|3/0/5|3/0/5|3/0/5|
|P2|`bot\\\_throughput`|3/0/5|3/0/5|3/0/5|3/0/5|
|P3|`bot\\\_do\\\_nothing`|0/8/0|0/8/0|0/8/0|0/8/0|
|P4|`run\\\_selfburn`|0/0/8|0/0/8|0/0/8|0/0/8|

The variants changed grief-front cooldown, radius and duration; the probes the
Red-Teamer selected are not sensitive to those dials at this seed count. This is
a real measurement — the crew measured, found no separation, and said so. It is
not evidence that the variants are equivalent; it is evidence that these four
probes cannot tell them apart.

**Two variants silently altered locked canon.** The merge log shows
`scale.min: -12 -> -10` and `scale.max: 12 -> 10` in the accepted variants. The
run's own question set lists "the scale and bands" as locked and out of scope.
The validation gate passed them because it checks structure, not canon — which is
precisely the division of labour the design intends, and precisely why Keeper B2
exists. Whether B2 caught it is visible in
`contradictions-run-20260728-230752-live.md`.


```

