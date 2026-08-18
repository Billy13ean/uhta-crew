# MINIGAME-BUILD — the selected design, built — mg-live-build-v2

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 01:50:15


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

> You tend the flame, and those who approach will stay only if it neither wavers nor burns.

Displays once, when the encounter first begins on sleep 0 — inside the game's narrated window; register-gated by the same checks as the verb narration.


## The Presenter's spec (Aesthetic Director's seat)

- **attention_cue:** Grey nomad sprites halt their wandering and turn to face the player's band from multiple directions simultaneously. Their bodies lean forward slightly, heads tilted toward the player. A faint pulse of warmth begins to glow above the player's lead figure—not yet a flame, just a gathering of light, like embers collecting.
- **entry_transition:** The world dims to 40% saturation and brightness. All non-participant sprites slow to half-speed, then freeze. The camera tightens its bounds, centering on the player's band with the nomad ring visible at the edges. The ember-glow above the player ignites into a small, flickering flame—gold-orange, unstable. The nomads begin their slow approach inward. The pause is held for 1.5 seconds before player input is accepted.
- **exit_transition:** The world's saturation and brightness return to 100% over 1 second. Frozen background sprites resume normal speed. The camera bounds expand back to standard play view. Converted nomads (if any) rise from kneeling, now gold-toned, and join the player's band formation. The flame above the player fades naturally. Play resumes.
- **feedback_win:** The nomads complete their approach and kneel in perfect unison—a synchronized drop to both knees, heads bowed low, hands open at their sides. Their grey sprites saturate fully to warm gold, glowing from within. The flame above the player stabilizes into a steady, radiant pillar—no flicker, pure gold-white. The light expands gently to touch all kneeling figures. Hold for 2 seconds in this tableau.
- **feedback_fail:** FLARE PATH: The flame explodes into a white starburst, searing outward with sharp rays. Nomads throw arms up, bodies recoil violently, then scatter in all directions—running sprites, chaotic movement, grey deepening to near-black. The flame collapses to nothing. / DIM PATH: The flame gutters, shrinks to a single ember, then extinguishes to grey ash that drifts upward. Nomads turn away slowly, shoulders slumped, and fade back into the fog—sprites losing opacity and saturation, edges dissolving. Some retain a faint gold outline, a ghost of what they almost became.
- **visual_hierarchy:** The flame above the player's body—its brightness, color, and stability → The nomad ring—their posture, distance, and movement toward or away from center → The player's own figure beneath the flame—grounded, still, the anchor point
  - *flame_steady* → Gold-white core with soft orange corona, gentle flicker, height approximately 1.5x sprite height, warm glow radius touching nearest nomads
  - *flame_too_bright* → Searing white-blue core, harsh flare extending 2x normal height, sharp crackle of light rays, corona bleeds into surrounding air
  - *flame_too_dim* → Ember-red, low flicker, height barely above sprite, orange glow fading to grey at edges, threatening to extinguish
  - *nomad_committed* → Upright posture, steady forward walk, bodies leaning slightly inward, grey sprites warming to faint gold undertone at edges
  - *nomad_hesitant* → Leaning back, torso angled away, forward movement paused or stuttering, one foot forward but weight shifted back
  - *nomad_recoiling* → Bodies turn 45° away, hands raised to shield face, backward steps, grey deepening, movement away from center
  - *nomad_drifting* → Torso sags, head turns aside, slow rotation away from center, sprites fading in saturation, edges softening into fog
  - *ring_closing* → Distance between nomads and player shrinks visibly, ring tightens from loose circle to close formation, individual sprites grow larger on screen
  - *steady_band_drift* → The flame's 'correct' brightness shifts subtly—the nomads' commitment response threshold moves, visible only by watching their reactions lag or anticipate the current flame state

## Finding it in play

- **Director test hook:** open the build with `#mg` in the URL (e.g. `uhta-slice.html#mg`) — the encounter force-arms from the start of play, regardless of spawn luck.
- **Normal play:** the attention cue above, then the trigger condition in the design; the entry transition pauses the world.


## The patch

| | |
|---|---|
| selected | `first-contact-hope` |
| from_run | `mg-live` |
| checks | `{'parse:logic_block': True, 'parse:selftest_block': True, 'parse:hook_line': True, 'all_preexisting_assertions_survive': True, 'adds_at_least_one_M_assertion': True, 'grew': True, 'whole_file_brace_balance': True, 'director_test_hook': True, 'first_use_line_present': True}` |
| repair_rounds | `1` |
| node_available | `True` |
| first_use_line | `You tend the flame, and those who approach will stay only if it neither wavers nor burns.` |
| instructor_repairs | `0` |
| presenter_repairs | `0` |

### Inserted at three anchors

1. **logic** (after the pure-resolver region): 6 lines
2. **self-test** (inside the on-load self-test): 8 lines — the new M-assertions gate the pure logic
3. **hook** (after the verb dispatch): 1 line(s)


**Programmer notes:** The encounter arms on sleep 0 if 8+ grey nomads exist (or if hash contains 'mg' for Director testing). When armed and not already active, it pauses the sim, dims the world to 40%, initializes the flame at mid-brightness with 8 nomads in a ring at distance 12. Each frame, left-click brightens the flame; it decays naturally. Nomads commit and approach when flame is in the drifting steady band, recoil/die if too bright or too dim. Win: all alive nomads reach distance <=2.5 with commit >=0.9 (converts 3 grey to devout). Flare: all nomads dead and flame >0.7 (burns out 2 NPCs). Dim: all nomads dead and flame <=0.7 (drifts 1 NPC to apathy). The first_use_line is injected into TEACHING_TEXT under key 'mg_first' and displayed via pending_teaching on first trigger at sleep 0.


## Applying it (Director)

```
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\mg-live-build-v2\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open the build: the self-test panel must show every G-assertion AND the new M-assertion(s) green. Then play to the encounter and judge the thing no container can: whether it feels like the GDD's sentence. **GDD §3's stop rule still applies to committing this to the canonical slice** — building it was gated on your selection; shipping it is gated on the stranger test, and that ruling is yours.

## Director verification

- [ ] panel all green, including M-assertions
- [ ] the encounter triggers where the design says
- [ ] wordless in play — no text appeared
- [ ] the two poles would not play the same game

