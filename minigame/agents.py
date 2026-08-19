"""The mini-game pipeline's three LLM roles: Designer, Judge, Refiner.

Same GER separation as ger/: the Judge diagnoses and cannot repair (a
`correction` key halts); the Refiner repairs exactly the findings and cannot
no-op; every FAIL is cited to a retrieved chunk or it halts. The Programmer
(build stage) lives in builder_stage.py because it runs on the far side of
the human gate.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from content.agents import AgentError, parse_json_payload, render_chunks
from crew.llm import LLMCall

from .checks import Finding
from .spec import ALLOWED_INPUTS, ENCOUNTER_RULES, OUTCOME_EFFECTS

GENERATOR_PV = "minigame-designer v1 (Assignment 6 #2)"
EVALUATOR_PV = "minigame-judge v1 (Assignment 6 #2)"
REFINER_PV = "minigame-refiner v1 (Assignment 6 #2)"

VALID_CLASSES = {"NOT-DIEGETIC", "POLE-SYMMETRY", "CONTRADICTS-CHUNK",
                 "EXCEEDS-SCOPE", "GENERIC"}


def _template(prompts_dir: Path, name: str) -> str:
    text = (prompts_dir / name).read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def _common(template: str, spec, selection) -> str:
    # The law the three roles argue under comes through the canon bench:
    # an AMENDED encounter rule reaches every prompt from here, and the
    # same effective text the Judge cites is what the run's
    # CANON-IN-FORCE.md records.
    from crew.canon import get_canon
    canon = get_canon()
    return (template
            .replace("{{SLOT_ID}}", spec.id)
            .replace("{{SLOT_LABEL}}", spec.label)
            .replace("{{BRIEF}}", spec.brief)
            .replace("{{RULES}}", canon.text("mg-encounter-rules",
                                             ENCOUNTER_RULES))
            .replace("{{ALLOWED_INPUTS}}", json.dumps(
                canon.param("mg-allowed-inputs", "allowed_inputs",
                            ALLOWED_INPUTS)))
            .replace("{{OUTCOME_EFFECTS}}", json.dumps(
                canon.param("mg-outcome-effects", "outcome_effects",
                            OUTCOME_EFFECTS)))
            .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection)))


# ---------------- Designer (the Generator) ----------------

def run_designer(llm, prompts_dir: Path, spec, selection,
                 agent_label: str | None = None) -> dict:
    agent = agent_label or f"mg-designer-{spec.id}"
    if not selection.selected:
        raise AgentError(
            agent,
            f"slot '{spec.id}' retrieved no chunks above the score threshold "
            f"— designing from an empty corpus cut is the invented-canon "
            f"failure this crew's pipelines exist to prevent.")
    user = _common(_template(prompts_dir, "minigame-designer.md"),
                   spec, selection)
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You design encounter mini-games for uhta, a wordless "
                "browser god-game about emotional contagion. You design only "
                "from the GDD and pattern chunks you are given."),
        user=user, temperature=0.9, max_tokens=1600,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected a single JSON design object, got "
                                f"{type(payload).__name__}")
    # The slot is the PIPELINE'S choice, not the model's — pin it, so a
    # cosmetic variant ("First contact"/"Hope") can never fail C2. Caught by
    # the first live run: the gate halted on capitalisation, which is a
    # schema formality, not a design defect.
    payload["id"] = spec.id
    payload["encounter"] = spec.encounter
    payload["pole"] = spec.pole
    return payload


# ---------------- Judge (the LLM Evaluator, layer 2) ----------------

@dataclass
class Judgment:
    verdict: str
    flag_class: str | None
    quoted_chunk: str
    reason: str

    @property
    def failed(self) -> bool:
        return self.verdict == "FAIL"

    def finding(self) -> Finding:
        return Finding("llm", self.flag_class or "PASS", self.reason,
                       self.quoted_chunk)


def render_candidate(cand: dict) -> str:
    return json.dumps(cand, ensure_ascii=False, indent=2)


def run_judge(llm, prompts_dir: Path, spec, selection, cand: dict,
              agent_label: str | None = None) -> Judgment:
    agent = agent_label or f"mg-judge-{spec.id}"
    user = (_common(_template(prompts_dir, "minigame-judge.md"),
                    spec, selection)
            .replace("{{CANDIDATE}}", render_candidate(cand)))
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Judge in uhta's mini-game GER loop: an "
                "adversarial evaluator of one encounter design at a time, "
                "enforcing the GDD's encounter rules. You must cite the "
                "chunk you rule from. You diagnose; you never repair."),
        user=user, temperature=0.0, max_tokens=900,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected a single JSON verdict object, got "
                                f"{type(payload).__name__}")
    if str(payload.get("correction") or "").strip():
        raise AgentError(
            agent,
            "returned a `correction`. The Judge diagnoses; the Refiner "
            "repairs. A judge that supplies the fix is grading its own "
            "homework.")
    v = str(payload.get("verdict", "")).strip().upper()
    if v not in ("PASS", "FAIL"):
        raise AgentError(agent, f"verdict={payload.get('verdict')!r}; "
                                f"expected exactly 'PASS' or 'FAIL'")
    cls = payload.get("class")
    cls = str(cls).strip().upper() if cls else None
    quoted = str(payload.get("quoted_chunk") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if v == "FAIL":
        if cls not in VALID_CLASSES:
            raise AgentError(agent, f"FAIL with class={cls!r}, not one of "
                                    f"{sorted(VALID_CLASSES)}")
        if not quoted:
            raise AgentError(agent, "FAIL without quoting a chunk — an "
                                    "uncited rejection cannot be audited")
        if not reason:
            raise AgentError(agent, "FAIL with no reason — the Refiner would "
                                    "have nothing to repair against")
    elif not quoted:
        raise AgentError(agent, "PASS without quoting the chunk the design "
                                "honors — a PASS heads to the Director's "
                                "desk; it must be checkable")
    return Judgment(v, cls, quoted, reason)


# ---------------- Refiner ----------------

def render_findings(findings: list[Finding]) -> str:
    return "\n".join(f"- {f.render()}" for f in findings) or "- (none)"


def _norm(cand: dict) -> str:
    return re.sub(r"\s+", " ", json.dumps(cand, sort_keys=True).lower())


def run_mg_refiner(llm, prompts_dir: Path, spec, selection, cand: dict,
                  findings: list[Finding],
                  agent_label: str | None = None) -> dict:
    agent = agent_label or f"mg-refiner-{spec.id}"
    if not findings:
        raise AgentError(agent, "dispatched with no findings — a Refiner "
                                "with nothing to repair should never have "
                                "been called. Pipeline sequencing bug.")
    user = (_common(_template(prompts_dir, "minigame-refiner.md"),
                    spec, selection)
            .replace("{{CANDIDATE}}", render_candidate(cand))
            .replace("{{FINDINGS}}", render_findings(findings)))
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Refiner in uhta's mini-game GER loop. You "
                "repair exactly the defects the Judge or the design gate "
                "found, changing as little else as possible."),
        user=user, temperature=0.2, max_tokens=1600,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected the repaired JSON design object, "
                                f"got {type(payload).__name__}")
    payload["id"] = spec.id
    payload["encounter"] = spec.encounter
    payload["pole"] = spec.pole
    if _norm(payload) == _norm(cand):
        raise AgentError(
            agent,
            "returned the design unchanged — a no-op refinement sends the "
            "identical design back to the identical judge and spends a "
            "breaker round learning nothing.")
    return payload
