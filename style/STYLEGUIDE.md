# The uhta Style Guide — v1.0

> Assignment 7 artifact · Nicholas Rouke · ELVTR Multi-Agent AI for Game Development
> Derived entirely from `uhta-gdd-v0.9.7` (full + abridged) and prior assignments
> (A4 content pipeline, A6 GER pipeline). Every rule below carries a GDD citation.
> This document is machine-read: `style/spec.py` loads it, hashes it into the run
> manifest, and asserts at selftest that every rule ID here exists in the spec.

---

## 0. What game this is for

*uhta* (ūhta, m. — "the last part of the night, before dawn") is a wordless
browser god-game about emotional contagion. You are a kaiju-scale counterpoint
to **Uhtcearu**, the grieving god whose sorrow is the sky. People live on a
−12..+12 emotion scale between **Hope** and **Fear**, with **Apathy** at grey
zero; belief spreads person to person; a generation passes every time you
**Sleep**. The seven verbs are **Walk, Flame, Roar, Beacon, Raze, Wait, Sleep**.

Text is nearly extinct in this game by design, which is exactly why the words
that do exist must be policed this hard. GDD §1 Tone: "Mournful, mythic,
wordless — **after the first dawn** … One voice, spent in the first cycle,
never heard again — the silence afterward is itself a statement."

## 1. The two registers

Every piece of game text belongs to exactly one register. A line judged in the
wrong register is a violation even if it would pass in the other.

**Register A — Instrumentation (the teacher).** The narrated first cycle only
(GDD §2.5): "as each verb is first used, it is named and its consequence stated
plainly … short declarative lines, no mythology." Enforced by the A6 GER
pipeline; restated here because the Evaluator must know both registers to score
either.

**Register B — Myth (everything after the words end).** Era/settlement flavor,
the endscreen epilogue candidate, any Director-sanctioned word moment outside
the first cycle. Mournful, mythic, restrained. **Canon constraint on surface:**
under the wordless pillar these lines have no mid-run surface; they are banked
candidates for the endscreen epilogue (GDD §6, Narrative F5 — open) and for
era-transition cards **pending a Director ruling**. The pipeline generates and
polices candidates; it does not decide where words appear. That is a gate this
loop deliberately does not own.

## 2. The rules

### Constraint type 1 — TONE (rules T1–T4)

- **T1 · Mournful restraint.** No enthusiasm, no triumph, no cheer. The world
  is in mourning even when Hope wins — Hope is "hard mode" (GDD v0.9 preamble)
  and the sky is a grief (§2.3: per-tick decay toward 0 *is* Uhtcearu's grief).
  Exclamation marks are banned outright (deterministic check F4).
- **T2 · Consequence over spectacle.** A line must land on what changed for
  people or land, not on how impressive the player is. Register A version:
  "states its consequence" (§2.5). Register B version: era flavor describes
  what the people built or lost, never congratulates.
- **T3 · Register discipline.** Register A: second person, declarative, no
  mythology. Register B: mythic allowed, but restrained — the comps are
  *Journey*/*Gris* (§1 Document intent), not epic fantasy. A Register B line
  that reads like a quest log or an achievement toast fails.
- **T4 · The color must matter.** A line about a run outcome or a verb must not
  read identically in a Hope run and a Fear run when canon says the outcomes
  differ (§4.5 worked example: the roar candidate failed partly because "it
  would read identically in a Hope run"). Era flavor for a Fear region names
  the sharp/industrial turn; for Hope, the green and growing one (§2.5:
  "green and growing where hope took root, sharp and industrial where fear
  did, ash where nothing you did outlived you").

### Constraint type 2 — VOCABULARY & LORE (rules V1–V4)

- **V1 · Canonical proper nouns only.** The god is **Uhtcearu** — never "the
  old gods," "the gods," or an invented pantheon (the A6 mock's canned
  EXCEEDS-SCOPE catch was exactly "the old gods"). The player-being is unnamed
  (§1: "an unnamed kaiju-scale being"); do not name it. The flame is **the
  white flame** before alignment tints it.
- **V2 · The emotion vocabulary is closed.** Poles are **Hope** and **Fear**,
  capitalized when meaning the poles; grey zero is **Apathy**; the frozen are
  **the burned** (§2.3 burnout); founders are **zealots**. Forbidden: mana,
  XP, karma, alignment points, morale, sanity — any imported game-economy
  noun. Stamina exists (§2.2) but is HUD-only vocabulary, banned from both
  registers (see V3).
- **V3 · No interface language.** No "press," "click," "key," "button,"
  "menu," "screen," "HUD," "WASD," or key names. This is the A6 Pre-Build
  Declaration's canonical failure ("press W A S D to move") and it applies
  to Register B with no exceptions.
- **V4 · Era nouns are fixed.** The three eras are **nomad camps → villages →
  Victorian towns**, with **clocktowers and smoking factories** as the named
  Victorian furniture; roads age **compacted earth → paver stone** (§2 visual-
  language canon, promoted v0.9.7). Era-invariant by ruling: zealots, loners,
  the burned, and the avatar — flavor text must not dress them in era clothes.

### Constraint type 3 — FORMAT & LENGTH (rules F1–F5, deterministic)

These are enforced in code (`style/checks.py`) before the LLM Evaluator runs;
any deterministic finding caps the score at 6/10 (policy, stated in §3).

- **F1 · Length.** Register A: ≤120 characters and ≤24 words (the A6 register
  gate's calibrated limits). Register B: ≤2 sentences and ≤160 characters —
  **a stated policy, not a GDD constant** (same honesty class as A6's limits).
- **F2 · No numerals.** Digits are banned in game text (GDD §2.3 no-numbers
  discipline; the game "communicates all of its state without a line of
  text," §2.5). "Fourteen sleeps" is as banned as "14" — spelled-out
  quantities of sim values are numbers wearing a coat.
- **F3 · No exclamation marks.** (Deterministic face of T1.)
- **F4 · No second person in Register B era flavor.** Era lines are about the
  world, not the player; the teacher's "you" died with the first dawn (§1
  Tone). The endscreen epilogue candidate is the one sanctioned exception
  (§6: "the teacher's voice returning once, at the very end") and is tagged
  `register: B-epilogue` to exempt it.
- **F5 · Output shape.** One line per candidate, plain prose, no markdown,
  no quotation marks around the line itself, no trailing ellipsis padding.

## 3. Scoring policy (read by the Evaluator)

Score is **1–10, never pass/fail**. Anchors: **10** = every rule honored and
no craft reservation — the Evaluator has nothing to say. **9** = every rule
honored; the only note is a craft preference (a metaphor slightly stacked, a
line that would be stronger with a sharper image) — still ship-ready for the
Director's bench, who owns craft calls. **8** = a rule is *strained* but not
broken (T4 color only implied, a V4 noun edging toward a neighbouring era).
**7 and below** = a named rule is violated. Deductions are argued in the
REASON by quoting the rule ID and the offending words. Any deterministic
F-finding caps the score at 6. **9 or 10 is accepted; a score below 9 routes
to the Refiner** with the REASON verbatim. Craft notes are never grounds to
withhold a 9: a line with no violated or strained rule must score 9 or 10. The
Evaluator **cannot repair** — a proposed rewrite in an Evaluator reply is a
contract violation and halts the run (A6 rule, kept).

## 4. Provenance

| Rule block | Source |
|---|---|
| Registers, T1–T3 | GDD §1 Tone, §2.5 experience canon, v0.9.2 ruling (wordless-after-first-dawn) |
| T4 | GDD §4.5 worked example (roar candidate FAIL), §2.5 landscape outcomes |
| V1–V2 | GDD §1 Summary, §2.3 systems (burnout, zealots), A6 mock catch |
| V3 | A6 Pre-Build Declaration failure class |
| V4 | GDD §2 visual-language canon (v0.9.7 promotion), v0.9.4 era ruling |
| F1 | A6 register gate (calibrated limits) + stated Register B policy |
| F2 | GDD §2.3 no-numbers discipline, §2.5 wordless-state pillar |
| F4 | GDD §1 Tone (one voice, spent), §6 Narrative F5 (epilogue exception) |
