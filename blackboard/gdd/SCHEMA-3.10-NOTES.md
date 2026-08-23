# Schema 3.10 — the Temple dials (harness extension, Run 24, 2026-08-21)

*Why this exists:* the crew can only tune numbers the reference simulator already reads (`crew/validate.py`: the baseline is the schema; `_deep_merge` drops any key the baseline lacks). The Temple endgame proposal (GDD §9) had no dials, so run `temple-grief-2` had nothing to vary — and the Designer, told to emit a "complete" file, rewrote fifteen baseline values from memory and crashed the harness. This pass gives the proposal dials and fixes the prompt. **No value here is ratified.** The control file is behaviourally identical to 3.9.1.

## Files

| file | change |
|---|---|
| `blackboard/sim/harness.py` | schema 3.10 blocks, all gated on flags that default off. Parity-tested bit-for-bit: old harness/3.9.1 == new harness/3.9.1 == new harness/3.10-control, 30 arms (6 seeds × do-nothing, walk, throughput, campaign_v3, selfburn, 20 sleeps). |
| `blackboard/rules/rules-v3.10-C.json` | **the 3.10 control**: 3.9.1-C + the new blocks, every `enabled` false, every `_values` note listing the accepted strings. Fourteenth ruleset file. |
| `crew/orchestrator.py` | `BASELINE = "rules-v3.10-C.json"` so the Keeper packets and the validator derive the key set from the control. |
| `prompts/mechanic-designer.md` | v4: output is a **delta**, not a complete file — matches what `_complete_variant` has always done. |
| `crew/validate.py` | schema-failure message no longer tells the model to emit the full file. |
| `tools/parity_schema310.py` | the parity check, re-runnable (`python tools/parity_schema310.py git` also diffs against `HEAD~1`). |

## The dials

```
world.temple.enabled                          false   (A/B/C: true)
world.temple.placement                        random_constrained | fixed
world.temple.min_dist_cave / min_dist_sites / min_dist_edge / min_dist_tribes   14 / 6 / 6 / 6
world.temple.footprint_radius_tiles           2       (entry radius)
world.temple.local_decay.enabled              false   (variant C)
world.temple.local_decay.radius_tiles         8
world.temple.local_decay.strength             1.0     (ADDED to the dominance term; a front REPLACES it and wins inside its own radius)
world.temple.local_decay.affects_dominant_pole_only   true   (matches 23b; the Keeper will want a word if a variant flips it)

world.uhtcearu_events.grief_front.spawn_at    largest_dominant_pole_tribe_position | temple_position   (variant B)
  ...grief_front.duration_counts_from         spawn | arrival   (arrival: no ageing until within arrival_radius_tiles of target, capped at max_travel_sleeps)
  ...grief_front.move_tiles_per_sleep         1 → the B tuning question (per-axis clamped now, so step>1 no longer overshoots)

win_loss.terminal_fires_on                    hold_complete | temple_entry
win_loss.temple_entry.harness_pilgrim_tiles_per_sleep   6   (H-9, below)
win_loss.temple_entry.disarm_if_hold_breaks   false
```

Placement draws from its **own** rng stream (`seed ^ 0x7E3A9C1F`), so enabling the temple moves nothing else in the world. Deterministic per seed; in the smoke sweep seeds 0–19 produced eight distinct sites, none within 14 of the cave.

## H-9 — a new harness assumption, and it is a dial

The scripted bots in `bots.py` know nothing about a temple. Without help, `terminal_fires_on: temple_entry` makes every bot run cap out (19/20 unfinished — measured). So while the win is armed the harness models the pilgrimage: the avatar moves `harness_pilgrim_tiles_per_sleep` toward the temple at each sleep boundary, **and a bot's walk action is consumed as a pilgrimage step** (its destination is ignored; its flames land where it stands). Uncosted — bots account their own stamina. `0` turns it off, which is the "bot must walk itself" arm. The Red-Teamer should attack the pace: too high and the walk is free; too low and the envelope is the pace, not the design.

## What the dials do (campaign_v3, 20 seeds, 32-sleep cap — smoke numbers, not metrics)

| arm | terminals | win sleeps (median) | armed → terminal | fronts | note |
|---|---|---|---|---|---|
| control (3.10, all off) | 16 W / 1 L / 3 cap | 14 | — | 45 | == 3.9.1 |
| A temple + temple_entry | 16 W / 1 L / 3 cap | 17 | 1–4 sleeps | 56 | the walk costs ~3 sleeps; 0 lost while armed (the bot keeps acting) |
| A, pace 0 | 0 W / 1 L / 19 cap | — | never | 95 | bots can't find the temple — H-9 is load-bearing |
| B temple-origin front, step 6, counts from arrival | 17 W / 1 L / 2 cap | 18 | 1–4 | 37 | travel 1–6 sleeps (mode 4); fewer fronts because travel delays the next one |
| C local decay r10 s2.0 | 15 W / 0 L / 5 cap | 18 | 1–4 | 64 | well exposure ≈ 5000 NPC-sleeps; Hope still wins |

These are the Playtester's job to measure properly. They are here so you know the dials move.

## Re-run

```powershell
docker compose build crew
docker compose run --rm crew --selftest
docker compose run --rm crew --version-tag v3.10.1 --run-id temple-grief-3 --seeds 20 --goal "Give grief a home: the Temple endgame as specified in GDD section 9, using the schema 3.10 dials in the baseline. Produce variants A (temple + temple_entry terminal only), B (A + grief front spawn_at temple_position, duration_counts_from arrival, tune move_tiles_per_sleep), C (A + local_decay enabled, tune radius and strength)." --questions "Does spawn_at temple_position re-enable the centroid-steering attack Run 23b closed? Can the hold-to-temple walk be lost, farmed, or trivialised, and how sensitive is it to harness_pilgrim_tiles_per_sleep? Does C make Hope runs unwinnable? Median added sleeps per variant vs the control? Can any variant make the front fire in a do-nothing run?"
```

`--version-tag v3.10.1`, not `v3.10`: variants are named `rules-<tag>-{A,B,C}.json`, and `rules-v3.10-C.json` is the baseline's name — the Playtester tells baseline from variant by filename.

## For the Keeper / the ruling

Canon contact is unchanged from §9: Run 23b `spawn_at` (origin now geographic again under B — target is not), "checked every tick, terminal immediately" (arm/fire under `temple_entry`), the unruled `[24,6]` coordinate (`placement: fixed` keeps it available), the §3 stop rule (gates the build, not this run). New since §9: **H-9 is itself a thing to rule on** — it is the harness's model of a human walking, and the metrics depend on it.
