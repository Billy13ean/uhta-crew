# Assignment 5 — Goal-Oriented Coding Agent

**uhta** · Nicholas Rouke · ELVTR Multi-Agent AI for Game Development

`run_builder.py` reads the Game Design Document, scans the game's source, works out
what the document requires that the code does not have, decides which of those gaps
to close first, and writes the code for it.

It is the third pipeline in this repository. `run_crew.py` (Assignment 3) designs
rulesets; `run_content.py` (Assignment 4) writes the game's prose; this one decides
what to build and builds it. `crew/` and `content/` do not import `builder/` — the
dependency runs one way, so adding this could not change what the other two do.

```bash
python run_builder.py --selftest    # 46 deterministic checks. No API key, no calls.
python run_builder.py --mock-llm    # end to end on canned fixtures
python run_builder.py               # live  (needs ANTHROPIC_API_KEY)
```

---

## 1. What the agent built

**The narrated teaching opening** — GDD §1:

> *"A narrator names each verb the first time you use it; the words end permanently
> at your first Sleep."*

The agent emitted an anchored patch against `uhta-slice.html` adding two pure
resolvers — `narrationOpen(sleepNo)` and `narrationFor(verb, spoken, sleepNo)` —
and **two new assertions to the build's own on-load acceptance self-test**, one per
rule the GDD states:

| new assertion | what it gates |
|---|---|
| `G12 narration: names each verb on FIRST use only` | the same verb narrates once; a *different* verb still narrates |
| `G13 narration: words end PERMANENTLY at the first Sleep` | after sleep 1 and after sleep 9, every verb is silent |

The build went **11/11 → 13/13**, verified by executing it, not by claiming it.

The resolvers are pure functions of their arguments, matching the house pattern
already in the file (`eraOf(sleep_no)`, `roadStageFor(born, now)`) — which is what
lets a headless test gate render behaviour with no browser and no Phaser.

### The gap was a `PARTIAL`, which is the more interesting result

The build is not missing a tutorial. It has `guide()` and a four-flag progression
(`tut.moved / flamed / slept / led`) that writes contextual text through `setTip()`
every frame. The agent found that code and reported it **contradicts §1 in three
specific places**:

| §1 requires | the existing `guide()` |
|---|---|
| the narrator names **each verb** on first use | flags track four *categories of progress*; Roar, Beacon, Raze and Wait are never named on first use |
| the words **end permanently** at the first Sleep | `guide()` never stops — its post-sleep branches are its longest strings |
| tone is mournful, mythic, **wordless** | register is instructional: `press W A S D`, `L-click flame`, `scroll zoom` |

A gap detector that reports *nothing exists* is indistinguishable from one that read
the GDD's own status column. Reporting *this exists, and here are the three lines
where it contradicts the document* is not something a status column can produce.

---

## 2. Why the agent selected that feature

**The ranking is arithmetic. No model produced it.** Every term is computed in
`builder/priority.py` and printed beside every feature in `PRIORITY.md`, so it can
be recomputed by hand:

```
score =  5.0 · (§4 acceptance criteria this feature blocks)
       +       tier weight   (CORE 4 · PASS 1 3 · PASS 2 2 · NICE 1 · PROPOSED 0 · CUT −2)
       +  1.5 if no unmet dependency, −3.0 if gated on the stranger test
       −  0.5 · estimated size
       −  4.0 if below the CORE/PASS-1 line AND not unblocking a §4 criterion
```

| # | feature | tier | scan | gate | tier | dep | cost | stop | **total** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `narrated-teaching-opening` | NICE | ABSENT | **+10.0** | +1.0 | +1.5 | −1.5 | **+0.0** | **+11.00** |
| 2 | `the-12-12-scale` | CORE | PARTIAL | +0.0 | +4.0 | +1.5 | −1.5 | +0.0 | +4.00 |
| … | | | | | | | | | |
| 24 | `wordless-endscreen` | NICE | ABSENT | +0.0 | +1.0 | +1.5 | −1.5 | **−4.0** | −3.00 |

**The winner comes from the bottom tier and wins by 7.0.** That is the whole point
of the exercise, and it turns on two terms:

**`gate`.** The narrated opening is the named blocker on Definition-of-Playable
criteria **1 and 3**. §4 is the acceptance test the entire project is paused on —
"0 of 6 tested" — so a criterion nobody can pass is worth more than a tier nobody
has reached. Two criteria × 5.0 = **+10.0**, and nothing else in the inventory
scores on this term at all.

**`stop`.** GDD §3 forbids building anything below the CORE/PASS-1 line until a
stranger has played the loop — *except work that unblocks a §4 criterion, which is
the gate rather than a violation.* The agent evaluates that carve-out from the
rule's text and waives the −4.0 penalty for this feature alone. Compare row 24:
`wordless-endscreen` is the same NICE tier, blocks no criterion, and keeps the full
penalty.

So the ranking reproduces the Director's own written stop rule — arriving at it
from the rule, not from its conclusion.

### The agent is not allowed to read the answer

§3's table self-reports Built / Unbuilt for every tier. Feeding that to the gap
detector would make this a table lookup wearing a codebase scan as a costume.

`Feature.for_detection()` returns only `id`, `name`, `gdd_section`, `kind`,
`description` and `signature`. Tier, claimed status and gate information are
withheld, and `--selftest` asserts the withholding three ways (B1–B3), including a
check that no tier or status *string* leaks through the payload.

That independence is what makes the **cross-check** worth reading. After detection
has committed to a verdict, `GAP-REPORT.md` compares it against §3's column, and
every disagreement is a finding. An agent that had merely read that column could
not possibly disagree with it.

---

## 3. Were you able to run it in your game?

**Yes — and the pipeline refuses to write a patch it has not run.**

The last of five validation checks is not static analysis. `check_selftest_runs()`
executes the patched build headlessly under Node with a minimal DOM stub (the build
already guards for a missing Phaser), reads back its self-test panel, and requires
every assertion green:

```
=== the committed build ===          11 PASS / 0 FAIL
=== the agent's patched build ===    13 PASS / 0 FAIL
  PASS  G12 narration: names each verb on FIRST use only
        [flame#1 spoke, flame#2 silent, roar#1 spoke]
  PASS  G13 narration: words end PERMANENTLY at the first Sleep
        [after sleep 1 silent; after sleep 9 silent]
  ✓ port faithful — all checks pass
```

**This check caught a real bug that `node --check` could not.** The first patch
anchored the narration module next to `setTip()`, which is syntactically perfect
and kills the build on load: `selfTest()` runs inline partway down the file, so
anything declared below it is in the temporal dead zone when the assertions
execute. The build died with `Cannot access 'narrationOpen' before initialization`
— and a syntax check passed it. Executing the patch is what found it. That failure
mode is now a named halt (`J10`) and a warning in `prompts/programmer.md`.

The in-place build is **not** modified. The run writes `uhta-slice.patched.html`
and `patch.diff` into its own directory and stops. The rules crew stops at a blank
`## Ruling`, the content pipeline stops at an unfilled `## Director selection`, and
this one stops here, for the same reason — the Director applies it.

---

## 4. How it works

```
extract    GDD  -> feature inventory       deterministic tables + Analyst (temp 0)
scan       code -> symbol / key-path index deterministic, SCAN_POLICY
gap        compare -> PRESENT/PARTIAL/ABSENT + evidence   probe, then adjudicate
prioritize -> ranked table, every term shown              NO LLM
generate   -> anchored patch + new assertions             Programmer (temp 0.2)
                                                          -> the Director applies it
```

Every arrow is a file, written through `crew/blackboard.py`, so every byte the
pipeline read lands in `RUN-LOG.md` with a size and a SHA-256 prefix. The scan's
inputs are auditable rather than asserted.

**Where the model sits, and where it does not, is the design.** The LLM writes
`observable_signature` (a judgement about implementation), adjudicates ambiguous
gaps, and writes code. It does not rank, does not score, and never authors a
number that reaches a document — the same rule the A3 Playtester's board follows.

### Two scoping policies, each with a reason per cut

**`BUILDER_POLICY` is not `CORPUS_POLICY`, and it can't be.** A4's policy scopes by
top-level section number and those numbers are v0.9.7's; v0.9.9 renumbers, so §3 is
now Build Order and §4 is now Definition of Playable. Reusing it unchanged would
exclude exactly the two sections this pipeline runs on, while including §5 and §6,
which are pipeline material.

The deeper reason isn't numbering: **the two pipelines want opposite things from
the same document.** A4 wanted game material only, because it was writing prose a
player reads — a narration line grounded in the agent roster would be about the
pipeline. A5 wants game material *plus* the build order and the acceptance test,
because those are the criteria the decision is made against.

**`SCAN_POLICY` is the code-side twin of A4's §4.5 exclusion.** This build vendors
Phaser inline — one line, **1,181,901 characters**. Phaser defines `Scene`,
`World`, `Tween`, `Zone`, `Wander`. Index it and nearly every feature the GDD names
comes back PRESENT. §4.5 was excluded from the corpus because indexing it let the
Writer retrieve the answer instead of writing one; Phaser is excluded from the scan
because indexing it makes every feature *look* already built. Same failure, one
level down: the corpus contains something that silently defeats the pipeline's
purpose, findable only by reading the actual bytes.

The run excludes **5 regions, 1,253,989 characters**, each with a recorded reason,
and `--selftest` E3 asserts that `TweenManager` and `WebGLRenderer` are *not* in
the index.

### Halt discipline

Inherited from the A3 crew and the A4 Critic, whose rule is *a catch shown, not
claimed*:

| stage | what halts the run |
|---|---|
| Analyst | a feature returned with an empty `observable_signature` — unscannable, so it would report ABSENT for free |
| Adjudicator | `PRESENT`/`PARTIAL` with no quoted line · `ABSENT` with nothing searched-for · **a quotation that isn't in the source** |
| Programmer | anchor missing or ambiguous · an existing assertion lost · no new assertion added · doesn't parse · **doesn't run green** |
| any stage | `FAILED.md` names the agent and the stage. Never a traceback to the terminal; exit 1. |

The fabricated-quotation check verifies the quoted line against the actual bytes.
An invented quote is the one failure this stage must not permit, because it reads
exactly like proof.

The Programmer gets **one** repair round-trip carrying the validator's own error
text; a second failure aborts. Same shape as A3's validation gate, for the same
reason: one bounded retry is a typo fixed, an unbounded one is a model arguing with
a checker.

---

## 5. Files

| path | what it is |
|---|---|
| `run_builder.py` | entry point + the 46-assertion selftest |
| `builder/policy.py` | `BUILDER_POLICY` and `SCAN_POLICY`, with reasons |
| `builder/features.py` | GDD → feature inventory; the status-column withholding |
| `builder/codescan.py` | symbol / literal / key-path index over authored source |
| `builder/gap.py` | layer-1 probe, layer-2 adjudication, the cross-check |
| `builder/priority.py` | the scoring function — no LLM |
| `builder/generate.py` | patch, five validation checks, one repair round-trip |
| `builder/pipeline.py` | stage sequencing, manifest, halt |
| `builder/assemble.py` | the evidence documents, generated from the run |
| `builder/fixtures.py` | `--mock-llm` backend |
| `prompts/{analyst,gap-adjudicator,programmer}.md` | versioned prompts |
| `blackboard/build/uhta-slice.html` | the game — the scan target |
| `blackboard/gdd/uhta-gdd-v0.9.9-condensed.md` | the current GDD |

Per run, in `out/<run-id>/`: `FEATURES.md` · `GAP-REPORT.md` · `PRIORITY.md` ·
`GENERATED.md` · `patch.diff` · `uhta-slice.patched.html` · `RUN-LOG.md` ·
`manifest.json`.

---

## 6. What this does not establish

- **The scan is regex over source, not a parser.** It finds evidence with a
  `file:line` attached, which is what the gap stage quotes. A feature implemented
  under a name nothing in its signature predicts will read as a false gap. The
  signature asks for several spellings to blunt this; it does not eliminate it.
- **The weights are the Director's judgement.** `W_GATE = 5.0` is a stated
  priority, not a measurement. What the arithmetic buys is that the judgement is
  visible and checkable, not that it is correct.
- **`--mock-llm` output is not evidence about the codebase.** Every artifact from
  a mock run is banner-stamped as such.
- **Whether the narration is any good is not a question this pipeline can answer.**
  It verified that the words appear once per verb and stop at the first Sleep. Its
  *lines* come from the A4 Writer→Critic loop, and whether they land is §4's
  stranger test — the layer none of these three pipelines has.
