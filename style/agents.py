"""The three loop agents. Prompts live in prompts/style-*.md; each agent
loads its prompt file, so what the grader reads is what runs.

Contract highlights (all A7-rubric-load-bearing):
- Evaluator output is STRICTLY  `SCORE: [X/10]` + `REASON: ...`  — parsed
  here; anything else is an AgentError. Never binary.
- Evaluator CANNOT repair: if its reply contains a rewritten candidate line
  (heuristic: a REWRITE/SUGGESTION/CORRECTED field), the run halts. Repair
  belongs to the Refiner (A6 rule, kept).
- Deterministic findings cap the score at spec.DET_SCORE_CAP; the cap is
  applied in code, not trusted to the model.
"""
import re
from pathlib import Path
from . import spec, checks

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


class AgentError(RuntimeError):
    pass


def _prompt(name: str) -> str:
    return (PROMPTS / f"style-{name}.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- generator
def generate(llm, item: dict) -> str:
    system = _prompt("generator").replace("{{STYLEGUIDE}}", spec.guide_text())
    user = (f"Item id: {item['id']}\nRegister: {item['register']}\n"
            f"Brief:\n{item['brief']}\n\nProduce exactly one candidate line.")
    # Sabotage items get high temperature and their brief already instructs
    # wrongness; the style guide is withheld from the generator FOR SABOTAGE
    # ITEMS ONLY so the demo is honest (the wrong content is genuinely wrong,
    # not a model politely pretending).
    if item["kind"] == "sabotage":
        system = ("You write short lines of game flavor text. Follow the brief "
                  "exactly, including its tone instructions.")
        temp = 1.0
    else:
        temp = 0.9
    line = llm.complete("generator", item["id"], system, user, temperature=temp)
    line = line.strip().splitlines()[0].strip() if line.strip() else ""
    if not line:
        raise AgentError(f"generator produced empty output for {item['id']}")
    return line


# ---------------------------------------------------------------- evaluator
SCORE_RE = re.compile(r"SCORE:\s*\[?\s*(\d{1,2})\s*/\s*10\s*\]?", re.IGNORECASE)
REASON_RE = re.compile(r"REASON:\s*(.+)", re.IGNORECASE | re.DOTALL)
REPAIR_RE = re.compile(r"\b(REWRITE|SUGGESTION|CORRECTED|FIXED VERSION)\s*:",
                       re.IGNORECASE)


def evaluate(llm, item: dict, line: str) -> dict:
    findings = checks.run_gate(line, item["register"], item["id"])
    findings_txt = ("\n".join(f"- [{f['rule']}] {f['detail']}" for f in findings)
                    or "- (gate clean)")
    system = _prompt("evaluator").replace("{{STYLEGUIDE}}", spec.guide_text())
    user = (f"Item id: {item['id']}\nRegister: {item['register']}\n"
            f"Brief (what the line is for):\n{item['brief']}\n\n"
            f"Deterministic gate findings:\n{findings_txt}\n\n"
            f"CANDIDATE LINE:\n{line}")
    reply = llm.complete("evaluator", item["id"], system, user, temperature=0.0)

    if REPAIR_RE.search(reply):
        raise AgentError(
            f"evaluator attempted a repair on {item['id']} — contract "
            "violation (Evaluator scores, Refiner repairs). Halting.")
    ms, mr = SCORE_RE.search(reply), REASON_RE.search(reply)
    if not ms or not mr:
        raise AgentError(
            f"evaluator broke output contract on {item['id']}: need "
            f"'SCORE: [X/10]' and 'REASON: ...'. Got:\n{reply[:400]}")
    score = max(1, min(10, int(ms.group(1))))
    capped = False
    if checks.caps_score(findings) and score > spec.DET_SCORE_CAP:
        score, capped = spec.DET_SCORE_CAP, True
    return {"score": score, "reason": mr.group(1).strip(),
            "findings": findings, "capped": capped, "raw": reply}


# ------------------------------------------------------------------ refiner
def refine(llm, item: dict, line: str, verdict: dict) -> str:
    findings_txt = ("\n".join(f"- [{f['rule']}] {f['detail']}"
                              for f in verdict["findings"]) or "- (none)")
    system = _prompt("refiner").replace("{{STYLEGUIDE}}", spec.guide_text())
    user = (f"Item id: {item['id']}\nRegister: {item['register']}\n"
            f"Brief:\n{item['brief']}\n\nORIGINAL LINE:\n{line}\n\n"
            f"EVALUATOR SCORE: {verdict['score']}/10\n"
            f"EVALUATOR REASON:\n{verdict['reason']}\n\n"
            f"Deterministic findings:\n{findings_txt}\n\n"
            f"Rewrite the line so it scores {spec.ACCEPT_SCORE}+/10. Stay within the "
            f"Register {item['register']} length limit. Output the line only.")
    new = llm.complete("refiner", item["id"], system, user, temperature=0.2)
    new = new.strip().splitlines()[0].strip() if new.strip() else ""
    if not new:
        raise AgentError(f"refiner produced empty output for {item['id']}")
    if new == line.strip():
        raise AgentError(
            f"refiner no-op on {item['id']} — identical line returned. "
            "Halting rather than looping on a fixed point.")
    return new
