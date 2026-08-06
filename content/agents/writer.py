"""Writer — generates candidate lines for one beat from its retrieved chunks.

Temperature 0.9, deliberately. The Keeper runs at 0 because a paraphrase of
canon is a failure; the Writer runs hot because N candidates that differ only by
comma placement are not a candidate set, and because the Critic downstream is
what makes a wide spread safe to ask for.
"""
from __future__ import annotations

from pathlib import Path

from crew.llm import LLMCall

from . import AgentError, parse_json_payload, render_chunks

PROMPT_VERSION = "writer v1 (content pipeline)"
TEMPERATURE = 0.9


def _load_prompt(prompts_dir: Path) -> tuple[str, str]:
    text = Path(prompts_dir / "writer.md").read_text(encoding="utf-8")
    system, _, template = text.partition("## SYSTEM")
    return system, template


def run_writer(llm, prompts_dir: Path, beat, selection, content_type: dict,
               n_candidates: int, agent_label: str | None = None) -> list[str]:
    agent = agent_label or f"writer-{beat.id}"
    if not selection.selected:
        raise AgentError(
            agent,
            f"beat '{beat.id}' retrieved no chunks above the score threshold. "
            f"Generating from an empty corpus cut is exactly the placeholder-lore "
            f"failure this pipeline exists to prevent.",
        )
    _, template = _load_prompt(prompts_dir)
    user = (
        template
        .replace("{{CONTENT_TYPE}}", content_type["title"])
        .replace("{{BEAT_LABEL}}", beat.label)
        .replace("{{BEAT_BRIEF}}", beat.brief)
        .replace("{{REGISTER}}", content_type["register"])
        .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection))
        .replace("{{N}}", str(n_candidates))
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Writer for uhta, a wordless god-game about emotional "
                "contagion. You write only from the GDD chunks you are given."),
        user=user, temperature=TEMPERATURE, max_tokens=2000,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, list):
        raise AgentError(agent, f"expected a JSON array of strings, got {type(payload).__name__}")
    lines = [str(x).strip() for x in payload if str(x).strip()]
    if not lines:
        raise AgentError(agent, "returned an empty candidate list")
    return lines
