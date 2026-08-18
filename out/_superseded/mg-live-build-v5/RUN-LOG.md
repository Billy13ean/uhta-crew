# RUN-LOG — mg-live-build-v5

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — director gate

Load the Director-selected design from the propose run. No selection, no build.
- `director-gate` selection `first-contact-hope` from `out/mg-live/CANDIDATES.json` — the human gate: this command line IS the Director's ruling
- `director-gate` **WRITE** `out/mg-live-build-v5/SELECTED-DESIGN.json` (2529 B, sha256:407614fd51100c5f)

## Stage 2 — instructor (Writer's seat, GDD §5)

One first-use narration line, held to the same register gate as the game's verb narration (ger.checks, reused). Displays once, sleep 0.
- `mg-instructor` **WRITE** `out/mg-live-build-v5/instructions.json` (126 B, sha256:2fe69081bd2728ce)
- `mg-instructor` line accepted (0 repair): "You hold the flame steady, and those who approach decide whether to trust you."

## Stage 3 — presenter (Aesthetic Director's seat, GDD §5)

The diegetic presentation spec: attention cue, pausing entry transition, visual hierarchy, signal map, feedback. Render language only.
- `mg-presenter` **WRITE** `out/mg-live-build-v5/presentation.json` (3992 B, sha256:569e31fdb42d644a)
- `mg-presenter` spec accepted (0 repair) — entry: The world dims to 40% saturation and brightness in a half-second fade. All band members ou…

## Stage 4 — programmer

Anchored patch under the A5 contract: three inserts, new M-assertions, every G-assertion survives, node parse check (node present).
- `mg-programmer` **READ** `blackboard/build/uhta-slice.html` (1353917 B, sha256:b8e3330e5833a25d)
- `anchors` logic: `function teachingFor(verb,sleep_no,spoken){if(sleep_no!==0)return null…`
- `anchors` frame: `    const g=this.world; g.clear(); this.ui.clear(); this.overlay.clear…`
- `anchors` input: `  onClick(p){`
- `anchors` selftest: `  out.push(['G5 road allegiance erodes enemy crossing', re>=4, `${re}/…`
- `anchors` hook: `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);`
- `mg-programmer` **WRITE** `out/mg-live-build-v5/patch-attempt-1.json` (8327 B, sha256:ff7fa6272dd83549)
- `mg-play-probe` attempt 1: RAN — 5/9 probe checks passed
- `mg-programmer` post-checks FAILED (the headless PLAY-PROBE drove your patched build in a real browser and it FAILED: P5_click_feeds_flame, P6_survives_8s_idle, P4_first_use_line_shown, P7_control) — one repair round-trip
- `mg-programmer` **WRITE** `out/mg-live-build-v5/patch-attempt-2.json` (5111 B, sha256:33a1ec416473321a)
- `mg-play-probe` attempt 2: RAN — 5/9 probe checks passed

**FAILED.md written** — agent=`mg-programmer` stage=`programmer`
