# ESCALATED — what the loop hands the Director — mock-demo-a6

> Pipeline `ger` (Assignment 6) · backend `mock` · model `mock-llm (tests/fixtures/ger)` · generated 2026-08-18 00:25:34

> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Generator, Evaluator and Refiner responses in this run were canned fixtures from `tests/fixtures/ger/`, replayed to prove the orchestration — including the deterministic register gate, the refinement loop and the circuit breaker — executes end to end without an API key. The register-gate findings ARE real (the gate is code, not a model); the prose verdicts are fixtures.


The circuit breaker stops spending on a verb after 2 failed refinements and hands it here WITH its evidence — the point of the loop is that a human reviews the residue, not every output. Global trip threshold: 3 escalations.


## `raze`

| round | line | findings |
|---|---|---|
| 0 | You raze the settlement — and who could stand unafraid before that? | [deterministic] R4 DECLARATIVE: contains ? — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims |
| 1 | You raze the settlement! Its people scatter, and fear takes every witness. | [deterministic] R4 DECLARATIVE: contains ! — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims |
| 2 | You raze the settlement and 5 tribes scatter in fear. | [deterministic] R5 NO-NUMBERS: contains a digit — §2.3 banded display: the player never sees a number; say 'everyone who hears you', not a radius |

**Director options:** write the `raze` line by hand; keep the build's current stub; or adjust the spec/prompt and re-run `--verbs raze`.

