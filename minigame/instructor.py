"""The Instructor — the Writer's seat (GDD §5), applied to encounters.

Added after the first Director playtest of a built encounter, whose finding
was blunt: a mechanically-correct mini-game with no words and no entrance is
invisible. The GDD's own answer is the narrated teaching opening — "a
narrator names each verb the first time you use it" — and the first-contact
encounter arms on sleep 0, INSIDE the narrated window, so a single first-use
line is canon-legal. (An encounter re-triggering after the first Sleep gets
no words: past that point the presentation spec has to carry everything,
which is the Presenter's job.)

The line is held to the SAME register rule as pipeline #1's narration —
ger.checks.run_register_checks, reused directly (the verb-independent
checks: no interface vocabulary, short, declarative, no numbers). One
generate, one repair against findings, then a halt: an instruction line that
cannot clear the gate twice is a prompt problem, not a retry problem.
"""
from __future__ import annotations

import json
from pathlib import Path

from content.agents import AgentError, parse_json_payload
from crew.llm import LLMCall
from ger.checks import run_register_checks
from ger.spec import REGISTER

INSTRUCTOR_PV = "minigame-instructor v1 (Assignment 6 #2, build v2)"


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "minigame-instructor.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def _call(llm, prompts_dir: Path, design: dict, findings_text: str,
          agent: str) -> str:
    user = (_template(prompts_dir)
            .replace("{{DESIGN}}", json.dumps(design, ensure_ascii=False,
                                              indent=2))
            .replace("{{REGISTER}}", REGISTER)
            .replace("{{REPAIR}}", findings_text or "(first attempt)"))
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Writer for uhta, seated for encounters: you "
                "write the single line the narrator speaks the first time "
                "this encounter begins, during the game's one narrated "
                "cycle. Short, declarative, second person; the register "
                "gate that judges the game's other narration judges you."),
        user=user, temperature=0.7, max_tokens=300,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict) or not str(payload.get(
            "first_use_line", "")).strip():
        raise AgentError(agent, f'expected {{"first_use_line": "..."}}, '
                                f"got: {str(payload)[:200]!r}")
    return str(payload["first_use_line"]).strip()


def run_instructor(llm, prompts_dir: Path, design: dict,
                   agent_label: str = "mg-instructor") -> dict:
    """Returns {"first_use_line": line, "repair_rounds": n}. The line has
    passed the register gate; a second failure halts."""
    line = _call(llm, prompts_dir, design, "", agent_label)
    findings = run_register_checks(line, verb=None)
    rounds = 0
    if findings:
        rounds = 1
        text = ("### REPAIR — your previous line failed the register gate; "
                "fix exactly this:\n"
                + "\n".join(f"- {f.render()}" for f in findings)
                + f"\n\nThe failed line was: {line!r}")
        line = _call(llm, prompts_dir, design, text, agent_label)
        findings = run_register_checks(line, verb=None)
        if findings:
            raise AgentError(
                agent_label,
                "the first-use line failed the register gate twice: "
                + "; ".join(f.check for f in findings)
                + f". Last line: {line!r}")
    return {"first_use_line": line, "repair_rounds": rounds}
