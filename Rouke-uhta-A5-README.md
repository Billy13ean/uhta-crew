# Rouke — *uhta* — Assignment 5: Goal-Oriented Coding Agent

**Nicholas Rouke · game: *uhta* · ELVTR Multi-Agent AI for Game Development · 13 August 2026**

---

## TL;DR

- **What the agent built.** The **narrated teaching opening** — GDD §1's *"a
  narrator names each verb the first time you use it; the words end permanently
  at your first Sleep."* Seven verb lines, a pure resolver enforcing both rules,
  hooks at every verb dispatch point, and two new self-test assertions. Build
  went **11/11 → 13/13**.
- **Why it selected that feature.** A deterministic score, no LLM, every term
  printed in `PRIORITY.md`. It won at **+11.50, margin 7.0** — from the **NICE**
  tier, the lowest positive weight in §3 — because it blocks Definition-of-Playable
  criteria **1 and 3** (+10.0), and because §3's stop rule carve-out waives the
  −4.0 penalty for work that unblocks a §4 criterion. The agent reproduced the
  Director's own written stop rule by evaluating it, not by being told it.
- **Did it run in the game.** **Yes.** Applied to `uhta-slice.html`, self-test
  green, narration confirmed in play — after a one-line Director amendment for a
  display-duration bug none of the automated checks could see.
- **The honest caveat.** The gap detector under-reports: several features it
  called ABSENT are plainly built. Cause diagnosed in §6 — layer 1's *confident*
  false negatives are exactly the ones layer 2 never re-examines.
- **Run it:** `python run_builder.py --selftest` → 71 assertions, no API key.

---

`run_builder.py` reads the uhta GDD, scans the game's codebase, finds what the
document requires and the code does not have, decides which gap to close first,
and writes the code for it.

It is the third pipeline in this repository. `run_crew.py` (Assignment 3)
designs rulesets; `run_content.py` (Assignment 4) writes the game's prose; this
one decides what to build. `crew/` and `content/` do not import `builder/`, so
adding it could not change what either of them does — `--selftest` on all three
is green.

```
python run_builder.py --selftest    71 deterministic assertions, no API key, no calls
python run_builder.py --mock-llm    end-to-end orchestration on canned fixtures
python run_builder.py --run-id X    live
docker compose run --rm builder --run-id X      # same, containerised
```

The committed evidence is `out/a5-live-v3/`. Every number below is from that run.

---

## 1. What the agent built

**The narrated teaching opening**, in `blackboard/build/uhta-slice.html`.

GDD §1: *"A narrator names each verb the first time you use it; the words end
permanently at your first Sleep."* The build had no such thing. It had `guide()`
— a persistent instructional tip bar keyed to four progress flags
(`moved`/`flamed`/`slept`/`led`), in the register of `press W A S D`, which never
stops.

The agent added:

| | |
|---|---|
| `TEACHING_TEXT` | one line per verb, all seven |
| `teachingFor(verb, sleep_no, spoken)` | pure resolver: `sleep_no!==0 → null`; `spoken.has(verb) → null` |
| hooks in `moveStep` | Walk |
| hooks in `tryAct` | flame · roar · raze · wait · beacon |
| hooks in `doSleep` | Sleep |
| an edit to `guide()` | pending narration takes priority over the old tips |
| `G12`, `G13` | new self-test assertions |

Both GDD rules are implemented literally. The stop is `sleep_no !== 0` — the
first Sleep, not a nearby threshold. First-use is `spoken.has(verb)` — a set of
verbs, not a progress flag. Self-test **11/11 → 13/13**, and the patched build
executes green headlessly.

### The Director amendment

The agent's patch cleared `pending_teaching` on first read. `setTip(this.guide())`
runs every frame from `update()`, so each line displayed for **one frame — about
16 ms — and vanished.** The player would never have seen it.

Every automated check passed: the code is reachable, parses, is asserted, and the
patched build runs green. The bug is invisible to all of them because the
assertions test the pure resolver `teachingFor`, not `guide()`. Ruling: **AMEND**,
one line, recorded in the build:

```js
/* [DIRECTOR AMEND — run a5-live-v3] The agent cleared pending_teaching on first READ,
   and setTip(this.guide()) runs every frame from update(), so each line showed for one
   frame (~16ms) and was gone. Hold it until the next verb overwrites it, and drop it at
   the first Sleep — GDD §1: 'the words end permanently at your first Sleep'. */
if(this.tut.pending_teaching){const txt=TEACHING_TEXT[this.tut.pending_teaching];
  if(txt&&SIM.sleep_no===0)msg=txt; else this.tut.pending_teaching=null;}
```

`out/a5-live-v3/uhta-slice.patched.html` is the agent's unmodified output;
`blackboard/build/uhta-slice.html` is that plus this amendment. The two are kept
separate on purpose, so "what the agent built" is answerable exactly.

---

## 2. Why the agent selected that feature

`builder/priority.py` — **no LLM.** The ranking is arithmetic, every term is
printed beside every feature in `PRIORITY.md`, and it can be recomputed by hand.
A ranking a model narrates cannot be checked by the person grading it.

```
score =  5.0 · (§4 criteria this feature blocks)
       +       tier weight   (CORE 4 · PASS 1 3 · PASS 2 2 · NICE 1 · PROPOSED 0 · CUT −2)
       +  1.5 if no unmet dependency, −3.0 if gated on the stranger test
       −  0.5 · estimated size
       −  4.0 if below the CORE/PASS-1 line AND not unblocking a §4 criterion
```

| # | feature | tier | gate | tier | dep | cost | stop | **total** |
|---|---|---|---|---|---|---|---|---|
| 1 | `narrated-teaching-opening` | **NICE** | +10.0 | +1.0 | +1.5 | −1.0 | **+0.0** | **+11.50** |
| 2 | `verb-flame` | CORE | +0.0 | +4.0 | +1.5 | −1.0 | +0.0 | +4.50 |
| 9 | `beacons` | PASS 1 | +0.0 | +3.0 | +1.5 | −1.0 | +0.0 | +3.50 |
| 17 | `verb-beacon` | PASS 2 | +0.0 | +2.0 | +1.5 | −1.0 | **−4.0** | −1.50 |

**Margin 7.0 — not a coin toss.**

The result is not obvious from the tiers. The narrated opening sits in **NICE**,
the lowest positive tier weight in §3, and it still wins by a wide margin. Two
terms do the work:

- **`gate +10.0`** — it is named by §4 as blocking Definition-of-Playable
  criteria **1 and 3**, at 5.0 each. Those criteria gate the entire remaining
  backlog: the loop has never been played by a stranger, and §4 is what the whole
  project is paused on.
- **`stop +0.0`** — §3's stop rule says *nothing new gets built below the
  CORE/PASS-1 line until §4 passes with a stranger at the keyboard, **except**
  work that unblocks a §4 criterion.* Encoded literally, that is a −4.0 penalty
  with a carve-out condition. Row 17 shows the penalty firing on a PASS-2 item;
  row 1 shows the carve-out waiving it.

So the agent reproduces the Director's own written stop rule by evaluating it,
rather than by being told its conclusion. That is the answer to *why this
feature*: **nothing in CORE or PASS 1 is missing, so tier weight cannot break the
tie, and the gate term decides.**

### The agent is not allowed to read the answer

§3's table self-reports Built / Unbuilt per tier. Feeding that to the gap
detector would make this pipeline a table lookup wearing a codebase scan as a
costume. `Feature.for_detection()` withholds `tier`, `gdd_claimed_status` and
`blocks_criteria`; the detector receives name, section, kind, description and
signature only. Three selftest assertions (`B1`–`B3`) enforce it.

The status column is used once, *after* detection has independently committed to
a verdict, for the cross-check in §6.

---

## 3. Were you able to run it in your game?

**Yes** — with the one-line amendment above.

- `blackboard/build/uhta-slice.html` loads and its acceptance panel reads
  **13 PASS / 0 FAIL** (was 11/11).
- `node tools/verify_slice.js blackboard/build/uhta-slice.html` reproduces that
  headlessly, and `builder/generate.py` runs the same check *before* accepting
  any patch — the patched build is executed, not merely parsed.
- Each verb is named once on the first waking cycle; after the first Sleep the
  narration stops permanently and the existing tips resume.

The in-place build is never modified by the pipeline. The run writes
`uhta-slice.patched.html` and `patch.diff` into its own directory and stops. The
rules crew stops at a blank `## Ruling`, the content pipeline at an unfilled
`## Director selection`; this one stops here, for the same reason.

---

## 4. How it works

```
extract    GDD  -> 63 features        deterministic tables + Analyst LLM
scan       code -> 856 symbols        deterministic, SCAN_POLICY
gap        compare -> PRESENT/PARTIAL/ABSENT + quoted evidence
prioritize -> ranked table            deterministic, no LLM
generate   -> anchored patch + assertions -> Director
```

**Two scoping policies, each with a reason per cut.** `content/retriever.py`
established the pattern; this pipeline needed two more.

`BUILDER_POLICY` exists because `CORPUS_POLICY` **cannot be reused**. It scopes
by top-level section number and those numbers are v0.9.7's; v0.9.9 renumbered, so
§3 is now Build Order and §4 is Definition of Playable. Reusing it would exclude
exactly the two sections this pipeline runs on. The deeper reason is not
numbering: the content pipeline wanted game material *only*, because it was
writing prose a player reads. This one wants game material *plus* the project's
build order and acceptance test, because those are the decision's criteria. Same
corpus, two policies, because the consumer differs.

`SCAN_POLICY` is the code-side analogue of A4's §4.5 exclusion. The build vendors
Phaser 3 inline — **one line, 1,181,901 characters.** Phaser defines `Scene`,
`World`, `Tween`, `Zone`, `Wander`. Index it and nearly every feature the GDD
names comes back PRESENT. The run excluded **5 regions, 1,253,989 characters**,
each with a recorded reason. A4 excluded §4.5 because indexing it let the Writer
retrieve the answer instead of writing one; this excludes Phaser because indexing
it makes every feature *look* already built. Both are only findable by reading the
actual bytes.

**Halt discipline**, inherited from the crew and extended. A stage that produces
something unusable stops the run by name rather than letting the next stage
invent a substitute:

| Guard | Rejects |
|---|---|
| Analyst | a feature with an empty `observable_signature` — it would report ABSENT for free |
| Analyst | a truncated response (open ```json fence, no close) — named as a `max_tokens` cutoff |
| Gap adjudicator | PRESENT/PARTIAL with no quoted code line; ABSENT with nothing searched-for |
| Gap adjudicator | a **fabricated** quotation — checked against the real bytes |
| Patch | an anchor that is not on the menu, or a reused `G`-number |
| Patch | a declaration nothing outside `selfTest()` references — **dead code** |
| Patch | JS that does not parse; a patched build that throws or goes red when run |

---

## 5. What three failed live runs changed

The first three live runs all halted in stage 5. Each was a hole in the patch
contract, and each is now a named regression test.

**Run 1 — hallucinated anchors.** The Programmer was asked for a line copied
verbatim from the file. It emitted `function roadStageFor(born,now){…}` and
`function eraOf(sleep_no){…'genesis'…}` — real function names, invented bodies.
The cause was structural: `code_context()` shows only the lines the *gap detector*
matched, and a genuinely-missing feature matches nothing, so the model was asked
to copy from a file it had never been shown. **Fix:** anchors are chosen from a
numbered menu of real lines by **index**. An index resolves or is out of range.
(`K5.1`, `K5.2`)

**Run 2 — anchors valid, insertion point inside a literal.** `SyntaxError:
Unexpected token 'const'`. Six of the eleven self-test anchors were the *opening
line* of a multi-line `out.push([…])`, and `const F32={` opens six lines of object
literal. **Fix:** menu entries must be balanced, complete statements — and `L4`
proves it behaviourally by inserting real code after all 27 and parsing each.

**Run 3 — the patch passed everything and delivered nothing.** It added a pure
resolver, asserted it, and never called it from the game. Build green, assertion
green, player sees nothing. It also numbered its assertion `G9` against an
existing `G9`. **Fix:** `check_reachable` makes unreferenced declarations a halt;
`check_assertions` rejects a reused G-number. (`M1`, `M2`)

**Run 4 (`a5-live-v3`) — landed**, 0 repair round-trips.

The direction of every fix was the same: **remove the model's freedom to compose
text that must match the file.** After run 3's fix the Programmer wired its code
in correctly and then invented an `edits` anchor — the last free-text field. It
now takes an id from a hook menu too. No anchor anywhere in the patch contract is
model-composed text. (`N1`–`N6`)

---

## 6. What this does not establish

**The gap detector under-reports, and the cross-check inherits it.** The run
recorded 19 disagreements with §3's Built/Unbuilt column. Read the list and most
are the detector being wrong, not the GDD: `verb-sleep`, `the-12-12-scale`,
`the-unification-win-loss-check`, `genesis`, `settling`, `beacons`,
`worship-stamina` and `peer-contagion` are all reported **ABSENT** and are all
plainly present in the build. The cause is precise —
`gap.needs_adjudication()` escalates a PARTIAL or a thin-signature ABSENT to the
LLM layer, but a **confident** ABSENT with a rich signature is never re-examined.
Layer 1 decided 50 of 63 features; its false negatives are exactly the ones layer
2 never sees. The cross-check is therefore evidence that the detector reads code
independently of the status column — which was its purpose — and **not** evidence
that the GDD is wrong.

The layer-2 findings are better: `verb-roar` PARTIAL because road-carving lives in
the render layer's `onClick` and not in the sim's roar branch is a fair reading.

**The Programmer's rationale cited a source that does not exist.** `GENERATED.md`
attributes the spec to *"GDD v0.9.2 ruling 5"*. The GDD is v0.9.9 and has no such
ruling. The requirement it implemented is real and correct — §1 says exactly what
the patch does — but the provenance was invented. Prose is the one output here
that nothing checks, which is precisely why the numbers in `PRIORITY.md` are
generated rather than written.

**One dead constant survived.** `TEACHING_CONSEQUENCES` is declared and never
referenced. `check_reachable` requires *one* declaration to be reachable, because
demanding it of all of them wrongly rejects a lookup table used only by its own
resolver. The looser rule lets an unused sibling through.

**The feature has still not been playtested.** GDD §4 remains 0 of 6 tested. This
pipeline can now unblock criteria 1 and 3; whether a stranger actually reaches
their first Sleep unaided is what §4 exists to find out, and no agent in this
repository can answer it.

**Cost.** Four live runs, roughly $3 total. The binding constraint was Director
review time, not tokens — consistent with GDD §6.

---

## 7. Files

| Path | What |
|---|---|
| `run_builder.py` | entry point · `--selftest` (71 assertions) · `--mock-llm` · live |
| `builder/policy.py` | `BUILDER_POLICY`, `SCAN_POLICY`, reason per cut |
| `builder/features.py` | GDD tables + Analyst; the withholding |
| `builder/codescan.py` | symbol / literal / key-path index |
| `builder/gap.py` | two-layer detection, evidence guards, cross-check |
| `builder/priority.py` | the ranking. No LLM |
| `builder/generate.py` | anchor menus, five checks, one repair round-trip |
| `prompts/{analyst,gap-adjudicator,programmer}.md` | versioned, with each live-run fix recorded in the header |
| `tools/verify_slice.js` | headless run of the build's own acceptance self-test |
| `out/a5-live-v3/` | the committed run |
| `Dockerfile.builder` | separate image — the crew image has no Node, and `builder/generate.py` needs it |
