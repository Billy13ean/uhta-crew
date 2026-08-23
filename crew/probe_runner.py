#!/usr/bin/env python3
"""Executes ONE probe arm against the real reference simulator and prints JSON.

This file is deliberately a separate process. The Playtester agent spawns it once
per (arm x ruleset) with:

    RULES=<abs path to the rules json>
    PYTHONPATH=<blackboard/sim>          # so `import harness` / `import bots` resolve
    cwd=<blackboard/sim>

because the harness reads `RULES` at import time and `bots.py` does
`import harness as H`. One ruleset per process is the only way to run several
rulesets in one crew run without module-reload games.

It knows a fixed whitelist of bot policies from `bots.py`. A probe naming a
policy outside the whitelist is rejected loudly rather than silently skipped —
the Red-Teamer does not get to invent bots, and the Playtester does not get to
quietly drop an arm and still call the board complete.

Usage:  probe_runner.py <spec.json>
Spec:   {"id","name","bot","seeds":[...],"max_sleeps":int,"poles":[...],
         "player_pole":1,"args":{...}}
"""
from __future__ import annotations

import json
import statistics
import sys
import traceback
from pathlib import Path


def _med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def main() -> int:
    spec = json.loads(open(sys.argv[1], encoding="utf-8").read())
    import harness as H
    import bots as B

    # Crew-side shims for policies that are broken against the current baseline.
    # `bots.py` is never modified; see crew/policy_shims.py and FINDINGS.md.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from crew import policy_shims

    bot = spec.get("bot")
    seeds = [int(s) for s in spec.get("seeds") or [0]]
    max_sleeps = int(spec.get("max_sleeps") or 25)
    poles = tuple(spec.get("poles") or (-1, -1, 1))
    player_pole = int(spec.get("player_pole") or 1)
    args = spec.get("args") or {}

    # --- the whitelist. Keys are what a probe may name in attacks.json. ---
    simple = {
        "bot_do_nothing": B.bot_do_nothing,
        "bot_wait_once": B.bot_wait_once,
        "bot_walk_one": B.bot_walk_one,
        "bot_throughput": B.bot_throughput,
    }
    composite = {
        # run_tyrant is routed to the crew shim, NOT to bots.py -- the upstream
        # version raises on every seed under the genesis start. Stamped on the
        # result below so a shimmed number is never read as an unshimmed one.
        "run_tyrant": lambda s: policy_shims.run_tyrant(s),
        "run_campaign_v3": lambda s: B.run_campaign_v3(s),
        # schema 3.10: same policy, full stat dict (see crew/policy_shims.py)
        "run_campaign_v3_audit": lambda s: policy_shims.run_campaign_v3_audit(s),
        "run_selfburn": lambda s: B.run_selfburn(s),
        "run_siege": lambda s: B.run_siege(
            s, use_roar=bool(args.get("use_roar", False)),
            roads=bool(args.get("roads", False))),
        "make_flamer": lambda s: H.run(
            B.make_flamer(int(args.get("tribe", 0)), int(args.get("pole", player_pole))),
            s, poles=poles, max_sleeps=max_sleeps, player_pole=player_pole),
    }

    if bot not in simple and bot not in composite:
        print(json.dumps({
            "id": spec.get("id"), "name": spec.get("name"), "bot": bot,
            "error": f"unknown bot policy '{bot}'. Allowed: "
                     + ", ".join(sorted(list(simple) + list(composite)))
        }))
        return 2

    # Per-seed isolation. A bot policy can raise against a ruleset it was not
    # written for -- `run_tyrant` hard-codes tribe index 2, which does not exist
    # under the genesis start's two founding tribes -- and an arm that dies is a
    # RESULT the Playtester must report, not a traceback that takes the crew
    # down. The rubric line is "coordinate without crashing".
    runs, seed_errors = [], []
    for s in seeds:
        try:
            if bot in simple:
                runs.append(H.run(simple[bot], s, poles=poles,
                                  max_sleeps=max_sleeps, player_pole=player_pole))
            else:
                runs.append(composite[bot](s))
        except Exception as exc:  # noqa: BLE001
            seed_errors.append({"seed": s, "error": f"{type(exc).__name__}: {exc}"})
    if not runs:
        print(json.dumps({
            "id": spec.get("id"), "name": spec.get("name"), "bot": bot,
            "seeds": seeds, "n": 0, "seed_errors": seed_errors,
            "error": f"every seed raised. First: {seed_errors[0]['error'] if seed_errors else 'unknown'}"
        }))
        return 0
    seeds = [s for s in seeds if s not in {e["seed"] for e in seed_errors}]

    # --- normalise across the two return shapes bots.py uses ---
    terminals = [r.get("terminal") for r in runs]
    wins = sum(1 for t in terminals if t and t[0] == "win")
    losses = sum(1 for t in terminals if t and t[0] == "loss")
    none = len(runs) - wins - losses
    term_sleeps = [t[1] for t in terminals if t]

    out = {
        "id": spec.get("id"),
        "name": spec.get("name"),
        "bot": bot,
        "seeds": seeds,
        "n": len(runs),
        "max_sleeps": max_sleeps,
        "player_pole": player_pole,
        "seed_errors": seed_errors,
        "shim": policy_shims.shim_metadata(bot) if policy_shims.is_shimmed(bot) else None,
        "wins": wins, "losses": losses, "none": none,
        "median_terminal_sleep": _med(term_sleeps),
        "terminal_sleep_range": [min(term_sleeps), max(term_sleeps)] if term_sleeps else None,
    }
    for key in ("final_wf", "final_lf", "selfburns", "pop", "fronts_spawned",
                "front_exposure", "sleeps", "max_wf", "stamina", "heads",
                "per_head", "flip_sleep", "fight_deaths",
                # schema 3.10 (Run 24): temple / armed-terminal audit stats, emitted by
                # H.run() only when world.temple.enabled — absent keys are simply skipped
                "win_armed_sleep", "armed_to_terminal_sleeps", "pilgrim_tiles",
                "well_exposure"):
        vals = [r[key] for r in runs if key in r and isinstance(r[key], (int, float))]
        if vals:
            out[f"median_{key}"] = round(_med(vals), 4)
            out[f"max_{key}"] = round(max(vals), 4)
            out[f"min_{key}"] = round(min(vals), 4)
    # schema 3.10: how many runs ARMED the win, and how many were lost while armed
    armed = [r for r in runs if r.get("win_armed_sleep") is not None]
    if any("win_armed_sleep" in r for r in runs):
        out["armed_runs"] = len(armed)
        out["lost_while_armed"] = sum(1 for r in runs if r.get("lost_while_armed"))
        travel = [t for r in runs for t in (r.get("front_travel_sleeps") or [])]
        if travel:
            out["median_front_travel_sleeps"] = _med(travel)
    fates = [len(r.get("fate_events", [])) for r in runs if "fate_events" in r]
    if fates:
        out["median_fate_events"] = _med(fates)
    out["per_seed_terminal"] = [
        [s, (t[0] if t else None), (t[1] if t else None)]
        for s, t in zip(seeds, terminals)
    ]
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 — a probe crash must be data, not a traceback
        print(json.dumps({"error": traceback.format_exc()[-3000:]}))
        sys.exit(3)
