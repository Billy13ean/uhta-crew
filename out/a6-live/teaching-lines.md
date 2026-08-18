# teaching-lines — first-use verb narration — a6-live

> Pipeline `ger` (Assignment 6) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 00:38:20


One rule-passing line per verb for the build's `TEACHING_TEXT` const (the mechanism A5 built; GDD §2.5 — 'a narrator names each verb the first time you use it', and the words end permanently at the first Sleep). ESCALATED verbs keep the build's current stub, marked.

| verb | status | line |
|---|---|---|
| `walk` | ACCEPTED (r0) | Walk — the ground remembers you, and becomes a road that carries your color. |
| `flame` | **ESCALATED** — stub retained | You kindle a flame. Nearby people feel its warmth and adopt your conviction. |
| `roar` | ACCEPTED (r0) | You roar, and everyone who witnesses it is frightened — whatever you intend. |
| `wait` | ACCEPTED (r0) | Wait — and those who watch you learn that you do not matter. |
| `beacon` | ACCEPTED (r0) | You light a beacon, and it radiates what you feel every generation, even while you sleep. |
| `raze` | ACCEPTED (r2) | You raze the settlement. The tribe scatters. Witnesses break. |
| `sleep` | ACCEPTED (r0) | You sleep, and where you lie, your light radiates through every moment until you wake. |

## Applying it

Two equivalent routes, both Director-applied — the pipeline modifies nothing in place:

1. **The snippet** — `teaching-text.snippet.js` in this directory is a drop-in replacement for the single `const TEACHING_TEXT={...};` line in `blackboard/build/uhta-slice.html`.
2. **The pre-patched build** — `uhta-slice.patched.html` in this directory is the build with that one line already replaced, verified (see manifest `patch`): the const still parses, all pre-existing self-test assertions survive verbatim, and re-extracting the const returns exactly the accepted lines. Open it and check the self-test panel: G12 (once per verb, sleep 0 only) and G13 (all 7 verbs covered) gate this exact mechanism.


---

## Director selection

*Left unfilled by the pipeline. The loop guarantees every line above passes the GDD §2.5 register rule; which words enter a wordless game is still a Director ruling (GDD §4.5, 'human as curator').*

**Apply as-is / edit / reject (per verb):** ____________________

**Signed (Director):** _______________  **Date:** ____________

