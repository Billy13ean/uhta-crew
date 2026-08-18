# teaching-lines — first-use verb narration — mock-demo-a6

> Pipeline `ger` (Assignment 6) · backend `mock` · model `mock-llm (tests/fixtures/ger)` · generated 2026-08-18 00:25:34

> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Generator, Evaluator and Refiner responses in this run were canned fixtures from `tests/fixtures/ger/`, replayed to prove the orchestration — including the deterministic register gate, the refinement loop and the circuit breaker — executes end to end without an API key. The register-gate findings ARE real (the gate is code, not a model); the prose verdicts are fixtures.


One rule-passing line per verb for the build's `TEACHING_TEXT` const (the mechanism A5 built; GDD §2.5 — 'a narrator names each verb the first time you use it', and the words end permanently at the first Sleep). ESCALATED verbs keep the build's current stub, marked.

| verb | status | line |
|---|---|---|
| `walk` | ACCEPTED (r0) | You walk, and the ground remembers — every tile you cross becomes a road that carries your color. |
| `flame` | ACCEPTED (r1) | You raise the flame, and those near it take on whatever you feel right now. |
| `roar` | ACCEPTED (r1) | You roar. Everyone who witnesses it is pushed toward fear, whatever color you carry. |
| `wait` | ACCEPTED (r0) | You wait. Those who watch you drift toward apathy — witnessed inaction is still an act. |
| `beacon` | ACCEPTED (r0) | You light a beacon. It radiates your color every generation, even while you are gone. |
| `raze` | **ESCALATED** — stub retained | You raze a structure. Its people scatter back to wandering. |
| `sleep` | ACCEPTED (r0) | You sleep, and a generation passes. Where you lie down keeps radiating what you feel. |

## Applying it

Two equivalent routes, both Director-applied — the pipeline modifies nothing in place:

1. **The snippet** — `teaching-text.snippet.js` in this directory is a drop-in replacement for the single `const TEACHING_TEXT={...};` line in `blackboard/build/uhta-slice.html`.
2. **The pre-patched build** — `uhta-slice.patched.html` in this directory is the build with that one line already replaced, verified (see manifest `patch`): the const still parses, all pre-existing self-test assertions survive verbatim, and re-extracting the const returns exactly the accepted lines. Open it and check the self-test panel: G12 (once per verb, sleep 0 only) and G13 (all 7 verbs covered) gate this exact mechanism.


---

## Director selection

*Left unfilled by the pipeline. The loop guarantees every line above passes the GDD §2.5 register rule; which words enter a wordless game is still a Director ruling (GDD §4.5, 'human as curator').*

**Apply as-is / edit / reject (per verb):** ____________________

**Signed (Director):** _______________  **Date:** ____________

