# DIRECTOR'S REPAIR — Steady the Flame, playable

> 2026-08-18. Base: `out/_superseded/mg-live-build-v4/patch-attempt-2.json`
> (the strongest Programmer attempt — statically green, crash-free, best
> structure). The GER loop's Programmer did not converge on full behavioral
> correctness inside its two-attempt budget across three live runs; per the
> crew's own contract ("the Director applies it — it ends at a human"),
> the Director's hands made six recorded fixes, each traced to a play-probe
> or playtest finding. Nothing here is invented: every fix answers a named
> defect with evidence.

## The six fixes

| # | defect (how it was found) | fix |
|---|---|---|
| 1 | ARM-THEN-INIT: the `#mg` wrap and the natural trigger both did `MG.active=true; mgInit(MG)` — and `mgInit` resets `active=false`, so the encounter disarmed the instant it armed (probe P2b, added after this was found) | arm AFTER init, both paths |
| 2 | Inhuman tuning: flame decay 0.006/frame ≈ idle death in ~1s (probe P6) | decay → 0.0005; commit decay softened (0.01→0.001 dim, 0.015→0.004 bright) |
| 3 | The dim rect was drawn into `this.world` — which the tile pass paints OVER, so the "world dims" entry never showed (screenshot evidence) | drawn into `this.overlay`, above the world |
| 4 | `guide()` calls `setTip()` at the END of every drawWorld, overwriting the Instructor's line the same frame (probe P4; the tip showed verb-narration instead) | hold the tip with the build's own `_ap5Hold` mechanism while the encounter is active |
| 5 | Win effects read `SIM.tribes[].pole` (unverified field) and minted `v=+8` regardless of pole — a Fear player would create Hope believers | `v = 8 * SIM.player_pole`; unverified lookup dropped |
| 6 | A held pointer fed the flame EVERY frame (+0.18 × ~6 frames per 50ms click) — one press rocketed 0.45→0.98 and bright-killed the run (probe P5/P6 interplay) | edge-triggered taps: one press, one breath |

## Evidence

- `play-probe.json` — **all 9 probe checks green**: no page errors, not
  pre-armed, activates under `#mg`, WASD moves during play, the line shows
  and holds, one tap feeds the flame, survives 8s+ idle, resolves, control
  returns after resolution.
- A steady-play bot **WON in ~13s** of in-band play, zero page errors,
  devout converts minted in the player's pole.
- `mg-1-encounter-start.png` — the entry: dimmed world, gold flame, grey
  ring, the narrator's line. `mg-3-end.png` — the win: the closed ring,
  saturated gold.

## Play it

```
start "" "file:///C:/dev/uhta-crew/out/mg-directors-cut/uhta-slice.minigame.patched.html#mg"
```

Click a path on the title. Tap left-click to feed the flame; gold is
steady, white is too bright, ember-red is fading. The correct move is
usually to do less.

## What this means for the pipeline

The play-probe (tools/mg_probe.js) is now a gating post-check in the build
phase, and every defect above became a named rule in the Programmer's
prompt (P-ARM-LAST, P-HUMAN-TUNING, P-NPC-WHITELIST, P-SELFTEST-PURE, the
transitioning-write ban). The honest ledger: the GER loop caught its
failures loudly at every step, and the residue — six small fixes — reached the
human with evidence attached, which is the assignment's thesis.

## Legibility pass (after the fourth Director playtest)

Finding: *"it triggers and works, but it's hard to understand what to do,
and I can't see the effect."* Both are Presenter-layer defects — the target
band existed only in math, and a tap's response was a few pixels. Fixes,
all render-layer, no game-logic change:

1. **The flame is now a POOL OF LIGHT** (radius = brightness) — a tap
   visibly swells it, decay visibly shrinks it, with a white pulse ring on
   every tap.
2. **The drifting target is VISIBLE as a thin ember ring** — the goal reads
   instantly and wordlessly: keep your light's edge on the ring.
3. **In-band feedback on the people:** each nomad shows a warm ember glint
   while your flame sits in their comfort.
4. **The effect survives the encounter:** converted wanderers carry a
   golden afterglow for ~4 seconds after the world returns, so you can see
   exactly who you changed.
5. **A more teaching line** (register-gate CLEAN): "Feed your flame with a
   touch, and hold it gentle — too bright breaks them, too dim loses them."

Re-validated: play-probe **9/9 green**, steady-play bot **WON in ~18s**,
zero page errors. `mg-2-midplay.png` shows the new read.

## Discovery pass (after the fifth Director playtest)

Finding: *"no introduction with the discoverable event — no wake when you
leave the cave, and only a FEW nomads."* The encounter teleported into
existence, unrelated to the world's actual people. Fixes:

1. **The band is REAL.** The encounter binds to the actual grey nomads
   within 9 tiles (3–8 of them) — the ring size is however many are truly
   there, and every outcome lands on those same people: win converts from
   the band, a flare burns band members, the afterglow sits at their true
   positions.
2. **The discoverable event.** Before anything takes over, warm glints
   kindle over the band for ~0.75s — the attention cue from the
   Presenter's spec, finally implemented. Then the world dims and the
   encounter begins.
3. **`#mg` no longer skips the intro.** The test hook now teleports a
   six-nomad band near the cave instead of force-arming — so the wake
   message, the walk out, and the discovery all play, every run,
   deterministically.
4. **Frame-rate independent pacing** — mgStep scales by the real frame
   delta (found when the probe's slower renderer stretched every timer).

Re-validated: probe **9/9** (activation polling + longer resolution window
added to the probe), win-bot **WON in ~15s**, zero errors.
`mg-0-cue.png` shows the intro: the woken world, the zealot, the band, the
glints. Known canon note: only the Hope first-contact game is built, so a
Fear run currently meets the Hope encounter — the Fear variant (The
Scatter) is an accepted candidate in `out/mg-live/` awaiting its own build.

## The cave (after the sixth Director playtest)

Finding: *"there should be a whole different section prior to the main
game."* Correct — and it is the GDD's own top queue item: §3 NICE #1, the
narrated opening's first moment (A4 beat n1: "the cave — the undetermined
flame"). Built as a self-contained DOM-canvas section that touches no
Phaser internals:

- Clicking the title now enters **the cave**: darkness, a white flame that
  lights only the stone grain around the bearer, and two mouths — ember
  (Fear) to the left, green (Hope) to the right.
- **Your pole is chosen by which mouth you WALK out of** (WASD), replacing
  the abstract title-click choice with the GDD's diegetic one. A white
  fade carries you out — the emergence — and the wake plays as before.
- The narration is the A4 live run's n1 PASS candidate, register-gate
  CLEAN: "You carry a white flame that lights only the stone around you —
  it becomes whatever you do with it."
- Real-time dt scaling from the start (the lesson already learned twice).

The play-probe grew its tenth check (**P0**: the cave opens, and walking
out the Hope mouth reaches phase 'play'). Re-validated: **probe 10/10
green**, win-bot completed the FULL arc — cave → emergence → wake →
discovery cue → encounter → **WON** — with zero page errors.
`cave-opening.png` shows the first moment.

## Anchor + transition pass (seventh playtest)

Finding: *"the circle moves around; it's too abrupt."* Fixes: the encounter
is now **anchored to the tile where it began** — everything draws at the
anchor and the avatar is held there while it is active (the probe's P3 was
inverted to assert exactly this); the entry dim eased over ~1.5s; the dark
**lifts gradually** through the exit instead of cutting; the cave's white
emergence lengthened; and the wake now **fades in through a dissolving
veil**. Probe **10/10 green**, win-bot full-arc victory, zero errors.
