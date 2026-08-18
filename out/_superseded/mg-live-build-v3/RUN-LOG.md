# RUN-LOG — mg-live-build-v3

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — director gate

Load the Director-selected design from the propose run. No selection, no build.
- `director-gate` selection `first-contact-hope` from `out/mg-live/CANDIDATES.json` — the human gate: this command line IS the Director's ruling
- `director-gate` **WRITE** `out/mg-live-build-v3/SELECTED-DESIGN.json` (2529 B, sha256:407614fd51100c5f)

## Stage 2 — instructor (Writer's seat, GDD §5)

One first-use narration line, held to the same register gate as the game's verb narration (ger.checks, reused). Displays once, sleep 0.
- `mg-instructor` **WRITE** `out/mg-live-build-v3/instructions.json` (137 B, sha256:eabe49b2f68a9292)
- `mg-instructor` line accepted (0 repair): "You tend the flame, and those who approach will stay only if it neither flares nor fades."

## Stage 3 — presenter (Aesthetic Director's seat, GDD §5)

The diegetic presentation spec: attention cue, pausing entry transition, visual hierarchy, signal map, feedback. Render language only.
- `mg-presenter` **WRITE** `out/mg-live-build-v3/presentation.json` (4093 B, sha256:eb833251b9fc15d8)
- `mg-presenter` spec accepted (0 repair) — entry: World pauses. All other bands freeze mid-step. The surrounding terrain desaturates to near…

## Stage 4 — programmer

Anchored patch under the A5 contract: three inserts, new M-assertions, every G-assertion survives, node parse check (node present).
- `mg-programmer` **READ** `blackboard/build/uhta-slice.html` (1353917 B, sha256:b8e3330e5833a25d)
- `anchors` logic: `function teachingFor(verb,sleep_no,spoken){if(sleep_no!==0)return null…`
- `anchors` frame: `    const g=this.world; g.clear(); this.ui.clear(); this.overlay.clear…`
- `anchors` input: `  onClick(p){`
- `anchors` selftest: `  out.push(['G5 road allegiance erodes enemy crossing', re>=4, `${re}/…`
- `anchors` hook: `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);`
- `mg-programmer` **WRITE** `out/mg-live-build-v3/patch-attempt-1.json` (5370 B, sha256:7129620855f4e559)
- `mg-programmer` **WRITE** `out/mg-live-build-v3/uhta-slice.minigame.patched.html` (1358017 B) — all post-checks passed
- `assemble` **WRITE** `out/mg-live-build-v3/MINIGAME-BUILD.md` (10081 B, sha256:73cd2b19ad8ae83e)

**Build run complete.** The in-place build was not touched — apply and verify per MINIGAME-BUILD.md.
