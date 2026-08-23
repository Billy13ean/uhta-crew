# uhta — "revisit later" backlog

Ideas captured in class or in passing that are NOT scoped into the current slice. Pull from here when there's room.

---

## 1. Title screen upgrade — hi-def pixel art + "rise and blur" transition
*Captured 2026-08-21 (note from class).*

**Want:**
- A title screen with **higher-definition pixel art** than the current 340×340 cave painting (`art/make_title_scene.py`, displayed at 2× nearest → 680×680).
- On **Start**, the title screen **rises upward and blurs out**, revealing the first section of the game underneath.

**Notes for when this is picked up:**
- The current title painting is the Plato's-cave opening (two tunnel mouths, red/green, avatar with white flame). The `opening` mode is byte-identical to the shipped title and the same painter also renders the cave *revisit* variants (`fear` / `hope` / `grey`) — any resolution bump should keep those in sync, or the landmark revisit will look lower-res than the title.
- "Higher def" options: (a) re-render the painter at 680×680 or 1020×1020 native instead of 2× upscaling; (b) keep the palette/dither rules (~38-colour uhta family, Bayer 8×8) so it still reads as the same world.
- Transition is cheap in the HTML build: title layer `transform: translateY(-100%)` + `filter: blur(Npx)` + opacity fade over ~600–900ms with an ease-in, game canvas already rendered beneath. Respect `prefers-reduced-motion` (cut straight to the game).
- Canon check: the cave is a *place*, not a menu — the wordmark is gated to the opening only. The transition should feel like leaving the cave, not dismissing a UI panel.

**Status:** idea only, not built.

---

## 2. Ambient contagion is wall-clock, and it can deny the idle player an ending
*Captured 2026-08-23 (A9 chaos agent, finding F02 — the live headed run).*

**Observed:** headless/fast, an idle run reaches the apathy loss (harness baseline: sleep 24). Headed at human pacing (`--slow 120`), the same seed idles 40 generations with **no terminal** (`out/a9-chaos/live-run.json`). Cause: `ambientStep()` fires every 1.05 s of wall-clock, decoupled from sim ticks, and mutates NPC belief — more beats per generation for a slow player, so the world stays aligned and grey never claims 0.8.

**Why it matters:** outcome depends on player pacing; Definition-of-Playable criterion 6 (the loss that teaches) may be unreachable for a browsing, human-paced player. And the beat crosses the "presentation only — Sim core untouched" boundary: it is a sim force the reference harness never models, so the parity claim has a hole the self-test cannot see (it compares fresh Worlds, not the live one).

**Options when picked up (a crew/canon question, not a quiet patch):**
- (a) tie the ambient beat to sim ticks instead of wall-clock (pacing-invariant, cheapest honest fix);
- (b) cap the beat's net effect per generation (keeps the visible life, bounds the force);
- (c) model the beat in the harness and re-tune the loss threshold with the crew (a ruleset generation + red-team round).

**Status:** open. Logged in `Rouke-uhta-A9-README.md` (F02); reproduce with `node tools/chaos_probe.js blackboard/build/uhta-slice.html --seed 7 --headed --slow 120`.
