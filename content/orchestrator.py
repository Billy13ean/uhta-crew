"""Orchestrator — dispatch only, for the content pipeline. No LLM in this module.

GDD §3.1 seats the Orchestrator dispatch-only and answers the obvious objection —
*could it be removed?* — with one specific breakage:

> with the Writer and Critic running batch generation, the run manifest is what
> guarantees a generated line set reaches the Critic **before** it reaches the
> build. Remove it and the only thing standing between bulk-generated prose and
> `uhta-slice.html` is the Director's memory of what he sent where.

This module is that guarantee, implemented rather than asserted. The Writer's
candidates are **written to the blackboard as an artifact** and the Critic reads
them back from disk. There is no in-memory handoff between the two roles, so a
line set that never reached the Critic is a missing file with a name, not a
silent omission — and the manifest records the artifact path for every dispatch.

It never reads an artifact's meaning: existence, size, parse, and that is all. It
routes; it cannot rule.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict

from crew.blackboard import MissingArtifactError

from .agents.critic import Verdict, run_critic
from .agents.writer import run_writer

DRAFT_DIR = "drafts"
VERDICT_DIR = "verdicts"


class ContentOrchestrator:
    #: Removing either of these is expected to HALT the run with a named error
    #: and exit 1 — the role-clarity demonstration, shown rather than claimed.
    DROPPABLE = ("writer", "critic")

    def __init__(self, bb, llm, prompts_dir, n_candidates: int,
                 drop_agent: str | None = None):
        self.bb = bb
        self.llm = llm
        self.prompts_dir = prompts_dir
        self.n_candidates = n_candidates
        self.drop_agent = drop_agent
        self.dispatches: list[dict] = []

    # ---------------- dispatch record ----------------

    def _record(self, beat_id: str, agent: str, artifact: str, t0: float,
                detail: str) -> None:
        self.dispatches.append({
            "beat": beat_id, "agent": agent, "artifact": artifact,
            "seconds": round(time.time() - t0, 2), "detail": detail,
        })

    # ---------------- the two stages ----------------

    def _writer_stage(self, beat, selection, ct, tag: str) -> str:
        """Dispatch the Writer and return the artifact path its output landed in."""
        name = f"{DRAFT_DIR}/{tag}-draft.json"
        if self.drop_agent == "writer":
            self.bb.note("orchestrator",
                         f"**--drop-agent writer** — not dispatching; `{name}` will "
                         f"not exist")
            return name
        t0 = time.time()
        candidates = run_writer(self.llm, self.prompts_dir, beat, selection, ct,
                                self.n_candidates, agent_label=f"writer-{tag}")
        self.bb.write(name, json.dumps({
            "beat": beat.id, "tag": tag, "label": beat.label,
            "retrieved": [{"key": r.chunk.key, "heading": r.chunk.heading,
                           "bm25": round(r.score, 2)} for r in selection.selected],
            "candidates": candidates,
        }, indent=2, ensure_ascii=False) + "\n", f"writer-{tag}")
        self._record(beat.id, f"writer-{tag}", name, t0,
                     f"{len(candidates)} candidates")
        return name

    def _critic_stage(self, beat, selection, ct, tag: str,
                      draft_name: str) -> tuple[str, list[str]]:
        """Dispatch the Critic **against the artifact**, not against a variable."""
        name = f"{VERDICT_DIR}/{tag}-verdict.json"
        # THE guarantee. If the Writer did not run, this halts naming the Writer,
        # and the Critic is never handed a line set that does not exist on disk.
        self.bb.require(draft_name, f"critic-{tag}", f"writer-{tag}")
        draft = json.loads(self.bb.read(draft_name, f"critic-{tag}", f"writer-{tag}"))
        candidates = draft["candidates"]

        if self.drop_agent == "critic":
            self.bb.note("orchestrator",
                         f"**--drop-agent critic** — not dispatching; `{name}` will "
                         f"not exist and assembly cannot proceed")
            return name, candidates

        t0 = time.time()
        verdicts = run_critic(self.llm, self.prompts_dir, beat, selection,
                              candidates, ct, agent_label=f"critic-{tag}")
        self.bb.write(name, json.dumps({
            "beat": beat.id, "tag": tag,
            "verdicts": [asdict(v) for v in verdicts],
        }, indent=2, ensure_ascii=False) + "\n", f"critic-{tag}")
        self._record(beat.id, f"critic-{tag}", name, t0,
                     f"{sum(1 for v in verdicts if not v.failed)}/{len(verdicts)} PASS")
        return name, candidates

    # ---------------- the public call ----------------

    def run_beat(self, beat, selection, ct, tag: str | None = None):
        """Writer -> artifact -> Critic -> artifact. Returns (candidates, verdicts),
        both read back from the blackboard rather than passed in memory."""
        tag = tag or beat.id
        draft_name = self._writer_stage(beat, selection, ct, tag)
        verdict_name, candidates = self._critic_stage(beat, selection, ct, tag,
                                                      draft_name)
        # Assembly reads the Critic's artifact. A verdict set that exists only in
        # this process never reaches an evidence document.
        self.bb.require(verdict_name, "assemble", f"critic-{tag}")
        payload = json.loads(self.bb.read(verdict_name, "assemble", f"critic-{tag}"))
        verdicts = [Verdict(**v) for v in payload["verdicts"]]
        return candidates, verdicts

    # ---------------- manifest support ----------------

    def summary(self) -> dict:
        return {
            "contract": "dispatch only — never gates, never authors, never tunes "
                        "(GDD §3.1)",
            "guarantee": "the Writer's candidates are written to the blackboard and "
                         "the Critic reads them back from disk; there is no "
                         "in-memory handoff between the two roles",
            "drop_agent": self.drop_agent,
            "dispatches": self.dispatches,
        }


def expected_halt_message(agent: str) -> str:
    """What `--drop-agent <agent>` is expected to produce. Used by --selftest."""
    if agent == "writer":
        return "produced by the writer"
    return "produced by the critic"


__all__ = ["ContentOrchestrator", "MissingArtifactError", "expected_halt_message"]
