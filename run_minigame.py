#!/usr/bin/env python3
"""uhta mini-game pipeline — Assignment 6, pipeline #2. Entry point.

Recommends encounter mini-games (the GDD's PROPOSED tier: three encounters x
two poles), runs each through a GER loop, STOPS at a human gate, and only
builds after the Director types a selection.

    python3 run_minigame.py                     PROPOSE, live. Ends at the
                                                Director selection block in
                                                MINIGAME-CANDIDATES.md.
    python3 run_minigame.py --build \\
        --select first-contact-hope \\
        --from-run mg-XXXX                      BUILD, live. The command line
                                                IS the human gate.

    python3 run_minigame.py --selftest          no API calls; asserts the
                                                deterministic spine.
    python3 run_minigame.py --mock-llm          no API calls; full propose on
                                                scripted fixtures (walks every
                                                path incl. an escalation).
                                                Add --build --select ... to
                                                mock the build phase too.

Flags: --slots first-contact-hope,vigil-fear (subset) · --max-rounds N ·
--escalation-limit N · --run-id NAME.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from content.agents import AgentError  # noqa: E402
from content.retriever import Retriever, Selection  # noqa: E402
from crew.blackboard import Blackboard  # noqa: E402
from crew.llm import LLMCall  # noqa: E402
from ger.breaker import CircuitBreaker  # noqa: E402
from minigame.agents import run_designer, run_judge, run_mg_refiner  # noqa: E402
from minigame.builder_stage import build_and_check, node_available  # noqa: E402
from minigame.instructor import run_instructor  # noqa: E402
from minigame.presenter import check_presentation  # noqa: E402
from minigame.checks import (Finding, apply_patch, brace_balanced,  # noqa: E402
                             check_patch, extract_anchors, run_design_checks)
from minigame.corpus import (CORPUS_FILES, build_minigame_corpus)  # noqa: E402
from minigame.pipeline import BUILD_REL, MinigamePipeline  # noqa: E402
from minigame.spec import (ALLOWED_INPUTS, OUTCOME_EFFECTS, SLOT_IDS,  # noqa: E402
                           SLOT_SPECS, spec_for)

BANNER = "=" * 74


class _ScriptedLLM:
    name, model = "scripted (selftest)", "none"
    calls = input_tokens = output_tokens = 0

    def __init__(self, payload: str):
        self.payload = payload

    def complete(self, call: LLMCall) -> str:  # noqa: ARG002
        return self.payload


GOOD = {
    "id": "first-contact-hope", "encounter": "first-contact", "pole": "hope",
    "name": "Steady the Flame", "premise": "A grey band circles you.",
    "loop": "Hold and release to keep the flame inside their comfort.",
    "signals": "Brightness is the flame; comfort is posture; commitment is "
               "kneeling.",
    "controls": ["space"], "outcome_win": "They kneel.",
    "outcome_fail": "They scatter or freeze.",
    "effects": ["convert_devout", "burnout"],
    "why_fun": "Restraint under temptation.",
    "pattern_source": "Threshold fight", "gdd_quote": "steady when they arrive",
}


def selftest() -> int:
    print(BANNER)
    print("uhta mini-game pipeline — SELFTEST (no API key, no API calls)")
    print(BANNER)
    failures: list[str] = []
    counted = [0]
    bb = Blackboard(f"mg-selftest-{time.strftime('%Y%m%d-%H%M%S')}",
                    root=ROOT, quiet=True)

    def check(name: str, ok: bool, detail: str = "") -> None:
        counted[0] += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    # ---- 1. corpus: the per-doc policy ----
    print("\n[1/7] Corpus — per-doc policy (same number, opposite meanings)")
    for name, rel in CORPUS_FILES.items():
        check(f"seeded corpus file present: {name}", bb.bb_path(rel).exists())
    docs = {n: bb.read_bb(r, "selftest") for n, r in CORPUS_FILES.items()}
    _, dropped, kept = build_minigame_corpus(docs)
    kept_keys = {c.key for c in kept}
    check("v0.9.9 §2 (the ONLY GDD section with the encounter table) is in",
          any(k.startswith("uhta-gdd-v0.9.9-condensed.md#2") for k in kept_keys))
    check("the encounter table's own text is retrievable",
          any("wavering ring" in c.text for c in kept))
    check("v0.9.9 §3 (tiers + the stop rule) is IN — a recommender that "
          "cannot read the stop rule cannot respect it",
          any(k.startswith("uhta-gdd-v0.9.9-condensed.md#3") for k in kept_keys))
    check("v0.9.9 §5 (AI architecture) is OUT",
          not any(k.startswith("uhta-gdd-v0.9.9-condensed.md#5")
                  for k in kept_keys))
    check("v0.9.7 §2.x mechanics detail is IN",
          "uhta-gdd-v0.9.7-full.md#2.2" in kept_keys)
    check("v0.9.7 §4.5 (the Director's worked example) is OUT — same doc, "
          "same number, opposite ruling vs v0.9.9 §4, which is the point of "
          "a per-doc policy",
          "uhta-gdd-v0.9.7-full.md#4.5" not in kept_keys
          and not any(k.startswith("uhta-gdd-v0.9.7-full.md#3")
                      for k in kept_keys))
    research = [c for c in kept if c.doc == "minigame-patterns.md"]
    check("the research patterns doc is indexed", len(research) >= 8,
          f"{len(research)} pattern chunks")
    check("every exclusion carries a reason",
          all(d.reason.strip() for d in dropped), f"{len(dropped)} exclusions")

    # ---- 2. retrieval per slot ----
    print("\n[2/7] Retrieval — three queries per slot, unioned")
    r = Retriever(kept)
    thin = [s.id for s in SLOT_SPECS
            if len(r.select_multi(s.queries).selected) < 2]
    check("every slot retrieves at least two chunks", not thin,
          f"thin: {thin or 'none'}")
    with_pattern = sum(
        1 for s in SLOT_SPECS
        if any(x.chunk.doc == "minigame-patterns.md"
               for x in r.select_multi(s.queries).selected))
    check("the pattern query reaches the research corpus for most slots",
          with_pattern >= 4, f"{with_pattern}/6 slots retrieved a pattern "
                             f"chunk")
    off = r.select("quarterly tax filing depreciation payroll", max_chunks=2)
    check("an off-topic control retrieves NOTHING", not off.selected)

    # ---- 3. the deterministic design gate ----
    print("\n[3/7] The design gate — every check fires, and only when it should")
    check("a well-formed design passes the gate",
          not run_design_checks(dict(GOOD)))
    cases = [
        ("C1 SCHEMA", {**GOOD, "loop": ""}),
        ("C2 VALID-SLOT", {**GOOD, "pole": "neutral"}),
        ("C3 BUILDABLE-INPUT", {**GOOD, "controls": ["shift-key"]}),
        ("C4 REAL-STAKES", {**GOOD, "effects": ["gold_coins"]}),
        ("C5 WORDLESS", {**GOOD, "signals": "a text label marks who is safe"}),
        ("C6 SHORT", {**GOOD, "name": "x" * 60}),
    ]
    for rule, cand in cases:
        got = {f.check for f in run_design_checks(cand)}
        check(f"{rule} fires on its bad design", rule in got,
              f"fired: {sorted(got) or 'nothing'}")
    check("meta fields may talk ABOUT interfaces (why_fun is not "
          "player-facing)",
          not run_design_checks({**GOOD, "why_fun":
                                 "no text, no HUD — restraint is the test"}))

    # ---- 4. judge and refiner guards ----
    print("\n[4/7] Judge and Refiner guards — cite it, never repair it, "
          "never no-op")
    spec = spec_for("first-contact-hope")
    sel = r.select_multi(spec.queries)

    def judge_with(payload: str):
        return run_judge(_ScriptedLLM(payload), ROOT / "prompts", spec, sel,
                         dict(GOOD), agent_label="mg-judge-selftest")

    guards = [
        ("a FAIL with no quoted chunk HALTS",
         '{"verdict":"FAIL","class":"GENERIC","quoted_chunk":"","reason":"r"}',
         "uncited"),
        ("a FAIL with an unknown class HALTS",
         '{"verdict":"FAIL","class":"VIBES","quoted_chunk":"x","reason":"r"}',
         "not one of"),
        ("a judge that tries to REPAIR halts",
         '{"verdict":"FAIL","class":"GENERIC","quoted_chunk":"x","reason":"r",'
         '"correction":"do it differently"}', "grading its own homework"),
        ("a PASS that quotes nothing HALTS",
         '{"verdict":"PASS","class":null,"quoted_chunk":"","reason":"r"}',
         "checkable"),
        ("an unparseable response HALTS", "thoughts, no json",
         "no JSON payload"),
    ]
    for name, payload, needle in guards:
        try:
            judge_with(payload)
            check(name, False, "no exception raised")
        except AgentError as exc:
            check(name, needle in str(exc), str(exc)[:90])

    same = json.dumps(GOOD)
    finding = [Finding("deterministic", "C5 WORDLESS", "text label")]
    try:
        run_mg_refiner(_ScriptedLLM(same), ROOT / "prompts", spec, sel,
                       dict(GOOD), finding, agent_label="mg-refiner-selftest")
        check("a refinement returning the design unchanged HALTS", False)
    except AgentError as exc:
        check("a refinement returning the design unchanged HALTS",
              "unchanged" in str(exc))
    try:
        run_mg_refiner(_ScriptedLLM(same), ROOT / "prompts", spec, sel,
                       dict(GOOD), [], agent_label="mg-refiner-selftest")
        check("dispatching the Refiner with NO findings HALTS", False)
    except AgentError as exc:
        check("dispatching the Refiner with NO findings HALTS",
              "sequencing bug" in str(exc))
    try:
        run_designer(_ScriptedLLM('{"x":1}'), ROOT / "prompts", spec,
                     Selection("q", [], []),
                     agent_label="mg-designer-selftest")
        check("designing from an EMPTY retrieval HALTS", False)
    except AgentError as exc:
        check("designing from an EMPTY retrieval HALTS",
              "empty corpus cut" in str(exc))

    # ---- 5. breaker (shared machinery, reused from ger/) ----
    print("\n[5/7] Circuit breaker — ger.breaker, reused as shared machinery")
    br = CircuitBreaker(max_rounds=2, escalation_limit=3)
    check("2 refinements allowed, a 3rd is not",
          br.allow_refinement(1) and not br.allow_refinement(2))

    # ---- 6. build v2: instructor + presenter gates ----
    print("\n[6/7] Build v2 — the Writer's and Aesthetic Director's seats")
    fx_instr = json.loads((ROOT / "tests" / "fixtures" / "minigame" /
                           "instructor.json").read_text(encoding="utf-8"))
    good_line = run_instructor(
        _ScriptedLLM(json.dumps(fx_instr)), ROOT / "prompts", dict(GOOD),
        agent_label="mg-instructor-selftest")
    check("a register-clean first-use line is accepted",
          good_line["first_use_line"] == fx_instr["first_use_line"]
          and good_line["repair_rounds"] == 0)
    try:
        run_instructor(
            _ScriptedLLM('{"first_use_line": "Press space to play the '
                         'flame mini-game now"}'),
            ROOT / "prompts", dict(GOOD), agent_label="mg-instructor-selftest")
        check("an instruction line in tutorial register HALTS after the "
              "repair budget", False)
    except AgentError as exc:
        check("an instruction line in tutorial register HALTS after the "
              "repair budget", "register gate twice" in str(exc),
              "R2 NO-UI-LANGUAGE — the guide() failure cannot re-enter "
              "through the mini-game door")
    fx_pres = json.loads((ROOT / "tests" / "fixtures" / "minigame" /
                          "presenter.json").read_text(encoding="utf-8"))
    check("a complete diegetic presentation spec passes its gate",
          not check_presentation(dict(fx_pres)))
    check("P1 SPEC-COMPLETE fires on a missing field",
          any(f.check == "P1 SPEC-COMPLETE" for f in check_presentation(
              {k: v for k, v in fx_pres.items() if k != "signal_map"})))
    check("P2 WORDLESS fires on interface furniture in the spec",
          any(f.check == "P2 WORDLESS" for f in check_presentation(
              {**fx_pres, "feedback_win": "a HUD banner announces victory"})))
    check("P3 UNMISSABLE-ENTRY fires when the entry does not pause the world",
          any(f.check == "P3 UNMISSABLE-ENTRY" for f in check_presentation(
              {**fx_pres, "entry_transition": "the encounter just begins"})))

    # ---- 7. anchors + the patch contract, against the REAL build ----
    print("\n[7/7] Build contract — anchors and the fixture patch vs the "
          "real slice")
    html = bb.read_bb(BUILD_REL, "selftest")
    anchors = extract_anchors(html)
    check("all FIVE anchors found exactly once (logic / frame / input / "
          "selftest / hook)",
          set(anchors) == {"logic", "frame", "input", "selftest", "hook"},
          "frame+input added after the second playtest: an encounter with "
          "no per-frame seat is invisible")
    fx = json.loads((ROOT / "tests" / "fixtures" / "minigame" /
                     "programmer.json").read_text(encoding="utf-8"))
    patched, checks_d, errors = build_and_check(html, anchors, fx,
                                                instructions=fx_instr)
    check("v2 checks: the Director test hook (#mg) is required and present",
          checks_d.get("director_test_hook", False))
    check("v2 checks: the Instructor's line is required in the patch, "
          "escaping-insensitively",
          checks_d.get("first_use_line_present", False))
    no_hook = dict(fx)
    no_hook["logic_block"] = fx["logic_block"].replace("location.hash",
                                                       "locationXhash")
    _, _, hook_errors = build_and_check(html, anchors, no_hook,
                                        instructions=fx_instr)
    check("a patch WITHOUT the test hook is rejected",
          any("test hook" in e for e in hook_errors))
    deadlock = dict(fx)
    deadlock["frame_line"] = fx["frame_line"] + "\n    transitioning=true;"
    _, _, dl_errors = build_and_check(html, anchors, deadlock,
                                      instructions=fx_instr)
    check("a patch that WRITES `transitioning` is rejected "
          "(the v2 WASD-freeze class, banned by name)",
          any("transitioning" in e for e in dl_errors))
    check("the hand-authored fixture patch passes EVERY post-check",
          not errors, "; ".join(errors)[:120] if errors else
          f"node={'yes' if node_available() else 'no (brace fallback)'}")
    check("every pre-existing G-assertion survives the fixture patch",
          checks_d.get("all_preexisting_assertions_survive", False))
    check("the fixture patch adds M-assertions",
          checks_d.get("adds_at_least_one_M_assertion", False))
    bad = dict(fx)
    bad["logic_block"] = "function mgBroken({"
    _, _, errors2 = build_and_check(html, anchors, bad)
    check("a syntactically broken patch is REJECTED by the checks",
          bool(errors2), (errors2 or ["?"])[0][:90])
    check("brace_balanced accepts the real fixture and rejects the broken one",
          brace_balanced(fx["logic_block"])
          and not brace_balanced("function x({"))

    p = MinigamePipeline(_ScriptedLLM(""), "selftest", ROOT,
                         run_id=bb.run_id + "-gate")
    try:
        p.load_selection("no-such-run", "first-contact-hope")
        check("build without a completed propose run HALTS", False)
    except Exception as exc:  # noqa: BLE001
        check("build without a completed propose run HALTS",
              "CANDIDATES.json" in str(exc))

    total = len(failures)
    print("\n" + BANNER)
    if failures:
        print(f"SELFTEST FAILED — {total} check(s): " + "; ".join(failures))
        print(BANNER)
        return 1
    print(f"SELFTEST PASSED — {counted[0]} assertions:")
    print("the per-doc corpus policy, per-slot retrieval, the design gate,")
    print("every judge/refiner halt guard, the shared breaker, and the patch")
    print("contract exercised against the real build with a real fixture")
    print("patch. No API key, no API calls, no model.")
    print(BANNER)
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="uhta mini-game pipeline (GER + human gate + Programmer) "
                    "— Assignment 6, pipeline #2.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mock-llm", action="store_true")
    ap.add_argument("--build", action="store_true",
                    help="run the BUILD phase (requires --select and "
                         "--from-run — the human gate)")
    ap.add_argument("--select", default=None,
                    help="the Director-selected candidate id")
    ap.add_argument("--from-run", default=None,
                    help="the propose run to read CANDIDATES.json from")
    ap.add_argument("--slots", default=None,
                    help="comma-separated slot subset (propose)")
    ap.add_argument("--max-rounds", type=int, default=None)
    ap.add_argument("--escalation-limit", type=int, default=None)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--no-open", action="store_true",
                    help="don't auto-open the Director's dashboard after a "
                         "completed propose run")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    slot_filter = None
    if args.slots:
        slot_filter = [s.strip() for s in args.slots.split(",")]
        unknown = [s for s in slot_filter if s not in SLOT_IDS]
        if unknown:
            print(f"\nUnknown slot(s): {', '.join(unknown)}. "
                  f"Known: {', '.join(SLOT_IDS)}\n")
            return 1

    if args.build and not (args.select and args.from_run):
        print("\n--build requires BOTH --select <id> AND --from-run <run>. "
              "That is the human gate: no typed selection, no build.\n")
        return 1

    mode = "mock" if args.mock_llm else "live"
    phase = "BUILD" if args.build else "PROPOSE"
    print(BANNER)
    print(f"uhta mini-game pipeline — {phase}, "
          f"{'MOCK-LLM' if mode == 'mock' else 'LIVE'} run")
    if mode == "mock":
        print("MOCK MODE: no API calls; scripted fixtures walk every loop")
        print("path (incl. one escalation). Produces NO real design work.")
        print("The design gate, retrieval, and patch post-checks are real.")
    print(BANNER)

    from crew.llm import LLMError, LiveLLM
    try:
        if mode == "mock":
            from minigame.fixtures import MinigameMockLLM
            llm = MinigameMockLLM(ROOT / "tests" / "fixtures" / "minigame")
        else:
            llm = LiveLLM()
    except LLMError as exc:
        print(f"\nSTARTUP FAILED: {exc}\n")
        return 1

    p = MinigamePipeline(llm, mode, ROOT, run_id=args.run_id,
                         slot_filter=slot_filter,
                         max_rounds=args.max_rounds,
                         escalation_limit=args.escalation_limit)
    llm.logger = p.bb.log
    rc = p.build(args.from_run, args.select) if args.build else p.propose()
    print(f"\nRun directory: out/{p.run_id}/")
    for f in sorted(p.bb.run_dir.iterdir()):
        if f.is_file():
            print(f"  {f.name}  ({f.stat().st_size} B)")

    # ---- the hand-off: put the Director's dashboard in front of the human ----
    if not args.build and rc == 0:
        dash = p.bb.run_dir / "MINIGAME-DASHBOARD.html"
        if dash.exists():
            in_container = Path("/.dockerenv").exists()
            print(f"\nDIRECTOR'S DASHBOARD: out/{p.run_id}/MINIGAME-DASHBOARD.html")
            if in_container:
                print("  (running in docker — no browser here; on the host:")
                print(f'   start "" "out\\{p.run_id}\\MINIGAME-DASHBOARD.html")')
            elif not args.no_open:
                try:
                    import webbrowser
                    if webbrowser.open(dash.resolve().as_uri()):
                        print("  opened in your default browser — check off "
                              "approvals, generate the ruling.")
                except Exception:  # noqa: BLE001 — opening is a courtesy, never a failure
                    pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
