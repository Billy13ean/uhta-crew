# uhta — ship checklist (from Class 13 "Final Screen Tips")

*Written 2026-08-21. Status column is what I could verify on disk in `C:\dev\uhta-crew` and in the project docs today — correct anything that's stale.*

**Dates that matter:** playable-link assignment due **Mon Sept 1** (max 50% without a link) · capstone due **Tue Sept 8** (playable link + pipeline description + one-page pipeline audit). Hot tip from class: submit a *link*, so you can keep polishing after you submit.

**Which build is "the game"?** Two candidates exist and neither is the whole thing:

- `blackboard/build/uhta-slice.html` — canonical, dated Aug 13, **no cave opening**, no Sonder hook (the string `SONDER HOOK` is absent; last night's three files never landed on disk).
- `out/mg-directors-cut/uhta-slice.minigame.patched.html` — Aug 18, has the cave + encounter + discovery cue, no Sonder hook.

First job is to pick one and make it the only one.

---

## 0. Gate — "can a stranger play it start to finish today?"

The class poll question. Everything below serves this.

- [ ] Decide the shipping build (recommend: promote the directors-cut to `blackboard/build/uhta-slice.html`, then re-apply the Sonder hook on top).
- [ ] Land the Sonder hook files from last night (`uhta-slice.html`, `sonder/bank/sonder-teller.js`, `sonder/README.md`) — check for `SONDER HOOK`, then run the commit in `claude/Rouke-uhta-sonder-hook-2026-08-21.md`.
- [ ] Open it with `#dev` and confirm the self-test is all green (13/13, or 14/14 with G14).
- [ ] Play one full run yourself, title → cave → wake → terminal, with no dev tools. Note every bug. Fix only bugs that stop a run.

## 1. Scope — the 50% cut exercise

Class 13: two weeks out, if you have ten half-working features you will not ship. Ask "if I threw away half of what's left, would the game be as good?"

- [ ] Write the list of everything still unfinished (Sonder hook landing, sound, title upgrade, stranger test, endscreen, trader agents, interactive structures, procedural maps, encounter mini-games…).
- [ ] Cross out half. The GDD stop rule already says NICE #2–5 and PROPOSED are frozen — honor it. `BACKLOG-later.md` (title-screen hi-def + rise-and-blur) stays in the backlog.
- [ ] Smallest complete loop check: Start → Action → Response → Win/Loss → End. The "End" half is the weak spot — see §4.

## 2. First 30 seconds

Class 13: the first screen decides reception; the beginning is the only part everyone sees.

- [x] A title screen exists (cave painting). Fancy is not required — done.
- [x] Something in-game says what the controls are (WASD / L-click flame / R-click / space to sleep lines exist; cave teaches wordlessly).
- [ ] One sentence of "why am I here / what am I doing" visible before the player has to act (the A4 n1 line — "You carry a white flame…" — is in the directors-cut build; confirm it's in the shipping build).
- [ ] Sound starts **off or low** on the title screen with a visible way to turn it up (class tip — and only matters once §3 exists).
- [ ] Time the load: file is 1.35 MB single HTML with Phaser inlined — should be well under the **10-second rule**, but confirm once it's on itch.io, not from `file://`.

## 3. Polish — sound (the one thing the build has none of)

Class 13: menu clicks + background music from a free asset pack changes perception more than any feature. Verified: the game script has zero `sound.play`/`AudioContext` calls of its own — total silence.

- [ ] Pick a free pack (itch.io / OpenGameArt / Kenney / freesound, CC0) — menu click, flame, roar, sleep/wake transition, one ambient loop. Don't chase perfect.
- [ ] Wire 4–6 SFX + one loop into Phaser's sound manager. Base64 them into the single HTML to keep the one-file build (watch size).
- [ ] Mute toggle + start-quiet default (ties to §2).
- [ ] Canon check: the CANON rules say final audio is CUT "until the loop is proven fun" — this is a *placeholder* pass, not final audio. Say so in the README.

## 4. The ending

Class 13: a player who hits the terminal should know it's over. The game has a unification win/loss check but no endscreen (NICE #2, unbuilt).

- [ ] Minimal terminal screen: one line for win, one for loss, "play again" → `newGame`. Wordless is the canon ideal, but a single line beats a frozen board.
- [ ] Verify the loss reads as *caused* (Definition of Playable criterion 6 is the one that matters).

## 5. Technical audit before upload

Class 13's common failure points.

- [ ] No hard-coded local paths. The Sonder hook uses `../../sonder/bank/sonder-bank.js` relative `<script src>` — on itch.io that path does not exist. Either inline the bank into the HTML or ship the folder in the zip with the same relative layout.
- [ ] Missing JS/JSON dependencies: open the shipping HTML from a fresh folder (copy it alone to `C:\temp`) and check the console for 404s / errors.
- [ ] Package size: zip the build, confirm itch's limits are fine (it's ~1.4 MB — fine) and it still loads fast.
- [ ] Test in a second browser and on a laptop screen size (the slice assumes a large canvas).

## 6. Publish — make it one click away

Class 12/13: itch.io, HTML5, "a stranger can play within two minutes of clicking."

- [ ] Create the itch.io project (password-protected is allowed for the assignment if you want it private).
- [ ] Upload the zip as an HTML5 game, set embed size to the game canvas, "This file will be played in the browser."
- [ ] Load it from the public link on a machine that is not yours. Start the 10-second stopwatch.
- [ ] Put the link in a one-page README (`Rouke-uhta-A10-README.md` or similar) — this is the Sept 1 deliverable.
- [ ] Publish *now*, not on the due date. Re-upload as you polish.

## 7. The stranger test (still 0 of 6 — the oldest open item in CANON.md)

Class 13: watch silently, don't explain controls, note where they get stuck; kids are the most honest testers; silence or "it's fine" is the dangerous feedback.

- [ ] Send the itch link to 3–5 people who have never seen the game. Do not explain anything.
- [ ] Sit with at least two of them (or screen-share). One question at each sleep boundary: "what changed, and why?"
- [ ] Score the six Definition-of-Playable criteria honestly and update `blackboard/CANON.md` and the GDD table.
- [ ] Fix only what the strangers tripped on. That list *is* the polish week.

## 8. The 90-second trailer

Class 13: games with a video get up to 4× the engagement on itch; start with action not the title; show the game not the code; record early, from whatever build you have.

- [ ] Record 2–3 minutes of real play now (OBS / Win+G). Cave exit, a flame conversion, a wake with roads appearing, a Sonder card, a terminal.
- [ ] Cut to 60–90 s, open on the most striking moment (a wake transition, probably), no tech-stack narration, no agent-pipeline talk.
- [ ] Upload to the itch page; embed on the README.
- [ ] Optional devlog: one short honest post about what you're excited about (the generational Sleep / the tellings). Passion, not architecture.

## 9. Capstone paperwork (Sept 8)

- [ ] Playable link (from §6).
- [ ] Pipeline: one sentence per agent is enough — crew (A3), content (A4), builder (A5), GER (A6), style (A7), sonder (A8). You've submitted these before; reuse.
- [ ] One-page pipeline audit: what each agent actually did for the shipped build, what it cost, which agents you'd cut (class tip: an agent you can't explain is a token saving).
- [ ] Tag the repo `capstone`, push, confirm the README renders on GitHub.

---

## Suggested order (two weeks)

1. Pick the build, land Sonder, play it clean (§0) — this weekend.
2. Endscreen + placeholder sound + start-quiet (§3, §4) — early next week.
3. Technical audit, itch upload, README with link (§5, §6) — by **Aug 28**, leaving a buffer before Sept 1.
4. Strangers play it; record footage the same days (§7, §8).
5. Fix what strangers hit; cut trailer; capstone write-up (§9) — by Sept 8.
