# MINIGAME-BUILD — the selected design, built — mg-live-build-v3

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 02:05:12


## What was built

**Steady the Flame** — `first-contact-hope` (first-contact/hope)

- **Premise:** A ring of grey nomads approach slowly from all sides, wavering between curiosity and fear. The flame above you flickers with each input—your task is to hold it steady as they close the distance.
- **Loop:** The flame brightness responds to left-click (brightens) and naturally decays toward dim. The nomads approach in a slow, uneven ring, pausing when the flame wavers outside a narrow 'steady' band. Hold the flame in the correct range—visible but not blazing—by tapping left-click sparingly to counteract decay. Over-click and the flame flares too bright, cracking the air with light; the nomads recoil and some break away. Under-maintain and it dims toward grey; wavering nomads drift back into the fog. The steady band itself drifts slightly, demanding constant reading rather than a fixed rhythm.
- **Diegetic signals:** Flame brightness is the flame itself, glowing above your body—gold-white core when steady, searing white when too bright, ember-dim when failing. Nomad commitment shows in their posture: upright and steady when the flame is right, leaning back and hesitating when it flares, turning away and fading when it dims. Distance closes visibly—they walk toward you, and their ring tightens as the encounter progresses. No meters, no UI—only the flame's glow and their bodies.
- **On success:** The ring closes completely. The nomads kneel in unison, their grey forms saturating to warm gold as they convert. Few in number, but their posture is deep—heads bowed, fully committed.
- **On failure:** The flame either shatters in a white flash (too bright) or gutters to ash (too dim). Nomads scatter or fade back into the fog. The encounter ends with no conversions, or worse—some grey out entirely, ringed in the faint gold they almost carried.
- **Why fun:** Tests restraint and reading a drifting target—the skill is knowing when to act and when to let the flame settle. The tension comes from fighting the instinct to over-correct; one extra click can undo the entire hold.
- **Pattern:** Threshold fight — the steady hold
- **GDD grounding:** They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less.
- **Controls:** left-click
- **Effects:** convert_devout, burnout, drift_apathy, no_effect

## The Instructor's line (Writer's seat, GDD §5)

> You tend the flame, and those who approach will stay only if it neither flares nor fades.

Displays once, when the encounter first begins on sleep 0 — inside the game's narrated window; register-gated by the same checks as the verb narration.


## The Presenter's spec (Aesthetic Director's seat)

- **attention_cue:** Grey nomads emerge from fog at world edge, moving inward in loose formation—not wandering, but approaching with intent. Their bodies lean forward slightly, hesitant but drawn. A faint shimmer above the player's band begins: the flame's first flicker, barely visible, pulsing softly gold against grey.
- **entry_transition:** World pauses. All other bands freeze mid-step. The surrounding terrain desaturates to near-monochrome, fog thickens at edges. Camera tightens focus: the player's band centered, the approaching nomads now clearly visible in a wide ring. The flame above the player ignites fully—a small, wavering gold-white glow suspended at head-height. Silence: ambient sound mutes to a low hum. The ring of nomads resumes movement, slow and synchronized, while the rest of the world remains frozen.
- **exit_transition:** The flame extinguishes (win: fades gently to nothing; fail: already gone). Camera pulls back to normal view. The frozen world desaturates further for one beat, then color and motion flood back in a single wave—surrounding bands resume movement, terrain regains saturation, ambient sound returns. Converted nomads (if any) rise from kneeling and join the player's band, their gold forms now moving in sync. The fog recedes to normal density. Play resumes.
- **feedback_win:** The ring closes to arm's length. All nomads kneel in perfect unison—a single fluid motion, bodies folding downward, heads bowed low. As they kneel, their grey forms saturate to warm gold from the ground up, like liquid light filling vessels. The flame above the player flares once, bright and clean, then settles to a steady golden glow. The kneeling figures remain still, fully committed, gold against grey fog.
- **feedback_fail:** Flare path: The flame explodes to searing white, a sharp crack of light that bleaches the entire screen for one frame. Nomads recoil violently—arms raised, bodies stumbling backward, then scattering outward in all directions, silhouettes dissolving into fog. The flame shatters to sparks and vanishes. Dim path: The flame shrinks to a red ember, flickers twice, then collapses to ash—a small grey puff. Nomads turn away slowly, their forms fading to transparency, walking back into fog without urgency. Some linger as faint grey outlines ringed in the barest gold glow—almost converted, now lost.
- **visual_hierarchy:** The flame itself—gold-white core, hovering above the player's body, brightest element on screen, eye drawn immediately to its flicker and sway → The ring of nomads—grey silhouettes in a wide circle, bodies upright, moving inward with visible hesitation, their posture readable against the desaturated fog → The player's band—still, grounded, centered beneath the flame, anchor point for the entire composition
  - *flame_steady* → Gold-white core, stable glow, soft halo—light does not pulse or flicker wildly, burns with even warmth
  - *flame_too_bright* → Searing white, harsh rays extending outward, air around it distorts with heat shimmer, no gold remaining—pure blinding light
  - *flame_too_dim* → Ember-red core shrinking, gold fading to grey-orange, glow barely reaching beyond the flame itself, edges dissolving into fog
  - *nomad_committed* → Upright posture, bodies leaning slightly forward, steady forward movement, silhouettes sharp and saturated toward warm grey
  - *nomad_hesitant_flare* → Bodies lean back, shoulders raised, movement stutters to pause, some turn heads away, silhouettes recoil from light
  - *nomad_hesitant_dim* → Bodies turn slightly sideways, heads tilt uncertain, forward movement slows to drift, edges of silhouettes begin to fade into fog
  - *nomad_breaking_away* → Full turn, bodies walking outward, silhouettes losing saturation, fading rapidly into surrounding fog, distance increasing
  - *ring_closing* → Visible distance shrinking—nomads larger on screen, circle tightening, individual figures more distinct, their shadows reaching toward center

## Finding it in play

- **Director test hook:** open the build with `#mg` in the URL (e.g. `uhta-slice.html#mg`) — the encounter force-arms from the start of play, regardless of spawn luck.
- **Normal play:** the attention cue above, then the trigger condition in the design; the entry transition pauses the world.


## The patch

| | |
|---|---|
| selected | `first-contact-hope` |
| from_run | `mg-live` |
| checks | `{'parse:logic_block': True, 'parse:frame_line': True, 'parse:input_line': True, 'parse:selftest_block': True, 'all_preexisting_assertions_survive': True, 'adds_at_least_one_M_assertion': True, 'grew': True, 'whole_file_brace_balance': True, 'director_test_hook': True, 'first_use_line_present': True}` |
| repair_rounds | `0` |
| node_available | `True` |
| first_use_line | `You tend the flame, and those who approach will stay only if it neither flares nor fades.` |
| instructor_repairs | `0` |
| presenter_repairs | `0` |

### Inserted at the five anchors (contract v3)

1. **logic** (top level): 20 line(s)
2. **frame** (inside drawWorld — the per-frame seat where the encounter lives): 17 line(s)
3. **input** (onClick guard — the encounter owns the pointer): 2 line(s)
4. **self-test**: 9 line(s) — the M-assertions gate the pure logic
5. **hook** (verb-trigger arming assist, optional): (omitted)


**Programmer notes:** Triggers on sleep 0 when 8+ grey nomads are within 6 tiles of the player. The flame brightness (50 baseline) responds to left-click (+12) and decays (-0.35/frame). A drifting target band (50±8, sinusoidal) defines 'steady'. Nomads approach from a ring (distance 180->20) and commit (0.5->1.0) when the flame is steady; they recoil if too bright (>target+15) or fade if too dim (<target-15). Win: all nomads reach distance ≤22 after 180 frames. Fail: flame exceeds bright threshold (flare) or falls below dim threshold. Outcome applies via SIM.npcs mutation (convert 3 greys to devout / burn 1 / zero 2). The encounter owns the pointer while active; WASD still moves the avatar (design assumes stationary play). Verify: the flame's glow shifts white/gold/ember as you tap-hold the rhythm, nomads visibly tighten the ring when steady, scatter on flare, fade on dim.


## Applying it (Director)

```
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\mg-live-build-v3\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open the build: the self-test panel must show every G-assertion AND the new M-assertion(s) green. Then play to the encounter and judge the thing no container can: whether it feels like the GDD's sentence. **GDD §3's stop rule still applies to committing this to the canonical slice** — building it was gated on your selection; shipping it is gated on the stranger test, and that ruling is yours.

## Director verification

- [ ] panel all green, including M-assertions
- [ ] the encounter triggers where the design says
- [ ] wordless in play — no text appeared
- [ ] the two poles would not play the same game

