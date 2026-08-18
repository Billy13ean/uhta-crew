# MINIGAME-BUILD — the selected design, built — mg-live-build

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 01:33:23


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

## The patch

| | |
|---|---|
| selected | `first-contact-hope` |
| from_run | `mg-live` |
| checks | `{'parse:logic_block': True, 'parse:selftest_block': True, 'parse:hook_line': True, 'all_preexisting_assertions_survive': True, 'adds_at_least_one_M_assertion': True, 'grew': True, 'whole_file_brace_balance': True}` |
| repair_rounds | `0` |
| node_available | `True` |

### Inserted at three anchors

1. **logic** (after the pure-resolver region): 29 lines
2. **self-test** (inside the on-load self-test): 5 lines — the new M-assertions gate the pure logic
3. **hook** (after the verb dispatch): 1 line(s)


**Programmer notes:** The encounter arms once on sleep 0 if 8+ grey nomads exist, then triggers when the player is within 6 tiles of 6+ grey nomads. A flame hovers above the player; left-click brightens it (+0.18), natural decay dims it (-0.022/frame). Nomads approach in a ring (distance 12->2) only when flame brightness is near a drifting target band (0.45±0.1*sin). Too bright (>0.85) or too dim (<0.25) causes them to hesitate or retreat. Win: ring closes (all d<3) with high commitment (avg>0.7) -> 3 nomads convert to devout. Fail: flame >0.9 burns 2 nomads, <0.15 drifts 2 into apathy. The Director should verify the flame's glow color (gold steady, white flare, dim ember) and nomad posture (lean back when hesitant, gold tint when committed).


## Applying it (Director)

```
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-mg.html
copy out\mg-live-build\uhta-slice.minigame.patched.html blackboard\build\uhta-slice.html
```

Open the build: the self-test panel must show every G-assertion AND the new M-assertion(s) green. Then play to the encounter and judge the thing no container can: whether it feels like the GDD's sentence. **GDD §3's stop rule still applies to committing this to the canonical slice** — building it was gated on your selection; shipping it is gated on the stranger test, and that ruling is yours.

## Director verification

- [ ] panel all green, including M-assertions
- [ ] the encounter triggers where the design says
- [ ] wordless in play — no text appeared
- [ ] the two poles would not play the same game

