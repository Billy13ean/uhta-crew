#!/usr/bin/env python3
"""uhta rules-pipeline crew — entry point.

Three run modes:

    python3 run_crew.py                 live. Calls the Anthropic API.
                                        Model: $CREW_MODEL (default claude-sonnet-4-5).
                                        Key:   $ANTHROPIC_API_KEY.

    python3 run_crew.py --selftest      NO API CALLS. Exercises the blackboard, the
                                        deterministic validation gate, and a real
                                        execution of the reference simulator on the
                                        ratified baseline. Exits 0 on success.

    python3 run_crew.py --mock-llm      NO API CALLS. Full end-to-end pipeline with a
                                        stub LLM replaying canned artifacts from
                                        tests/fixtures/. Proves the orchestration runs;
                                        produces NO real design work.

    python3 run_crew.py --mock-llm --drop-agent red-teamer
                                        Role-clarity demonstration: removes an agent
                                        from the dispatch sequence. The run is EXPECTED
                                        to halt with a named error and exit 1. A
                                        completed run there would be the failure.

See README.md for what the crew produces and why uhta needs it.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from crew.blackboard import Blackboard, MissingArtifactError  # noqa: E402
from crew.orchestrator import BASELINE, DEFAULT_SEEDS, Orchestrator  # noqa: E402
from crew.validate import Validator, required_paths  # noqa: E402

BANNER = "=" * 74


# --------------------------------------------------------------------------
# --selftest
# --------------------------------------------------------------------------

def selftest() -> int:
    """No API calls. Three things must hold, and each is asserted, not narrated:
    the blackboard round-trips and halts loudly on a missing artifact; the
    validation gate accepts the baseline and rejects real breakage with a named
    reason; the reference simulator actually executes and returns real numbers.
    """
    print(BANNER)
    print("uhta crew — SELFTEST (no API key required, no API calls made)")
    print(BANNER)
    failures: list[str] = []
    run_id = f"selftest-{time.strftime('%Y%m%d-%H%M%S')}"
    bb = Blackboard(run_id, root=ROOT, quiet=True)
    baseline_path = bb.bb_path(f"rules/{BASELINE}")
    sim_dir = bb.bb_path("sim")

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    # ---- 1. blackboard ----
    print("\n[1/3] Blackboard — filesystem as shared memory (GDD §3.3)")
    canon = bb.read_bb("CANON.md", "selftest")
    check("seeded blackboard readable", "CANON.md" in canon or len(canon) > 1000,
          f"CANON.md {len(canon)} chars")
    bb.write("probe-artifact.md", "# round-trip\n", "selftest")
    back = bb.read("probe-artifact.md", "selftest", "selftest")
    check("run-dir write/read round-trip", back.strip() == "# round-trip")
    check("read/write ledger populated", len(bb.ledger) >= 3,
          f"{len(bb.ledger)} entries logged")
    try:
        bb.require("metrics-that-was-never-produced.md", "keeper-b2", "playtester")
        check("missing artifact halts naming its producer", False, "no exception raised")
    except MissingArtifactError as exc:
        named = "playtester" in str(exc) and "keeper-b2" in str(exc)
        check("missing artifact halts naming its producer", named,
              "error names both the missing producer and the blocked consumer")
    for p in (bb.bb_path("sim/harness.py"), bb.bb_path("sim/bots.py"),
              bb.bb_path("gdd/uhta-gdd-v0.9.7-abridged.md"),
              bb.bb_path("CANON-process.md"), baseline_path):
        check(f"seeded file present: {p.name}", p.exists())

    # ---- 2. validation gate ----
    print("\n[2/3] Validation gate — deterministic, before anything is imported (GDD §3.5)")
    v = Validator(baseline_path, sim_dir)
    req = v.required
    check("required key set derived from the baseline (not hand-typed)",
          len(req) > 100 and "world.uhtcearu_events.grief_front.front_strength" in req,
          f"{len(req)} key paths derived from {BASELINE}")
    check("meta.* excluded from the required set",
          not any(p.startswith("meta.") for p in req))

    res = v.validate_file(baseline_path, "BASELINE")
    check("the ratified baseline passes all three checks", res.ok, res.summary())
    if res.smoke:
        print(f"         smoke run: terminal={res.smoke.get('terminal')} "
              f"pop={res.smoke.get('pop')} sleeps={res.smoke.get('sleeps')}")

    base = json.loads(baseline_path.read_text(encoding="utf-8"))
    broken = json.loads(json.dumps(base))
    del broken["world"]["uhtcearu_events"]["grief_front"]["front_strength"]
    del broken["burnout"]["timer_X_sleeps"]
    r2 = v.check_schema(json.dumps(broken), "BROKEN-SCHEMA", "n/a")
    check("a variant missing baseline keys is REJECTED", not r2.ok,
          f"named {r2.error.count(chr(10))-3 if r2.error else 0} missing path(s)")
    check("rejection names the exact missing paths",
          "world.uhtcearu_events.grief_front.front_strength" in r2.error
          and "burnout.timer_X_sleeps" in r2.error)

    r3 = v.check_schema("{ this is not json", "BROKEN-PARSE", "n/a")
    check("malformed JSON is REJECTED at parse", not r3.ok, r3.error.split(":")[0])

    # Schema-complete but semantically broken: every required key path is present,
    # so checks (a) and (b) pass. The harness reads this one on every sleep, so
    # check (c) is the only thing standing between it and the Red-Teamer.
    unloadable = json.loads(json.dumps(base))
    unloadable["world"]["generation_ticks_per_sleep"] = "three"
    tmp = bb.path("selftest-unloadable.json")
    r4 = v.validate_text(json.dumps(unloadable), "BROKEN-LOAD", tmp)
    check("a schema-complete but unloadable ruleset is REJECTED by the harness check",
          not r4.ok, (r4.error.splitlines()[0] if r4.error else ""))
    tmp.unlink(missing_ok=True)

    # ---- 3. real harness execution ----
    print("\n[3/3] Reference simulator — REAL execution on the ratified baseline")
    specs = [
        {"id": "S1", "name": "do-nothing softlock control", "bot": "bot_do_nothing",
         "seeds": DEFAULT_SEEDS, "max_sleeps": 40, "player_pole": 1,
         "invariant": "apathy loss in every seed"},
        {"id": "S2", "name": "fate-aware hope campaign", "bot": "run_campaign_v3",
         "seeds": DEFAULT_SEEDS, "max_sleeps": 32, "player_pole": 1,
         "invariant": "the campaign line wins in the majority of seeds"},
        {"id": "S3", "name": "overlap self-burn control", "bot": "run_selfburn",
         "seeds": DEFAULT_SEEDS[:4], "max_sleeps": 8, "player_pole": 1,
         "invariant": "selfburns stay 0"},
    ]
    spec_dir = bb.path("probe-specs")
    spec_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["RULES"] = str(baseline_path.resolve())
    env["PYTHONPATH"] = str(sim_dir.resolve()) + os.pathsep + env.get("PYTHONPATH", "")
    runner = ROOT / "crew" / "probe_runner.py"
    results = []
    for spec in specs:
        sp = spec_dir / f"spec-{spec['id']}.json"
        sp.write_text(json.dumps(spec), encoding="utf-8")
        t0 = time.time()
        proc = subprocess.run([sys.executable, str(runner), str(sp)], cwd=str(sim_dir),
                              env=env, capture_output=True, text=True, timeout=900)
        dt = round(time.time() - t0, 2)
        line = next((l for l in reversed(proc.stdout.splitlines())
                     if l.strip().startswith("{")), "")
        if not line:
            check(f"probe {spec['id']} executed", False, proc.stderr.strip()[-300:])
            continue
        r = json.loads(line)
        if "error" in r:
            check(f"probe {spec['id']} executed", False, r["error"][:200])
            continue
        r["seconds"] = dt
        results.append(r)
        print(f"  [PASS] probe {spec['id']} ({spec['bot']}) executed in {dt}s "
              f"over {r['n']} seeds")
        print(f"         wins={r['wins']} losses={r['losses']} none={r['none']} "
              f"med_terminal_sleep={r.get('median_terminal_sleep')} "
              f"med_final_wf={r.get('median_final_wf')} "
              f"med_final_lf={r.get('median_final_lf')} "
              f"med_selfburns={r.get('median_selfburns')} "
              f"med_fronts={r.get('median_fronts_spawned')}")

    check("all three harness probes returned real stats", len(results) == 3)
    s1 = next((r for r in results if r["id"] == "S1"), None)
    if s1:
        check("do-nothing reaches the apathy loss in every seed (G8/A11)",
              s1["losses"] == s1["n"], f"{s1['losses']}/{s1['n']} losses")
    s3 = next((r for r in results if r["id"] == "S3"), None)
    if s3:
        check("self-burn control stays at 0 self-burns",
              s3.get("max_selfburns", 0) == 0, f"max={s3.get('max_selfburns')}")
    check("numbers are non-trivial (a stub would return zeros)",
          bool(s1 and s1.get("median_pop", 0) > 50),
          f"median population {s1.get('median_pop') if s1 else 'n/a'} NPCs")

    bb.write("selftest-results.json", json.dumps(
        {"run_id": run_id, "baseline": BASELINE, "required_key_paths": len(req),
         "harness_results": results, "failures": failures}, indent=2) + "\n", "selftest")

    print("\n" + BANNER)
    if failures:
        print(f"SELFTEST FAILED — {len(failures)} check(s): " + "; ".join(failures))
        print(BANNER)
        return 1
    print(f"SELFTEST PASSED — blackboard, validation gate, and {len(results)} real "
          f"harness probes.")
    print(f"Artifacts: out/{run_id}/  (RUN-LOG.md, selftest-results.json)")
    print(BANNER)
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="uhta rules-pipeline crew (Orchestrator, Keeper x2, "
                    "Mechanic Designer, Red-Teamer, Playtester).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--selftest", action="store_true",
                   help="no API calls; exercise blackboard, validation gate, real harness")
    g.add_argument("--mock-llm", action="store_true",
                   help="no API calls; full pipeline with canned fixtures (NOT design work)")
    ap.add_argument("--goal", default=None, help="Director goal for this run")
    ap.add_argument("--questions", default=None, help="the run's question set")
    ap.add_argument("--seeds", type=int, default=len(DEFAULT_SEEDS),
                    help=f"how many fixed seeds per arm (default {len(DEFAULT_SEEDS)}; "
                         f"the uhta project standard is 20)")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--version-tag", default="v3.9.2",
                    help="version tag for produced artifacts (default v3.9.2)")
    ap.add_argument("--drop-agent", default=None,
                    choices=list(Orchestrator.DROPPABLE),
                    help="REMOVE an agent from the dispatch sequence. The run is "
                         "expected to HALT with a named error at the first agent "
                         "that needs the missing artifact. This is the role-clarity "
                         "demonstration: 'no agent could be removed without breaking "
                         "the pipeline', shown rather than asserted. Exit code 1 on "
                         "the halt is the PASSING result.")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    mode = "mock" if args.mock_llm else "live"
    seeds = list(range(max(1, args.seeds)))

    print(BANNER)
    print(f"uhta crew — {'MOCK-LLM' if mode == 'mock' else 'LIVE'} run")
    if mode == "mock":
        print("MOCK MODE: no API calls. Agent responses are canned fixtures from")
        print("tests/fixtures/. This proves the pipeline executes; it produces NO")
        print("real design work. Harness numbers are still real.")
    print(BANNER)

    from crew.llm import LLMError, build_llm
    try:
        llm = build_llm(mode, ROOT / "tests" / "fixtures")
    except LLMError as exc:
        print(f"\nSTARTUP FAILED: {exc}\n")
        return 1

    if args.drop_agent:
        print(f"\n--drop-agent {args.drop_agent}: this agent will NOT be dispatched.")
        print("EXPECTED RESULT: the pipeline halts with a clear error naming it, and")
        print("exits 1. A completed run here would be the failure.\n")

    orch = Orchestrator(llm=llm, mode=mode, run_id=args.run_id, goal=args.goal,
                        questions=args.questions, seeds=seeds, root=ROOT,
                        version_tag=args.version_tag, drop_agent=args.drop_agent)
    llm.logger = orch.bb.log
    rc = orch.run()
    print(f"\nRun directory: out/{orch.run_id}/")
    for p in sorted(orch.bb.run_dir.iterdir()):
        if p.is_file():
            print(f"  {p.name}  ({p.stat().st_size} B)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
