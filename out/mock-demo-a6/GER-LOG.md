# GER-LOG — every round of the loop — mock-demo-a6

> Pipeline `ger` (Assignment 6) · backend `mock` · model `mock-llm (tests/fixtures/ger)` · generated 2026-08-18 00:25:34

> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Generator, Evaluator and Refiner responses in this run were canned fixtures from `tests/fixtures/ger/`, replayed to prove the orchestration — including the deterministic register gate, the refinement loop and the circuit breaker — executes end to end without an API key. The register-gate findings ARE real (the gate is code, not a model); the prose verdicts are fixtures.


Per verb: the Generator's draft, every Evaluator verdict (layer 1 deterministic gate, then the layer 2 judge), every Refiner repair, and where the loop stopped. `round 0` is the draft; refinement rounds are capped at 2 per verb by the circuit breaker.


## `walk` — **ACCEPTED** (0 refinement(s))

**Generator draft:**

> You walk, and the ground remembers — every tile you cross becomes a road that carries your color.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


## `flame` — **ACCEPTED** (1 refinement(s))

**Generator draft:**

> The old gods kindled this flame in the first dark; raise it and their covenant spreads your feeling.

- FAIL — [llm] EXCEEDS-SCOPE: 'The old gods' and 'their covenant' are invented cosmology no retrieved chunk supports — mythology where the register demands instrumentation. [MOCK FIXTURE] — chunk: "short declarative lines, no mythology"

**Refiner round 1:**

> You raise the flame, and those near it take on whatever you feel right now.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


## `roar` — **ACCEPTED** (1 refinement(s))

**Generator draft:**

> Press R to roar — everyone nearby is frightened, whatever you intend.

- FAIL — [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'Press' — the register is the narrator naming what the being does, not which key is pressed

**Refiner round 1:**

> You roar. Everyone who witnesses it is pushed toward fear, whatever color you carry.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


## `wait` — **ACCEPTED** (0 refinement(s))

**Generator draft:**

> You wait. Those who watch you drift toward apathy — witnessed inaction is still an act.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


## `beacon` — **ACCEPTED** (0 refinement(s))

**Generator draft:**

> You light a beacon. It radiates your color every generation, even while you are gone.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


## `raze` — **ESCALATED** → see ESCALATED.md (2 refinement(s))

**Generator draft:**

> You raze the settlement — and who could stand unafraid before that?

- FAIL — [deterministic] R4 DECLARATIVE: contains ? — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims

**Refiner round 1:**

> You raze the settlement! Its people scatter, and fear takes every witness.

- FAIL — [deterministic] R4 DECLARATIVE: contains ! — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims

**Refiner round 2:**

> You raze the settlement and 5 tribes scatter in fear.

- FAIL — [deterministic] R5 NO-NUMBERS: contains a digit — §2.3 banded display: the player never sees a number; say 'everyone who hears you', not a radius


## `sleep` — **ACCEPTED** (0 refinement(s))

**Generator draft:**

> You sleep, and a generation passes. Where you lie down keeps radiating what you feel.

- PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk honored: "a narrator names each verb the first time you use it"


**Totals:** 7 verbs · 11 evaluated rounds · 5 FAIL verdicts, every one either repaired by the Refiner or escalated by the breaker — the pipeline has no third path.

