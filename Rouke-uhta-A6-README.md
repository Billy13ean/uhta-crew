# Assignment 6 — a GER pipeline for *uhta*

> Nicholas Rouke · ELVTR Multi-Agent AI for Game Development · due 18 Aug
> The pipeline: `run_ger.py` + `ger/` — the fourth pipeline in `uhta-crew`,
> alongside `run_crew.py` (A3, the game's numbers), `run_content.py` (A4, the
> game's words in bulk) and `run_builder.py` (A5, the goal-oriented coder).

---

## 0. Pre-Build Declaration (submitted before any code was written)

**1. What content type does your game currently generate manually,
inconsistently, or not at all?**
First-use verb narration: the single line the narrator speaks the first time
the player uses each of uhta's seven verbs (Walk, Flame, Roar, Beacon, Raze,
Wait, Sleep). The current build has no narration at all — its `guide()`
tutorial text is instructional UI copy, hand-written.

**2. What specific rule from your GDD must every piece of that content
satisfy?**
The narration register rule (GDD §2.5): "short, declarative, second person.
Names the verb and states its consequence … 'short declarative lines, no
mythology'" — in a game whose tone is "mournful, mythic, wordless" after the
first dawn (§1).

**3. What does a failure look like — concretely, in your game's terms?**
A line like "press W A S D to move": instructional interface language. My
build already contains this failure — `guide()` says exactly that.

---

## 1. What the pipeline generates, and why this content type

**The game is *uhta*** — a wordless browser god-game about emotional
contagion, where the only words the player ever hears are one narrated
opening cycle: "a narrator names each verb the first time you use it," and
"the words end permanently at your first Sleep" (GDD §2.5).

The A5 run built the display mechanism for exactly those words — a
`TEACHING_TEXT` const in `blackboard/build/uhta-slice.html`, seven verbs,
gated by self-test assertions G12 (each verb narrated once, on sleep 0 only)
and G13 (all seven verbs covered). But the A5 submission runbook's "Known
gaps" section says plainly: *the narration lines in the patch are the
mechanism's, not the Writer's* — the Programmer agent stubbed them so its
patch would pass its own assertions. Seven placeholder lines are shipping in
the build today.

**The GER pipeline generates the seven real lines** and closes that loop:

```
per verb:  Generator ──> Evaluator ──FAIL──> Refiner ──> Evaluator ──…
              (0.9)      (gate + judge)        (0.2)
                             │ PASS                        round cap hit
                             ▼                                  │
                         ACCEPTED                    Circuit Breaker: ESCALATE
                                                     (global cap: halt the run)
```

Retrieval is the A4 retriever reused as-is — BM25 over the GDD with the same
`game-material-only` corpus policy, §4.5 excluded (it contains my own
hand-written worked narration example; indexing it lets a generator retrieve
the answer instead of writing one), two queries per verb per the GDD §4.5
two-chunk rule. Six verbs reuse A4's narration-beat queries verbatim; **Raze
is new** — A4 had no raze beat, so the mechanism A5 built covers a verb the
content pipeline never wrote. The gap between those two artifacts is itself
something this assignment surfaced.

## 2. The Evaluator — the rule, and where it lives in the GDD

The rule is the §2.5 register rule from the declaration, enforced in **two
layers**, and the split is the design:

**Layer 1 — a deterministic register gate (`ger/checks.py`). No LLM.**
Everything a regex CAN check is checked for free, reproducibly, before any
model is consulted:

| check | rule text it enforces |
|---|---|
| R1 NAMES-VERB | §2.5 "a narrator names each verb the first time you use it" |
| R2 NO-UI-LANGUAGE | the wordless-tone corollary: `press`, `click`, `WASD`, `key`… is a tutorial overlay, not a narrator |
| R3 SHORT | §2.5 "short declarative lines" (gate: 120 chars / 24 words — above every line the Director has shipped, so it rejects paragraphs, not style) |
| R4 DECLARATIVE | same clause — the narrator states, never asks or exclaims |
| R5 NO-NUMBERS | §2.3 banded display — the player never sees a number |
| R6 SECOND-PERSON | §2.5 "second person" |

**Layer 2 — an LLM judge (temp 0)** that spends its call only on what a regex
cannot decide, using A4's Critic flag vocabulary unchanged: `EXCEEDS-SCOPE`
(mythology, invented canon), `CONTRADICTS-CHUNK` (asserts or omits against
the verb's own §2.2 row), `WRONG-REGISTER`, `GENERIC`. A FAIL with no quoted
chunk, no class, or no reason **halts the run** — an uncited rejection cannot
be audited.

One structural rule distinguishes this Evaluator from A4's Critic, enforced
in code: **it cannot repair.** A response carrying a `correction` key raises
`AgentError`. Diagnosis is the Evaluator's; repair is the Refiner's; a judge
that supplies the fix is grading its own homework, and the loop would never
exercise the Refiner it exists to demonstrate.

## 3. The Refiner and the Circuit Breaker

The **Refiner** (temp 0.2) receives the failing line plus the findings —
deterministic check names with the offending fragment, and/or the judge's
cited verdict — and returns one repaired line. A refinement that returns the
line unchanged halts: a no-op repair sends the identical line back to the
identical judge and spends a breaker round learning nothing.

The **Circuit Breaker** has two tiers, and keeps a distinction the rest of
the repo already draws. Per verb: after 2 failed refinements the verb is
**ESCALATED** — the loop stops spending on it, and `ESCALATED.md` hands the
Director the full round history, every line, every finding. Escalation is a
first-class outcome, not a failure: the blocker this assignment names is that
reviewing every output manually is slower than writing the content yourself,
and the fix is a loop that self-corrects the cheap failures and hands a human
only the residue, with evidence attached. Globally: **3 escalations trip the
run** — at that rate the Generator/Evaluator pair is misaligned and every
further call is money spent proving it; the trip fires the moment the limit
is reached, not at end of run. Structural contract violations (unparseable
output, unquoted FAILs, no-op refinements) never reach the breaker — they
halt immediately, exactly as in A3/A4/A5. The breaker meters **content that
won't converge**; halts punish **contracts that were broken**.

## 4. Did the pipeline catch something I would have missed?

Yes — and by design it caught things in **shipped text**, not just its own
drafts. Stage 2 is a baseline audit: before generating anything, the
Evaluator is pointed at the text already in the build.

1. **The register gate fails the shipped `guide()` tutorial strings** —
   `press W A S D`, `Left-click`, `press space` — the exact failure class the
   Pre-Build Declaration named, found in text that is in the game today (and
   that survived four assignments of review). `BASELINE-AUDIT.md` lists each
   string with its findings.
2. **The judge audits the seven stub `TEACHING_TEXT` lines** A5's Programmer
   wrote. All seven pass the deterministic gate — their defects are judgment
   defects, which is the point of having a layer 2. The expected catch (and
   the canned one the mock run demonstrates): the stub roar line — *"You
   roar. The sound carves a road through the land."* — names the road and
   omits Roar's load-bearing consequence, the **unconditional Fear push on
   every witness regardless of flame color** (§2.2). A Hope player reading
   that stub learns nothing about the verb's cost, which is the single most
   important thing to know before roaring. See the live run's
   `BASELINE-AUDIT.md` for what the real judge ruled.
3. **In the loop itself**, every FAIL verdict in `GER-LOG.md` is a catch with
   the chunk it was ruled from — and every one was either repaired by the
   Refiner or escalated by the breaker. The pipeline has no third path.

## 5. Run modes and evidence

```
python3 run_ger.py --selftest    # 38 assertions, no API key, no calls
python3 run_ger.py --mock-llm    # full loop on fixtures scripted to walk
                                 # EVERY path: round-0 accepts, a determin-
                                 # istic catch+repair (roar), an LLM
                                 # catch+repair (flame), and an ESCALATION
                                 # (raze) — banner-stamped, not content
python3 run_ger.py               # live (~21–35 calls, ~$1, 5–10 min)
```

Every run writes to `out/<run-id>/`: `RUN-LOG.md` (every blackboard read and
write — each round's draft and findings are files, and the Evaluator judges
the line it reads off disk), `BASELINE-AUDIT.md`, `GER-LOG.md`,
`teaching-lines.md` (ending, like every pipeline in this repo, at an unfilled
`## Director selection` block), `ESCALATED.md` when the breaker fired,
`teaching-text.snippet.js`, and `uhta-slice.patched.html` — the build with
the one `TEACHING_TEXT` line replaced, written only after deterministic
post-checks (const occurs exactly once; every pre-existing self-test
assertion survives verbatim; re-extracting the const returns exactly the
accepted lines). The in-place build is never touched; the Director applies.

## 6. Honest limits

- **The register gate's numbers are mine.** 120 chars / 24 words is a stated,
  testable proxy for "short", calibrated above every shipped line — not a GDD
  constant.
- **The breaker's thresholds are budget policy,** not measured optima: 2
  rounds per verb ≈ the point where a third identical failure has stopped
  being information; 3 escalations of 7 ≈ systemic.
- **A mock run proves orchestration, not content.** Its verdicts are canned
  and say so in every artifact; the register-gate findings within it are real
  (the gate is code).
- **This still does not test whether the game is fun.** The words this
  pipeline writes feed Definition-of-Playable criteria 1 and 3; the stranger
  test remains 0 of 6.
