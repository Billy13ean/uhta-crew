# MG-ESCALATED — what the loop hands the Director — mock-demo-mg

> Pipeline `minigame` (Assignment 6 #2) · backend `mock` · model `mock-llm (tests/fixtures/minigame)` · generated 2026-08-18 01:19:28

> **MOCK-LLM FIXTURE RUN — NOT REAL DESIGN WORK.** Designer, Judge, Refiner and Programmer responses were canned fixtures from `tests/fixtures/minigame/`, replayed to prove the orchestration — the design gate, the loop, the breaker, the human gate and the patch contract — executes end to end. The design-gate findings and patch post-checks ARE real (they are code); the designs and verdicts are fixtures.


After 2 failed refinements a slot is escalated with its full history; 3 escalations trip the run.


## `holding-fear`

| round | design | findings |
|---|---|---|
| 0 | The Breaking (v1) | [deterministic] C3 BUILDABLE-INPUT: controls ['shift-key'] not in the slice's input vocabulary ['wasd-move', 'mouse-move', 'left-click', 'right-click', 'space', 'e-key'] — a design this build cannot receive input for cannot be built into it |
| 1 | The Breaking (v2) | [deterministic] C4 REAL-STAKES: effects ['gold_coins'] not in the sim's outcome vocabulary ['convert_devout', 'convert_shallow', 'burnout', 'drift_apathy', 'stamina_gain', 'stamina_loss', 'resistance_drop', 'story_spreads', 'no_effect'] — stakes must pay in the main loop's real currencies |
| 2 | The Breaking (v3) | [deterministic] C3 BUILDABLE-INPUT: controls ['arrow-keys'] not in the slice's input vocabulary ['wasd-move', 'mouse-move', 'left-click', 'right-click', 'space', 'e-key'] — a design this build cannot receive input for cannot be built into it |

**Director options:** design `holding-fear` by hand; drop the slot; or adjust the spec and re-run `--slots holding-fear`.

