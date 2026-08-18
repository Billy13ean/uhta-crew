# MINIGAME-CANDIDATES — encounter mini-games, awaiting a ruling — mock-demo-mg

> Pipeline `minigame` (Assignment 6 #2) · backend `mock` · model `mock-llm (tests/fixtures/minigame)` · generated 2026-08-18 01:19:28

> **MOCK-LLM FIXTURE RUN — NOT REAL DESIGN WORK.** Designer, Judge, Refiner and Programmer responses were canned fixtures from `tests/fixtures/minigame/`, replayed to prove the orchestration — the design gate, the loop, the breaker, the human gate and the patch contract — executes end to end. The design-gate findings and patch post-checks ARE real (they are code); the designs and verdicts are fixtures.


One design per encounter slot survived the GER loop (Generator -> two-layer Evaluator -> Refiner, circuit breaker on the residue). **Nothing has been built.** GDD §3's stop rule gates encounter BUILDS on the stranger test; this run spent tokens on design, and the build stage below cannot run without your typed selection — the gate is structural.


## `first-contact-hope` — ACCEPTED
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
- **Judge:** PASS — Wordless, diegetic, pole-honest, and every stake pays in the sim's own currencies. [MOCK FIXTURE — canned verdict, no model judged this design]
  - chunk honored: "a short, wordless, diegetic exchange — no interface, no text, only your body and theirs"

## `first-contact-fear` — ACCEPTED
**The Scatter** — `first-contact-fear` (first-contact/fear)

- **Premise:** The band breaks at your roar and runners peel off along every open line.
- **Loop:** For a few strides you are faster than they are. Each runner flees along a visible line toward the dark; you cut lines by moving through them. You cannot reach every line — every step toward one runner opens another's escape.
- **Diegetic signals:** Escape routes read as the runners' own paths and the gaps between rocks; a runner you head off stops dead and cowers; an escaped runner shrinks into the dark still carrying the story.
- **On success:** Everyone you head off turns shallowly to your color, trembling.
- **On failure:** The ones who escape spread the tale of you outward to camps you have never seen.
- **Why fun:** Chase geometry as instant triage — commitment costs are visible the moment you move, and you cannot catch everyone by design.
- **Pattern:** Interception — the cutoff
- **GDD grounding:** you have a handful of strides to cut off the runners
- **Controls:** wasd-move
- **Effects:** convert_shallow, story_spreads
- **Judge:** PASS — Wordless, diegetic, pole-honest, and every stake pays in the sim's own currencies. [MOCK FIXTURE — canned verdict, no model judged this design]
  - chunk honored: "a short, wordless, diegetic exchange — no interface, no text, only your body and theirs"

## `vigil-hope` — ACCEPTED
**The Weaving** — `vigil-hope` (vigil/hope)

- **Premise:** Sleep takes you; your believers hang in the dark as points of your color.
- **Loop:** With your last stamina you draw a thread from believer to believer with slow movements. The thread holds only while your pace stays gentle and your turns stay wide; a rushed segment frays and snaps. Longer chains reach further and are harder to hold.
- **Diegetic signals:** The thread is drawn light between bodies; fraying shows as the thread thinning and trembling; a completed chain settles into a steady channel glow.
- **On success:** Completed chains carry belief between the sleepers all generation.
- **On failure:** A snapped thread leaves its two ends dark; unchained believers stand alone against the grey.
- **Why fun:** The ambition tradeoff — every extra link is reach you want and risk you must hold with smoother hands.
- **Pattern:** Path tracing — the drawn line
- **GDD grounding:** Completed chains become channels belief travels while you are gone
- **Controls:** mouse-move, left-click
- **Effects:** convert_devout, stamina_loss
- **Judge:** PASS — Wordless, diegetic, pole-honest, and every stake pays in the sim's own currencies. [MOCK FIXTURE — canned verdict, no model judged this design]
  - chunk honored: "a short, wordless, diegetic exchange — no interface, no text, only your body and theirs"

## `vigil-fear` — ACCEPTED
**The Watch** — `vigil-fear` (vigil/fear)

- **Premise:** Your believers are points of light and the dark presses in from every side.
- **Loop:** You hold a shadow-shield over one cluster at a time while the dark gnaws at every unshielded light. Coverage is the shield's own shadow; the pressure visibly shifts, and you drag your protection between clusters knowing the rest are burning down.
- **Diegetic signals:** A shielded cluster sits in your cast shadow and burns steady; an unshielded cluster gutters, dims, and greys — the flame height itself is the state.
- **On success:** Dawn arrives with the clusters you chose still burning.
- **On failure:** The lights you abandoned are grey by morning, standing exactly where you left them.
- **Why fun:** Triage under guaranteed loss — the skill is deciding what to lose, and living with it.
- **Pattern:** Triage — protect what you can; Diegetic state display
- **GDD grounding:** You shield what you can and you cannot shield everything
- **Controls:** mouse-move, left-click
- **Effects:** drift_apathy, convert_shallow
- **Judge:** PASS — Wordless, diegetic, pole-honest, and every stake pays in the sim's own currencies. [MOCK FIXTURE — canned verdict, no model judged this design]
  - chunk honored: "a short, wordless, diegetic exchange — no interface, no text, only your body and theirs"

## `holding-hope` — ACCEPTED
**The Procession** — `holding-hope` (holding/hope)

- **Premise:** A rooted settlement resists you everywhere but along your own roads.
- **Loop:** You walk your road toward the heart and converts fall in behind you, one by one. The line holds only while your pace stays slow and your turns stay wide; move too fast or cut too sharply and the tail detaches where you rushed. Whoever is still with you at the heart converts a resident.
- **Diegetic signals:** The line of followers IS the state — its length, its gaps, and the stragglers left standing where the line broke.
- **On success:** The unbroken line reaches the heart; residents step out and kneel.
- **On failure:** The line breaks; whoever you dropped stands where you lost them, and the settlement's doors close.
- **Why fun:** The leader's restraint is the skill — the whole tension is between the pace you want and the pace the line can hold.
- **Pattern:** Procession — follow-the-leader escort
- **GDD grounding:** the line breaks if you move too fast or turn too sharply
- **Controls:** wasd-move
- **Effects:** convert_devout, resistance_drop
- **Judge:** PASS — Wordless, diegetic, pole-honest, and every stake pays in the sim's own currencies. [MOCK FIXTURE — canned verdict, no model judged this design]
  - chunk honored: "a short, wordless, diegetic exchange — no interface, no text, only your body and theirs"

## `holding-fear` — **ESCALATED** (see MG-ESCALATED.md; cannot be selected)

---

## Director selection — the human gate

*The pipeline stops here by construction. To build ONE selected design (a minimal playable slice under the A5 patch contract):*

```
python3 run_minigame.py --build --select <id> --from-run mock-demo-mg
```

Selectable ids: first-contact-fear, first-contact-hope, holding-hope, vigil-fear, vigil-hope

**Selected:** ____________  **Rejected because:** ____________

**Signed (Director):** _______________  **Date:** ____________

