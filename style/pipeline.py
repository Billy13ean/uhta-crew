"""A7 pipeline orchestration.

Stages (manifest-numbered):
  1 load spec + hash STYLEGUIDE.md
  2 per item: Generator -> [gate -> Evaluator -> (accept | Refiner)]*
    breaker: MAX_REFINEMENTS per item then ESCALATED;
             ESCALATION_LIMIT escalations trip the run (exit 1)
  3 assemble artifacts: STYLE-LOG.md, BEFORE-AFTER.md (the rubric's three
    demos), candidates.md (ends at an unfilled Director selection block),
    manifest.json, RUN-LOG.md
No human input is read anywhere between stage 1 and stage 3 — the loop is
autonomous by construction; the Director gate is after it, as always.
"""
import json, hashlib, time
from pathlib import Path
from . import spec, agents


def _log(run_dir: Path, msg: str, payload: str = ""):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    if payload:
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        line += f" ({len(payload.encode('utf-8'))} B, sha {h})"
    with open(run_dir / "RUN-LOG.md", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(llm, run_dir: Path, mock: bool = False,
        escalation_limit: int = spec.ESCALATION_LIMIT) -> int:
    run_dir.mkdir(parents=True, exist_ok=True)
    banner = ("> **FIXTURE OUTPUT** — mock run; verdicts are scripted, "
              "gate findings are real (the gate is code).\n\n") if mock else ""
    missing = spec.guide_integrity()
    if missing:
        (run_dir / "FAILED.md").write_text(
            f"# FAILED — spec/guide drift\nMissing from STYLEGUIDE.md: {missing}\n",
            encoding="utf-8")
        return 1
    _log(run_dir, f"stage 1: STYLEGUIDE.md sha {spec.guide_sha()}")

    results, escalations = [], 0
    for item in spec.ITEMS:
        history = []
        try:
            line = agents.generate(llm, item)
            _log(run_dir, f"stage 2 gen {item['id']}", line)
            rounds = 0
            while True:
                verdict = agents.evaluate(llm, item, line)
                _log(run_dir, f"stage 2 eval {item['id']} r{rounds} "
                              f"score {verdict['score']}/10", verdict["reason"])
                history.append({"round": rounds, "line": line,
                                "score": verdict["score"],
                                "reason": verdict["reason"],
                                "findings": verdict["findings"],
                                "capped": verdict["capped"]})
                if verdict["score"] >= spec.ACCEPT_SCORE:
                    results.append({"item": item, "status": "ACCEPTED",
                                    "history": history, "final": line})
                    break
                if rounds >= spec.MAX_REFINEMENTS:
                    escalations += 1
                    results.append({"item": item, "status": "ESCALATED",
                                    "history": history, "final": None})
                    _log(run_dir, f"stage 2 ESCALATED {item['id']} "
                                  f"({escalations}/{escalation_limit})")
                    break
                line = agents.refine(llm, item, line, verdict)
                _log(run_dir, f"stage 2 refine {item['id']} r{rounds}", line)
                rounds += 1
        except agents.AgentError as e:
            (run_dir / "FAILED.md").write_text(
                f"# FAILED — AgentError\nItem: {item['id']}\n\n{e}\n",
                encoding="utf-8")
            _log(run_dir, f"HALT AgentError {item['id']}: {e}")
            return 1
        if escalations >= escalation_limit:
            (run_dir / "FAILED.md").write_text(
                f"# FAILED — circuit-breaker\n{escalations} escalations "
                f">= limit {escalation_limit}. The spec or prompts need a "
                "look before re-running.\n", encoding="utf-8")
            _write_artifacts(run_dir, results, banner, mock,
                             status="BREAKER_TRIPPED")
            return 1

    _write_artifacts(run_dir, results, banner, mock, status="COMPLETED")
    return 0


def _write_artifacts(run_dir: Path, results, banner, mock, status):
    # STYLE-LOG.md — every round of every item
    log = [banner + "# STYLE-LOG — every round\n"]
    for r in results:
        log.append(f"\n## {r['item']['id']} — {r['status']}\n")
        for h in r["history"]:
            cap = " (capped by deterministic gate)" if h["capped"] else ""
            fnd = "".join(f"\n  - [{f['rule']}] {f['detail']}"
                          for f in h["findings"]) or "\n  - gate clean"
            log.append(f"**round {h['round']}** — SCORE: {h['score']}/10{cap}\n"
                       f"> {h['line']}\n\nREASON: {h['reason']}\n"
                       f"\nGate findings:{fnd}\n")
    (run_dir / "STYLE-LOG.md").write_text("".join(log), encoding="utf-8")

    # BEFORE-AFTER.md — the three rubric demos, one per violation class
    ba = [banner + "# Before / After — the three violation classes\n"]
    for r in results:
        if r["item"]["kind"] != "sabotage":
            continue
        first, last = r["history"][0], r["history"][-1]
        ba.append(f"\n## Violation class: {r['item']['violation_class']} "
                  f"({r['item']['id']}) — {r['status']}\n\n"
                  f"**BEFORE**\n> {first['line']}\n\n"
                  f"**EVALUATOR** — SCORE: {first['score']}/10\n\n"
                  f"REASON: {first['reason']}\n\n")
        if r["status"] == "ACCEPTED":
            ba.append(f"**AFTER** (round {last['round']}, "
                      f"SCORE: {last['score']}/10)\n> {r['final']}\n")
        else:
            ba.append("**ESCALATED** — the breaker fired; full history in "
                      "STYLE-LOG.md. The pipeline never silently ships.\n")
    (run_dir / "BEFORE-AFTER.md").write_text("".join(ba), encoding="utf-8")

    # candidates.md — accepted era/genuine content, Director gate unfilled
    cand = [banner + "# Style-cleared candidates\n"]
    for r in results:
        if r["item"]["kind"] == "era" and r["status"] == "ACCEPTED":
            cand.append(f"- **{r['item']['id']}**: {r['final']}\n")
    esc = [r["item"]["id"] for r in results if r["status"] == "ESCALATED"]
    if esc:
        cand.append(f"\nESCALATED (no candidate shipped): {', '.join(esc)}\n")
    cand.append("\n## Director selection\n\n"
                "(unfilled — surface ruling and picks belong to the human "
                "gate, outside the loop)\n\n**Signed (Director):** ____\n")
    (run_dir / "candidates.md").write_text("".join(cand), encoding="utf-8")

    if esc:
        (run_dir / "ESCALATED.md").write_text(
            banner + "# Escalated items\n" +
            "".join(f"- {i}\n" for i in esc), encoding="utf-8")

    manifest = {
        "pipeline": "style (A7)", "status": status, "mock": mock,
        "styleguide_sha": spec.guide_sha(),
        "items": {r["item"]["id"]: r["status"] for r in results},
        "artifacts": sorted(p.name for p in run_dir.iterdir()),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
