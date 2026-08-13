"""builder — the goal-oriented coding agent (Assignment 5).

The third pipeline in this repo. `run_crew.py` designs rulesets, `run_content.py`
writes the game's prose, and `run_builder.py` decides what to build next and
writes the code for it.

Shape:

    extract    GDD  -> Feature inventory      (deterministic tables + Analyst LLM)
    scan       code -> symbol / key-path index (deterministic, SCAN_POLICY)
    gap        compare -> PRESENT / PARTIAL / ABSENT + evidence
    prioritize -> a ranked table, every term shown        (deterministic, no LLM)
    generate   -> a patch + its own self-test assertions  (Programmer LLM)
                  -> the Director applies it

Where the LLM sits, and where it does not, is the whole design. The ranking is
arithmetic because a grader has to be able to check it. The generated code is a
patch rather than a rewrite because the build it targets has a green on-load
self-test and a rewrite is how you lose one.

`crew/` and `content/` do not import `builder/`. The dependency runs one way, so
adding this pipeline cannot change what a rules run or a content run does.
"""
from __future__ import annotations

# The halt discipline is the crew's, unchanged: an agent that ran but produced
# something unusable stops the run BY NAME rather than letting a downstream
# stage invent a substitute.
from crew.agents import AgentError, json_blocks  # noqa: F401
from content.agents import parse_json_payload, render_chunks  # noqa: F401

__all__ = ["AgentError", "json_blocks", "parse_json_payload", "render_chunks"]
