"""Content pipeline orchestration — deterministic, no LLM in this module.

Shape: retrieve -> generate -> criticise -> assemble -> human. Every arrow is a
file, exactly as in `crew/`. This module sequences the stages, records what each
one did, and halts by name when anything fails.

It ends at an unfilled `## Director selection` block. The pipeline produces
candidates; which words become the only words in a wordless game is a Director
ruling (GDD §4.5, "human as curator").
"""
from __future__ import annotations

import json
import platform
import time
import traceback
from pathlib import Path

from crew.agents import AgentError
from crew.blackboard import Blackboard, MissingArtifactError

from . import assemble
from .agents.critic import PROMPT_VERSION as CRITIC_PV
from .agents.writer import PROMPT_VERSION as WRITER_PV
from .orchestrator import ContentOrchestrator
from .beats import AB_BEAT_ID, BEATS, CONTENT_TYPES
from .retriever import (BM25_B, BM25_K1, CORPUS_POLICY, SCORE_THRESHOLD,
                        TOKEN_BUDGET, Retriever, build_corpus)

CORPUS_FILES = {
    "CANON.md": "CANON.md",
    "CANON-process.md": "CANON-process.md",
    "uhta-gdd-v0.9.7-full.md": "gdd/uhta-gdd-v0.9.7-full.md",
    "uhta-gdd-v0.9.7-abridged.md": "gdd/uhta-gdd-v0.9.7-abridged.md",
}


class ContentPipeline:
    def __init__(self, llm, mode: str, root: Path, run_id: str | None = None,
                 n_candidates: int = 6, beat_filter: list[str] | None = None,
                 drop_agent: str | None = None):
        self.llm = llm
        self.mode = mode
        self.root = Path(root)
        self.run_id = run_id or f"content-{time.strftime('%Y%m%d-%H%M%S')}-{mode}"
        self.bb = Blackboard(self.run_id, root=self.root)
        self.prompts_dir = self.root / "prompts"
        self.n_candidates = n_candidates
        self.beats = [b for b in BEATS if not beat_filter or b.id in beat_filter]
        self.orch = ContentOrchestrator(self.bb, llm, self.prompts_dir,
                                        n_candidates, drop_agent=drop_agent)
        self.drop_agent = drop_agent
        self.current_stage = "corpus"
        self.stages: list[dict] = []
        self.corpus_stats: dict = {}
        self.results: list[dict] = []
        self.ab: dict | None = None

    # ---------------- bookkeeping ----------------

    def _stage(self, name: str, status: str, t0: float, detail: str = "") -> None:
        self.stages.append({
            "stage": name, "status": status,
            "seconds": round(time.time() - t0, 2), "detail": detail,
        })

    def _manifest(self, status: str) -> dict:
        return {
            "run_id": self.run_id,
            "pipeline": "content (Assignment 4 — dynamic content pipeline)",
            "status": status,
            "mode": self.mode,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": getattr(self.llm, "model", "n/a"),
            "llm_backend": getattr(self.llm, "name", "n/a"),
            "llm_calls": getattr(self.llm, "calls", 0),
            "llm_tokens": {"input": getattr(self.llm, "input_tokens", 0),
                           "output": getattr(self.llm, "output_tokens", 0)},
            "python": platform.python_version(),
            "candidates_per_beat": self.n_candidates,
            "beats": [{"id": b.id, "type": b.type, "label": b.label} for b in self.beats],
            "corpus": self.corpus_stats,
            "retrieval": {
                "scorer": "BM25 (pure python, content/retriever.py)",
                "k1": BM25_K1, "b": BM25_B,
                "idf": "non-negative: ln(1 + (N - df + 0.5)/(df + 0.5))",
                "chunk_rule": "one ### subsection (GDD §4.5); ## when it has no children",
                "score_threshold": SCORE_THRESHOLD,
                "token_budget": TOKEN_BUDGET,
                "selection_rule": "GDD §4.5 two-chunk rule — one cut per beat query "
                                  "(mechanical consequence, experience), unioned",
            },
            "prompt_versions": {"writer": WRITER_PV, "critic": CRITIC_PV,
                                "orchestrator": "content-orchestrator v1 (dispatch "
                                                "only, no LLM)",
                                "pipeline": "content-pipeline v1 (no LLM)"},
            "orchestration": self.orch.summary(),
            "ab_beat": AB_BEAT_ID,
            "director_selection": "PENDING",
            "stages": self.stages,
            "artifact_sha256": self.bb.artifact_hashes(),
            "blackboard_ledger": self.bb.ledger_json(),
        }

    def _write_manifest(self, status: str) -> None:
        (self.bb.run_dir / "manifest.json").write_text(
            json.dumps(self._manifest(status), indent=2) + "\n", encoding="utf-8")

    def _failed(self, agent: str, stage: str, error: str) -> None:
        body = (
            f"# FAILED — {self.run_id}\n\n"
            f"| field | value |\n|---|---|\n"
            f"| pipeline | content (Assignment 4) |\n"
            f"| agent | **{agent}** |\n"
            f"| stage | **{stage}** |\n"
            f"| time | {time.strftime('%Y-%m-%d %H:%M:%S')} |\n\n"
            f"## Error\n\n```\n{error}\n```\n\n"
            f"## What this means\n\n"
            f"The pipeline halted rather than assembling evidence documents around a\n"
            f"missing or invalid stage. There is no fallback by design: a RAG-TRACE\n"
            f"with no retrieval, or a CRITIC-LOG with an unrepaired rejection, would\n"
            f"read like evidence and not be any.\n\n"
            f"See `RUN-LOG.md` for the read/write trail up to the halt and\n"
            f"`manifest.json` for per-stage status.\n"
        )
        (self.bb.run_dir / "FAILED.md").write_text(body, encoding="utf-8")
        self.bb.log(f"\n**FAILED.md written** — agent=`{agent}` stage=`{stage}`\n")

    # ---------------- stages ----------------

    def stage_corpus(self) -> Retriever:
        t0 = time.time()
        self.current_stage = "corpus"
        self.bb.stage(1, "corpus", "Chunk the blackboard, scope it by CORPUS_POLICY, "
                                   "build the BM25 index. Deterministic; no LLM.")
        docs = {name: self.bb.read_bb(rel, "corpus") for name, rel in CORPUS_FILES.items()}
        all_chunks, dropped, kept = build_corpus(docs)
        if not kept:
            raise MissingArtifactError("blackboard corpus", "blackboard seeding", "corpus")
        self.corpus_stats = {
            "files": list(CORPUS_FILES),
            "policy": CORPUS_POLICY["name"],
            "policy_rationale": CORPUS_POLICY["rationale"],
            "chunks_total": len(all_chunks),
            "chunks_indexed": len(kept),
            "chunks_excluded": len(dropped),
            "words_indexed": sum(c.words for c in kept),
            "words_excluded": sum(d.words for d in dropped),
            "exclusions": [{"key": d.key, "heading": d.heading, "words": d.words,
                            "reason": d.reason} for d in dropped],
            "indexed": [{"key": c.key, "heading": c.heading, "words": c.words,
                         "est_tokens": c.tokens} for c in kept],
        }
        self.bb.note("corpus", f"indexed **{len(kept)}** chunks "
                               f"({self.corpus_stats['words_indexed']} words); "
                               f"excluded **{len(dropped)}** "
                               f"({self.corpus_stats['words_excluded']} words), "
                               f"each with a reason")
        self._stage("corpus", "OK", t0,
                    f"{len(kept)} in / {len(dropped)} out")
        return Retriever(kept)

    def stage_generate(self, retriever: Retriever) -> None:
        t0 = time.time()
        self.current_stage = "generation"
        self.bb.stage(2, "retrieval + generation (dispatched)",
                      "Per beat: two-query retrieval (GDD §4.5), then the "
                      "Orchestrator dispatches Writer (temp 0.9) -> blackboard "
                      "artifact -> Critic (temp 0.0) -> blackboard artifact. The "
                      "Critic reads the candidates off disk, never from memory.")
        for beat in self.beats:
            ct = CONTENT_TYPES[beat.type]
            selection = retriever.select_multi(beat.queries)
            self.bb.note(
                f"retriever-{beat.id}",
                "selected " + ", ".join(
                    f"`{r.chunk.doc} §{r.chunk.section}` (bm25 {r.score:.2f})"
                    for r in selection.selected)
                + f" — {len(selection.exclusions)} exclusion(s) recorded")
            candidates, verdicts = self.orch.run_beat(beat, selection, ct)
            passed = sum(1 for v in verdicts if not v.failed)
            self.bb.note(f"critic-{beat.id}",
                         f"{passed}/{len(verdicts)} PASS, "
                         f"{len(verdicts) - passed} FAIL (each with a correction)")
            self.results.append({"beat": beat, "selection": selection,
                                 "candidates": candidates, "verdicts": verdicts})
        total = sum(len(r["verdicts"]) for r in self.results)
        fails = sum(1 for r in self.results for v in r["verdicts"] if v.failed)
        self._stage("generation", "OK", t0, f"{total} candidates, {fails} caught")

    def stage_ab(self, retriever: Retriever) -> None:
        """The Voice Judgment evidence: the same beat retrieved two ways, both
        candidate sets judged by the same Critic at temperature 0."""
        t0 = time.time()
        beat = next((b for b in self.beats if b.id == AB_BEAT_ID), None)
        if beat is None:
            self._stage("ab", "SKIPPED", t0, f"beat {AB_BEAT_ID} not in this run")
            return
        self.current_stage = "ab"
        self.bb.stage(3, "A/B — the retrieval tweak, measured",
                      "Arm A reproduces the naive hand-run: a single experience-side "
                      "query, top-1. Arm B is the GDD §4.5 two-chunk rule. Same beat, "
                      "same Writer settings, and the SAME judging context for both "
                      "arms — only the Writer's view varies.")
        ct = CONTENT_TYPES[beat.type]
        arm_a = retriever.select(beat.query_experience, max_chunks=1)
        arm_b = retriever.select_multi(beat.queries)

        out = {}
        for name, sel in (("A-naive-top1", arm_a), ("B-two-chunk-rule", arm_b)):
            # The judge is held constant at arm B's (richer) cut for BOTH arms.
            # Only the WRITER's view varies — otherwise the comparison measures
            # two things at once and the result means nothing.
            cands, verds = self.orch.run_beat(beat, sel, ct, tag=f"ab-{name}",
                                              critic_selection=arm_b)
            out[name] = {"selection": sel, "judged_against": arm_b,
                         "candidates": cands, "verdicts": verds}
            self.bb.note(f"ab-{name}",
                         f"{sum(1 for v in verds if not v.failed)}/{len(verds)} PASS")
        self.ab = {"beat": beat, "arms": out}
        self._stage("ab", "OK", t0, f"beat {beat.id}, 2 arms")

    def stage_assemble(self) -> None:
        t0 = time.time()
        self.current_stage = "assembly"
        self.bb.stage(4, "assembly",
                      "Every evidence document generated from this run's data. "
                      "Deterministic; no LLM. Nothing here is typed by hand.")
        assemble.write_all(self)
        self._stage("assembly", "OK", t0, "content files + 4 evidence documents")

    # ---------------- run ----------------

    def run(self) -> int:
        try:
            retriever = self.stage_corpus()
            self.stage_generate(retriever)
            self.stage_ab(retriever)
            self.stage_assemble()
            self._write_manifest("COMPLETE_PENDING_DIRECTOR")
            self.bb.log("\n**Run complete.** Ends at an unfilled `## Director "
                        "selection` block — the pipeline proposes; the Director picks.\n")
            return 0
        except (AgentError, MissingArtifactError) as exc:
            agent = getattr(exc, "agent", None) or getattr(exc, "producer", "pipeline")
            stage = self.current_stage
            self._failed(agent, stage, str(exc))
            self._stage(stage, "FAILED", time.time(), str(exc)[:200])
            self._write_manifest("FAILED")
            print(f"\n{exc}\n")
            return 1
        except Exception as exc:  # noqa: BLE001 — nothing escapes as a bare traceback
            self._failed("pipeline", "unknown", traceback.format_exc())
            self._write_manifest("FAILED")
            print(f"\nUNEXPECTED FAILURE: {exc}\nSee out/{self.run_id}/FAILED.md\n")
            return 1
