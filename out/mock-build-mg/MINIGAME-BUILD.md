# MINIGAME-BUILD — the selected design, built — mock-build-mg

> Pipeline `minigame` (Assignment 6 #2) · backend `mock` · model `mock-llm (tests/fixtures/minigame)` · generated 2026-08-18 01:19:31

> **MOCK-LLM FIXTURE RUN — NOT REAL DESIGN WORK.** Designer, Judge, Refiner and Programmer responses were canned fixtures from `tests/fixtures/minigame/`, replayed to prove the orchestration — the design gate, the loop, the breaker, the human gate and the patch contract — executes end to end. The design-gate findings and patch post-checks ARE real (they are code); the designs and verdicts are fixtures.


## What was built

**Steady the Flame** — `first-contact-hope` (first-contact/hope)

- **Premise:** A grey band circles you at the edge of the firelight, wavering between approach and flight.
- **Loop:** Your flame breathes on its own; holding space feeds it, releasing lets it fade. Each nomad drifts inward only while the light sits inside their comfort — too bright and the nearest flinch back, too dim and the farthest turn away. The correct move is usually to do less.
- **Diegetic signals:** Brightness is the flame itself; each nomad's comfort shows in their posture — leaning in, shielding their eyes, or turning; commitment shows as kneeling.
- **On success:** Those who reach you kneel and take your color deeply; the fire settles.
- **On failure:** A flare or a fade; the flinchers freeze grey, ringed in your color, and the rest scatter.
- **Why fun:** Restraint under temptation — the urge to feed the flame is the trap, and the skill is modulation, not action.
- **Pattern:** Threshold fight — the steady hold
- **GDD grounding:** commit only if the flame is steady when they arrive
- **Controls:** space
- **Effects:** convert_devout, burnout

## The patch

| | |
|---|---|
| selected | `first-contact-hope` |
| from_run | `mock-demo-mg` |
| checks | `{'parse:logic_block': True, 'parse:selftest_block': True, 'parse:hook_line': True, 'all_preexisting_assertions_survive': True, 'adds_at_least_one_M_assertion': True, 'grew': True, 'whole_file_brace_balance': True}` |
| repair_rounds | `0` |
| node_available | `True` |

### Inserted at three anchors

1. **logic** (after the pure-resolver region): 5 lines
2. **self-test** (inside the on-load self-test): 2 lines — the new M-assertions gate the pure logic
3. **hook** (after the verb dispatch): 1 line(s)


**Programmer notes:** MOCK FIXTURE PATCH — not a designed mini-game. It exercises the full A5-style contract against the real slice: three anchored inserts, two new M-assertions on pure logic, every G-assertion surviving, node parse checks. The live Programmer's payload replaces this with the Director-selected design's playable overlay.


## Applying it (Director)

```
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\mock-build-mg\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open the build: the self-test panel must show every G-assertion AND the new M-assertion(s) green. Then play to the encounter and judge the thing no container can: whether it feels like the GDD's sentence. **GDD §3's stop rule still applies to committing this to the canonical slice** — building it was gated on your selection; shipping it is gated on the stranger test, and that ruling is yours.

## Director verification

- [ ] panel all green, including M-assertions
- [ ] the encounter triggers where the design says
- [ ] wordless in play — no text appeared
- [ ] the two poles would not play the same game

