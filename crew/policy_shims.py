"""Crew-side shims for bot policies that are broken against the current baseline.

WHY THIS MODULE EXISTS
----------------------
`blackboard/sim/bots.py` is vendored **byte-identical** to the game repo's
`sim/bots.py`, and it stays that way. The Playtester owns that file (GDD §3.1);
a crew that silently rewrote the reference suite to make its own arms pass would
be manufacturing the evidence it then reports — precisely the failure the gates
exist to prevent. So when an upstream policy is broken, the fix lives *here*, in
crew-side code, visibly labelled, and the upstream file is left alone for the
Director to fix properly.

THE ONE SHIM CURRENTLY REGISTERED
---------------------------------
**`run_tyrant` — genesis incompatibility.** `bots.py` predates the genesis start.
Its tyrant arm is:

    def run_tyrant(seed):
        w = World(seed); w.player_pole = -1
        while w.sleep_no < 15 and not w.terminal:
            make_flamer(2, -1)(w, s)          # <-- hard-coded tribe index 2
            w.do_sleep()

Under the legacy start (`zealot_poles=(-1,-1,1)`, three pre-clustered tribes)
index 2 is the **hope** tribe — the one opposing the fear player. Under the
ratified baseline `world.genesis.enabled` is true with
`founding_poles: [-1, 1]`, so the world begins with exactly **two** tribes and
`w.tribes[2]` raises `IndexError` on the first wake, every seed.

The shim reproduces the policy's *intent* rather than its literal index: resolve
the target once, at t0, as the first tribe whose pole opposes the player's —
which is what index 2 meant in the world the policy was written for — and fall
back to the last tribe index if no opposing tribe exists. Resolving **once**
(rather than re-picking each wake) is deliberate: the legacy policy pinned one
tribe for the whole run, and schism grows the tribe list mid-run, so re-picking
would be a different policy wearing the same name.

Everything else is unchanged: fear pole, 15-sleep cap, `make_flamer` from the
vendored `bots.py` doing the actual acting. The shim chooses an index; it does
not reimplement the behaviour.

MEASURED, on `rules-v3.9.1-C`, seeds 0-7 (see FINDINGS.md):
    wins 1/8 · max_wf per seed 0.372 … 0.938 (median 0.540) · fronts 0-2
It is a live arm producing a real spread, not a crash converted into noise.

REPORTING ADDITION (declared, so it is not mistaken for a behaviour change):
the shim's return dict carries the legacy keys (`terminal`, `max_wf`, `sleeps`)
**plus** the same end-of-run world statistics `harness.run()` reports —
`final_wf`, `final_lf`, `selfburns`, `pop`, `fronts_spawned`, `front_exposure`.
Those are read off the finished `World`; no action the bot takes changes because
of them. It means the tyrant arm can answer grief-front questions, which the
upstream version could not.

EVERY USE IS LOGGED. `probe_runner` stamps `shim` metadata onto the arm's result;
the Playtester writes it to `RUN-LOG.md` and into the metrics raw-facts appendix.
A shimmed number is never presented as an unshimmed one.
"""
from __future__ import annotations

SHIM_NOTE = ("policy `{name}` executed via crew shim ({reason}); "
             "upstream `blackboard/sim/bots.py` unchanged")


def _opposing_tribe_index(world, player_pole: int) -> int:
    """The index the legacy hard-coded 2 stood for: the first tribe opposing the
    player. Falls back to the last tribe if the world has no opposing tribe."""
    for t in world.tribes:
        if t.pole == -player_pole:
            return t.idx
    return world.tribes[-1].idx


def run_tyrant(seed: int, **_ignored):
    """Genesis-safe `bots.run_tyrant`. See the module docstring."""
    import bots as B
    from harness import World

    w = World(seed)
    w.player_pole = -1
    target = _opposing_tribe_index(w, w.player_pole)   # resolved ONCE, as legacy did
    stats = {"stamina_total": 0.0}
    bot = B.make_flamer(target, -1)
    while w.sleep_no < 15 and not w.terminal:
        bot(w, stats)
        w.do_sleep()
    return {
        # legacy keys, unchanged
        "terminal": w.terminal,
        "max_wf": w.max_wf,
        "sleeps": w.sleep_no,
        # reporting-only additions (see module docstring)
        "final_wf": w.win_count() / w.pop(),
        "final_lf": w.loss_count() / w.pop(),
        "selfburns": w.selfburn_nozealot,
        "pop": w.pop(),
        "fronts_spawned": w.fronts_spawned,
        "front_exposure": round(w.front_exposure_npc_sleeps, 2),
        "stamina_total": stats["stamina_total"],
        "_shim_target_tribe": target,
    }


def run_campaign_v3_audit(seed: int, **_ignored):
    """`bots.run_campaign_v3` with the World kept in scope so the harness's full
    stat dict — including the schema 3.10 temple / armed-terminal audit keys —
    can be reported. The POLICY is upstream's, line for line (fate-aware hope
    campaign, cap 32, hope-only: player_pole is NOT honoured, exactly as upstream).
    Upstream returns only its own five keys, which is why run temple-grief-4 could
    not see whether any campaign run was lost while armed."""
    import bots as B
    import harness as H
    from harness import World, cheb

    w = World(seed); w.player_pole = 1
    s = {'stamina_total': 0.0}
    roads_paid = set()
    while w.sleep_no < 32 and not w.terminal:
        tgt = None
        for t in w.tribes:
            if not t.zealotless and t.pole == -1:
                tgt = t; break
        if tgt is None:
            shallow = [x for x in w.npcs if not x.zealot and 0 <= x.I < 4]
            tgt = w.tribes[shallow[0].tribe] if shallow else w.tribes[2]
        b = B.wake_budget(w)
        if tgt.idx not in roads_paid and tgt.pole == -1 and not tgt.zealotless:
            pay = min(4.0, b-3); s['stamina_total'] += pay; b -= pay
            w.tribes[tgt.idx].road_tiles = 4; roads_paid.add(tgt.idx)
        if w.player_pos != tgt.center:
            d = cheb(w.player_pos, tgt.center); c = min(d*H.WALK_C, max(0.0, b-H.FLAME_C))
            w.act('walk', pos=tgt.center, cost=c); b -= c; s['stamina_total'] += c
        while b >= H.FLAME_C and not w.terminal:
            w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; s['stamina_total'] += H.FLAME_C
        if w.terminal: break
        w.do_sleep()
    out = {
        # upstream keys, unchanged
        "terminal": w.terminal, "sleeps": w.sleep_no,
        "final_wf": w.win_count() / w.pop(), "fate_events": getattr(w, 'fate_events', []),
        "stamina": s['stamina_total'], "selfburns": w.selfburn_nozealot,
        # reporting-only additions: the harness's own counters
        "final_lf": w.loss_count() / w.pop(), "pop": w.pop(),
        "fronts_spawned": w.fronts_spawned,
        "front_exposure": round(w.front_exposure_npc_sleeps, 2),
        "front_events": list(w.front_events),
    }
    if getattr(H, 'TEMPLE_ON', False):   # schema 3.10 audit keys, same shape as H.run()
        out["temple_pos"] = list(w.temple_pos)
        out["win_armed_sleep"] = w.win_armed_sleep
        out["armed_to_terminal_sleeps"] = (w.sleep_no - w.win_armed_sleep) if (w.win_armed_sleep is not None and w.terminal) else None
        out["lost_while_armed"] = bool(w.win_armed and w.terminal and w.terminal[0] == 'loss')
        out["pilgrim_tiles"] = w.pilgrim_tiles
        out["front_travel_sleeps"] = list(w.front_travel_sleeps)
        out["well_exposure"] = round(w.well_exposure_npc_sleeps, 2)
    return out


#: name -> shim record. `probe_runner` routes these names here instead of to
#: `bots.py`, and stamps the metadata onto every arm that uses one.
SHIMS = {
    "run_tyrant": {
        "fn": run_tyrant,
        "upstream": "blackboard/sim/bots.py::run_tyrant",
        "reason": "upstream hard-codes tribe index 2, which does not exist under "
                  "the genesis start's two founding tribes",
        "change": "target tribe resolved once at t0 as the first tribe opposing "
                  "the player's pole (what index 2 meant under the legacy start); "
                  "policy, pole and 15-sleep cap unchanged",
        "findings_ref": "FINDINGS.md #1",
    },
    "run_campaign_v3_audit": {
        "fn": run_campaign_v3_audit,
        "upstream": "blackboard/sim/bots.py::run_campaign_v3",
        "reason": "upstream returns only its own five keys, so the schema 3.10 "
                  "temple / armed-terminal counters (and the grief-front counters) "
                  "are invisible on the campaign line",
        "change": "policy reproduced line for line (hope-only, cap 32); the World "
                  "is kept in scope and the harness's full stat dict is reported",
        "findings_ref": "SCHEMA-3.10-NOTES.md (run temple-grief-4)",
    },
}


def is_shimmed(name: str) -> bool:
    return name in SHIMS


def shim_metadata(name: str) -> dict:
    rec = SHIMS[name]
    return {
        "policy": name,
        "upstream": rec["upstream"],
        "reason": rec["reason"],
        "change": rec["change"],
        "findings_ref": rec["findings_ref"],
        "note": SHIM_NOTE.format(name=name, reason=rec["reason"]),
    }
