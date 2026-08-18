"""Refiner — rewrites a failing line to address the Evaluator's findings.

Temp 0.2: low, because this is repair against a written diagnosis, not fresh
invention — but not 0, because a refinement loop at temperature 0 that failed
once can fail identically forever, and the circuit breaker would be tripping
on determinism rather than on difficulty.

One structural guarantee: a refinement that returns the input line unchanged
raises AgentError and halts. A no-op repair would send the identical line
back to the identical judge, and the loop would burn its remaining rounds
learning nothing — the breaker exists for lines that CANNOT converge, not for
an agent that declined to try.
"""
from __future__ import annotations

import re
from pathlib import Path

from content.agents import AgentError, parse_json_payload, render_chunks
from crew.llm import LLMCall

from .checks import Finding

PROMPT_VERSION = "ger-refiner v1 (Assignment 6)"
TEMPERATURE = 0.2


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "ger-refiner.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def _norm(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def render_findings(findings: list[Finding]) -> str:
    return "\n".join(f"- {f.render()}" for f in findings) or "- (none)"


def run_refiner(llm, prompts_dir: Path, spec, selection, line: str,
                findings: list[Finding], register: str,
                agent_label: str | None = None) -> str:
    agent = agent_label or f"ger-refiner-{spec.verb}"
    if not findings:
        raise AgentError(agent, "dispatched with no findings — a Refiner with "
                                "nothing to repair should never have been called. "
                                "This is a pipeline sequencing bug, not a content "
                                "failure.")
    user = (
        _template(prompts_dir)
        .replace("{{VERB}}", spec.verb)
        .replace("{{VERB_LABEL}}", spec.label)
        .replace("{{BRIEF}}", spec.brief)
        .replace("{{REGISTER}}", register)
        .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection))
        .replace("{{LINE}}", line)
        .replace("{{FINDINGS}}", render_findings(findings))
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Refiner in uhta's GER loop. You repair exactly "
                "the defects the Evaluator found, changing as little else as "
                "possible, writing only from the GDD chunks you are given."),
        user=user, temperature=TEMPERATURE, max_tokens=400,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict) or not str(payload.get("line", "")).strip():
        raise AgentError(agent, f'expected {{"line": "..."}} with a non-empty '
                                f"line, got: {str(payload)[:200]!r}")
    refined = str(payload["line"]).strip()
    if _norm(refined) == _norm(line):
        raise AgentError(
            agent,
            f"returned the line unchanged: {line!r}. A no-op refinement sends "
            f"the identical line back to the identical judge — the remaining "
            f"rounds would be spent learning nothing.")
    return refined
