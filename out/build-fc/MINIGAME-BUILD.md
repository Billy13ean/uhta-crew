# MINIGAME-BUILD — the selected design, built — build-fc

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 23:30:38


## What was built

**Steady the Flame** — `first-contact-hope` (first-contact/hope)

- **Premise:** A ring of grey nomads approaches slowly from all sides, wavering as they walk. They will only commit if your flame burns steady—not too bright, not too dim—when the first of them arrives at arm's reach.
- **Loop:** You hold space to raise the flame, release to let it dim. The flame pulses with a natural rhythm—it wants to flare when held, fade when released. The nomads approach in an uneven ring, each at their own pace, hesitating when the flame surges too bright, drifting sideways when it dims too low. You must read their distance and modulate pressure: short taps to keep the glow inside the narrow band they will accept, doing less as they draw near. One overcorrection—a flare that makes them flinch or a fade that breaks their focus—and that nomad turns away. The encounter ends when the first nomad reaches you or when all have drifted out of range.
- **Diegetic signals:** Flame brightness is the size and intensity of the light-corona around your body. Nomad commitment shows in posture: they lean forward when the flame is steady, recoil and raise a hand to shield their eyes when it flares, turn their heads and slow when it dims. Distance is literal: you see how many steps each nomad has left. The acceptable band is never shown numerically—you learn it by watching them hesitate at the edges.
- **On success:** The first nomad to reach you kneels, and the flame settles into their chest. One to three others who were still approaching when contact happened also kneel in sequence. Each converts deep—already devout.
- **On failure:** All nomads have turned away or stopped outside reach, standing with shoulders turned, gazes elsewhere. They walk back into the grey. No conversion.
- **Why fun:** The skill is fine motor restraint and rhythm-reading against a drifting target. The tension comes from knowing that doing more usually feels safer, but here the correct move is to do less—to trust the hold rather than chase it.
- **Pattern:** Threshold fight — the steady hold
- **GDD grounding:** They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less.
- **Controls:** space
- **Effects:** convert_devout, no_effect

## The Instructor's line (Writer's seat, GDD §5)

> You hold the flame steady, and those who approach without flinching will kneel.

Displays once, when the encounter first begins on sleep 0 — inside the game's narrated window; register-gated by the same checks as the verb narration.


## The Presenter's spec (Aesthetic Director's seat)

- **attention_cue:** Grey figures emerge from the fog at the world's edge, moving in a slow converging pattern—not toward any destination, but toward *you*. Their gait is unsteady, wavering side-to-side. As they cross into medium distance, they begin to synchronize: all heads turn to face your position, bodies still drifting but gazes locked.
- **entry_transition:** The world PAUSES. All other band members freeze mid-stride. The camera tightens to frame you at center with the approaching ring visible at the edges. The world outside the encounter zone desaturates to 40% grey. A subtle vignette darkens the periphery. Your flame—normally a small ambient glow—pulses once, bright then dim, announcing itself as the active element. The nomads resume their approach in slow-motion for one second, then accelerate to normal speed. The encounter has begun.
- **exit_transition:** The vignette lifts. The world outside the encounter zone returns to full saturation over one second. Your converted nomads rise from kneeling and join your band's formation, their inner glow fading to match your other followers. The camera pulls back to normal play framing. The world UNPAUSES: your band resumes movement, the grey expanse returns to its ambient state. The encounter is over.
- **feedback_win:** The first nomad reaches arm's length and drops to both knees in one fluid motion. Your flame detaches—a mote of golden light—and drifts into their chest, where it settles and glows beneath the skin. One to three others who were mid-approach also kneel in sequence, each receiving a mote. The kneeling figures' bodies gain a faint inner luminosity. All other nomads stop, turn, and walk slowly back into the grey—not fleeing, simply departing.
- **feedback_fail:** All nomads stop outside arm's reach, bodies angled away, gazes averted. They stand for one beat—a moment of collective refusal—then turn and walk back into the grey in a loose, uncoordinated scatter. Your flame dims to its ambient minimum and stays there. The ring dissolves into fog.
- **visual_hierarchy:** Your flame's corona—size and intensity of the light-halo around your body, the only element you directly control → The nearest nomad's posture and facing—leaning in, recoiling, or turning away—your immediate feedback loop → The ring's overall geometry—how many are still approaching vs. drifting sideways or retreating, the strategic read
  - *flame_too_dim* → Corona shrinks to a faint outline, barely larger than your sprite. Light is cool and weak, casting no shadows on nearby ground.
  - *flame_steady_low* → Corona is a soft halo one body-width in radius, warm yellow-white, gentle pulse like breathing.
  - *flame_steady_acceptable* → Corona is steady at 1.5 body-widths, golden, no flicker—this is the target band. Nomads lean forward.
  - *flame_steady_high* → Corona reaches 2 body-widths, bright white-gold, beginning to flicker at the edges. Nomads hesitate, posture stiffens.
  - *flame_too_bright* → Corona flares to 3+ body-widths, harsh white light with sharp edges. Nomads recoil, raise one hand to shield eyes, shoulders pull back.
  - *nomad_committed* → Body leans forward from the waist, both arms relaxed at sides, head and gaze fixed on you, stride steady and purposeful.
  - *nomad_hesitating* → Stride slows, head tilts slightly, one shoulder drops—they're reading the flame, deciding whether to continue.
  - *nomad_recoiling* → Upper body pulls back, one hand rises to eye level (shielding gesture), stride breaks into a backward step or sideways drift.
  - *nomad_drifting* → Head turns 45° away, gaze breaks, body angles sideways, movement becomes lateral rather than approach.
  - *nomad_retreating* → Full turn, shoulders squared away from you, walking back into the grey with steady pace—they've given up.
  - *distance_close* → Nomad is within 3-4 body-lengths—you can see facial features, posture details. This is the critical zone.
  - *distance_medium* → Nomad is 5-10 body-lengths away—posture is readable, but details are soft. You have time to correct.
  - *distance_far* → Nomad is at the edge of the encounter circle, 10+ body-lengths. A silhouette with basic facing and lean visible.

## Finding it in play

- **Director test hook:** open the build with `#mg` in the URL (e.g. `uhta-slice.html#mg`) — the encounter force-arms from the start of play, regardless of spawn luck.
- **Normal play:** the attention cue above, then the trigger condition in the design; the entry transition pauses the world.


## The patch

| | |
|---|---|
| selected | `first-contact-hope` |
| from_run | `mg-live-2` |
| checks | `{'parse:logic_block': True, 'parse:frame_line': True, 'parse:input_line': True, 'parse:selftest_block': True, 'all_preexisting_assertions_survive': True, 'adds_at_least_one_M_assertion': True, 'grew': True, 'whole_file_brace_balance': True, 'never_writes_transitioning': True, 'director_test_hook': True, 'first_use_line_present': True}` |
| repair_rounds | `0` |
| node_available | `True` |
| play_probe | `SKIPPED: playwright not available on this machine` |
| playwright_available | `False` |
| first_use_line | `You hold the flame steady, and those who approach without flinching will kneel.` |
| instructor_repairs | `0` |
| presenter_repairs | `1` |

### Inserted at the five anchors (contract v3)

1. **logic** (top level): 76 line(s)
2. **frame** (inside drawWorld — the per-frame seat where the encounter lives): 77 line(s)
3. **input** (onClick guard — the encounter owns the pointer): 2 line(s)
4. **self-test**: 13 line(s) — the M-assertions gate the pure logic
5. **hook** (verb-trigger arming assist, optional): (omitted)


**Programmer notes:** Triggers when 5+ grey nomads are within 8 tiles of the player (or immediately via #mg hash). Eight nomads spawn in a ring 180-220 pixels from the avatar. Hold SPACE to raise the flame (rises to 100), release to let it dim (falls to 0). Flame pulses naturally with sin wave. Nomads approach when flame is 40-65 (accounting for pulse); outside that band they hesitate, then drift sideways and eventually turn away. Win when first nomad reaches <20px distance; fail when all have drifted out. On win, converts 1-3 nearby grey NPCs to devout (v=10). Flame corona size and color show the current level; nomad color shows commitment (green lean) vs recoil (red + shield gesture as a small circle). Encounter lasts 30-60s with natural rhythm-reading gameplay.


## Applying it (Director)

```
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\build-fc\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open the build: the self-test panel must show every G-assertion AND the new M-assertion(s) green. Then play to the encounter and judge the thing no container can: whether it feels like the GDD's sentence. **GDD §3's stop rule still applies to committing this to the canonical slice** — building it was gated on your selection; shipping it is gated on the stranger test, and that ruling is yours.

## Director verification

- [ ] panel all green, including M-assertions
- [ ] the encounter triggers where the design says
- [ ] wordless in play — no text appeared
- [ ] the two poles would not play the same game

