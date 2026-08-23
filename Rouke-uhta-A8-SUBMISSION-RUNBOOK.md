# A8 submission runbook — Narrative Engine Prototype (Sonder)

**Due Mon 25 Aug, 11:59 PM ET · 10 pts · optional**

The build is done and tagged (`assignment-8`, commit `cbb40f6`). This is a verify-and-package pass, ~45 minutes plus one playthrough.

## The rubric, mapped to what already exists

| Criterion | Pts | Where it lives | Status |
|---|---|---|---|
| State tracking — JSON facts ledger, visible in output/logs | 4.0 | `sonder/sessions/<run>/ledger.json` + per-turn `turn-NN.json`, each carrying the full `ledger` and a `diff` block; ledger tracks player, band, zealots, world, facts, promises, betrayals, loyalties, history | ✅ |
| Reactive dialogue — responses change with ledger state | 3.0 | Transcripts show it (Brand's cracked spear, Ila's water-skin secret, heirlooms touched-never-explained, the press chosen by colour-band) | ✅ |
| Consistency over 5+ turns | 2.0 | `sessions/tate-260821-001438-c66d` runs **12 turns**; several others run 8+ | ✅, see note |
| ReadMe — world, what's tracked, one surprising moment | 1.0 | `sonder/README.md` §1 (the world), §2 (what the ledger tracks), §5 (the moment the agent surprised me) | ✅ |

**The note:** the 5+ turn sessions predate your rules v2–v4 (the press, the choice, era snapshots, heirloom hand-offs). The only post-v2 session (`bram-260821-170242`) is 3 turns. The rubric doesn't care; your own bar does.

## Steps

1. **One fresh live playthrough, 6+ turns** (~20–30 min): `cd C:\dev\uhta-crew\sonder` then the run command in `sonder/RUNBOOK.md` (no flags — live DM, dealt character). While playing, check: the press lands at the end of every section, the choice/question closes the run, no "zealot" leak, ledger diff in every `turn-NN.json`.
2. **`--compile`** the bank afterward (per RUNBOOK) so the new telling joins `sonder/bank/`.
3. Commit: `git add sonder && git commit -m "A8: post-v2 live session + compiled telling" && git push`. Move the tag if you want it on the final state: `git tag -f assignment-8 && git push -f origin assignment-8`.
4. **Submit.** The clean shape, matching how A3–A7 went in: the GitHub link pinned to the tag — `https://github.com/Billy13ean/uhta-crew/tree/assignment-8/sonder` — plus `sonder/README.md` as the ReadMe deliverable. If the portal wants files: zip `sonder/` minus `__pycache__` and `sessions/` except your best two sessions (the 12-turn `tate-260821-001438-c66d` and the fresh one from step 1).
5. In the submission text, point the grader at one thing: *the ledger is not just visible in the logs — every turn file carries the full ledger plus the diff that turn caused, so the 4-point criterion is checkable turn by turn.*

**If Monday gets tight:** skip step 1 and submit as-is — the 12-turn session covers every rubric line. Step 1 is for your standard, not theirs.

---

# A9 submission runbook — Adversarial QA Agent

**Due Thu 27 Aug, 11:59 PM ET · 10 pts · optional**

Everything is built and has run three times against the real slice. Landing steps:

1. Files arriving in this commit: `tools/chaos_probe.js` (the agent), `out/a9-chaos/chaos-report-seed{7,23}.json` + `chaos-report-idle.json` (three complete runs; seeds 7 and 23 each carry finding F01), `Rouke-uhta-A9-README.md`.
2. Optional but recommended — reproduce one run yourself so you've seen it: `node tools/chaos_probe.js blackboard\build\uhta-slice.html --seed 7 --out out\a9-chaos\rerun.json` (needs `npm i playwright` if node_modules isn't set up locally; it uses the same dependency as `tools/mg_probe.js`).
3. Commit (`out/*` is gitignored — force-add the reports):
   ```
   git add tools\chaos_probe.js Rouke-uhta-A9-README.md Rouke-uhta-A8-SUBMISSION-RUNBOOK.md
   git add -f out\a9-chaos
   git commit -m "A9: chaos_probe adversarial QA agent — 10 invariants, 14 behaviors, 3 seeded runs; finding F01 ZERO_STAMINA_NO_FEEDBACK"
   git tag assignment-9 && git push origin main --tags
   ```
4. Submit the link pinned to the tag + the README. The rubric's 4-point line ("found at least one real bug… names the mechanic") is F01, named to `moveStep()/tryAct()` in the stamina economy; the 3-point line (active breaking, clear definition of broken) is the invariant list; the 2-point line is the JSON reports' location / error_type / game_context fields.
5. **Worth 15 minutes before Sept 1 anyway:** fix F01 in the slice — one `setTip('You are spent. Sleep brings the next generation.')` in the early-return path — and note in the submission that the agent's finding shipped. Graders love a closed loop.
