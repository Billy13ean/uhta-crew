"""`--mock-llm` backend for the mini-game pipeline. NO API CALLS, NO REAL
DESIGN WORK.

The fixture script walks every path in one propose run:

    first-contact-hope / first-contact-fear / vigil-hope   accepted round 0
    vigil-fear    fixture design puts a text label in `signals` — caught by
                  the DETERMINISTIC design gate (C5 WORDLESS); repaired;
                  accepted round 1
    holding-hope  fixture design has Fear's texture — the mock Judge FAILs
                  it POLE-SYMMETRY; repaired; accepted round 1
    holding-fear  three fixture versions fail three different deterministic
                  checks (C3 bad control, C4 fake currency, C3 again) —
                  ESCALATED by the breaker; the candidates doc marks it
                  unselectable

and the build phase replays a hand-authored minimal patch that passes the
REAL post-checks against the REAL slice — proving the contract is
satisfiable, not merely specified.
"""
from __future__ import annotations

import json
from pathlib import Path

from crew.llm import LLMError, MockLLM


class MinigameMockLLM(MockLLM):
    name = "mock"
    model = "mock-llm (tests/fixtures/minigame)"

    def __init__(self, fixtures_dir: Path, logger=None):
        super().__init__(fixtures_dir, logger=logger)
        self._designs = self._load("designs.json")
        self._refined = self._load("refiner.json")
        self._verdicts = self._load("judge.json")
        self._programmer = self._load("programmer.json")
        self._instructor = self._load("instructor.json")
        self._presenter = self._load("presenter.json")
        self._ref_round: dict[str, int] = {}

    def _load(self, name: str):
        p = self.dir / name
        if not p.exists():
            raise LLMError(f"--mock-llm: missing minigame fixture {p}")
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _slot_of(agent: str) -> str:
        # labels look like mg-designer-first-contact-hope
        for prefix in ("mg-designer-", "mg-judge-", "mg-refiner-"):
            if agent.startswith(prefix):
                return agent[len(prefix):]
        return agent

    @staticmethod
    def _candidate_name(user: str) -> str:
        marker = "### The design under judgment"
        if marker not in user:
            return ""
        block = user.split(marker, 1)[1]
        try:
            start = block.index("{")
            depth = 0
            for i, ch in enumerate(block[start:], start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return str(json.loads(block[start:i + 1])
                                   .get("name", ""))
        except (ValueError, json.JSONDecodeError):
            pass
        return ""

    def _log(self, agent: str, what: str) -> None:
        if self.logger:
            self.logger(f"- `{agent}` MOCK replay <- "
                        f"`tests/fixtures/minigame/` ({what})")

    def complete(self, call) -> str:
        self.calls += 1
        agent = call.agent

        if agent.startswith("mg-designer-"):
            slot = self._slot_of(agent)
            d = self._designs.get(slot)
            if d is None:
                raise LLMError(f"--mock-llm: no designer fixture for "
                               f"'{slot}'")
            self._log(agent, "design")
            return "```json\n" + json.dumps(d, ensure_ascii=False) + "\n```"

        if agent.startswith("mg-refiner-"):
            slot = self._slot_of(agent)
            seq = self._refined.get(slot, [])
            i = self._ref_round.get(slot, 0)
            if i >= len(seq):
                raise LLMError(f"--mock-llm: refiner fixture for '{slot}' "
                               f"exhausted at round {i + 1}")
            self._ref_round[slot] = i + 1
            self._log(agent, f"refined design round {i + 1}")
            return "```json\n" + json.dumps(seq[i], ensure_ascii=False) + "\n```"

        if agent.startswith("mg-judge-"):
            name = self._candidate_name(call.user)
            row = self._verdicts["fail_names"].get(name)
            if row:
                payload = {"verdict": "FAIL", "class": row["class"],
                           "quoted_chunk": row["quoted_chunk"],
                           "reason": row["reason"]}
            else:
                payload = {"verdict": "PASS", "class": None,
                           "quoted_chunk":
                               self._verdicts["pass"]["quoted_chunk"],
                           "reason": self._verdicts["pass"]["reason"]}
            self._log(agent, f"verdict {payload['verdict']}")
            return "```json\n" + json.dumps(payload, ensure_ascii=False) + "\n```"

        if agent == "mg-instructor":
            self._log(agent, "first-use line")
            return ("```json\n"
                    + json.dumps(self._instructor, ensure_ascii=False)
                    + "\n```")

        if agent == "mg-presenter":
            self._log(agent, "presentation spec")
            return ("```json\n"
                    + json.dumps(self._presenter, ensure_ascii=False)
                    + "\n```")

        if agent == "mg-programmer":
            self._log(agent, "hand-authored fixture patch")
            return ("```json\n"
                    + json.dumps(self._programmer, ensure_ascii=False)
                    + "\n```")

        raise LLMError(f"--mock-llm: no minigame fixture route for agent "
                       f"'{agent}'")
