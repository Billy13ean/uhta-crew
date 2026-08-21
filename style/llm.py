"""LLM client for the A7 pipeline.

Self-contained on purpose: style/ imports nothing from crew/ or ger/, so it
cannot regress them (mirror of the A6 stance "nothing imports ger/").
Carries forward the crew-021217 lesson: halt after 3 consecutive refusals
with a diagnosis instead of burning the budget.
"""
import os

MODEL = "claude-sonnet-4-6"
_consecutive_refusals = 0


class LLMError(RuntimeError):
    pass


class MockLLM:
    """Fixture-driven client. Scripts are lists of replies consumed in order,
    keyed by (agent, item_id). fixtures.py builds the script."""

    def __init__(self, script: dict):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def complete(self, agent: str, item_id: str, system: str, user: str,
                 temperature: float = 0.0, max_tokens: int = 800) -> str:
        key = (agent, item_id)
        self.calls.append(key)
        if key not in self.script or not self.script[key]:
            raise LLMError(f"mock script exhausted for {key}")
        return self.script[key].pop(0)


class LiveLLM:
    def __init__(self):
        try:
            import anthropic  # the one-dependency budget, still spent here
        except ImportError as e:
            raise LLMError("anthropic package required for live runs") from e
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMError("ANTHROPIC_API_KEY not set (put it in .env)")
        self.client = anthropic.Anthropic(api_key=key)

    def complete(self, agent: str, item_id: str, system: str, user: str,
                 temperature: float = 0.0, max_tokens: int = 800) -> str:
        global _consecutive_refusals
        resp = self.client.messages.create(
            model=MODEL, max_tokens=max_tokens, temperature=temperature,
            system=system, messages=[{"role": "user", "content": user}])
        if getattr(resp, "stop_reason", None) == "refusal":
            _consecutive_refusals += 1
            if _consecutive_refusals >= 3:
                raise LLMError(
                    "3 consecutive refusals — halting. Diagnose the prompt "
                    "(see crew/probe_refusal.py pattern) before re-running.")
            raise LLMError(f"refusal from model ({agent}/{item_id})")
        _consecutive_refusals = 0
        return "".join(b.text for b in resp.content if b.type == "text").strip()
