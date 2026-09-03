# A10 Pipeline-Run Video — Recording Runbook (SILENT TAKE)

**Nicholas Rouke · uhta** — target: 2–3 minutes, one take, no narration, no editing.
Recorder: **Windows 11 Snipping Tool** (open it → video-camera icon → select the whole
screen → Start; saves MP4 and records across window switches). On Windows 10 use OBS
Studio with a Display Capture source — Game Bar won't follow you between windows.
Upload unlisted to YouTube (or Drive with link sharing), paste the URL into the
submission doc's **Pipeline Run Video Link** field.

**Silent-video rule:** every beat must leave readable text on screen for ~3 seconds —
the terminal is the narrator. The `echo` caption lines below print section headers into
the terminal so the video explains itself; type them as written.

## Before you hit record

```powershell
cd C:\dev\uhta-crew
docker compose build crew        # so the pull noise isn't in the video
notepad .env                     # confirm ANTHROPIC_API_KEY is set (don't show this on screen)
```

Have two things open and ready: a terminal at `C:\dev\uhta-crew`, and a browser tab on
https://billy13ean.itch.io/uhta (not yet clicked).

## The take

**Beat 1 — what we're looking at (0:00–0:20).** Terminal on screen, then type:

```powershell
echo === UHTA AGENT CREW: Keeper / Mechanic Designer / Red-Teamer / Playtester ===
echo === LIVE BALANCE RUN: temple endgame (the run that produced rules-v3.10.2-A) ===
dir prompts
```

**Beat 2 — kick off the run (0:20–0:40).** Run (one line):

```powershell
docker compose run --rm crew python run_crew.py --run-id a10-video --goal "Temple endgame, GDD section 9, schema 3.10 dials. The ratified baseline rules-v3.10-C.json IS the control; do not emit a variant identical to it. Variant A MUST set world.temple.enabled=true and win_loss.terminal_fires_on=temple_entry and nothing else. B = A plus grief_front spawn_at=temple_position, duration_counts_from=arrival, and a tuned move_tiles_per_sleep. C = A plus world.temple.local_decay.enabled=true with tuned radius_tiles and strength."
```

(This is the exact goal that produced the ratified `rules-v3.10.2-A.json` — a known-good
replay. If the Designer refuses, add `-e CREW_MODEL=claude-opus-4-1` after `--rm` and
rerun.)

**Beat 3 — let the stages log (0:40–1:40).** The orchestrator prints each stage as it
runs (packet → variants → validation gate → attacks → harness batteries →
contradictions) — that console output IS the narration; just leave it on screen. The run
takes a few minutes: pause the recording while it grinds and resume when output appears
(one visible timestamp jump is fine, the manifest corroborates).

**Beat 4 — show the generated artifacts (1:40–2:20).** Type, letting each result sit
~3 seconds:

```powershell
echo === WHAT THE AGENTS PRODUCED ===
dir out\a10-video
echo === THE GAME DATA (variant A) ===
type out\a10-video\rules-v3.10.2-A.json | more
echo === REAL TOKEN COST, RECORDED PER RUN ===
type out\a10-video\manifest.json
```

Scroll so `llm_tokens` in the manifest is visible — that's the line the cost analysis is
calculated from.

**Beat 5 — the pipeline-to-game connection (2:20–3:00).** Type one last caption, then
switch to the browser:

```powershell
echo === THIS DATA IS WHAT THE SHIPPED BUILD PLAYS: billy13ean.itch.io/uhta ===
```

Open the itch page, click Run, play ~20 seconds through the tutorial's first card or two.
Stop recording. Done — the captions carry the story, no voice needed.

## If you'd rather not run live on camera

Same silent take against the existing `out\temple-grief-4` directory (the completed
ratified run — same artifacts, same manifest with its 140,732/28,222 token record):
Beat 1's captions, then `type out\temple-grief-4\RUN-LOG.md | more` in place of Beat 3,
then Beats 4–5 with the paths swapped to `out\temple-grief-4`. Still authentic evidence;
the manifest timestamps corroborate it.
