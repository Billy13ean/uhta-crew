# RUN-LOG — mg-live-build

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — director gate

Load the Director-selected design from the propose run. No selection, no build.
- `director-gate` selection `first-contact-hope` from `out/mg-live/CANDIDATES.json` — the human gate: this command line IS the Director's ruling
- `director-gate` **WRITE** `out/mg-live-build/SELECTED-DESIGN.json` (2529 B, sha256:407614fd51100c5f)

## Stage 2 — programmer

Anchored patch under the A5 contract: three inserts, new M-assertions, every G-assertion survives, node parse check (node present).
- `mg-programmer` **READ** `blackboard/build/uhta-slice.html` (1353917 B, sha256:b8e3330e5833a25d)
- `anchors` logic: `function teachingFor(verb,sleep_no,spoken){if(sleep_no!==0)return null…`
- `anchors` selftest: `  out.push(['G5 road allegiance erodes enemy crossing', re>=4, `${re}/…`
- `anchors` hook: `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);`
- `mg-programmer` **WRITE** `out/mg-live-build/uhta-slice.minigame.patched.html` (1357331 B) — all post-checks passed
- `assemble` **WRITE** `out/mg-live-build/MINIGAME-BUILD.md` (4838 B, sha256:edac6c6273cf080f)

**Build run complete.** The in-place build was not touched — apply and verify per MINIGAME-BUILD.md.
