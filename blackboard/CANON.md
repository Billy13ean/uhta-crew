# CANON.md — v17 | 2026-07-28 | gates [G1–G21 · Runs 17–22 · review-board closeout (v0.9.1/v0.9.2) · Run 23/23b SALVAGE — rules-v3.9.1-C ratified · A1-feedback closeout (v0.9.7)]

> **Process canon lives in `CANON-process.md`** (Keeper escalation, build order, Definition of Playable, roster, RAG corpus, report-discipline defect). This file is the always-on digest, capped at **900 words** (`prompts/keeper.md` Mode A); the split is what brought it back under.

**Open, promoted to top of queue:** the loop has never been tested by anyone but the Director. Thirteen ruleset generations verified, zero external playtests, 0 of 6 Playability criteria tested.

## Delta from v15

### Runs 20–22 — the living world, now canon (was WIP at v15)
**Genesis (v3.6):** the world self-forms — grey nomad loners (55) + symmetric founding zealots (1F/1H) that gather, settle (min 5 followers at devout average), colonize. Terminal grace until formed (aligned ≥ 0.4 or first settle). genesis-off reproduces legacy exactly. **Schism (v3.7):** full+devout settlements fission same-pole daughter colonies (pop cap 16, fission radius 10, max 6 tribes) — the world grows by spreading, not ballooning. **Road allegiance (v3.7.1):** roads carry pole+strength; enemies crossing erode toward grey (then detach re-recruitable) and wear the road; enemy zealots damped on your color. **Rebalance (v3.7.3, Director):** difficulty is **asymmetric by design — Fear easy, Hope hard** (bot proxy at that gate: FEAR ~22/25, HOPE ~20/25 — **superseded, do not read as current**; at v3.9.1 the arms measure hope 21/25 / fear 16/20, and the genesis bots invert the OFF baseline. The stance is intent; re-benchmark before reading direction). hope_trade DISABLED (revisit as visible trader agents). **Ascension (v3.8):** follower-driven power tiers 0–3 (beacons 1→4, flame/aura radius, stamina cap 10→24), recomputed each sleep; the kaiju scales with the flock. **Peer contagion (v3.8.1):** belief spreads NPC-to-NPC (~0.1/neighbor, cap 0.7, r2); apathy spreads too.

### Review-board closeout — Director rulings (GDD v0.9.1, v0.9.2)
1. **Flame tint:** the cave choice sets only the starting tint; alignment is fully re-tintable through play. Identity is emergent.
2. **Counterpoint:** musical sense — a second, undetermined voice against Uhtcearu's theme, not a hope-predisposed opposite. Reconciles purpose-born with blank-slate.
3. **Document intent:** academic/portfolio piece; experience comps only (Journey/Gris; Reus/Black & White); no commercial claim.
4. **Win-vs-loss tie → LOSS.** *Discovery at implementation (Run 23):* the v3.7 sim silently gave the WIN the tie; `win_loss.tie_priority: "loss"` now enforced data-driven. No organic tie observed in ~420 runs; synthetic tie verified loss-first. **(v17 note: this is the canonical worked example of the §3.2 escalation rule — a `CONTRADICTS-LOCKED` flag against this line, ruled UPHOLD.)**
5. **The opening is narrated (wordless after the first dawn):** a text narrator — the teacher — names each verb and its consequence during the genesis cycle only; the words end permanently at the first sleep. Teaching-text is instrumentation, not authorship; the endscreen question stays open (§6).
6. **GRIEF CANON:** grief is not a pole — it is the *gravity*. Long-term grief traps people in apathy; the per-tick decay toward 0 IS Uhtcearu's grief. Uhtcearu never fights for a color; he drowns the board in grey. Catastrophes therefore wear the dominant pole toward 0 and never recruit for the opposite.

### Run 23 → 23b — Uhtcearu active events: the GRIEF FRONT (rules-v3.9.1-C, ratified)
Run 23 proposed three antagonist philosophies (tide / judge / law); **Director selected A (Grief Front)**. attacks-v5 verdicted it **safe but half-dead as shipped** (in-sphere drift delta 0.000/sleep; centroid spawn and instantaneous trigger both dodgeable) with a data-only salvage set; **Director ruled salvage-as-antagonist.** Co-gated fix set (Run 23b):
- `front_strength 4.0` → inside-front decay 2.0/tick **exactly equals zealot pull**: a true STALL. Held believers neither deepen nor grey; the front can never flip (decay can't cross 0), burn (decay is not same-pole pressure), or kill. Stragglers bounded by the step cap at −1/tick.
- `spawn_at largest_dominant_pole_tribe_position` — the fog condenses ON the winner's largest tribe; kills centroid-steered siege aiming.
- `trigger_trailing_window_sleeps 3` — fires on trailing-max dominance ≥ 0.55; kills hover-then-sprint scheduling.
- `affects_dominant_pole_only true` — grief wears only the winner, never greys enemy holdouts.
- Cooldown held at 2 (3-on/2-off, ~0.65 late-game uptime).

**Verified (metrics-v3.9.1, ~40 arms):** 80/80 legacy equivalence; 0 assert violations; hope campaign 23→21/25 at unchanged median, fear 16/20 untouched; 96% of fronts do real work; no front-as-shield, no in-front haven, no high-dominance sandwich. Full numbers stay in `outputs/v2/metrics-v3.9.1.md` — this digest carries decisions, not evidence. **Antagonist identity confirmed: "grief takes the stragglers; the shepherded stand."**

### Pipeline status
GDD (**v0.9.7**) → Orchestrator dispatch → Keeper packet → Mechanic Designer → Director select → Red-Team → Director salvage ruling → Playtester (harness, ~40 arms) → ratify → build port; Writer → Critic → Director for content. **Thirteen ruleset generations** — one committed `rules-*.json` file each, `rules-v1-B` → `rules-v3.9.1-C`. Fifteen Keeper reports across runs 1–19. Reference sim: `sim/harness-v3.9.py` (supersedes sim/harness.py; grief front + tie priority, data-driven, absent-field = prior behavior).

### Remaining work — human-owned / post-gate
**The external playtest (top of queue).** Narrated teaching opening (blocks 1, 3); front-render legibility (blocks 5); Keeper report backlog runs 20–23; fun-tuning; spawn-position lever; miracle polarity; difficulty-proxy re-benchmark; endscreen question; deferred §2.6 systems; trader agents; **CrewAI port 7/28**; **content pipeline 7/30**; capstone 9/1.

## Open questions (delta from v16)
Resolved: living-world gate (runs 20–22); review-board quick fixes; wordless-teaching; grief scale position; Uhtcearu active events; Keeper flag destination, core-vs-nice ordering, the meaning of "playable", orchestrator deferral (all → `CANON-process.md`). Remain: front feel items; endscreen; miracle polarity; **difficulty-proxy hygiene — the Fear-easy/Hope-hard stance is intent, not a measured result (metrics-v3.9.1 §F reads hope-favored)**; fun-tuning envelope; deferred systems; trader agents; whether the six Playability criteria are the right six; narration and endscreen content, blocked behind the Writer + Critic pipeline.
