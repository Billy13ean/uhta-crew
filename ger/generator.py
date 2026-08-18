"""Generator — one retrieval-grounded narration line per verb. Temp 0.9.

Hot for the same reason A4's Writer was hot: the Evaluator downstream is what
makes variance safe to ask for. The difference from A4 is the unit of work —
the Writer produced N candidates for a human curator; the Generator produces
ONE line per verb for a machine judge, because the GER loop's error-correction
is refinement, not selection.
"""
from __future__ import annotations

from pathlib import Path

from content.agents import AgentError, parse_json_payload, render_chunks
from crew.llm import LLMCall

PROMPT_VERSION = "ger-generator v1 (Assignment 6)"
TEMPERATURE = 0.9


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "ger-generator.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def run_generator(llm, prompts_dir: Path, spec, selection, register: str,
                  agent_label: str | None = None) -> str:
    agent = agent_label or f"ger-generator-{spec.verb}"
    if not selection.selected:
        raise AgentError(
            agent,
            f"verb '{spec.verb}' retrieved no chunks above the score threshold. "
            f"Generating from an empty corpus cut is the placeholder-lore "
            f"failure this crew's pipelines exist to prevent.")
    user = (
        _template(prompts_dir)
        .replace("{{VERB}}", spec.verb)
        .replace("{{VERB_LABEL}}", spec.label)
        .replace("{{BRIEF}}", spec.brief)
        .replace("{{REGISTER}}", register)
        .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection))
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You write the words for uhta, a wordless browser god-game "
                "about emotional contagion. You write only from the GDD chunks "
                "you are given."),
        user=user, temperature=TEMPERATURE, max_tokens=400,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict) or not str(payload.get("line", "")).strip():
        raise AgentError(
            agent,
            f'expected {{"line": "..."}} with a non-empty line, got: '
            f"{str(payload)[:200]!r}")
    return str(payload["line"]).strip()
