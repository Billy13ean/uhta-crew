"""uhta rules-pipeline crew — raw Python orchestration.

No CrewAI, no LangChain. The only third-party dependency is `anthropic`, and the
two no-key run modes (`--selftest`, `--mock-llm`) do not need even that.

Modules
-------
blackboard   the filesystem as shared memory; read/write ledger; halt errors
validate     the deterministic gate between the Designer and everything downstream
llm          Anthropic client with retries, plus the fixture-replay stub
probe_runner one process per (arm x ruleset), executing the real reference sim
orchestrator dispatch, artifact verification, manifest, run log
agents/      the five LLM-backed roles
"""

__version__ = "1.0.0"
