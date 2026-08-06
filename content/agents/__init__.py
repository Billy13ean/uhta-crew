"""The content pipeline's two LLM-backed roles: Writer and Critic.

Both reuse `crew.agents`' response-parsing helpers and `AgentError` verbatim —
the halt discipline is the same one the rules crew uses, for the same reason:
an agent that ran but produced something unusable must stop the run by name
rather than let a downstream stage invent a substitute.
"""
from __future__ import annotations

import json

from crew.agents import AgentError, json_blocks  # noqa: F401  (re-exported)


def parse_json_payload(agent: str, text: str):
    """Parse the single JSON payload an agent was asked for.

    Accepts a ```json fence, an unlabelled fence containing JSON, or a bare
    array/object. Anything else halts with the structural defect quoted, because
    a Writer whose output cannot be parsed has not written anything.
    """
    candidates = json_blocks(text)
    if not candidates:
        stripped = text.strip()
        if stripped.startswith("[") or stripped.startswith("{"):
            candidates = [stripped]
    if not candidates:
        raise AgentError(
            agent,
            "no JSON payload in the response. Expected a single ```json fenced "
            f"block. Got {len(text)} chars beginning: {text.strip()[:200]!r}",
        )
    last_err: Exception | None = None
    for block in candidates:
        try:
            return json.loads(block)
        except json.JSONDecodeError as exc:
            last_err = exc
    raise AgentError(
        agent,
        f"the JSON payload does not parse ({last_err}). First block began: "
        f"{candidates[0].strip()[:200]!r}",
    )


def render_chunks(selection) -> str:
    """The retrieved chunks, as the Writer and Critic both see them.

    Identical text for both roles by construction: the Critic must judge against
    exactly what the Writer was given, or its verdict is about a different
    document.
    """
    parts = []
    for i, r in enumerate(selection.selected, 1):
        c = r.chunk
        parts.append(
            f"--- CHUNK {i} — {c.doc} §{c.section} · \"{c.heading}\" "
            f"(bm25 {r.score:.2f}, ~{c.tokens} tokens) ---\n{c.text}"
        )
    return "\n\n".join(parts) if parts else "(no chunk cleared the retrieval threshold)"
