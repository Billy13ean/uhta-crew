"""GER pipeline orchestration — deterministic, no LLM in this module.

Shape:  corpus -> baseline audit -> [ per verb: generate -> evaluate ->
(refine -> evaluate)* -> accept | escalate ] -> assemble -> human.

Every arrow is a file. Each round's draft and findings are written to the
blackboard before the next stage reads them — the Evaluator judges the line
it reads OFF DISK, not the one in the Generator's return value, exactly as
A4's Critic read the Writer's candidates off disk. RUN-LOG.md is therefore
the complete record of the loop, round by round.

The run ends at an unfilled `## Director selection` block in
teaching-lines.md, like every pipeline in this repo: the loop proposes one
rule-passing line per verb; whether those words enter the build is a Director
ruling, applied by copying the generated snippet (or the pre-patched build)
by hand.
"""
from __future__ import annotations

import json
import platform
import time
import traceback
from pathlib import Path

from content.agents import AgentError
from content.pipeline import CORPUS_FILES
from content.retriever import (BM25_B, BM25_K1, CORPUS_POLICY, SCORE_THRESHOLD,
                               TOKEN_BUDGET, Retriever, build_corpus)
from crew.blackboard import Blackboard, MissingArtifactError
from crew.canon import get_canon

from . import PIPELINE_VERSION, assemble
from .breaker import (BreakerTripped, CircuitBreaker, RoundRecord, VerbOutcome)
from .checks import (extract_guide_strings, extract_teaching_text,
                     run_register_checks, BuildExtractionError)
from .evaluator import PROMPT_VERSION as EVALUATOR_PV, run_evaluator
from .generator import PROMPT_VERSION as GENERATOR_PV, run_generator
from .refiner import PROMPT_VERSION as REFINER_PV, run_refiner
from .spec import REGISTER, VERB_SPECS

BUILD_REL = "build/uhta-slice.html"


class GerPipeline:
    def __init__(self, llm, mode: str, root: Path, run_id: str | None = None,
                 verb_filter: list[str] | None = None,
                 max_rounds: int | None = None,
                 escalation_limit: int | None = None,
                 skip_baseline: bool = False):
        self.llm = llm
        self.mode = mode
        self.root = Path(root)
        self.run_id = run_id or f"ger-{time.strftime('%Y%m%d-%H%M%S')}-{mode}"
        self.bb = Blackboard(self.run_id, root=self.root)
        self.prompts_dir = self.root / "prompts"
        self.specs = [s for s in VERB_SPECS
                      if not verb_filter or s.verb in verb_filter]
        kwargs = {}
        if max_rounds is not None:
            kwargs["max_rounds"] = max_rounds
        if escalation_limit is not None:
            kwargs["escalation_limit"] = escalation_limit
        self.breaker = CircuitBreaker(**kwargs)
        self.skip_baseline = skip_baseline
        #: The law in force: the canon bench applies any Director ruling
        #: (canon/CANON-RULING.json) over the baseline REGISTER; the run
        #: records it in CANON-IN-FORCE.md and the manifest.
        self.canon = get_canon()
        self.register = self.canon.text("ger-register", REGISTER)

        self.current_stage = "corpus"
        self.stages: list[dict] = []
        self.corpus_stats: dict = {}
        self.build_lines: dict[str, str] = {}       # the build's current TEACHING_TEXT
        self.baseline: list[dict] = []              # audit rows
        self.guide_audit: list[dict] = []           # guide() strings vs the gate
        self.outcomes: list[VerbOutcome] = []
        self.selections: dict[str, object] = {}
        self.patch_report: dict = {}

    # ---------------- bookkeeping ----------------

    def _stage(self, name: str, status: str, t0: float, detail: str = "") -> None:
        self.stages.append({"stage": name, "status": status,
                            "seconds": round(time.time() - t0, 2),
                            "detail": detail})

    def _manifest(self, status: str) -> dict:
        return {
            "run_id": self.run_id,
            "pipeline": "ger (Assignment 6 — Generator/Evaluator/Refiner/"
                        "Circuit Breaker)",
            "pipeline_version": PIPELINE_VERSION,
            "status": status,
            "mode": self.mode,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": getattr(self.llm, "model", "n/a"),
            "llm_backend": getattr(self.llm, "name", "n/a"),
            "llm_calls": getattr(self.llm, "calls", 0),
            "llm_tokens": {"input": getattr(self.llm, "input_tokens", 0),
                           "output": getattr(self.llm, "output_tokens", 0)},
            "python": platform.python_version(),
            "content_type": "first-use verb narration (the build's "
                            "TEACHING_TEXT const, seven verbs)",
            "rule_enforced": "GDD §2.5 narration register — short, declarative, "
                             "second person, names the verb, states its "
                             "consequence, no mythology; §2.3 no numbers; no "
                             "interface language",
            "canon": self.canon.summary(),
            "verbs": [s.verb for s in self.specs],
            "corpus": self.corpus_stats,
            "retrieval": {
                "scorer": "BM25 (content/retriever.py, reused)",
                "k1": BM25_K1, "b": BM25_B,
                "score_threshold": SCORE_THRESHOLD,
                "token_budget": TOKEN_BUDGET,
                "selection_rule": "GDD §4.5 two-chunk rule per verb "
                                  "(mechanical consequence + experience)",
            },
            "prompt_versions": {"generator": GENERATOR_PV,
                                "evaluator": EVALUATOR_PV,
                                "refiner": REFINER_PV,
                                "pipeline": PIPELINE_VERSION},
            "breaker": self.breaker.summary(),
            "outcomes": [{
                "verb": o.verb, "status": o.status,
                "refinements_used": o.refinements_used,
                "final_line": o.final_line,
            } for o in self.outcomes],
            "baseline_audit": self.baseline,
            "patch": self.patch_report,
            "director_selection": "PENDING",
            "stages": self.stages,
            "artifact_sha256": self.bb.artifact_hashes(),
            "blackboard_ledger": self.bb.ledger_json(),
        }

    def _write_manifest(self, status: str) -> None:
        (self.bb.run_dir / "manifest.json").write_text(
            json.dumps(self._manifest(status), indent=2) + "\n",
            encoding="utf-8")

    def _failed(self, agent: str, stage: str, error: str) -> None:
        body = (
            f"# FAILED — {self.run_id}\n\n"
            f"| field | value |\n|---|---|\n"
            f"| pipeline | ger (Assignment 6) |\n"
            f"| agent | **{agent}** |\n"
            f"| stage | **{stage}** |\n"
            f"| time | {time.strftime('%Y-%m-%d %H:%M:%S')} |\n\n"
            f"## Error\n\n```\n{error}\n```\n\n"
            f"## What this means\n\n"
            f"The run halted rather than continuing around a broken contract or a\n"
            f"tripped breaker. Structural failures (unparseable responses, unquoted\n"
            f"FAILs, no-op refinements) halt immediately; the circuit breaker halts\n"
            f"when escalations show the loop is not converging systemically. Either\n"
            f"way, what was produced before the halt is real and is in this\n"
            f"directory — see RUN-LOG.md for the trail and ESCALATED.md (if\n"
            f"present) for the evidence per escalated verb.\n"
        )
        (self.bb.run_dir / "FAILED.md").write_text(body, encoding="utf-8")
        self.bb.log(f"\n**FAILED.md written** — agent=`{agent}` stage=`{stage}`\n")

    # ---------------- evaluation (both layers) ----------------

    def _evaluate(self, spec, selection, line: str, label_suffix: str):
        """Layer 1 (deterministic gate), then layer 2 (LLM judge) only if the
        gate is clean. Returns (findings, judgment|None)."""
        det = run_register_checks(line, spec.verb)
        if det:
            self.bb.note(f"ger-evaluator-{spec.verb}",
                         f"layer-1 register gate: **{len(det)} finding(s)** "
                         f"{label_suffix} — line never reached the LLM judge")
            return det, None
        judgment = run_evaluator(self.llm, self.prompts_dir, spec, selection,
                                 line, self.register,
                                 agent_label=f"ger-evaluator-{spec.verb}")
        if judgment.failed:
            return [judgment.finding()], judgment
        return [], judgment

    # ---------------- stages ----------------

    def stage_corpus(self) -> Retriever:
        t0 = time.time()
        self.current_stage = "corpus"
        self.bb.stage(1, "corpus",
                      "Chunk the blackboard, scope it by CORPUS_POLICY (reused "
                      "from A4 — this pipeline writes player-facing prose, so "
                      "the same game-material-only cut applies, §4.5 exclusion "
                      "included), build the BM25 index. Deterministic; no LLM.")
        docs = {name: self.bb.read_bb(rel, "corpus")
                for name, rel in CORPUS_FILES.items()}
        all_chunks, dropped, kept = build_corpus(docs)
        if not kept:
            raise MissingArtifactError("blackboard corpus", "blackboard seeding",
                                       "corpus")
        self.corpus_stats = {
            "files": list(CORPUS_FILES),
            "policy": CORPUS_POLICY["name"],
            "chunks_indexed": len(kept),
            "chunks_excluded": len(dropped),
            "words_indexed": sum(c.words for c in kept),
        }
        self.bb.note("corpus", f"indexed **{len(kept)}** chunks; excluded "
                               f"**{len(dropped)}**, each with a reason "
                               f"(policy `{CORPUS_POLICY['name']}`)")
        self._stage("corpus", "OK", t0, f"{len(kept)} in / {len(dropped)} out")
        return Retriever(kept)

    def stage_baseline(self, retriever: Retriever) -> None:
        """Point the Evaluator at the text ALREADY IN THE BUILD. Layer 1 runs
        on both TEACHING_TEXT and guide(); layer 2 judges the seven stub lines.
        This is the pipeline answering the ReadMe question 'did it catch
        something you would have missed' against shipped text, not a strawman."""
        t0 = time.time()
        self.current_stage = "baseline-audit"
        self.bb.stage(2, "baseline audit",
                      "Extract the build's current TEACHING_TEXT (the stub "
                      "lines A5's Programmer wrote) and guide()'s tutorial "
                      "strings, and run the Evaluator over shipped text.")
        html = self.bb.read_bb(BUILD_REL, "baseline-audit")
        self.build_lines = extract_teaching_text(html)
        missing = [s.verb for s in VERB_SPECS if s.verb not in self.build_lines]
        if missing:
            raise BuildExtractionError(
                f"TEACHING_TEXT is missing verbs {missing} — the spec list and "
                f"the build disagree, which the selftest asserts against.")

        for g in extract_guide_strings(html):
            det = run_register_checks(g, verb=None)
            self.guide_audit.append({
                "text": g,
                "findings": [f.render() for f in det],
            })
        caught = sum(1 for r in self.guide_audit if r["findings"])
        self.bb.note("baseline-audit",
                     f"guide() tutorial strings: **{caught}/"
                     f"{len(self.guide_audit)}** fail the register gate — the "
                     f"shipped failure the gate exists to catch")

        if self.skip_baseline:
            self.bb.note("baseline-audit", "--skip-baseline: layer-2 judgment "
                                           "of the stub lines skipped")
        for spec in self.specs:
            line = self.build_lines[spec.verb]
            det = run_register_checks(line, spec.verb)
            judgment = None
            if not det and not self.skip_baseline:
                judgment = run_evaluator(
                    self.llm, self.prompts_dir, spec,
                    self.selections.setdefault(
                        spec.verb, retriever.select_multi(spec.queries)),
                    line, self.register,
                    agent_label=f"ger-evaluator-baseline-{spec.verb}")
            row = {
                "verb": spec.verb, "line": line,
                "layer1": [f.render() for f in det],
                "layer2": None if judgment is None else {
                    "verdict": judgment.verdict, "class": judgment.flag_class,
                    "quoted_chunk": judgment.quoted_chunk,
                    "reason": judgment.reason},
            }
            row["caught"] = bool(det) or (judgment is not None and judgment.failed)
            self.baseline.append(row)
        flagged = sum(1 for r in self.baseline if r["caught"])
        self.bb.note("baseline-audit",
                     f"stub TEACHING_TEXT lines: **{flagged}/"
                     f"{len(self.baseline)}** flagged")
        self._stage("baseline-audit", "OK", t0,
                    f"guide {caught}/{len(self.guide_audit)} caught, "
                    f"stubs {flagged}/{len(self.baseline)} flagged")

    def stage_ger_loop(self, retriever: Retriever) -> None:
        t0 = time.time()
        self.current_stage = "ger-loop"
        self.bb.stage(3, "GER loop (per verb)",
                      f"generate -> evaluate -> (refine -> evaluate) x "
                      f"{self.breaker.max_rounds} -> accept or escalate. Every "
                      f"draft and every finding lands on the blackboard before "
                      f"the next stage reads it.")
        for spec in self.specs:
            selection = self.selections.setdefault(
                spec.verb, retriever.select_multi(spec.queries))
            self.bb.note(
                f"retriever-{spec.verb}",
                "selected " + ", ".join(
                    f"`{r.chunk.doc} §{r.chunk.section}` (bm25 {r.score:.2f})"
                    for r in selection.selected))

            outcome = VerbOutcome(spec.verb, "ACCEPTED")
            line = run_generator(self.llm, self.prompts_dir, spec, selection,
                                 self.register)
            round_no = 0
            while True:
                self.bb.write(f"rounds/{spec.verb}-r{round_no}-draft.json",
                              json.dumps({"verb": spec.verb, "round": round_no,
                                          "line": line}, ensure_ascii=False,
                                         indent=2),
                              f"ger-{'generator' if round_no == 0 else 'refiner'}"
                              f"-{spec.verb}")
                # the Evaluator judges the line it reads off disk
                on_disk = json.loads(self.bb.read(
                    f"rounds/{spec.verb}-r{round_no}-draft.json",
                    f"ger-evaluator-{spec.verb}",
                    f"ger-{'generator' if round_no == 0 else 'refiner'}"
                    f"-{spec.verb}"))["line"]
                findings, judgment = self._evaluate(
                    spec, selection, on_disk, f"(round {round_no})")
                self.bb.write(
                    f"rounds/{spec.verb}-r{round_no}-findings.json",
                    json.dumps({
                        "verb": spec.verb, "round": round_no,
                        "verdict": "PASS" if not findings else "FAIL",
                        "findings": [f.render() for f in findings],
                        "judgment": None if judgment is None else {
                            "verdict": judgment.verdict,
                            "class": judgment.flag_class,
                            "quoted_chunk": judgment.quoted_chunk,
                            "reason": judgment.reason},
                    }, ensure_ascii=False, indent=2),
                    f"ger-evaluator-{spec.verb}")
                outcome.rounds.append(
                    RoundRecord(round_no, on_disk, findings, judgment))

                if not findings:
                    self.bb.note(f"ger-{spec.verb}",
                                 f"**ACCEPTED** at round {round_no} "
                                 f"({outcome.refinements_used} refinement(s))")
                    break
                if not self.breaker.allow_refinement(round_no):
                    self.bb.note(
                        f"circuit-breaker",
                        f"`{spec.verb}` **ESCALATED** — "
                        f"{self.breaker.max_rounds} refinement round(s) spent, "
                        f"still failing ({findings[0].check})")
                    self.breaker.escalate(outcome)   # may raise BreakerTripped
                    break
                line = run_refiner(self.llm, self.prompts_dir, spec, selection,
                                   on_disk, findings, self.register)
                round_no += 1
            self.outcomes.append(outcome)

        accepted = sum(1 for o in self.outcomes if o.status == "ACCEPTED")
        self._stage("ger-loop", "OK", t0,
                    f"{accepted} accepted, {len(self.breaker.escalated)} "
                    f"escalated")

    def stage_assemble(self) -> None:
        t0 = time.time()
        self.current_stage = "assembly"
        self.bb.stage(4, "assembly",
                      "Evidence documents and the drop-in patch, generated "
                      "from this run's data. Deterministic; no LLM.")
        assemble.write_all(self)
        self._stage("assembly", "OK", t0, "evidence documents + snippet + "
                                          "patched build")

    # ---------------- run ----------------

    def run(self) -> int:
        try:
            self.bb.write("CANON-IN-FORCE.md", self.canon.render_in_force(),
                          "canon-bench")
            retriever = self.stage_corpus()
            self.stage_baseline(retriever)
            self.stage_ger_loop(retriever)
            self.stage_assemble()
            self._write_manifest("COMPLETE_PENDING_DIRECTOR")
            self.bb.log("\n**Run complete.** Ends at an unfilled `## Director "
                        "selection` block in teaching-lines.md — the loop "
                        "proposes; the Director applies.\n")
            return 0
        except BreakerTripped as exc:
            # partial evidence is still evidence: write what exists, then halt
            for o in self.breaker.escalated:
                if o not in self.outcomes:
                    self.outcomes.append(o)
            try:
                assemble.write_all(self)
            except Exception:  # noqa: BLE001 — assembly must not mask the trip
                pass
            self._failed("circuit-breaker", self.current_stage, str(exc))
            self._stage(self.current_stage, "TRIPPED", time.time(),
                        str(exc)[:200])
            self._write_manifest("BREAKER_TRIPPED")
            print(f"\n{exc}\n")
            return 1
        except (AgentError, MissingArtifactError, BuildExtractionError) as exc:
            agent = getattr(exc, "agent", None) or getattr(exc, "producer",
                                                           "pipeline")
            self._failed(agent, self.current_stage, str(exc))
            self._stage(self.current_stage, "FAILED", time.time(),
                        str(exc)[:200])
            self._write_manifest("FAILED")
            print(f"\n{exc}\n")
            return 1
        except Exception as exc:  # noqa: BLE001 — nothing escapes as a bare traceback
            self._failed("pipeline", "unknown", traceback.format_exc())
            self._write_manifest("FAILED")
            print(f"\nUNEXPECTED FAILURE: {exc}\nSee out/{self.run_id}/FAILED.md\n")
            return 1
