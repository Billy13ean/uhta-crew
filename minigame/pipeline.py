"""Mini-game pipeline orchestration — deterministic, no LLM in this module.

Two entry points, separated by the human gate:

    MinigamePipeline(...).propose()   corpus -> GER loop -> candidates doc.
                                      ENDS at the Director selection block.
    MinigamePipeline(...).build(...)  requires the Director's typed ruling
                                      (--select, --from-run) -> Programmer ->
                                      anchored patch -> post-checks -> the
                                      Director applies by hand.

Every arrow is a file; the Judge reads each candidate off disk, as in ger/.
"""
from __future__ import annotations

import json
import platform
import time
import traceback
from pathlib import Path

from content.agents import AgentError
from content.retriever import (SCORE_THRESHOLD, TOKEN_BUDGET, Retriever)
from crew.blackboard import Blackboard, MissingArtifactError
from ger.breaker import (BreakerTripped, CircuitBreaker, RoundRecord,
                         VerbOutcome)

from . import PIPELINE_VERSION, assemble
from .agents import (EVALUATOR_PV, GENERATOR_PV, REFINER_PV, run_designer,
                     run_judge, run_mg_refiner)
from .builder_stage import (PROGRAMMER_PV, build_and_check, node_available,
                            playwright_available, run_play_probe,
                            run_programmer)
from .instructor import INSTRUCTOR_PV, run_instructor
from .presenter import PRESENTER_PV, run_presenter
from .checks import (BuildAnchorError, extract_anchors, run_design_checks)
from .corpus import CORPUS_FILES, MINIGAME_POLICY, build_minigame_corpus
from .spec import SLOT_IDS, SLOT_SPECS

BUILD_REL = "build/uhta-slice.html"


class MinigamePipeline:
    def __init__(self, llm, mode: str, root: Path, run_id: str | None = None,
                 slot_filter: list[str] | None = None,
                 max_rounds: int | None = None,
                 escalation_limit: int | None = None):
        self.llm = llm
        self.mode = mode
        self.root = Path(root)
        self.run_id = run_id or f"mg-{time.strftime('%Y%m%d-%H%M%S')}-{mode}"
        self.bb = Blackboard(self.run_id, root=self.root)
        self.prompts_dir = self.root / "prompts"
        self.specs = [s for s in SLOT_SPECS
                      if not slot_filter or s.id in slot_filter]
        kwargs = {}
        if max_rounds is not None:
            kwargs["max_rounds"] = max_rounds
        if escalation_limit is not None:
            kwargs["escalation_limit"] = escalation_limit
        self.breaker = CircuitBreaker(**kwargs)

        self.current_stage = "corpus"
        self.stages: list[dict] = []
        self.corpus_stats: dict = {}
        self.outcomes: list[VerbOutcome] = []
        self.accepted: dict[str, dict] = {}     # slot id -> design
        self.selections: dict[str, object] = {}
        self.build_report: dict = {}
        self.instructions: dict = {}
        self.presentation: dict = {}

    # ---------------- bookkeeping ----------------

    def _stage(self, name: str, status: str, t0: float, detail: str = "") -> None:
        self.stages.append({"stage": name, "status": status,
                            "seconds": round(time.time() - t0, 2),
                            "detail": detail})

    def _manifest(self, status: str, phase: str) -> dict:
        return {
            "run_id": self.run_id,
            "pipeline": "minigame (Assignment 6 #2 — GER + human gate + "
                        "Programmer)",
            "pipeline_version": PIPELINE_VERSION,
            "phase": phase,
            "status": status,
            "mode": self.mode,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": getattr(self.llm, "model", "n/a"),
            "llm_backend": getattr(self.llm, "name", "n/a"),
            "llm_calls": getattr(self.llm, "calls", 0),
            "llm_tokens": {"input": getattr(self.llm, "input_tokens", 0),
                           "output": getattr(self.llm, "output_tokens", 0)},
            "python": platform.python_version(),
            "content_type": "encounter mini-game designs (GDD §2 PROPOSED "
                            "tier: three encounters x two poles)",
            "rule_enforced": "GDD §2 encounter rules — wordless/diegetic "
                             "('no interface, no text, only your body and "
                             "theirs'), pole asymmetry ('the two poles never "
                             "play the same game'), individual-scale",
            "slots": [s.id for s in self.specs],
            "corpus": self.corpus_stats,
            "retrieval": {"scorer": "BM25 (content/retriever.py, reused)",
                          "score_threshold": SCORE_THRESHOLD,
                          "token_budget": TOKEN_BUDGET,
                          "selection_rule": "three queries per slot "
                                            "(encounter, mechanics, pattern), "
                                            "unioned — the §4.5 rule extended"},
            "prompt_versions": {"designer": GENERATOR_PV, "judge": EVALUATOR_PV,
                                "refiner": REFINER_PV,
                                "programmer": PROGRAMMER_PV,
                                "instructor": INSTRUCTOR_PV,
                                "presenter": PRESENTER_PV,
                                "pipeline": PIPELINE_VERSION},
            "breaker": self.breaker.summary(),
            "outcomes": [{"slot": o.verb, "status": o.status,
                          "refinements_used": o.refinements_used}
                         for o in self.outcomes],
            "build": self.build_report,
            "director_gate": "PROPOSE ENDS AT SELECTION; BUILD REQUIRES "
                             "--select — the gate is structural",
            "stages": self.stages,
            "artifact_sha256": self.bb.artifact_hashes(),
            "blackboard_ledger": self.bb.ledger_json(),
        }

    def _write_manifest(self, status: str, phase: str) -> None:
        (self.bb.run_dir / "manifest.json").write_text(
            json.dumps(self._manifest(status, phase), indent=2) + "\n",
            encoding="utf-8")

    def _failed(self, agent: str, stage: str, error: str) -> None:
        body = (
            f"# FAILED — {self.run_id}\n\n"
            f"| field | value |\n|---|---|\n"
            f"| pipeline | minigame (Assignment 6 #2) |\n"
            f"| agent | **{agent}** |\n"
            f"| stage | **{stage}** |\n"
            f"| time | {time.strftime('%Y-%m-%d %H:%M:%S')} |\n\n"
            f"## Error\n\n```\n{error}\n```\n\n"
            f"See RUN-LOG.md for the trail; runs are independent — fix and "
            f"re-run.\n")
        (self.bb.run_dir / "FAILED.md").write_text(body, encoding="utf-8")
        self.bb.log(f"\n**FAILED.md written** — agent=`{agent}` "
                    f"stage=`{stage}`\n")

    # ---------------- shared: corpus ----------------

    def stage_corpus(self) -> Retriever:
        t0 = time.time()
        self.current_stage = "corpus"
        self.bb.stage(1, "corpus",
                      "Chunk three documents under the PER-DOC policy "
                      "(v0.9.9 game sections + v0.9.7 §2 mechanics + the "
                      "seeded mini-game patterns research doc), build the "
                      "BM25 index. Deterministic; no LLM.")
        docs = {name: self.bb.read_bb(rel, "corpus")
                for name, rel in CORPUS_FILES.items()}
        all_chunks, dropped, kept = build_minigame_corpus(docs)
        if not kept:
            raise MissingArtifactError("minigame corpus", "blackboard seeding",
                                       "corpus")
        self.corpus_stats = {
            "files": list(CORPUS_FILES),
            "policy": MINIGAME_POLICY["name"],
            "chunks_indexed": len(kept),
            "chunks_excluded": len(dropped),
            "words_indexed": sum(c.words for c in kept),
            "exclusions": [{"key": d.key, "reason": d.reason}
                           for d in dropped],
        }
        self.bb.note("corpus", f"indexed **{len(kept)}** chunks; excluded "
                               f"**{len(dropped)}**, each with a reason "
                               f"(policy `{MINIGAME_POLICY['name']}`)")
        self._stage("corpus", "OK", t0, f"{len(kept)} in / {len(dropped)} out")
        return Retriever(kept)

    # ---------------- propose ----------------

    def _evaluate(self, spec, selection, cand: dict, label: str):
        det = run_design_checks(cand)
        if det:
            self.bb.note(f"mg-judge-{spec.id}",
                         f"layer-1 design gate: **{len(det)} finding(s)** "
                         f"{label} — design never reached the LLM judge")
            return det, None
        judgment = run_judge(self.llm, self.prompts_dir, spec, selection, cand)
        if judgment.failed:
            return [judgment.finding()], judgment
        return [], judgment

    def stage_ger_loop(self, retriever: Retriever) -> None:
        t0 = time.time()
        self.current_stage = "ger-loop"
        self.bb.stage(2, "GER loop (per encounter slot)",
                      f"design -> evaluate -> (refine -> evaluate) x "
                      f"{self.breaker.max_rounds} -> accept or escalate. "
                      f"Every draft and every finding lands on the "
                      f"blackboard before the next stage reads it.")
        for spec in self.specs:
            selection = self.selections.setdefault(
                spec.id, retriever.select_multi(spec.queries))
            self.bb.note(
                f"retriever-{spec.id}",
                "selected " + (", ".join(
                    f"`{r.chunk.doc} §{r.chunk.section}` (bm25 {r.score:.2f})"
                    for r in selection.selected) or "(nothing)"))

            outcome = VerbOutcome(spec.id, "ACCEPTED")
            cand = run_designer(self.llm, self.prompts_dir, spec, selection)
            round_no = 0
            while True:
                src = "designer" if round_no == 0 else "refiner"
                self.bb.write(f"rounds/{spec.id}-r{round_no}-draft.json",
                              json.dumps(cand, ensure_ascii=False, indent=2),
                              f"mg-{src}-{spec.id}")
                on_disk = json.loads(self.bb.read(
                    f"rounds/{spec.id}-r{round_no}-draft.json",
                    f"mg-judge-{spec.id}", f"mg-{src}-{spec.id}"))
                findings, judgment = self._evaluate(
                    spec, selection, on_disk, f"(round {round_no})")
                self.bb.write(
                    f"rounds/{spec.id}-r{round_no}-findings.json",
                    json.dumps({
                        "slot": spec.id, "round": round_no,
                        "verdict": "PASS" if not findings else "FAIL",
                        "findings": [f.render() for f in findings],
                    }, ensure_ascii=False, indent=2),
                    f"mg-judge-{spec.id}")
                outcome.rounds.append(
                    RoundRecord(round_no, json.dumps(on_disk,
                                                     ensure_ascii=False),
                                findings, judgment))

                if not findings:
                    self.accepted[spec.id] = on_disk
                    self.bb.note(f"mg-{spec.id}",
                                 f"**ACCEPTED** at round {round_no} "
                                 f"({outcome.refinements_used} refinement(s))")
                    break
                if not self.breaker.allow_refinement(round_no):
                    self.bb.note("circuit-breaker",
                                 f"`{spec.id}` **ESCALATED** — "
                                 f"{self.breaker.max_rounds} refinement "
                                 f"round(s) spent, still failing "
                                 f"({findings[0].check})")
                    self.breaker.escalate(outcome)
                    break
                cand = run_mg_refiner(self.llm, self.prompts_dir, spec,
                                      selection, on_disk, findings)
                round_no += 1
            self.outcomes.append(outcome)
        self._stage("ger-loop", "OK", t0,
                    f"{len(self.accepted)} accepted, "
                    f"{len(self.breaker.escalated)} escalated")

    def propose(self) -> int:
        try:
            retriever = self.stage_corpus()
            self.stage_ger_loop(retriever)
            t0 = time.time()
            self.current_stage = "assembly"
            self.bb.stage(3, "assembly",
                          "Candidates document + evidence. Deterministic; "
                          "no LLM. The run ENDS here, at the Director gate.")
            assemble.write_propose(self)
            self._stage("assembly", "OK", t0, "candidates + evidence")
            self._write_manifest("COMPLETE_AWAITING_DIRECTOR_SELECTION",
                                 "propose")
            self.bb.log("\n**Propose run complete.** Nothing was built. The "
                        "Director rules in MINIGAME-CANDIDATES.md, then:\n"
                        f"`python3 run_minigame.py --build --select <id> "
                        f"--from-run {self.run_id}`\n")
            return 0
        except BreakerTripped as exc:
            for o in self.breaker.escalated:
                if o not in self.outcomes:
                    self.outcomes.append(o)
            try:
                assemble.write_propose(self)
            except Exception:  # noqa: BLE001
                pass
            self._failed("circuit-breaker", self.current_stage, str(exc))
            self._write_manifest("BREAKER_TRIPPED", "propose")
            print(f"\n{exc}\n")
            return 1
        except (AgentError, MissingArtifactError) as exc:
            agent = getattr(exc, "agent", None) or getattr(exc, "producer",
                                                           "pipeline")
            self._failed(agent, self.current_stage, str(exc))
            self._write_manifest("FAILED", "propose")
            print(f"\n{exc}\n")
            return 1
        except Exception as exc:  # noqa: BLE001
            self._failed("pipeline", "unknown", traceback.format_exc())
            self._write_manifest("FAILED", "propose")
            print(f"\nUNEXPECTED FAILURE: {exc}\n"
                  f"See out/{self.run_id}/FAILED.md\n")
            return 1

    # ---------------- build (after the human gate) ----------------

    def load_selection(self, from_run: str, select_id: str) -> dict:
        path = self.root / "out" / from_run / "CANDIDATES.json"
        if not path.exists():
            raise MissingArtifactError(f"out/{from_run}/CANDIDATES.json",
                                       "a completed propose run",
                                       "build stage")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.bb.note("director-gate",
                     f"selection `{select_id}` from `out/{from_run}/"
                     f"CANDIDATES.json` — the human gate: this command line "
                     f"IS the Director's ruling")
        designs = {d["id"]: d for d in data.get("accepted", [])}
        if select_id not in designs:
            raise AgentError(
                "director-gate",
                f"--select {select_id!r} is not an ACCEPTED candidate of run "
                f"{from_run!r}. Accepted: {sorted(designs) or '(none)'}. "
                f"Escalated designs cannot be built — that is the gate "
                f"working, not a bug.")
        return designs[select_id]

    def build(self, from_run: str, select_id: str) -> int:
        try:
            t0 = time.time()
            self.current_stage = "director-gate"
            self.bb.stage(1, "director gate",
                          "Load the Director-selected design from the "
                          "propose run. No selection, no build.")
            design = self.load_selection(from_run, select_id)
            self.bb.write("SELECTED-DESIGN.json",
                          json.dumps(design, ensure_ascii=False, indent=2),
                          "director-gate")
            self._stage("director-gate", "OK", t0, select_id)

            # ---- build v2: the Writer's and Aesthetic Director's seats ----
            t0 = time.time()
            self.current_stage = "instructor"
            self.bb.stage(2, "instructor (Writer's seat, GDD §5)",
                          "One first-use narration line, held to the same "
                          "register gate as the game's verb narration "
                          "(ger.checks, reused). Displays once, sleep 0.")
            self.instructions = run_instructor(self.llm, self.prompts_dir,
                                               design)
            self.bb.write("instructions.json",
                          json.dumps(self.instructions, ensure_ascii=False,
                                     indent=2), "mg-instructor")
            self.bb.note("mg-instructor",
                         f"line accepted "
                         f"({self.instructions['repair_rounds']} repair): "
                         f"\"{self.instructions['first_use_line']}\"")
            self._stage("instructor", "OK", t0)

            t0 = time.time()
            self.current_stage = "presenter"
            self.bb.stage(3, "presenter (Aesthetic Director's seat, GDD §5)",
                          "The diegetic presentation spec: attention cue, "
                          "pausing entry transition, visual hierarchy, "
                          "signal map, feedback. Render language only.")
            self.presentation = run_presenter(self.llm, self.prompts_dir,
                                              design)
            self.bb.write("presentation.json",
                          json.dumps(self.presentation, ensure_ascii=False,
                                     indent=2), "mg-presenter")
            self.bb.note("mg-presenter",
                         f"spec accepted "
                         f"({self.presentation.get('repair_rounds', 0)} "
                         f"repair) — entry: "
                         f"{str(self.presentation['entry_transition'])[:90]}…")
            self._stage("presenter", "OK", t0)

            t0 = time.time()
            self.current_stage = "programmer"
            self.bb.stage(4, "programmer",
                          "Anchored patch under the A5 contract: three "
                          "inserts, new M-assertions, every G-assertion "
                          "survives, node parse check "
                          f"({'node present' if node_available() else 'node ABSENT — brace-balance fallback'}).")
            html = self.bb.read_bb(BUILD_REL, "mg-programmer")
            anchors = extract_anchors(html)
            for name, line in anchors.items():
                self.bb.note("anchors", f"{name}: `{line[:70]}…`" if
                             len(line) > 70 else f"{name}: `{line}`")

            probe_status = "not run"

            def _attempt(patch: dict, n: int):
                nonlocal probe_status
                self.bb.write(f"patch-attempt-{n}.json",
                              json.dumps(patch, ensure_ascii=False, indent=2),
                              "mg-programmer")
                patched, checks, errors = build_and_check(
                    html, anchors, patch, instructions=self.instructions)
                if errors:
                    return patched, checks, errors
                # static checks green -> the Playtester's seat: PLAY it.
                if self.mode != "live":
                    probe_status = ("SKIPPED: mock fixture patch is not a "
                                    "playable game; the probe gates live "
                                    "builds")
                    self.bb.note("mg-play-probe", probe_status)
                    return patched, checks, errors
                cand = self.bb.run_dir / f"probe-candidate-{n}.html"
                cand.write_text(patched, encoding="utf-8")
                pchecks, perrors, probe_status = run_play_probe(
                    self.root, cand,
                    str(self.instructions.get("first_use_line", "")))
                checks.update(pchecks)
                errors.extend(perrors)
                self.bb.note(
                    "mg-play-probe",
                    f"attempt {n}: {probe_status}"
                    + ("" if not pchecks else
                       f" — {sum(1 for v in pchecks.values() if v)}/"
                       f"{len(pchecks)} probe checks passed"))
                return patched, checks, errors

            patch = run_programmer(self.llm, self.prompts_dir, design,
                                   anchors, html,
                                   instructions=self.instructions,
                                   presentation=self.presentation)
            patched, checks, errors = _attempt(patch, 1)
            repair_rounds = 0
            if errors:
                repair_rounds = 1
                self.bb.note("mg-programmer",
                             f"post-checks FAILED ({'; '.join(errors)[:160]}) "
                             f"— one repair round-trip")
                patch = run_programmer(self.llm, self.prompts_dir, design,
                                       anchors, html,
                                       instructions=self.instructions,
                                       presentation=self.presentation,
                                       repair_error="\n".join(errors))
                patched, checks, errors = _attempt(patch, 2)
                if errors:
                    raise AgentError(
                        "mg-programmer",
                        "patch failed post-checks twice: "
                        + "; ".join(errors))

            (self.bb.run_dir / "uhta-slice.minigame.patched.html").write_text(
                patched, encoding="utf-8")
            self.bb.note("mg-programmer",
                         f"**WRITE** `out/{self.run_id}/"
                         f"uhta-slice.minigame.patched.html` "
                         f"({len(patched)} B) — all post-checks passed")
            self.build_report = {
                "selected": select_id, "from_run": from_run,
                "checks": checks, "repair_rounds": repair_rounds,
                "node_available": node_available(),
                "play_probe": probe_status,
                "playwright_available": playwright_available(),
                "first_use_line": self.instructions.get("first_use_line"),
                "instructor_repairs":
                    self.instructions.get("repair_rounds", 0),
                "presenter_repairs":
                    self.presentation.get("repair_rounds", 0),
            }
            self._stage("programmer", "OK", t0,
                        f"{repair_rounds} repair round(s)")

            t0 = time.time()
            self.current_stage = "assembly"
            assemble.write_build(self, design, patch)
            self._stage("assembly", "OK", t0)
            self._write_manifest("COMPLETE_PENDING_DIRECTOR_APPLY", "build")
            self.bb.log("\n**Build run complete.** The in-place build was "
                        "not touched — apply and verify per "
                        "MINIGAME-BUILD.md.\n")
            return 0
        except (AgentError, MissingArtifactError, BuildAnchorError) as exc:
            agent = getattr(exc, "agent", None) or getattr(exc, "producer",
                                                           "pipeline")
            self._failed(agent, self.current_stage, str(exc))
            self._write_manifest("FAILED", "build")
            print(f"\n{exc}\n")
            return 1
        except Exception as exc:  # noqa: BLE001
            self._failed("pipeline", "unknown", traceback.format_exc())
            self._write_manifest("FAILED", "build")
            print(f"\nUNEXPECTED FAILURE: {exc}\n"
                  f"See out/{self.run_id}/FAILED.md\n")
            return 1
