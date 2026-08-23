"""Orchestrator — dispatch only. GDD §3.1; contract in `prompts/orchestrator.md`.

Deterministic Python, no LLM. It sequences the six stages, verifies the named
artifact after each one, writes `manifest.json` and `RUN-LOG.md`, and on any
failure writes `FAILED.md` naming the agent and the stage. It never reads an
artifact's meaning — existence, size, parse, hash, and that is all.

Canon says it "never gates, never authors, never tunes". The one place that bites
is variant selection: in the real pipeline the Director selects (GDD §3.3,
`MD -->|2-3 variants| D`, `D -->|selects| RT`). An unattended run still needs to
hand the Red-Teamer *a* target, so the Orchestrator applies a documented,
deterministic stand-in — first variant to clear the validation gate, in emitted
order — and records it as `selection.by = "orchestrator-standin"` with
`director_gate: "PENDING"`. It computes no preference between variants and makes
no recommendation. The metrics exist so a human can choose.
"""
from __future__ import annotations

import json
import platform
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

from .agents import AgentError
from .agents.keeper import PROMPT_VERSION as KEEPER_PV, run_keeper_b1, run_keeper_b2
from .agents.mechanic_designer import PROMPT_VERSION as MD_PV, run_mechanic_designer
from .agents.playtester import PROMPT_VERSION as PT_PV, run_playtester
from .agents.red_teamer import PROMPT_VERSION as RT_PV, run_red_teamer
from .blackboard import Blackboard, MissingArtifactError, REPO_ROOT
from .llm import LLMError
from .validate import Validator

DEFAULT_SEEDS = [0, 1, 2, 3, 4, 5, 6, 7]
BASELINE = "rules-v3.10-C.json"   # schema 3.10 control (Run 24): 3.9.1 + default-off temple dials
GDD = "uhta-gdd-v0.9.10-condensed.md"

DEFAULT_GOAL = (
    "Front feel (GDD §6, CANON v17 open questions). metrics-v3.9.1 §E records that "
    "the Grief Front's straggler wear now saturates the +/-1 step cap: an unheld "
    "convert at v=5 fully greys in 5 ticks, ~2.4x the pre-salvage rate, while the "
    "in-sphere stall is exact at 0.000/tick. Propose 2-3 rules variants that soften "
    "unshepherded straggler wear WITHOUT weakening the in-sphere stall and WITHOUT "
    "touching locked canon, so the render can sell one antagonist rather than two."
)

DEFAULT_QUESTIONS = """1. Can straggler wear be brought below the step-cap saturation point while
   `front_strength 4.0` keeps inside-front decay exactly equal to zealot pull
   (2.0/tick)? Which dial does it — front_strength, cooldown, duration, radius, or
   the trigger threshold — and what does each cost?
2. What is the late-game front duty cycle at cooldown 2 (3-on/2-off, measured
   ~0.65 uptime, metrics-v3.9.1 §F), and does a longer cooldown buy legibility
   without making the antagonist a rumour?
3. Does any proposed change re-open a closure the Run-23b salvage bought — the
   GF6 siege engine (spawn anchor), the GF5 hover-sprint shadow (trailing window),
   or the cleanup-assist (affects_dominant_pole_only)?
4. Locked and out of scope: the grief canon itself (CANON ruling 6 — grief wears
   the dominant pole and never recruits for the opposite), zealot immunity,
   `win_loss` in all its parts, the scale and bands, and `hope_trade` (stays
   disabled)."""


@dataclass
class RunContext:
    run_id: str
    goal: str
    question_set: str
    seeds: list[int]
    version_tag: str
    prompts_dir: Path
    baseline_name: str = BASELINE
    gdd_name: str = GDD
    selected_variant_name: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def packet_name(self) -> str:
        return f"packet-mechanic-designer-{self.version_tag}.md"

    @property
    def rationale_name(self) -> str:
        return "designer-rationale.md"

    @property
    def attacks_md_name(self) -> str:
        return f"attacks-{self.version_tag}.md"

    @property
    def attacks_json_name(self) -> str:
        return "attacks.json"

    @property
    def metrics_name(self) -> str:
        return f"metrics-{self.version_tag}.md"

    @property
    def contradictions_name(self) -> str:
        return f"contradictions-{self.run_id}.md"

    def variant_name(self, letter: str) -> str:
        return f"rules-{self.version_tag}-{letter}.json"


class Orchestrator:
    DROPPABLE = ("keeper-b1", "mechanic-designer", "red-teamer", "playtester",
                 "keeper-b2")

    def __init__(self, llm, mode: str, run_id: str | None = None,
                 goal: str | None = None, questions: str | None = None,
                 seeds: list[int] | None = None, root: Path | None = None,
                 version_tag: str = "v3.9.2", drop_agent: str | None = None):
        self.root = Path(root) if root else REPO_ROOT
        self.mode = mode
        self.drop_agent = drop_agent
        self.llm = llm
        self.run_id = run_id or f"run-{time.strftime('%Y%m%d-%H%M%S')}-{mode}"
        self.bb = Blackboard(self.run_id, root=self.root)
        self.ctx = RunContext(
            run_id=self.run_id,
            goal=(goal or DEFAULT_GOAL).strip(),
            question_set=(questions or DEFAULT_QUESTIONS).strip(),
            seeds=list(seeds or DEFAULT_SEEDS),
            version_tag=version_tag,
            prompts_dir=self.root / "prompts",
        )
        self.validator = Validator(self.bb.bb_path(f"rules/{BASELINE}"),
                                   self.bb.bb_path("sim"))
        self.stages: list[dict] = []
        self.selection: dict = {}

    # ---------------- manifest ----------------

    def _manifest(self, status: str) -> dict:
        return {
            "run_id": self.run_id,
            "status": status,
            "mode": self.mode,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": getattr(self.llm, "model", "n/a"),
            "llm_backend": getattr(self.llm, "name", "n/a"),
            "llm_calls": getattr(self.llm, "calls", 0),
            "llm_tokens": {"input": getattr(self.llm, "input_tokens", 0),
                           "output": getattr(self.llm, "output_tokens", 0)},
            "python": platform.python_version(),
            "director_goal": self.ctx.goal,
            "question_set": self.ctx.question_set,
            "seed_list": self.ctx.seeds,
            "baseline_ruleset": self.ctx.baseline_name,
            "gdd": self.ctx.gdd_name,
            "validation_gate": {
                "kind": "deterministic",
                "required_key_paths_derived_from": self.ctx.baseline_name,
                "required_key_path_count": len(self.validator.required),
                "repair_round_trips_allowed": 1,
            },
            "prompt_versions": {
                "keeper": KEEPER_PV, "mechanic-designer": MD_PV,
                "red-teamer": RT_PV, "playtester": PT_PV,
                "orchestrator": "orchestrator v1 (crew port, no LLM)",
            },
            "selection": self.selection,
            "director_gate": "PENDING",
            "stages": self.stages,
            "artifact_sha256": self.bb.artifact_hashes(),
            "blackboard_ledger": self.bb.ledger_json(),
        }

    def _write_manifest(self, status: str) -> None:
        (self.bb.run_dir / "manifest.json").write_text(
            json.dumps(self._manifest(status), indent=2) + "\n", encoding="utf-8")

    def _verify(self, stage: str, agent: str, artifacts: list[str]) -> None:
        """Artifact verification. Existence + non-empty + (for .json) parses."""
        for a in artifacts:
            p = self.bb.path(a)
            if not p.exists() or p.stat().st_size == 0:
                raise MissingArtifactError(f"out/{self.run_id}/{a}", agent, "orchestrator")
            if a.endswith(".json"):
                try:
                    json.loads(p.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    raise AgentError(agent, f"{a} is not parseable JSON: {exc}") from exc
        self.bb.note("orchestrator",
                     f"artifact verification for stage `{stage}`: OK — "
                     + ", ".join(f"`{a}`" for a in artifacts))

    def _stage(self, n: int, name: str, agent: str, fn, artifacts: list[str]):
        if self.drop_agent == agent:
            self.bb.stage(n, agent,
                          f"**{name} — AGENT REMOVED (`--drop-agent {agent}`).** "
                          f"The Orchestrator did not dispatch it. Expected "
                          f"artifact(s) will not exist: "
                          + ", ".join(f"`{a}`" for a in artifacts)
                          + "\n\nThis is the role-clarity demonstration: the next "
                            "agent that needs one of these files halts the pipeline "
                            "and names this one.")
            self.stages.append({"n": n, "stage": name, "agent": agent,
                                "status": "SKIPPED (--drop-agent)", "seconds": 0.0,
                                "artifacts": artifacts})
            return None
        self.bb.stage(n, agent, f"**{name}** — dispatched by the Orchestrator. "
                                f"Expected artifact(s): "
                                + ", ".join(f"`{a}`" for a in artifacts))
        t0 = time.time()
        try:
            result = fn()
            self._verify(name, agent, artifacts)
        except Exception:
            self.stages.append({"n": n, "stage": name, "agent": agent,
                                "status": "FAILED", "seconds": round(time.time() - t0, 2),
                                "artifacts": artifacts})
            raise
        self.stages.append({"n": n, "stage": name, "agent": agent, "status": "OK",
                            "seconds": round(time.time() - t0, 2),
                            "artifacts": artifacts})
        return result

    # ---------------- the pipeline ----------------

    def run(self) -> int:
        self.bb.log(
            f"\n**Director goal.**\n\n> {self.ctx.goal}\n\n"
            f"**Question set.**\n\n```\n{self.ctx.question_set}\n```\n\n"
            f"**Mode:** `{self.mode}` · **Model:** `{getattr(self.llm, 'model', 'n/a')}` "
            f"· **Seeds:** `{self.ctx.seeds}` · **Baseline:** `{self.ctx.baseline_name}`\n"
        )
        if self.mode == "mock":
            self.bb.log(
                "\n> **MOCK-LLM RUN — TEST FIXTURE, NOT DESIGN WORK.** No API calls "
                "were made. Every agent response in this run was replayed verbatim "
                "from `tests/fixtures/`. The orchestration, the blackboard, the "
                "validation gate and the harness executions are all real; the "
                "*judgement* is not, and nothing in `out/` from a mock run is "
                "evidence about uhta.\n"
            )
        try:
            # 1 -------------------------------------------------- Keeper B1
            self._stage(1, "keeper_b1", "keeper-b1",
                        lambda: run_keeper_b1(self.bb, self.llm, self.ctx),
                        [self.ctx.packet_name])

            # 2 -------------------------------------- Mechanic Designer (+gate)
            design = self._stage(
                2, "mechanic_designer", "mechanic-designer",
                lambda: run_mechanic_designer(self.bb, self.llm, self.ctx, self.validator),
                [self.ctx.rationale_name, "validation.json"])
            if design is None:   # --drop-agent mechanic-designer
                design = {"valid": [], "all": [], "attempts": []}
                raise MissingArtifactError(
                    f"out/{self.run_id}/{self.ctx.variant_name('A')}",
                    "mechanic-designer", "validation-gate")
            valid = [Path(r.path).name for r in design["valid"]]

            # 3 ------------------------------------------- validation gate report
            self.stages.append({
                "n": 3, "stage": "validation_gate", "agent": "(deterministic)",
                "status": "OK", "seconds": 0.0,
                "artifacts": ["validation.json"] + valid,
                "detail": {
                    "required_key_paths": len(self.validator.required),
                    "attempts": len(design["attempts"]),
                    "accepted": valid,
                    "rejected": [r.variant for r in design["all"] if not r.ok],
                },
            })
            self.bb.note("validation-gate",
                         f"GATE PASSED — {len(valid)} variant(s) cleared all three checks "
                         f"(parse, {len(self.validator.required)} baseline-derived key "
                         f"paths, harness load+smoke): {', '.join(valid)}")

            # --- stand-in selection (see class docstring) ---
            self.ctx.selected_variant_name = valid[0]
            self.selection = {
                "selected_variant": valid[0],
                "by": "orchestrator-standin",
                "rule": "first variant to clear the deterministic validation gate, "
                        "in the order the Designer emitted them",
                "note": "In the real pipeline the human Director selects (GDD §3.3). "
                        "This is a placeholder so an unattended run has a Red-Team "
                        "target; it expresses no preference between variants.",
                "director_gate": "PENDING",
                "candidates": valid,
            }
            self.bb.note("orchestrator",
                         f"stand-in selection for the Red-Teamer: `{valid[0]}` "
                         f"(rule: first gate-passing variant). Director gate: PENDING.")

            # 4 -------------------------------------------------- Red-Teamer
            self._stage(4, "red_teamer", "red-teamer",
                        lambda: run_red_teamer(self.bb, self.llm, self.ctx,
                                               self.ctx.selected_variant_name),
                        [self.ctx.attacks_md_name, self.ctx.attacks_json_name])

            # 5 --------------------------------------------------- Playtester
            self._stage(5, "playtester", "playtester",
                        lambda: run_playtester(self.bb, self.llm, self.ctx, valid),
                        [self.ctx.metrics_name, "execution-log.json"])

            # 6 -------------------------------------------------- Keeper B2
            self._stage(6, "keeper_b2", "keeper-b2",
                        lambda: run_keeper_b2(self.bb, self.llm, self.ctx),
                        [self.ctx.contradictions_name])

            # 7 ------------------------------------------------ Director gate
            # The Orchestrator's definition of done (GDD §3.1): "the named artifact
            # exists AND the Director has it stapled to its Keeper diff." So the
            # gate bundle is verified as a unit -- which is what makes Keeper-B2
            # non-removable even though nothing downstream of it is automated.
            bundle = [self.ctx.selected_variant_name, self.ctx.metrics_name,
                      self.ctx.attacks_md_name, self.ctx.contradictions_name]
            for a, producer in zip(bundle, ["mechanic-designer", "playtester",
                                            "red-teamer", "keeper-b2"]):
                if not self.bb.exists(a):
                    raise MissingArtifactError(f"out/{self.run_id}/{a}", producer,
                                               "director-gate")
            self.bb.note("orchestrator",
                         "Director-gate bundle verified: proposal + attacks + metrics "
                         "+ Keeper diff. The diff is stapled above the proposal, per "
                         "GDD §3.2 — the Director never sees a proposal without it.")
            self.stages.append({
                "n": 7, "stage": "director_gate", "agent": "Director (human)",
                "status": "PENDING", "seconds": 0.0,
                "artifacts": [self.ctx.contradictions_name],
                "detail": "Outside this crew. The Director fills the `## Ruling` block "
                          "in the contradiction report with UPHOLD / AMEND / DEFER, "
                          "and selects the variant to ratify.",
            })
            self._write_manifest("COMPLETE_PENDING_DIRECTOR")
            self.bb.log(
                f"\n---\n\n## Run complete — pending the Director gate\n\n"
                f"All six agent stages produced their artifacts. Stage 7 (the Director "
                f"gate) is human and is not part of this crew: open "
                f"`{self.ctx.contradictions_name}`, fill the `## Ruling` block, and "
                f"select the variant to ratify.\n"
            )
            return 0

        except (MissingArtifactError, AgentError, LLMError) as exc:
            agent = getattr(exc, "consumer", None) or getattr(exc, "agent", None)
            if agent is None and isinstance(exc, LLMError):
                agent = str(exc).split(":", 1)[0].strip() or "unknown"
            agent = agent or "unknown"
            missing_from = getattr(exc, "producer", None)
            stage = self.stages[-1]["stage"] if self.stages else "startup"
            self.bb.write_failed(missing_from or agent, stage, str(exc))
            self._write_manifest("FAILED")
            print(f"\n{'='*72}\nPIPELINE HALTED\n{'='*72}\n{exc}\n"
                  f"\nWrote out/{self.run_id}/FAILED.md\n", flush=True)
            return 1
        except Exception as exc:  # noqa: BLE001 — never surface a raw traceback
            stage = self.stages[-1]["stage"] if self.stages else "startup"
            self.bb.write_failed("unknown", stage,
                                 f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}")
            self._write_manifest("FAILED")
            print(f"\n{'='*72}\nPIPELINE HALTED (unexpected)\n{'='*72}\n"
                  f"{type(exc).__name__}: {exc}\n"
                  f"\nFull traceback in out/{self.run_id}/FAILED.md\n", flush=True)
            return 1
