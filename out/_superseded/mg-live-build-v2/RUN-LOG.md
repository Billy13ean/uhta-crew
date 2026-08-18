# RUN-LOG — mg-live-build-v2

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — director gate

Load the Director-selected design from the propose run. No selection, no build.
- `director-gate` selection `first-contact-hope` from `out/mg-live/CANDIDATES.json` — the human gate: this command line IS the Director's ruling
- `director-gate` **WRITE** `out/mg-live-build-v2/SELECTED-DESIGN.json` (2529 B, sha256:407614fd51100c5f)

## Stage 2 — instructor (Writer's seat, GDD §5)

One first-use narration line, held to the same register gate as the game's verb narration (ger.checks, reused). Displays once, sleep 0.
- `mg-instructor` **WRITE** `out/mg-live-build-v2/instructions.json` (137 B, sha256:3311e604996f9f90)
- `mg-instructor` line accepted (0 repair): "You tend the flame, and those who approach will stay only if it neither wavers nor burns."

## Stage 3 — presenter (Aesthetic Director's seat, GDD §5)

The diegetic presentation spec: attention cue, pausing entry transition, visual hierarchy, signal map, feedback. Render language only.
- `mg-presenter` **WRITE** `out/mg-live-build-v2/presentation.json` (3892 B, sha256:186e23c53aba2163)
- `mg-presenter` spec accepted (0 repair) — entry: The world dims to 40% saturation and brightness. All non-participant sprites slow to half-…

## Stage 4 — programmer

Anchored patch under the A5 contract: three inserts, new M-assertions, every G-assertion survives, node parse check (node present).
- `mg-programmer` **READ** `blackboard/build/uhta-slice.html` (1353917 B, sha256:b8e3330e5833a25d)
- `anchors` logic: `function teachingFor(verb,sleep_no,spoken){if(sleep_no!==0)return null…`
- `anchors` selftest: `  out.push(['G5 road allegiance erodes enemy crossing', re>=4, `${re}/…`
- `anchors` hook: `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);`
- `mg-programmer` **WRITE** `out/mg-live-build-v2/patch-attempt-1.json` (5487 B, sha256:b02ea58b75be7f48)
- `mg-programmer` post-checks FAILED (the Instructor's first_use_line is not in the patch — it must be displayed once, via the existing tip/teaching mechanism, when the encounter first begins on sle) — one repair round-trip
- `mg-programmer` **WRITE** `out/mg-live-build-v2/patch-attempt-2.json` (5033 B, sha256:db17abefac43d959)
- `mg-programmer` **WRITE** `out/mg-live-build-v2/uhta-slice.minigame.patched.html` (1357850 B) — all post-checks passed
- `assemble` **WRITE** `out/mg-live-build-v2/MINIGAME-BUILD.md` (9617 B, sha256:31b4073865c0ec20)

**Build run complete.** The in-place build was not touched — apply and verify per MINIGAME-BUILD.md.
