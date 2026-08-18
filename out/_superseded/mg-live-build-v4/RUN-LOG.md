# RUN-LOG — mg-live-build-v4

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — director gate

Load the Director-selected design from the propose run. No selection, no build.
- `director-gate` selection `first-contact-hope` from `out/mg-live/CANDIDATES.json` — the human gate: this command line IS the Director's ruling
- `director-gate` **WRITE** `out/mg-live-build-v4/SELECTED-DESIGN.json` (2529 B, sha256:407614fd51100c5f)

## Stage 2 — instructor (Writer's seat, GDD §5)

One first-use narration line, held to the same register gate as the game's verb narration (ger.checks, reused). Displays once, sleep 0.
- `mg-instructor` **WRITE** `out/mg-live-build-v4/instructions.json` (126 B, sha256:2fe69081bd2728ce)
- `mg-instructor` line accepted (0 repair): "You hold the flame steady, and those who approach decide whether to trust you."

## Stage 3 — presenter (Aesthetic Director's seat, GDD §5)

The diegetic presentation spec: attention cue, pausing entry transition, visual hierarchy, signal map, feedback. Render language only.
- `mg-presenter` **WRITE** `out/mg-live-build-v4/presentation.json` (3947 B, sha256:6698de2f5a30dfee)
- `mg-presenter` spec accepted (0 repair) — entry: The world desaturates to 40% brightness in a radial fade from the player outward (0.8 sec)…

## Stage 4 — programmer

Anchored patch under the A5 contract: three inserts, new M-assertions, every G-assertion survives, node parse check (node present).
- `mg-programmer` **READ** `blackboard/build/uhta-slice.html` (1353917 B, sha256:b8e3330e5833a25d)
- `anchors` logic: `function teachingFor(verb,sleep_no,spoken){if(sleep_no!==0)return null…`
- `anchors` frame: `    const g=this.world; g.clear(); this.ui.clear(); this.overlay.clear…`
- `anchors` input: `  onClick(p){`
- `anchors` selftest: `  out.push(['G5 road allegiance erodes enemy crossing', re>=4, `${re}/…`
- `anchors` hook: `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);`
- `mg-programmer` **WRITE** `out/mg-live-build-v4/patch-attempt-1.json` (7596 B, sha256:751b0f255ee8afe2)
- `mg-play-probe` attempt 1: RAN — 7/8 probe checks passed
- `mg-programmer` post-checks FAILED (the headless PLAY-PROBE drove your patched build in a real browser and it FAILED: P4_first_use_line_shown. Probe detail: {"title": {"phase": "title", "active": ) — one repair round-trip
- `mg-programmer` **WRITE** `out/mg-live-build-v4/patch-attempt-2.json` (5518 B, sha256:5642db399cf9db41)
- `mg-play-probe` attempt 2: RAN — 7/8 probe checks passed

**FAILED.md written** — agent=`mg-programmer` stage=`programmer`
