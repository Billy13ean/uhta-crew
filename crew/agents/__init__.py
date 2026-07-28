"""The five LLM-backed agent roles, plus shared response parsing.

Each agent module exposes one `run_*(...)` function. Every one of them begins by
asserting its upstream artifacts via `Blackboard.require`, which raises
`MissingArtifactError` naming the agent that should have produced them. That is
the mechanism behind the role-clarity claim: the dependencies are enforced by the
code path, not asserted in a README.
"""
from __future__ import annotations

import re


def fenced_blocks(text: str, lang: str | None = None) -> list[str]:
    """Every fenced code block in `text`, optionally filtered by info string."""
    out: list[str] = []
    pattern = re.compile(r"```([A-Za-z0-9_+-]*)[^\S\n]*\n(.*?)```", re.DOTALL)
    for m in pattern.finditer(text):
        info, body = m.group(1).strip().lower(), m.group(2)
        if lang is None or info == lang.lower():
            out.append(body)
    return out


def json_blocks(text: str) -> list[str]:
    """JSON blocks, falling back to unlabelled fences that look like objects."""
    blocks = fenced_blocks(text, "json")
    if blocks:
        return blocks
    return [b for b in fenced_blocks(text) if b.lstrip().startswith("{")]


def markdown_block(text: str, fallback: str | None = None) -> str:
    """The first ```markdown fence, else the first unlabelled fence, else raw."""
    blocks = fenced_blocks(text, "markdown")
    if blocks:
        return blocks[0].strip()
    plain = [b for b in fenced_blocks(text) if not b.lstrip().startswith("{")]
    if plain:
        return plain[0].strip()
    return (fallback if fallback is not None else text).strip()


def strip_fences(text: str) -> str:
    """Remove a single wrapping fence if the whole response is one block."""
    t = text.strip()
    if t.startswith("```"):
        blocks = fenced_blocks(t)
        if len(blocks) == 1:
            return blocks[0].strip()
    return t


class AgentError(RuntimeError):
    """An agent produced an output the pipeline cannot use.

    Distinct from MissingArtifactError: the agent ran, but its output was
    unusable. Both halt the run; both name the agent.
    """

    def __init__(self, agent: str, detail: str):
        self.agent = agent
        super().__init__(f"AGENT FAILURE [{agent}]: {detail}")
