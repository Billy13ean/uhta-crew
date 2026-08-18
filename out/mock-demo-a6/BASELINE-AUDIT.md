# BASELINE AUDIT — the Evaluator vs the shipped build — mock-demo-a6

> Pipeline `ger` (Assignment 6) · backend `mock` · model `mock-llm (tests/fixtures/ger)` · generated 2026-08-18 00:25:34

> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Generator, Evaluator and Refiner responses in this run were canned fixtures from `tests/fixtures/ger/`, replayed to prove the orchestration — including the deterministic register gate, the refinement loop and the circuit breaker — executes end to end without an API key. The register-gate findings ARE real (the gate is code, not a model); the prose verdicts are fixtures.


The rule under enforcement (GDD §2.5): *"Short, declarative, second person. Names the verb and states its consequence. Instrumentation, not lore — GDD §2.5: 'short declarative lines, no mythology'. No interface language: this is a wordless game's one narrated cycle, not a tutorial overlay — the narrator names what the being DOES, never which key the player presses. No numbers (§2.3, banded display)."*

Before generating anything, the Evaluator was pointed at the text already in `blackboard/build/uhta-slice.html`: the seven stub `TEACHING_TEXT` lines A5's Programmer wrote as placeholders, and the `guide()` tutorial strings the A5 repo findings measured against the GDD. A pipeline that only ever judges its own output has never been tested against a real failure.


## guide() tutorial strings vs the register gate

| # | string (truncated) | findings |
|---|---|---|
| 1 | `The world wakes as grey wanderers. Your <b>${p}</b> zealot gathers the first of …` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 124 chars / 26 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 2 | `<b>Left-click</b> to wash a wave of your color over the wanderers and deepen you…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'Left-click' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 167 chars / 32 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 3 | `Your flame dims (the shrinking ring). Press <b>space</b> to <b>sleep</b> — a gen…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'Press' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 130 chars / 21 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 4 | `Your <b>WASD</b> trail becomes a road stamped your color — it erodes enemies who…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'WASD' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 172 chars / 31 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 5 | `a ruined basin waits — stand beside it and press <b>E</b> to light it in your co…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed |
| 6 | `Flame nearly spent — press <b>space</b> to rest; the world lives a generation on…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed |
| 7 | `The land turns <b>${p}</b>'s color — hold it.${oppZealot?` | [deterministic] R4 DECLARATIVE: contains ? — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims |

**7 of 7** shipped tutorial strings fail the register gate — `press`, `W A S D`, click vocabulary. This is the exact failure class the Pre-Build Declaration named, found in text that is in the game today.


## The build's current TEACHING_TEXT stubs, judged

### `walk`

> You walk. The grey wanderers see your trail and follow roads.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

### `flame`

> You kindle a flame. Nearby people feel its warmth and adopt your conviction.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

### `roar`

> You roar. The sound carves a road through the land.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line names only the road and omits Roar's load-bearing consequence — every witness is frightened whatever the flame's color. A Hope player reading this stub learns nothing about the cost. [MOCK FIXTURE]
  - chunk cited: "NPCs within witness radius take an unconditional Fear push regardless of flame color"

### `wait`

> You wait and witness. Apathy grows where you stand idle.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

### `beacon`

> You light a beacon. It calls the devoted even while you sleep.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

### `raze`

> You raze a structure. Its people scatter back to wandering.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

### `sleep`

> You sleep. The world moves without you; your people spread your belief.

- layer 2: PASS — Names the verb, states its consequence from the retrieved chunk, and holds the register. [MOCK FIXTURE — canned verdict, no model judged this line]
  - chunk cited: "a narrator names each verb the first time you use it"

**1 of 7** stub lines flagged. Each flagged stub is a line currently shipping in the build that the loop replaces (or escalates) below.

