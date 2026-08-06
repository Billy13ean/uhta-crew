"""`--mock-llm` backend for the content pipeline. NO API CALLS, NO REAL CONTENT.

This exists for one reason: to prove the orchestration executes end to end
without a key. It is not a source of evidence about uhta's text and every
artifact a mock run produces says so in its first lines.

It differs from `crew.llm.MockLLM` in one way, and the difference is forced by
the Critic's contract: the Critic must return **exactly one verdict per
candidate**, and the candidate count is a CLI flag. A single frozen JSON file
cannot satisfy that for every `--candidates N`. So the canned *text* lives in
`tests/fixtures/content/`, and this module assembles it into a correctly-shaped
payload for whatever N the run used. The verdict *pattern* — which candidate
fails, with which class — is fixed here and documented, so a mock run
deterministically exercises both the PASS path and the catch-and-correct path.
"""
from __future__ import annotations

import json
from pathlib import Path

from crew.llm import LLMError, MockLLM


class ContentMockLLM(MockLLM):
    name = "mock"
    model = "mock-llm (tests/fixtures/content)"

    #: 1-indexed candidate positions the mock Critic rejects. Position 2 always
    #: fails so `CRITIC-LOG.md` in a mock run is non-empty and the correction
    #: path is exercised; position 5 fails when the run is wide enough to have
    #: one, so the "by flag class" table has more than one row.
    FAIL_POSITIONS = {2: "GENERIC", 5: "WRONG-REGISTER"}

    def __init__(self, fixtures_dir: Path, logger=None):
        super().__init__(fixtures_dir, logger=logger)
        self._pool = self._load("writer-pool.json")
        self._critic = self._load("critic-text.json")

    def _load(self, name: str):
        p = self.dir / name
        if not p.exists():
            raise LLMError(f"--mock-llm: missing content fixture {p}")
        return json.loads(p.read_text(encoding="utf-8"))

    # ---- helpers ----

    @staticmethod
    def _n_requested(user: str, default: int = 6) -> int:
        marker = "Return **exactly "
        if marker in user:
            try:
                return int(user.split(marker, 1)[1].split(" ", 1)[0])
            except (ValueError, IndexError):
                pass
        return default

    @staticmethod
    def _candidate_lines(user: str) -> list[str]:
        if "### Candidates" not in user:
            return []
        block = user.split("### Candidates", 1)[1].split("### Output", 1)[0]
        out = []
        for line in block.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            head, sep, rest = line.partition(". ")
            if sep and head.isdigit():
                out.append(rest.strip())
        return out

    # ---- the backend ----

    def complete(self, call) -> str:
        self.calls += 1
        if call.agent.startswith("writer"):
            n = self._n_requested(call.user)
            # rotate the pool by a stable hash of the agent label so different
            # beats produce different (still canned) candidate sets
            offset = sum(ord(ch) for ch in call.agent) % len(self._pool)
            lines = [self._pool[(offset + i) % len(self._pool)] for i in range(n)]
            if self.logger:
                self.logger(f"- `{call.agent}` MOCK replay <- "
                            f"`tests/fixtures/content/writer-pool.json` ({n} lines)")
            return "```json\n" + json.dumps(lines, ensure_ascii=False) + "\n```"

        if call.agent.startswith("critic"):
            cands = self._candidate_lines(call.user)
            verdicts = []
            for i, line in enumerate(cands, 1):
                cls = self.FAIL_POSITIONS.get(i)
                if cls:
                    verdicts.append({
                        "index": i, "verdict": "FAIL", "class": cls,
                        "quoted_chunk": self._critic["quoted_chunk"],
                        "reason": self._critic["fail_reason"],
                        "correction": self._critic["correction"],
                    })
                else:
                    verdicts.append({
                        "index": i, "verdict": "PASS", "class": None,
                        "quoted_chunk": self._critic["quoted_chunk"],
                        "reason": self._critic["pass_reason"],
                        "correction": None,
                    })
            if self.logger:
                self.logger(f"- `{call.agent}` MOCK replay <- "
                            f"`tests/fixtures/content/critic-text.json` "
                            f"({len(verdicts)} verdicts)")
            return "```json\n" + json.dumps(verdicts, ensure_ascii=False) + "\n```"

        raise LLMError(f"--mock-llm: no content fixture for agent '{call.agent}'")
