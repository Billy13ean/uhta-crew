"""Assignment 4 — the dynamic content pipeline for uhta.

Separate from `crew/` (the rules pipeline): different agents, different
artifacts, its own entry point in `run_content.py`. It reuses `crew/blackboard.py`,
`crew/llm.py` and `crew.agents.AgentError` verbatim. Nothing in `crew/` imports
this package — the dependency runs one way only.
"""
