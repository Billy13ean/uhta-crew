#!/usr/bin/env python3
"""uhta GER pipeline — Assignment 6. Entry point.

Generator -> Evaluator -> Refiner -> Circuit Breaker, targeting the build's
seven first-use verb narration lines (the `TEACHING_TEXT` const the A5 run
built the display mechanism for). The Evaluator enforces the GDD §2.5
narration register — short, declarative, second person, names the verb,
states its consequence, no mythology — in two layers: a deterministic
register gate, then an LLM judge that must quote the chunk it rules from.

Three run modes:

    python3 run_ger.py                  live. Calls the Anthropic API.
                                        Model: $CREW_MODEL (default claude-sonnet-4-5).
                                        Key:   $ANTHROPIC_API_KEY.

    python3 run_ger.py --selftest       NO API CALLS. Asserts the deterministic
                                        spine: build extraction, every register
                                        check, per-verb retrieval, every halt
                                        guard in all three agents, the circuit
                                        breaker's arithmetic, and the patch
                                        round-trip. Exits 0 on success.

    python3 run_ger.py --mock-llm       NO API CALLS. Full loop on canned
                                        fixtures scripted to exercise every
                                        path: round-0 accepts, a deterministic
                                        catch + repair, an LLM catch + repair,
                                        and one verb the breaker ESCALATES.

Useful flags: --verbs roar,raze (subset) · --max-rounds N (refinements per
verb, default 2) · --escalation-limit N (global breaker trip, default 3) ·
--skip-baseline (audit layer 1 only, no LLM judgment of the shipped stubs) ·
--run-id NAME.

See Rouke-uhta-A6-README.md for what this is and why, and any completed run
directory for what it produced.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from content.agents import AgentError  # noqa: E402
from content.pipeline import CORPUS_FILES  # noqa: E402
from content.retriever import (Retriever, Selection, build_corpus)  # noqa: E402
from crew.blackboard import Blackboard, MissingArtifactError  # noqa: E402
from crew.llm import LLMCall  # noqa: E402
from ger.breaker import BreakerTripped, CircuitBreaker, RoundRecord, VerbOutcome  # noqa: E402
from ger.checks import (BANNED_UI_TOKENS, MAX_CHARS, MAX_WORDS,  # noqa: E402
                        extract_guide_strings,
                        extract_teaching_text, js_escape,
                        render_teaching_snippet, run_register_checks,
                        strip_html, _TEACHING_RE)
from ger.evaluator import run_evaluator  # noqa: E402
from ger.generator import run_generator  # noqa: E402
from ger.pipeline import BUILD_REL, GerPipeline  # noqa: E402
from ger.refiner import run_refiner  # noqa: E402
from ger.spec import REGISTER, VERBS, VERB_SPECS, spec_for  # noqa: E402

BANNER = "=" * 74


class _ScriptedLLM:
    """Returns a fixed string. Used only by --selftest to drive agent halt
    guards without an API key. Never used by a real run."""
    name, model = "scripted (selftest)", "none"
    calls = input_tokens = output_tokens = 0

    def __init__(self, payload: str):
        self.payload = payload

    def complete(self, call: LLMCall) -> str:  # noqa: ARG002
        return self.payload


# --------------------------------------------------------------------------
# --selftest
# --------------------------------------------------------------------------

def selftest() -> int:
    print(BANNER)
    print("uhta GER pipeline — SELFTEST (no API key required, no API calls)")
    print(BANNER)
    failures: list[str] = []
    counted = [0]
    run_id = f"ger-selftest-{time.strftime('%Y%m%d-%H%M%S')}"
    bb = Blackboard(run_id, root=ROOT, quiet=True)

    def check(name: str, ok: bool, detail: str = "") -> None:
        counted[0] += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    # ---- 1. the build is the spec ----
    print("\n[1/8] Build extraction — the verb list IS the build's verb list")
    check("the build is seeded on the blackboard", bb.bb_path(BUILD_REL).exists())
    html = bb.read_bb(BUILD_REL, "selftest")
    teaching = extract_teaching_text(html)
    check("TEACHING_TEXT extracts exactly the seven spec verbs",
          set(teaching) == set(VERBS), f"build: {sorted(teaching)}")
    check("the TEACHING_TEXT const appears exactly once (patch anchor)",
          len(_TEACHING_RE.findall(html)) == 1)
    guides = extract_guide_strings(html)
    check("guide() tutorial strings extract (narrow anchor, not a scan)",
          len(guides) >= 4, f"{len(guides)} strings")

    # ---- 2. the deterministic register gate ----
    print("\n[2/8] The register gate — every check fires, and only when it should")
    cases = [
        ("R1 NAMES-VERB", "You move and the ground remembers you.", "walk"),
        ("R2 NO-UI-LANGUAGE", "Press the walk key to walk forward.", "walk"),
        ("R3 SHORT", "You walk. " + "The road remembers you always. " * 12, "walk"),
        ("R4 DECLARATIVE", "You walk — and does the ground remember?", "walk"),
        ("R5 NO-NUMBERS", "You walk 6 tiles and the road remembers.", "walk"),
        ("R6 SECOND-PERSON", "The being walks; the ground remembers it.", "walk"),
    ]
    for rule, line, verb in cases:
        got = {f.check for f in run_register_checks(line, verb)}
        check(f"{rule} fires on its bad line", rule in got,
              f"fired: {sorted(got) or 'nothing'}")
    clean = "You walk. Every tile you cross becomes a road that carries your color."
    check("a clean line passes every register check",
          not run_register_checks(clean, "walk"))
    check("HTML is stripped before checking (<b> tags are not words)",
          strip_html("<b>walk</b>") == "walk")
    stub_fails = {v: [f.check for f in run_register_checks(line, v)]
                  for v, line in teaching.items()}
    check("all seven shipped stubs pass the deterministic gate "
          "(their defects are layer-2 defects)",
          not any(stub_fails.values()), str({k: v for k, v in stub_fails.items() if v}))
    guide_caught = [g for g in guides if any(
        f.check == "R2 NO-UI-LANGUAGE" for f in run_register_checks(g, None))]
    check("the gate catches the shipped guide() strings (press / W A S D / click)",
          len(guide_caught) >= 4,
          f"{len(guide_caught)}/{len(guides)} caught — the failure the "
          f"Pre-Build Declaration named, found in the real build")
    check("banned-token list is word-bounded (no substring false positives)",
          not run_register_checks(
              "You walk. Your presence presses no one; the express road carries you.",
              "walk"),
          "'presses'/'express' contain 'press' but only as substrings")

    # ---- 3. retrieval, per verb ----
    print("\n[3/8] Retrieval — every verb clears the two-chunk rule")
    docs = {n: bb.read_bb(r, "selftest") for n, r in CORPUS_FILES.items()}
    _, _, kept = build_corpus(docs)
    r = Retriever(kept)
    thin = [s.verb for s in VERB_SPECS if len(r.select_multi(s.queries).selected) < 2]
    check("all seven verbs retrieve two chunks", not thin, f"thin: {thin or 'none'}")
    raze = r.rank(spec_for("raze").query_mechanic)
    check("the NEW raze query ranks the §2.2 verb table first "
          "(A4 had no raze beat; this pipeline had to add one)",
          raze[0].chunk.section == "2.2", f"top: §{raze[0].chunk.section} "
          f"bm25 {raze[0].score:.2f}")
    off = r.select("sourdough starter hydration oven crumb", max_chunks=2)
    check("an off-topic control retrieves NOTHING", not off.selected)

    # ---- 4. evaluator halt guards ----
    print("\n[4/8] Evaluator guards — diagnosis must be cited, and never a repair")
    spec = spec_for("roar")
    sel = r.select_multi(spec.queries)

    def ev(payload: str):
        return run_evaluator(_ScriptedLLM(payload), ROOT / "prompts", spec, sel,
                             "You roar.", REGISTER,
                             agent_label="ger-evaluator-selftest")

    ev_guards = [
        ("a FAIL with no quoted chunk HALTS",
         '{"verdict":"FAIL","class":"GENERIC","quoted_chunk":"","reason":"r"}',
         "without quoting"),
        ("a FAIL with an unknown class HALTS",
         '{"verdict":"FAIL","class":"VIBES","quoted_chunk":"x","reason":"r"}',
         "not one of"),
        ("a FAIL with no reason HALTS",
         '{"verdict":"FAIL","class":"GENERIC","quoted_chunk":"x","reason":""}',
         "nothing to repair"),
        ("a PASS that quotes nothing HALTS",
         '{"verdict":"PASS","class":null,"quoted_chunk":"","reason":"r"}',
         "must be checkable"),
        ("an evaluator that tries to REPAIR halts (GER separation of roles)",
         '{"verdict":"FAIL","class":"GENERIC","quoted_chunk":"x","reason":"r",'
         '"correction":"a fixed line"}',
         "grading its own homework"),
        ("an unparseable response HALTS",
         "no json here", "no JSON payload"),
        ("a non-PASS/FAIL verdict HALTS",
         '{"verdict":"MAYBE","quoted_chunk":"x","reason":"r"}', "exactly"),
    ]
    for name, payload, needle in ev_guards:
        try:
            ev(payload)
            check(name, False, "no exception raised")
        except AgentError as exc:
            check(name, needle in str(exc), str(exc)[:90])
    j = ev('{"verdict":"PASS","class":null,"quoted_chunk":"witness radius",'
           '"reason":"cites the row"}')
    check("a well-formed PASS parses", not j.failed and j.quoted_chunk)

    # ---- 5. generator + refiner guards ----
    print("\n[5/8] Generator and Refiner guards")
    try:
        run_generator(_ScriptedLLM('{"line":"x"}'), ROOT / "prompts", spec,
                      Selection("q", [], []), REGISTER,
                      agent_label="ger-generator-selftest")
        check("generating from an EMPTY retrieval HALTS", False)
    except AgentError as exc:
        check("generating from an EMPTY retrieval HALTS",
              "empty corpus cut" in str(exc) or "no chunks" in str(exc))
    try:
        run_generator(_ScriptedLLM('{"nope": 1}'), ROOT / "prompts", spec, sel,
                      REGISTER, agent_label="ger-generator-selftest")
        check("a generator payload with no line HALTS", False)
    except AgentError:
        check("a generator payload with no line HALTS", True)

    from ger.checks import Finding
    finding = [Finding("deterministic", "R2 NO-UI-LANGUAGE", "press")]
    try:
        run_refiner(_ScriptedLLM('{"line":"You roar at the world."}'),
                    ROOT / "prompts", spec, sel, "you roar at the world.",
                    finding, REGISTER, agent_label="ger-refiner-selftest")
        check("a refinement returning the line unchanged HALTS", False)
    except AgentError as exc:
        check("a refinement returning the line unchanged HALTS",
              "unchanged" in str(exc), "case/whitespace-insensitive comparison")
    try:
        run_refiner(_ScriptedLLM('{"line":"You roar and all fear it."}'),
                    ROOT / "prompts", spec, sel, "You roar.", [], REGISTER,
                    agent_label="ger-refiner-selftest")
        check("dispatching the Refiner with NO findings HALTS", False)
    except AgentError as exc:
        check("dispatching the Refiner with NO findings HALTS",
              "sequencing bug" in str(exc))
    got = run_refiner(_ScriptedLLM('{"line":"You roar and every witness fears it."}'),
                      ROOT / "prompts", spec, sel, "You roar.", finding, REGISTER,
                      agent_label="ger-refiner-selftest")
    check("a real refinement returns the new line",
          got == "You roar and every witness fears it.")

    # ---- 6. the circuit breaker ----
    print("\n[6/8] Circuit breaker — meters content, and knows when to stop the run")
    br = CircuitBreaker(max_rounds=2, escalation_limit=3)
    check("refinement 1 and 2 are allowed, 3 is not",
          br.allow_refinement(0) and br.allow_refinement(1)
          and not br.allow_refinement(2))
    o1 = VerbOutcome("raze", "ACCEPTED", [RoundRecord(0, "x", finding)])
    o2 = VerbOutcome("roar", "ACCEPTED", [RoundRecord(0, "x", finding)])
    o3 = VerbOutcome("wait", "ACCEPTED", [RoundRecord(0, "x", finding)])
    br.escalate(o1)
    br.escalate(o2)
    check("two escalations do not trip a limit of three",
          not br.summary()["tripped"]
          and [o.verb for o in br.escalated] == ["raze", "roar"]
          and o1.status == "ESCALATED")
    try:
        br.escalate(o3)
        check("the THIRD escalation trips the breaker immediately", False)
    except BreakerTripped as exc:
        check("the THIRD escalation trips the breaker immediately",
              "raze" in str(exc) and "roar" in str(exc) and "wait" in str(exc),
              "not at end of run — every later call is money spent on a "
              "known conclusion")

    # ---- 7. the patch round-trip ----
    print("\n[7/8] The patch — snippet renders, applies once, and changes nothing else")
    check("js_escape survives quotes and backslashes",
          js_escape("it's a \\ test") == "it\\'s a \\\\ test")
    new_lines = dict(teaching)
    new_lines["roar"] = ("You roar. Everyone who witnesses it is pushed toward "
                         "fear, whatever color you carry — it's unconditional.")
    snippet = render_teaching_snippet(new_lines, VERBS)
    patched = _TEACHING_RE.sub(lambda m: snippet, html, count=1)
    check("re-extracting the patched const returns exactly the new lines",
          extract_teaching_text(patched) == new_lines,
          "including the escaped apostrophe")
    import re as _re
    _g_marks = _re.findall(r"\['(G\d+)", html)
    check("every pre-existing self-test assertion survives the patch verbatim",
          _g_marks == _re.findall(r"\['(G\d+)", patched),
          f"{len(set(_g_marks))} assertions (G1–G13 incl. A5's G12/G13)")
    check("nothing outside the const changed",
          len(patched) - len(html) == len(snippet) - (_TEACHING_RE.search(html).end()
                                                      - _TEACHING_RE.search(html).start()))

    # ---- 8. the canon bench ----
    print("\n[8/8] The canon bench — registry drift, rulings, and the "
          "no-ignore contract")
    from crew.canon import Canon, CanonError
    import json as _json
    _registry = _json.loads((ROOT / "canon" / "rules.json")
                            .read_text(encoding="utf-8"))
    _c0 = Canon(_registry)
    check("registry baseline matches the spec (ger-register text)",
          _c0.text("ger-register") == REGISTER)
    check("registry baseline matches the gate (length caps + UI tokens)",
          _c0.param("ger-length-caps", "max_chars") == MAX_CHARS
          and _c0.param("ger-length-caps", "max_words") == MAX_WORDS
          and _c0.param("ger-no-ui-language", "banned_tokens")
          == BANNED_UI_TOKENS)
    _amend = Canon(_registry, {"rules": {"ger-length-caps": {
        "status": "AMENDED", "params": {"max_chars": 10, "max_words": 3}}}})
    check("an AMENDED cap is enforced (clean 76-char line now fails R3)",
          any(f.check == "R3 SHORT"
              for f in run_register_checks(clean, "walk", canon=_amend)))
    _repeal = Canon(_registry, {"rules": {"ger-no-ui-language": {
        "status": "REPEALED", "reason": "selftest"}}})
    _ui_line = "You press the walk key and walk."
    check("a REPEALED R2 is skipped (UI line passes R2, and only R2)",
          not any(f.check == "R2 NO-UI-LANGUAGE"
                  for f in run_register_checks(_ui_line, "walk",
                                               canon=_repeal))
          and any(f.check == "R2 NO-UI-LANGUAGE"
                  for f in run_register_checks(_ui_line, "walk", canon=_c0)))
    check("the repeal is LOUD — CANON-IN-FORCE names the skip",
          "REPEALED — not enforced this run" in _repeal.render_in_force())
    try:
        Canon(_registry, {"rules": {"ger-register": {"status": "WAIVED"}}})
        check("status WAIVED is rejected (no ignore, by the Director's own "
              "ruling)", False)
    except CanonError as exc:
        check("status WAIVED is rejected (no ignore, by the Director's own "
              "ruling)", "off the bench" in str(exc))
    try:
        Canon(_registry, {"rules": {"ger-register": {"status": "REPEALED"}}})
        check("the register law itself cannot be repealed (amend, don't "
              "delete)", False)
    except CanonError as exc:
        check("the register law itself cannot be repealed (amend, don't "
              "delete)", "not repealable" in str(exc))
    try:
        Canon(_registry, {"rules": {"no-such-rule": {"status": "UPHELD"}}})
        check("a ruling naming an unknown rule id HALTS", False)
    except CanonError:
        check("a ruling naming an unknown rule id HALTS", True)

    total = len(failures)
    print("\n" + BANNER)
    if failures:
        print(f"SELFTEST FAILED — {total} check(s): " + "; ".join(failures))
        print(BANNER)
        return 1
    print(f"SELFTEST PASSED — {counted[0]} assertions:")
    print("build extraction, the register gate (fired on the")
    print("shipped guide() strings), per-verb retrieval, every halt guard in all")
    print("three agents, the circuit breaker, the patch round-trip, and the")
    print("canon bench (registry drift, amend/repeal, the no-ignore contract).")
    print("No API key, no API calls, no model.")
    print(BANNER)
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="uhta GER pipeline (Generator, Evaluator, Refiner, "
                    "Circuit Breaker) — Assignment 6.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--selftest", action="store_true",
                   help="no API calls; assert the deterministic spine and every "
                        "halt guard")
    g.add_argument("--mock-llm", action="store_true",
                   help="no API calls; full loop on canned fixtures scripted to "
                        "exercise every path incl. an escalation (NOT content)")
    ap.add_argument("--verbs", default=None,
                    help="comma-separated verb subset (default: all seven)")
    ap.add_argument("--max-rounds", type=int, default=None,
                    help="refinement rounds per verb before escalation (default 2)")
    ap.add_argument("--escalation-limit", type=int, default=None,
                    help="escalated verbs that trip the whole run (default 3)")
    ap.add_argument("--skip-baseline", action="store_true",
                    help="baseline audit runs layer 1 only (no LLM judgment of "
                         "the shipped stub lines)")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    verb_filter = None
    if args.verbs:
        verb_filter = [v.strip() for v in args.verbs.split(",")]
        unknown = [v for v in verb_filter if v not in VERBS]
        if unknown:
            print(f"\nUnknown verb(s): {', '.join(unknown)}. "
                  f"Known: {', '.join(VERBS)}\n")
            return 1

    mode = "mock" if args.mock_llm else "live"
    print(BANNER)
    print(f"uhta GER pipeline — {'MOCK-LLM' if mode == 'mock' else 'LIVE'} run")
    if mode == "mock":
        print("MOCK MODE: no API calls. Generator/Evaluator/Refiner responses are")
        print("canned fixtures from tests/fixtures/ger/, scripted to exercise")
        print("every loop path including one escalation. This proves the")
        print("orchestration; it produces NO real content. The deterministic")
        print("register gate and retrieval are still real.")
    print(BANNER)

    from crew.llm import LLMError, LiveLLM
    try:
        if mode == "mock":
            from ger.fixtures import GerMockLLM
            llm = GerMockLLM(ROOT / "tests" / "fixtures" / "ger")
        else:
            llm = LiveLLM()
    except LLMError as exc:
        print(f"\nSTARTUP FAILED: {exc}\n")
        return 1

    p = GerPipeline(llm, mode, ROOT, run_id=args.run_id,
                    verb_filter=verb_filter, max_rounds=args.max_rounds,
                    escalation_limit=args.escalation_limit,
                    skip_baseline=args.skip_baseline)
    llm.logger = p.bb.log
    rc = p.run()
    print(f"\nRun directory: out/{p.run_id}/")
    for f in sorted(p.bb.run_dir.iterdir()):
        if f.is_file():
            print(f"  {f.name}  ({f.stat().st_size} B)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
