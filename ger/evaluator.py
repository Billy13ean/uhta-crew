"""Evaluator, layer 2 — the LLM judge. Temp 0. Diagnosis only, never repair.

Layer 1 (ger/checks.py) has already passed the line through the mechanical
register gate before this module is consulted, so this judge spends its call
on exactly the things a regex cannot decide: mythology and invented canon
(EXCEEDS-SCOPE), contradiction of the verb's own GDD row (CONTRADICTS-CHUNK),
register failures of style rather than vocabulary (WRONG-REGISTER), and the
line that breaks no rule and still says nothing only uhta could say (GENERIC).
The flag vocabulary is A4's Critic vocabulary, unchanged, so a reader of both
pipelines' logs reads one language.

Two structural guarantees, enforced in code:

    1. A FAIL with no quoted chunk, no class, or no reason raises AgentError
       and halts — an uncited rejection cannot be audited (the A4 guard).
    2. This agent CANNOT return a correction. The GER separation of powers is
       that the Evaluator diagnoses and the Refiner repairs; an evaluator that
       repairs is grading its own homework, and the loop would never exercise
       the Refiner it exists to demonstrate. Any `correction` key in the
       response halts the run.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from content.agents import AgentError, parse_json_payload, render_chunks
from crew.llm import LLMCall

from .checks import Finding

PROMPT_VERSION = "ger-evaluator v1 (Assignment 6)"
TEMPERATURE = 0.0

VALID_CLASSES = {"CONTRADICTS-CHUNK", "EXCEEDS-SCOPE", "WRONG-REGISTER", "GENERIC"}


@dataclass
class Judgment:
    verdict: str            # PASS | FAIL
    flag_class: str | None
    quoted_chunk: str
    reason: str

    @property
    def failed(self) -> bool:
        return self.verdict == "FAIL"

    def finding(self) -> Finding:
        return Finding("llm", self.flag_class or "PASS", self.reason,
                       self.quoted_chunk)


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "ger-evaluator.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def run_evaluator(llm, prompts_dir: Path, spec, selection, line: str,
                  register: str, agent_label: str | None = None) -> Judgment:
    agent = agent_label or f"ger-evaluator-{spec.verb}"
    user = (
        _template(prompts_dir)
        .replace("{{VERB}}", spec.verb)
        .replace("{{VERB_LABEL}}", spec.label)
        .replace("{{BRIEF}}", spec.brief)
        .replace("{{REGISTER}}", register)
        .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection))
        .replace("{{LINE}}", line)
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Evaluator in uhta's GER loop: an adversarial "
                "judge that must cite the retrieved chunk a line breaks or "
                "honors. You diagnose; you never repair."),
        user=user, temperature=TEMPERATURE, max_tokens=800,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected a single JSON verdict object, got "
                                f"{type(payload).__name__}")

    if str(payload.get("correction") or "").strip():
        raise AgentError(
            agent,
            "returned a `correction`. The Evaluator diagnoses; the Refiner "
            "repairs. An evaluator that supplies the fix is grading its own "
            "homework, and the GER loop's separation of roles is the point.")

    v = str(payload.get("verdict", "")).strip().upper()
    if v not in ("PASS", "FAIL"):
        raise AgentError(agent, f"verdict={payload.get('verdict')!r}; expected "
                                f"exactly 'PASS' or 'FAIL'")
    cls = payload.get("class")
    cls = str(cls).strip().upper() if cls else None
    quoted = str(payload.get("quoted_chunk") or "").strip()
    reason = str(payload.get("reason") or "").strip()

    if v == "FAIL":
        if cls not in VALID_CLASSES:
            raise AgentError(
                agent,
                f"FAIL with class={cls!r}, not one of {sorted(VALID_CLASSES)}. "
                f"An uncategorised flag cannot be audited.")
        if not quoted:
            raise AgentError(
                agent,
                "FAIL without quoting a chunk. The Evaluator must cite the "
                "text the line breaks, not paraphrase it.")
        if not reason:
            raise AgentError(agent, "FAIL with no reason — the Refiner would "
                                    "have nothing to repair against.")
    else:
        if not quoted:
            raise AgentError(
                agent,
                "PASS without quoting the chunk the line honors. A PASS goes "
                "into a game with no other words in it; it must be checkable.")
    return Judgment(v, cls, quoted, reason)
