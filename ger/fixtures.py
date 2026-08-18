"""`--mock-llm` backend for the GER pipeline. NO API CALLS, NO REAL CONTENT.

Same contract as `content.fixtures.ContentMockLLM`: canned text lives in
`tests/fixtures/ger/`, this module shapes it into valid agent responses, and
every artifact a mock run produces is banner-stamped as fixture output.

The fixture SCRIPT is chosen so a mock run deterministically exercises every
path the live loop has:

    walk / wait / beacon / sleep   accepted at round 0 (the happy path)
    roar     the generator fixture says "Press R to roar" — caught by the
             DETERMINISTIC register gate (R2 NO-UI-LANGUAGE) before any judge
             is consulted; the Refiner fixture repairs it; accepted at round 1
    flame    the generator fixture invents mythology ("the old gods") — caught
             by the mock LLM judge as EXCEEDS-SCOPE; repaired; accepted at
             round 1
    raze     three fixture lines fail three different deterministic checks
             (R4 '?', R4 '!', R5 digit) — the circuit breaker ESCALATES it
             after the round budget, and the run completes with ESCALATED.md

The baseline audit's mock judgments come from the same verdict table: the
build's stub `roar` line is failed CONTRADICTS-CHUNK (it names the road and
omits the unconditional Fear push — the catch a live run is expected to make),
the other stubs pass.
"""
from __future__ import annotations

import json
from pathlib import Path

from crew.llm import LLMError, MockLLM


class GerMockLLM(MockLLM):
    name = "mock"
    model = "mock-llm (tests/fixtures/ger)"

    def __init__(self, fixtures_dir: Path, logger=None):
        super().__init__(fixtures_dir, logger=logger)
        self._gen = self._load("generator.json")
        self._ref = self._load("refiner.json")
        self._verdicts = self._load("evaluator.json")
        self._ref_round: dict[str, int] = {}

    def _load(self, name: str):
        p = self.dir / name
        if not p.exists():
            raise LLMError(f"--mock-llm: missing GER fixture {p}")
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _verb_of(agent: str) -> str:
        return agent.rsplit("-", 1)[-1]

    @staticmethod
    def _line_under_judgment(user: str) -> str:
        marker = "### The line under judgment"
        if marker not in user:
            return ""
        block = user.split(marker, 1)[1]
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("> "):
                return line[2:].strip()
        return ""

    def _log(self, agent: str, what: str) -> None:
        if self.logger:
            self.logger(f"- `{agent}` MOCK replay <- `tests/fixtures/ger/` "
                        f"({what})")

    def complete(self, call) -> str:
        self.calls += 1
        agent = call.agent

        if agent.startswith("ger-generator-"):
            verb = self._verb_of(agent)
            line = self._gen.get(verb)
            if line is None:
                raise LLMError(f"--mock-llm: no generator fixture for '{verb}'")
            self._log(agent, "generator line")
            return json.dumps({"line": line}, ensure_ascii=False)

        if agent.startswith("ger-refiner-"):
            verb = self._verb_of(agent)
            seq = self._ref.get(verb, [])
            i = self._ref_round.get(verb, 0)
            if i >= len(seq):
                raise LLMError(f"--mock-llm: refiner fixture for '{verb}' "
                               f"exhausted at round {i + 1} — the script only "
                               f"covers {len(seq)} round(s)")
            self._ref_round[verb] = i + 1
            self._log(agent, f"refiner round {i + 1}")
            return json.dumps({"line": seq[i]}, ensure_ascii=False)

        if agent.startswith("ger-evaluator-"):
            line = self._line_under_judgment(call.user)
            row = self._verdicts["fail_lines"].get(line)
            if row:
                payload = {"verdict": "FAIL", "class": row["class"],
                           "quoted_chunk": row["quoted_chunk"],
                           "reason": row["reason"]}
            else:
                payload = {"verdict": "PASS", "class": None,
                           "quoted_chunk": self._verdicts["pass"]["quoted_chunk"],
                           "reason": self._verdicts["pass"]["reason"]}
            self._log(agent, f"verdict {payload['verdict']}")
            return json.dumps(payload, ensure_ascii=False)

        raise LLMError(f"--mock-llm: no GER fixture route for agent '{agent}'")
