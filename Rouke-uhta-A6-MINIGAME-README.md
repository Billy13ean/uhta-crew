# Assignment 6, pipeline #2 — a mini-game GER pipeline for *uhta*

> Nicholas Rouke · ELVTR Multi-Agent AI for Game Development · due 18 Aug
> The pipeline: `run_minigame.py` + `minigame/` — the fifth pipeline in
> `uhta-crew`, and the first with a **human gate in the middle**: it
> recommends encounter mini-games, stops for a Director ruling, and only
> then hands the selected design to a Programmer agent that patches the
> game. Submitted alongside pipeline #1 (`Rouke-uhta-A6-README.md`, the
> narration GER pipeline).

---

## 0. Pre-Build Declaration (submitted before any code was written)

**1. What content type does your game currently generate manually,
inconsistently, or not at all?**
Encounter mini-game designs. My GDD's PROPOSED tier specifies three
encounter types × two poles (first contact, the vigil, the holding) — the
only moment the player touches individuals — designed on paper, never
generated, never built.

**2. What specific rule from your GDD must every piece of that content
satisfy?**
The GDD §2 encounter rules: encounters are wordless and diegetic — "no
interface, no text, only your body and theirs" — and "the two poles never
play the same game" (Hope plays patience, depth, few; Fear plays speed,
force, many).

**3. What does a failure look like — concretely, in your game's terms?**
A mini-game that needs a HUD, prompt text, or button labels — or a Hope
variant that plays like Fear's, e.g. a first contact where Hope also chases
down runners.

---

## 1. The shape — GER, then a human, then a Programmer

```
PROPOSE   corpus ──> per slot (3 encounters x 2 poles):
          Designer ──> Evaluator ──FAIL──> Refiner ──> Evaluator ──…
            (0.9)     (gate+judge)          (0.2)         │
                          │ PASS               round cap: │ ESCALATE
                          ▼                    (breaker; 3 trips the run)
          MINIGAME-CANDIDATES.md  ──── THE RUN ENDS HERE ────

DIRECTOR  reads the candidates, rules, and types:
          python3 run_minigame.py --build --select <id> --from-run <run>

BUILD     Programmer (0.2) ──> anchored patch ──> deterministic post-checks
          ──> ONE repair round ──> uhta-slice.minigame.patched.html
          ──> the Director applies and verifies in a browser
```

The human gate is **structural, not procedural**: the build phase's required
arguments ARE the Director's ruling. There is no code path from generation
to build that does not pass through a person typing a selection — and an
ESCALATED design cannot be selected at all (`--select holding-fear` on the
demo run exits 1 with "Escalated designs cannot be built — that is the gate
working, not a bug").

**Why encounters.** The GDD designs exactly this content and gates building
it: the PROPOSED tier's encounter table is "the one place you touch a
person," and §3's stop rule holds encounter builds behind the stranger test.
The pipeline respects that gate in its architecture — propose-mode spends
tokens on design (which the stop rule does not restrict), build-mode cannot
run without the Director, and MINIGAME-BUILD.md states plainly that applying
the patch to the canonical slice remains gated on the stranger test. The
recommender can read the stop rule because §3 is deliberately in its corpus.

## 2. Research + retrieval — the recommender half

The corpus is three documents under a **per-document policy**
(`minigame/corpus.py`), because A4's number-keyed policy cannot serve it:
GDD v0.9.9's §3/§4 are game material (tiers, stop rule, Definition of
Playable) while v0.9.7's §3/§4 are pipeline material (AI architecture,
technical strategy, and the Director's hand-written worked example in §4.5).
Same numbers, opposite rulings — so the policy is keyed by (document,
section), every cut with a reason, asserted in `--selftest`.

- `uhta-gdd-v0.9.9-condensed.md` §1–§4 — the only GDD with the encounter
  table.
- `uhta-gdd-v0.9.7-full.md` §2 only — the mechanics detail (verb costs,
  burnout, systems) the condensed doc compresses.
- `blackboard/research/minigame-patterns.md` — **the researched half**: ten
  mini-game design patterns curated from published design writing (herding /
  pressure steering, threshold-fight steady holds, timing windows, path
  tracing, procession escort, interception, triage, weak-point sequencing,
  diegetic no-HUD state display, and integration principles for mini-games
  in a host game), each summarised with its source and its wordless
  feasibility. Sources include Game Developer's RPG mini-game and fishing
  taxonomy pieces, the Kyon herding devblog, and Wayline's diegetic
  interface essay.

Each slot retrieves with **three queries** (the §4.5 two-chunk rule,
extended): the encounter's own design intent, the supporting mechanics, and
a pattern. `--selftest` asserts all six slots retrieve a research-corpus
chunk — the recommender half is measured, not asserted.

## 3. The Evaluator — the rule, in two layers

**Layer 1 — a deterministic design gate** (`minigame/checks.py`), because a
design document is structured and a schema can check structure for free:

| check | rule it enforces |
|---|---|
| C1 SCHEMA | every field of the design contract present |
| C2 VALID-SLOT | one of the six GDD slots |
| C3 BUILDABLE-INPUT | controls ⊆ the slice's real inputs — a design this build cannot receive input for cannot be built into it |
| C4 REAL-STAKES | effects ⊆ the sim's outcome vocabulary — the integration-research principle 'stakes wired to the main loop', made mechanical |
| C5 WORDLESS | no interface/text vocabulary in player-facing fields — "no interface, no text, only your body and theirs" |
| C6 SHORT | "a short, wordless, diegetic exchange" |

**Layer 2 — an LLM Judge** (temp 0) with encounter-specific flag classes:
`NOT-DIEGETIC` (implied interfaces count, even with no banned word),
`POLE-SYMMETRY` (the two poles playing the same game — or this pole wearing
the other's texture), plus `CONTRADICTS-CHUNK` / `EXCEEDS-SCOPE` / `GENERIC`
from the house vocabulary. Every FAIL must quote the chunk it rules from;
every PASS must quote the chunk it honors; a `correction` key halts — the
Judge diagnoses, the Refiner repairs, same separation as pipeline #1.

The Refiner returns the full repaired design; a no-op halts. The circuit
breaker is **ger.breaker imported unchanged** — shared machinery, same
thresholds (2 refinements per item, 3 escalations trip the run).

## 4. The build stage — the A5 contract at three anchors, v2

**Build v2 exists because of the first Director playtest**, whose finding
was blunt: a mechanically-correct encounter with no entrance and no words
is invisible — the Director could not find it, and could not have learned
it if he had. The fix was not to break the wordless rule but to seat the
two GDD §5 roles the build stage had skipped:

- **The Instructor (the Writer's seat)** writes ONE first-use narration
  line — legal because the encounter arms on sleep 0, inside the game's
  narrated window — held to the same register gate as the verb narration
  (`ger.checks`, reused; a `press`/`click` line cannot re-enter through
  the mini-game door, asserted in `--selftest`).
- **The Presenter (the Aesthetic Director's seat)** produces a diegetic
  presentation spec — an attention cue, an entry transition that MUST
  pause and reframe the world (gate P3), a visual hierarchy, a signal map,
  feedback moments — held to the same wordless vocabulary as designs
  (gate P2).

Two new deterministic post-checks hold the Programmer to them: the patch
must contain a `location.hash` **Director test hook** (`uhta-slice.html#mg`
force-arms the encounter, so verification never depends on spawn luck) and
the Instructor's line **verbatim** (matched escaping-insensitively). In the
first live v2 run the Programmer omitted the line, the check caught it, and
the one repair round-trip fixed it — the contract doing exactly what it is
for.

**Contract v3 exists because of the SECOND Director playtest**: the v2
patch was correct and still imperceptible, and the diagnosis was
structural — a three-anchor contract gave the Programmer no seat in the
per-frame loop, so the generated encounter could only advance one tick per
verb click. v3 is five anchors: **frame** (inside `drawWorld`, right after
the per-frame graphics clears — the encounter steps, reads input and draws
into the build's own `this.overlay` Graphics object here, leak-free) and
**input** (the first line of `onClick` — an early-return guard so the
encounter owns the pointer, and feeding the flame does not also fire the
Flame verb), alongside logic, self-test, and an now-OPTIONAL verb-trigger
hook (a proximity-triggered design legitimately has nothing to put there —
the first v3 run proved it by omitting the key, and the contract was wrong
before the Programmer was).

The Programmer receives the selected design, the instructions, the
presentation spec, and code excerpts around the five deterministically-
extracted anchors in the real build (anchored regexes, not a scan — the
vendored-Phaser lesson):

1. **logic** — after the pure-resolver region: state, pure `mg*` functions,
   the overlay, input handling;
2. **self-test** — inside the on-load self-test: new `M`-numbered
   assertions on the pure logic;
3. **hook** — after the verb dispatch: one guarded line that arms the
   encounter.

Deterministic post-checks before anything is written: each anchor unique;
every pre-existing G-assertion survives verbatim; at least one M-assertion
added; each block passes `node --check` (a labelled brace-balance fallback
if node is absent); the file grew. One repair round-trip with the checker's
error text, then FAILED.md. The in-place build is never touched.

The mock fixture patch is **hand-authored real code that passes every one of
those checks against the real slice** — proof the contract is satisfiable,
not merely specified. What no check can decide — whether the encounter
*feels* like the GDD's sentence — is on the Director checklist in
MINIGAME-BUILD.md, because that is the part of this rubric a container
cannot grade.

## 5. Run modes and evidence

```
python3 run_minigame.py --selftest      # 48 assertions, no key, no calls
python3 run_minigame.py --mock-llm --run-id mock-demo-mg
                                        # propose: every path — 3 round-0
                                        # accepts, a C5 catch+repair, a
                                        # POLE-SYMMETRY catch+repair, and
                                        # holding-fear ESCALATED
python3 run_minigame.py --mock-llm --build --select first-contact-hope \
        --from-run mock-demo-mg         # build: fixture patch, checks green
python3 run_minigame.py                 # LIVE propose (~15–25 calls, ~$1)
python3 run_minigame.py --build --select <id> --from-run <run>
                                        # LIVE build (1–2 large calls)
```

Artifacts per propose run: **`MINIGAME-DASHBOARD.html` — the human gate as an interactive checklist**: one card per candidate carrying THE RULES and THE VISUALS (drop-in for the render layer) plus the Judge's cited verdict; the Director checks approvals and the page generates the signed ruling with the exact build command per approved item (the gate stays structural — the dashboard writes the command, a human runs it); `MINIGAME-CANDIDATES.md` (the same gate in prose, ending at the unfilled
Director selection), `CANDIDATES.json` (what the build phase reads),
`MG-GER-LOG.md`, `MG-ESCALATED.md`, `rounds/` (every draft and finding as a
file — the Judge reads candidates off disk), `RUN-LOG.md`, `manifest.json`.
Per build run: `SELECTED-DESIGN.json`, `MINIGAME-BUILD.md`,
`uhta-slice.minigame.patched.html`.

**The Playtester's seat, added mid-assignment:** `tools/mg_probe.js` — a
headless-Chromium play-probe that now GATES every live build. It drives the
patched build like a player (cave, WASD, taps, idle, resolution) and
rejects what static checks cannot see; two statically-green patches were
convicted by it. On machines without playwright it records
`SKIPPED: playwright not available` rather than passing silently.

**The playable evidence:** `out/mg-directors-cut/` — the Director-ratified
build of the selected design (Steady the Flame), probe 10/10 green,
win-bot full-arc victory, zero page errors, with `DIRECTORS-REPAIR.md` as
the honest iteration ledger: seven Director playtests, every finding named
(a transitioning freeze, a missing per-frame seat, an implied-meter
NOT-DIEGETIC catch, legibility, discovery, anchoring), every fix traced to
evidence. That ledger is this assignment's thesis in miniature: the loop
catches the cheap failures; the human gets the residue with proof
attached.

## 6. Honest limits — including the bug the guards caught

- **The first live run halted on a pipeline bug, and the halt discipline is
  what found it.** The Designer wrote `"First contact" / "Hope"`; the C2
  slot check compared raw strings and failed it; the Refiner — correctly —
  saw nothing wrong with the design and returned it unchanged, which
  tripped the no-op-refinement guard and halted the run by name
  (`FAILED.md`, agent `mg-refiner-first-contact-hope`). The fix: the slot
  identifiers are the pipeline's choice, so the agents now pin them, and C2
  normalises before comparing. A loop without the no-op guard would have
  silently burned its round budget on a cosmetic mismatch; instead the bug
  cost one halt and six calls. The second run accepted all six slots, with
  one real catch (the Judge failing vigil-fear's draft NOT-DIEGETIC for an
  "implied resource meter disguised as diegetic dimming" — the repaired
  design is better).

- **The live Programmer patch is the riskiest artifact in either pipeline.**
  A playable overlay is a much larger generation than pipeline #1's seven
  lines; the contract catches syntax, anchor and assertion failures, but
  "compiles and asserts" is not "plays well" — the Director checklist is
  the real acceptance test, in a browser.
- **The research corpus is curated by hand** (ten patterns, cited). A
  different curation would push the Designer differently; the corpus file
  is versioned in `blackboard/research/` so that influence is inspectable.
- **The stop rule still stands.** This pipeline designs and, on command,
  builds a patch — it does not and cannot decide that an encounter ships.
  0 of 6 stranger-test criteria have changed.
