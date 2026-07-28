"""Playtester — real harness execution, then interpretation. GDD §3.1, §3.5.

This is the agent the whole crew's credibility rests on, so it is built the
opposite way round from the others: **the code runs the simulator and the model
never touches a number.**

  1. Require `attacks.json` (Red-Teamer) and the variants (Mechanic Designer).
  2. For every probe x every ruleset (baseline + each validated variant), spawn
     `crew/probe_runner.py` as a subprocess with `RULES=<abs path to that rules
     json>`, `cwd`/`PYTHONPATH` set to `blackboard/sim` so `import harness`
     resolves. One process per (arm, ruleset): the harness reads RULES at import
     time, so this is the only honest way to measure two rulesets in one run.
  3. Assemble the consolidated board and the raw-facts appendix mechanically from
     the execution log.
  4. Hand the model the facts, tell it in the prompt that they are facts it may
     not alter, and ask for the four interpretive sections only.
  5. Staple: header + machine board + model prose + machine appendix + repro.

The consequence is structural rather than rhetorical: even a model that decides
to hallucinate a win rate cannot get it into the board, because the board is not
generated from the model's output. The worst it can do is contradict the table
printed directly above its own paragraph.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from ..llm import LLMCall
from . import AgentError, markdown_block

PROMPT_VERSION = "playtester v3 (crew port)"
PROBE_TIMEOUT_S = 900

BOARD_COLUMNS = [
    ("wins", "wins"),
    ("losses", "losses"),
    ("none", "none"),
    ("median_terminal_sleep", "med sleep"),
    ("median_final_wf", "med wf"),
    ("median_final_lf", "med lf"),
    ("median_selfburns", "med selfburn"),
    ("median_fronts_spawned", "med fronts"),
    ("median_front_exposure", "med expo"),
]


def _run_probe(probe: dict, rules_path: Path, sim_dir: Path, spec_dir: Path) -> dict:
    spec_path = spec_dir / f"spec-{probe['id']}-{rules_path.stem}.json"
    spec_path.write_text(json.dumps(probe), encoding="utf-8")
    env = dict(os.environ)
    env["RULES"] = str(rules_path.resolve())
    env["PYTHONPATH"] = str(sim_dir.resolve()) + os.pathsep + env.get("PYTHONPATH", "")
    runner = Path(__file__).resolve().parent.parent / "probe_runner.py"
    cmd = [sys.executable, str(runner), str(spec_path)]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(sim_dir), env=env, capture_output=True,
                              text=True, timeout=PROBE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"id": probe["id"], "ruleset": rules_path.name,
                "error": f"probe exceeded {PROBE_TIMEOUT_S}s", "seconds": PROBE_TIMEOUT_S}
    dt = round(time.time() - t0, 2)
    line = next((l for l in reversed(proc.stdout.splitlines()) if l.strip().startswith("{")), "")
    if not line:
        return {"id": probe["id"], "ruleset": rules_path.name, "seconds": dt,
                "error": f"no JSON on stdout (exit {proc.returncode}).\n"
                         f"stderr: {proc.stderr.strip()[-1500:]}"}
    try:
        res = json.loads(line)
    except json.JSONDecodeError as exc:
        return {"id": probe["id"], "ruleset": rules_path.name, "seconds": dt,
                "error": f"unparseable runner output: {exc}"}
    res.setdefault("id", probe["id"])
    res.setdefault("name", probe.get("name", ""))
    res.setdefault("bot", probe.get("bot", ""))
    res["ruleset"] = rules_path.name
    res["seconds"] = dt
    res["cmd"] = f"RULES={rules_path.name} PYTHONPATH=blackboard/sim " \
                 f"python3 crew/probe_runner.py {spec_path.name}"
    res["invariant"] = probe.get("invariant", "")
    res["attack_id"] = probe.get("attack_id", "")
    return res


def _board(results: list[dict]) -> str:
    used = [k for k, _ in BOARD_COLUMNS
            if any(k in r for r in results if "error" not in r)] or ["wins"]
    labels = {k: lbl for k, lbl in BOARD_COLUMNS}
    head = "| probe | attack | bot | n | ruleset | " + " | ".join(
        labels[k] for k in used) + " |"
    sep = "|---" * (5 + len(used)) + "|"
    rows = [head, sep]
    notes: list[str] = []
    for r in results:
        cells = [f"`{r.get('id','?')}`", r.get("attack_id", "") or "—",
                 f"`{r.get('bot','?')}`", str(r.get("n", "—")), f"`{r['ruleset']}`"]
        if "error" in r:
            rows.append("| " + " | ".join(cells) + " | **ERROR** | " +
                        " | ".join(["—"] * (len(used) - 1)) + " |")
            notes.append(f"- **{r.get('id')} @ `{r['ruleset']}` ERRORED** — "
                         f"{r['error'].splitlines()[0][:220]}")
            continue
        for k in used:
            v = r.get(k)
            cells.append("—" if v is None else (f"{v:g}" if isinstance(v, float) else str(v)))
        rows.append("| " + " | ".join(cells) + " |")
        if r.get("seed_errors"):
            notes.append(f"- **{r.get('id')} @ `{r['ruleset']}` is PARTIAL** — "
                         f"{len(r['seed_errors'])} seed(s) raised and were dropped from "
                         f"the aggregate: {r['seed_errors'][0]['error'][:180]}")
    out = "\n".join(rows)
    if notes:
        out += "\n\n**Arm notes (machine-generated):**\n\n" + "\n".join(notes)
    return out


def run_playtester(bb, llm, ctx, valid_variants: list[str]) -> Path:
    agent = "playtester"
    # --- HARD DEPENDENCIES. No attacks.json => no arms => halt. ---
    bb.require(ctx.attacks_json_name, agent, "red-teamer")
    bb.require(ctx.attacks_md_name, agent, "red-teamer")
    for v in valid_variants:
        bb.require(v, agent, "mechanic-designer")
    bb.require(ctx.packet_name, agent, "keeper-b1")

    attacks = json.loads(bb.read(ctx.attacks_json_name, agent, "red-teamer"))
    attacks_md = bb.read(ctx.attacks_md_name, agent, "red-teamer")
    packet = bb.read(ctx.packet_name, agent, "keeper-b1")

    probes = attacks["probes"]
    sim_dir = bb.bb_path("sim")
    spec_dir = bb.path("probe-specs")
    spec_dir.mkdir(parents=True, exist_ok=True)

    rulesets: list[Path] = [bb.bb_path(f"rules/{ctx.baseline_name}")]
    rulesets += [bb.path(v) for v in valid_variants]

    bb.note(agent, f"executing {len(probes)} probe(s) x {len(rulesets)} ruleset(s) "
                   f"= {len(probes)*len(rulesets)} real harness arms")

    results: list[dict] = []
    shims_used: dict[str, dict] = {}
    errors = 0
    t0 = time.time()
    for rp in rulesets:
        for probe in probes:
            res = _run_probe(probe, rp, sim_dir, spec_dir)
            results.append(res)
            if "error" in res:
                errors += 1
                bb.note(agent, f"  {res['id']} @ `{rp.name}` -> **ERROR** "
                               f"{res['error'].splitlines()[0][:160]}")
            else:
                bb.note(agent, f"  {res['id']} @ `{rp.name}` -> n={res.get('n')} "
                               f"w/l/n={res.get('wins')}/{res.get('losses')}/{res.get('none')} "
                               f"({res['seconds']}s)")
            if res.get("shim"):
                shims_used[res["shim"]["policy"]] = res["shim"]
                bb.note(agent, f"    SHIM: {res['shim']['note']}")
    total_s = round(time.time() - t0, 1)

    if errors == len(results):
        raise AgentError(agent, "every probe arm errored; there is nothing to report. "
                                "See execution-log.json.")

    bb.write("execution-log.json", json.dumps(
        {"run_id": ctx.run_id, "baseline": ctx.baseline_name,
         "variants": valid_variants, "seed_policy": ctx.seeds,
         "total_seconds": total_s, "arms": len(results), "errored_arms": errors,
         "results": results}, indent=2) + "\n", agent)

    board = _board(results)
    facts_json = json.dumps(
        [{k: v for k, v in r.items() if k not in ("per_seed_terminal", "cmd")}
         for r in results], indent=2)
    repro = "\n".join(
        f"RULES=$(pwd)/{'blackboard/rules/' + ctx.baseline_name if r['ruleset'] == ctx.baseline_name else 'out/' + ctx.run_id + '/' + r['ruleset']} \\\n"
        f"  PYTHONPATH=$(pwd)/blackboard/sim python3 crew/probe_runner.py "
        f"out/{ctx.run_id}/probe-specs/spec-{r['id']}-{Path(r['ruleset']).stem}.json"
        for r in results[:len(probes)]
    )

    variant_summary = "\n".join(
        f"- `{v}` — hypothesis: "
        + json.loads(bb.path(v).read_text(encoding='utf-8'))
            .get("meta", {}).get("hypothesis", "(none stated)")[:400]
        for v in valid_variants
    ) + f"\n- `{ctx.baseline_name}` — the ratified baseline, measured as the control arm."

    prompt = (ctx.prompts_dir / "playtester.md").read_text(encoding="utf-8")
    system, _, template = prompt.partition("## SYSTEM")
    user = (template
            .replace("{{CONTEXT_PACKET}}", packet)
            .replace("{{VARIANT_SUMMARY}}", variant_summary)
            .replace("{{ATTACKS_JSON}}", json.dumps(attacks, indent=2))
            .replace("{{ATTACKS_MD}}", attacks_md)
            .replace("{{MEASURED_FACTS}}", board + "\n\n```json\n" + facts_json + "\n```")
            .replace("{{REPRO}}", repro))

    out = llm.complete(LLMCall(
        agent=agent,
        system="You are the Playtester for uhta. " + system.strip()[:400],
        user=user, temperature=0.2, max_tokens=8000,
    ))
    prose = markdown_block(out)
    if "## Reading the board" not in prose:
        raise AgentError(agent, "interpretation is missing the '## Reading the board' "
                                "section required by the metrics schema.")
    for banned in ("## Consolidated board", "## Raw measured facts"):
        if banned in prose:
            prose = prose.split(banned)[0].rstrip()

    partials = sum(1 for r in results if r.get("seed_errors") and "error" not in r)
    if shims_used:
        rows = "\n".join(
            f"| `{m['policy']}` | {m['upstream']} | {m['reason']} | {m['change']} | {m['findings_ref']} |"
            for m in shims_used.values())
        shim_block = (
            "## Policy shims in force (machine-generated)\n\n"
            "One or more arms above ran a **crew-side shim** rather than the vendored "
            "policy, because the upstream policy is broken against this baseline. "
            "`blackboard/sim/bots.py` was NOT modified — the crew does not rewrite the "
            "reference suite it reports on. Numbers from a shimmed arm are real, and "
            "they are not measurements of the upstream policy as written.\n\n"
            "| policy | upstream | why it is shimmed | what the shim changes | ref |\n"
            "|---|---|---|---|---|\n" + rows + "\n\n")
    else:
        shim_block = ""

    incomplete = ""
    if errors or partials:
        incomplete = (
            f"> **RUN MARKED INCOMPLETE.** {errors} of {len(results)} arms errored "
            f"outright and {partials} returned partial results (one or more seeds "
            f"raised and were dropped from the aggregate). See the arm notes under "
            f"the board and `execution-log.json`. A board with a hole in it is a "
            f"result, not a rounding error.\n\n")
    fixture_note = (llm.FIXTURE_BANNER + "\n") if getattr(llm, "name", "") == "mock" else ""

    doc = (
        f"# Metrics — {ctx.version_tag} — {ctx.metrics_name}\n\n"
        f"{fixture_note}"
        f"> Run `{ctx.run_id}` | baseline `{ctx.baseline_name}` | variants "
        f"{', '.join('`'+v+'`' for v in valid_variants)} | seeds "
        f"{ctx.seeds} | {len(results)} arms in {total_s}s.\n>\n"
        f"> **Provenance of every number below.** The consolidated board and the raw\n"
        f"> facts appendix were generated by `crew/agents/playtester.py` directly from\n"
        f"> `execution-log.json`, which records real subprocess executions of the\n"
        f"> vendored reference simulator (`blackboard/sim/harness.py`, the file the\n"
        f"> uhta blackboard calls `sim/harness-v3.9.py`), one process per (arm x\n"
        f"> ruleset) with `RULES` bound to that ruleset. No language model produced,\n"
        f"> edited, or approved a number in this document. The prose between the board\n"
        f"> and the appendix is the Playtester agent's interpretation of those numbers\n"
        f"> and nothing else.\n\n"
        f"{incomplete}"
        f"## Consolidated board\n\n*(machine-generated from `execution-log.json`)*\n\n"
        f"{board}\n\n"
        f"{prose}\n\n"
        f"{shim_block}"
        f"## Raw measured facts (machine-generated, authoritative)\n\n"
        f"```json\n{facts_json}\n```\n\n"
        f"## Reproduce\n\n"
        f"From the repo root, with the run directory intact:\n\n"
        f"```bash\n{repro}\n```\n\n"
        f"Each command re-runs one arm. `out/{ctx.run_id}/probe-specs/` holds one spec\n"
        f"file per (probe x ruleset); `execution-log.json` holds the full result set\n"
        f"including per-seed terminals.\n"
    )
    return bb.write(ctx.metrics_name, doc, agent)
