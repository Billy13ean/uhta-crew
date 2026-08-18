"""The Presenter — the Aesthetic Director's seat (GDD §5), applied to
encounters. "Visual language; render layer only, never belief math."

Same origin as the Instructor: the first built encounter was correct and
invisible. In a wordless game "UI design" means DIEGETIC PRESENTATION — an
entrance nobody can miss, a visual hierarchy that tells the eye what to read
first, and a signal map that puts every piece of state into bodies, light
and distance. The Presenter produces that spec; the Programmer implements
it; the deterministic gate holds it to the same wordless vocabulary the
design gate holds designs to.

Required spec fields:

    entry_transition   how the game unmistakably announces the encounter —
                       must pause the world and visibly reframe the scene
    visual_hierarchy   what the player's eye should find first, second,
                       third
    signal_map         state -> visual, for every state the design names
    feedback_win / feedback_fail   the resolution moments, readable without
                       words
    exit_transition    how the world resumes
    attention_cue      the pre-encounter tell (how the player knows one is
                       ABOUT to be available), diegetic

One generate, one repair, then a halt — same budget as the Instructor.
"""
from __future__ import annotations

import json
from pathlib import Path

from content.agents import AgentError, parse_json_payload
from crew.llm import LLMCall

from ger.checks import strip_html

from .checks import Finding, _UI_RE

PRESENTER_PV = "minigame-presenter v1 (Assignment 6 #2, build v2)"

REQUIRED_SPEC_FIELDS = ["entry_transition", "visual_hierarchy", "signal_map",
                        "feedback_win", "feedback_fail", "exit_transition",
                        "attention_cue"]


def check_presentation(spec: dict) -> list[Finding]:
    f: list[Finding] = []
    missing = [k for k in REQUIRED_SPEC_FIELDS
               if not spec.get(k) or (isinstance(spec.get(k), (list, dict))
                                      and not spec[k])]
    if missing:
        f.append(Finding("deterministic", "P1 SPEC-COMPLETE",
                         f"missing/empty field(s): {', '.join(missing)}"))
        return f
    flat = json.dumps({k: spec[k] for k in REQUIRED_SPEC_FIELDS},
                      ensure_ascii=False)
    m = _UI_RE.search(strip_html(flat))
    if m:
        f.append(Finding(
            "deterministic", "P2 WORDLESS",
            f"the presentation spec names interface furniture "
            f"({m.group(0)!r}) — in a wordless game the presentation IS "
            f"bodies, light and space, never widgets"))
    if not str(spec["entry_transition"]).strip() or \
            "pause" not in str(spec["entry_transition"]).lower():
        f.append(Finding(
            "deterministic", "P3 UNMISSABLE-ENTRY",
            "entry_transition must state that the world PAUSES — the first "
            "Director playtest proved an unannounced encounter is an "
            "invisible one"))
    return f


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "minigame-presenter.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def _call(llm, prompts_dir: Path, design: dict, findings_text: str,
          agent: str) -> dict:
    user = (_template(prompts_dir)
            .replace("{{DESIGN}}", json.dumps(design, ensure_ascii=False,
                                              indent=2))
            .replace("{{REPAIR}}", findings_text or "(first attempt)"))
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Aesthetic Director for uhta, seated for "
                "encounters: visual language, render layer only, never "
                "belief math. You design how a wordless encounter is "
                "SEEN — its entrance, its hierarchy, its signals."),
        user=user, temperature=0.4, max_tokens=1200,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected a JSON presentation spec, got "
                                f"{type(payload).__name__}")
    return payload


def run_presenter(llm, prompts_dir: Path, design: dict,
                  agent_label: str = "mg-presenter") -> dict:
    spec = _call(llm, prompts_dir, design, "", agent_label)
    findings = check_presentation(spec)
    rounds = 0
    if findings:
        rounds = 1
        text = ("### REPAIR — your previous spec failed the presentation "
                "gate; fix exactly this:\n"
                + "\n".join(f"- {f.render()}" for f in findings))
        spec = _call(llm, prompts_dir, design, text, agent_label)
        findings = check_presentation(spec)
        if findings:
            raise AgentError(
                agent_label,
                "the presentation spec failed the gate twice: "
                + "; ".join(f.check for f in findings))
    spec["repair_rounds"] = rounds
    return spec
