"""LLM access for the crew. Raw Anthropic SDK — no CrewAI, no LangChain.

Three modes, chosen by run_crew.py:

  LiveLLM   real API calls. Model from env CREW_MODEL (default claude-sonnet-4-5),
            key from ANTHROPIC_API_KEY. 3 attempts, exponential backoff, on
            transient errors only.
  MockLLM   returns canned artifacts from tests/fixtures/. NO API CALLS, NO
            DESIGN WORK. Exists to prove the orchestration executes end to end
            without a key. Every artifact it produces is stamped as a fixture.
  (selftest bypasses the LLM entirely — it never constructs one.)

Determinism policy (GDD §4.1, "nothing auto-promotes"): temperature 0 for the
Keeper and for any output that is checked by a machine downstream (rules JSON,
attacks.json). The Designer's rationale prose and the Playtester's interpretation
run at 0.2 — still low, but a variant sweep whose three hypotheses are token-
identical is not a sweep.
"""
from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-5"
MAX_ATTEMPTS = 6
BASE_BACKOFF_S = 2.0


class LLMError(RuntimeError):
    pass

class RefusalError(LLMError):
    """stop_reason='refusal' — a safety-classifier decline. Empirically
    stochastic on this crew's benign game-design content (see FINDINGS.md),
    so it is treated as retryable rather than terminal."""
    pass

@dataclass
class LLMCall:
    agent: str
    system: str
    user: str
    temperature: float = 0.0
    max_tokens: int = 8000
    stop_hint: str = ""


class BaseLLM:
    name = "base"
    model = "none"

    def complete(self, call: LLMCall) -> str:
        raise NotImplementedError


class LiveLLM(BaseLLM):
    name = "live"

    def __init__(self, model: str | None = None, logger=None):
        try:
            import anthropic  # noqa: F401
        except ImportError as exc:
            raise LLMError(
                "The `anthropic` package is not installed. Install it "
                "(`pip install -r requirements.txt`) or run with --selftest / "
                "--mock-llm, which make no API calls."
            ) from exc
        import anthropic

        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise LLMError(
                "ANTHROPIC_API_KEY is not set. Set it in .env (see .env.example), "
                "or run with --selftest / --mock-llm, which make no API calls."
            )
        self.model = model or os.environ.get("CREW_MODEL") or DEFAULT_MODEL
        self._client = anthropic.Anthropic(api_key=key)
        self._anthropic = anthropic
        self.logger = logger
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def _transient(self, exc: Exception) -> bool:
        if isinstance(exc, RefusalError):
            return True
        a = self._anthropic
        transient_types = tuple(
            t for t in (
                getattr(a, "APIConnectionError", None),
                getattr(a, "APITimeoutError", None),
                getattr(a, "RateLimitError", None),
                getattr(a, "InternalServerError", None),
            ) if t is not None
        )
        if transient_types and isinstance(exc, transient_types):
            return True
        status = getattr(exc, "status_code", None)
        return status is not None and (status == 429 or 500 <= status < 600)

    def complete(self, call: LLMCall) -> str:
        last: Exception | None = None
        used = 0
        for attempt in range(1, MAX_ATTEMPTS + 1):
            used = attempt
            try:
                with self._client.messages.stream(
                    model=self.model,
                    max_tokens=call.max_tokens,
                    temperature=call.temperature,
                    system=call.system,
                    messages=[{"role": "user", "content": call.user}],
                ) as stream:
                    resp = stream.get_final_message()
                self.calls += 1
                
                usage = getattr(resp, "usage", None)
                if usage is not None:
                    self.input_tokens += getattr(usage, "input_tokens", 0) or 0
                    self.output_tokens += getattr(usage, "output_tokens", 0) or 0
                text = "".join(
                    b.text for b in resp.content if getattr(b, "type", "") == "text"
                ).strip()
                if not text:
                    stop = getattr(resp, "stop_reason", None)
                    detail = (
                        f"{call.agent}: model returned no text content. "
                        f"stop_reason={stop!r} "
                        f"blocks={[getattr(b, 'type', '?') for b in resp.content]} "
                        f"out_tokens={getattr(usage, 'output_tokens', None)}"
                    )
                    if stop == "refusal":
                        raise RefusalError(detail)
                    raise LLMError(detail)
                return text
            except Exception as exc:  # noqa: BLE001 — classified immediately below
                last = exc
                if attempt >= MAX_ATTEMPTS or not self._transient(exc):
                    break
                delay = BASE_BACKOFF_S * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                if self.logger:
                    self.logger(
                        f"- `{call.agent}` transient API error "
                        f"({type(exc).__name__}); retry {attempt}/{MAX_ATTEMPTS - 1} "
                        f"in {delay:.1f}s"
                    )
                time.sleep(delay)
        kind = "transient, retries exhausted" if self._transient(last) else "non-transient, not retried"
        raise LLMError(
            f"{call.agent}: Anthropic API call failed after {used} attempt(s) "
            f"({kind}). Last error: {type(last).__name__}: {last}"
        ) from last


class MockLLM(BaseLLM):
    """Canned-artifact stub. Produces NO design work — see README, 'Run modes'.

    Fixture selection is by `call.agent` plus, for the Designer, a repair suffix
    so that a repair round-trip can be exercised deterministically if a fixture
    for it exists.
    """

    name = "mock"
    model = "mock-llm (tests/fixtures)"

    FIXTURE_BANNER = (
        "> **MOCK-LLM FIXTURE — NOT REAL DESIGN WORK.** This document was replayed "
        "verbatim from `tests/fixtures/` by `--mock-llm`, a no-API-key test mode "
        "whose only purpose is to prove the orchestration executes end to end. "
        "No model saw the packet; no judgement was exercised; nothing here is "
        "evidence about uhta. Harness NUMBERS in this run are still real (the "
        "Playtester always executes the simulator) — the PROSE around them is a "
        "fixture.\n"
    )

    def __init__(self, fixtures_dir: Path, logger=None):
        self.dir = Path(fixtures_dir)
        self.logger = logger
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        if not self.dir.exists():
            raise LLMError(f"Mock fixtures directory not found: {self.dir}")

    def complete(self, call: LLMCall) -> str:
        name = f"{call.agent}.md"
        p = self.dir / name
        if not p.exists():
            raise LLMError(
                f"--mock-llm: no fixture for agent '{call.agent}' "
                f"(expected {p}). Mock mode replays fixtures only."
            )
        self.calls += 1
        if self.logger:
            self.logger(f"- `{call.agent}` MOCK replay <- `tests/fixtures/{name}`")
        return p.read_text(encoding="utf-8")


def build_llm(mode: str, fixtures_dir: Path, logger=None) -> BaseLLM:
    if mode == "mock":
        return MockLLM(fixtures_dir, logger=logger)
    return LiveLLM(logger=logger)
