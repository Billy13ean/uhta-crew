#!/usr/bin/env python3
"""uhta — goal-oriented coding agent (Assignment 5).

Reads the GDD, scans the codebase, finds what the document requires and the code
does not have, decides which gap to close first, and writes the code.

    python run_builder.py --selftest     deterministic checks, no API key, no calls
    python run_builder.py --mock-llm     end-to-end orchestration on canned fixtures
    python run_builder.py                live

The third pipeline in this repo. `crew/` and `content/` do not import `builder/`.
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from crew.blackboard import Blackboard          # noqa: E402
from crew.llm import build_llm                  # noqa: E402
from content.retriever import CORPUS_POLICY     # noqa: E402

from builder import AgentError, assemble, codescan, features as feat, gap  # noqa: E402
from builder import generate, priority                                     # noqa: E402
from builder.fixtures import BuilderMockLLM                                # noqa: E402
from builder.pipeline import BuilderRun, BUILD_TARGET, GDD_DOC             # noqa: E402
from builder.policy import (BUILDER_POLICY, SCAN_POLICY, VENDOR_LINE_CHARS,
                            classify_line)                                 # noqa: E402

PROMPTS = REPO / "prompts"


# ==========================================================================
# SELFTEST
# ==========================================================================

def _ok(fn) -> bool:
    """True if `fn()` does not raise. For asserting the happy path of a check
    whose failure mode is an exception rather than a return value."""
    try:
        fn()
        return True
    except Exception:
        return False


class _StubLLM:
    """Returns one canned payload. Used only to exercise the halt guards."""

    def __init__(self, payload: str):
        self.payload = payload

    def complete(self, call):
        return self.payload


def selftest() -> int:
    print("uhta builder pipeline — SELFTEST (no API key required, no API calls)\n")
    checks: list[tuple[str, bool, str]] = []

    def ck(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    def raises(name: str, fn, want=AgentError, contains: str = "") -> None:
        try:
            fn()
            ck(name, False, "no exception raised")
        except want as exc:
            ck(name, contains.lower() in str(exc).lower(),
               f"raised {want.__name__}" + (f", looked for {contains!r}" if contains else ""))
        except Exception as exc:  # noqa: BLE001
            ck(name, False, f"raised {type(exc).__name__}: {exc}")

    run_id = f"selftest-{time.strftime('%Y%m%d-%H%M%S')}"
    bb = Blackboard(run_id, root=REPO, quiet=True)

    # ---- A. the GDD parses -------------------------------------------------
    gdd = bb.read_bb(GDD_DOC, "selftest")
    verbs = feat.parse_verbs(gdd)
    ck("A1 §2 verb table parses to 7 verbs", len(verbs) == 7,
       ", ".join(v.name for v in verbs))

    tiered, statuses = feat.parse_tiers(gdd)
    ck("A2 §3 tier table yields all six tiers",
       set(statuses) == set(feat.TIER_ORDER), f"{sorted(statuses)}")
    ck("A3 §3 NICE tier lists the narrated opening first",
       any("narrated" in f.name.lower() for f in tiered if f.tier == "NICE"),
       ", ".join(f.name for f in tiered if f.tier == "NICE")[:90])

    crits = feat.parse_criteria(gdd)
    blocked = [c.number for c in crits if c.blocked]
    ck("A4 §4 yields 6 criteria, 1 and 3 blocked",
       len(crits) == 6 and blocked == [1, 3], f"{len(crits)} criteria, blocked {blocked}")

    fs, cs, meta = feat.extract_deterministic(gdd)
    vt = {f.name: f.tier for f in fs if f.id.startswith("verb-")}
    ck("A6 every verb the CORE row names is tiered CORE, not left untiered",
       all(vt.get(v) == "CORE" for v in ("Walk", "Flame", "Roar", "Wait", "Sleep")),
       ", ".join(f"{k}={v}" for k, v in sorted(vt.items())))

    narr = next((f for f in fs if "narrated" in f.name.lower()), None)
    ck("A5 the blocked criteria link to the narrated opening",
       narr is not None and narr.blocks_criteria == [1, 3],
       f"blocks_criteria={narr.blocks_criteria if narr else None}")

    # ---- B. THE withholding ------------------------------------------------
    d = narr.for_detection()
    ck("B1 for_detection() withholds tier / claimed status / gate info",
       "tier" not in d and "gdd_claimed_status" not in d and "blocks_criteria" not in d,
       f"keys exposed: {sorted(d)}")
    ck("B2 the status column IS parsed (cross-check needs it)",
       bool(narr.gdd_claimed_status), repr(narr.gdd_claimed_status)[:60])
    blob = repr(d).lower()
    ck("B3 no tier or status string leaks through the detection payload",
       "unbuilt" not in blob and "nice" not in blob and "built" not in blob,
       "payload is name/section/kind/description/signature only")

    # ---- C. the two policies differ, and for a stated reason ----------------
    ck("C1 BUILDER_POLICY keeps §3 and §4, which CORPUS_POLICY drops",
       {"3", "4"} <= set(BUILDER_POLICY["include_top_level"])
       and {"3", "4"} <= set(CORPUS_POLICY["exclude_top_level"]),
       "the build decision needs the build order and the acceptance test")
    ck("C2 BUILDER_POLICY drops §5/§6, which are pipeline material",
       {"5", "6"} <= set(BUILDER_POLICY["exclude_top_level"]),
       ", ".join(sorted(BUILDER_POLICY["exclude_top_level"])))
    ck("C3 every exclusion carries a reason, none empty",
       all(v.strip() for v in BUILDER_POLICY["exclude_top_level"].values()), "")

    # ---- D. SCAN_POLICY ----------------------------------------------------
    ck("D1 a minified vendor preamble is caught by signature",
       (classify_line('!function(t,e){"object"==typeof exports' + "x" * 10) or ("", ""))[0]
       == "vendor_signature", "")
    ck("D2 an over-long line is caught by length",
       (classify_line("a" * (VENDOR_LINE_CHARS + 1)) or ("", ""))[0] == "vendor_line", "")
    ck("D3 a base64 asset payload is caught",
       (classify_line("const A='data:image/png;base64,iVBORw0KGg';") or ("", ""))[0]
       == "data_uri", "")
    ck("D4 ordinary authored source is not excluded",
       classify_line("  const FLAME_PUSH=PP.flame_push_base,FLAME_R=PP.flame_radius_tiles;") is None, "")

    # ---- E. the scan, on the real build ------------------------------------
    idx = codescan.build_index(bb, "selftest")
    st = idx.stats()
    ck("E1 the Phaser bundle is excluded from the index",
       any(e.chars > 1_000_000 for e in idx.exclusions),
       f"{st['excluded_regions']} region(s), {st['excluded_chars']:,} chars cut")
    ck("E2 authored symbols ARE indexed",
       all(idx.find_symbol(s) for s in ("selfTest", "eraOf", "roadStageFor", "setTip", "guide")),
       f"{st['symbols']} symbols total")
    ck("E3 Phaser-only symbols are NOT in the index",
       not idx.find_symbol("TweenManager") and not idx.find_symbol("WebGLRenderer"),
       "if these were present, every feature would score PRESENT")
    ck("E4 ruleset key paths derive from the live file",
       idx.has_key_path("world.schism.pop_cap") and idx.has_key_path("burnout.timer_X_sleeps"),
       f"{st['key_paths']} paths")

    # ---- F. layer-1 probe behaves ------------------------------------------
    def mk(fid, name, **sig):
        f = feat.Feature(id=fid, name=name, gdd_section="2", tier="PASS 2", kind="system")
        f.signature = feat.Signature(**sig)
        return f

    built = mk("schism", "Schism",
               identifiers=["schism", "SCHISM", "pop_cap"],
               rules_key_paths=["world.schism.pop_cap", "world.schism.max_tribes"],
               strings=["schism"])
    s_built, _ = gap.probe(built, idx)
    ck("F1 a genuinely built system scores PRESENT",
       gap.classify(s_built) == gap.PRESENT, f"score {s_built:.2f}")

    absent = mk("narration", "Narrated teaching opening",
                identifiers=["narrationFor", "NARRATION", "narrate", "narrationOpen"],
                strings=["narration"])
    s_abs, _ = gap.probe(absent, idx)
    ck("F2 the narrated opening does NOT score PRESENT",
       gap.classify(s_abs) != gap.PRESENT, f"score {s_abs:.2f} -> {gap.classify(s_abs)}")

    # ---- G. adjudication guards --------------------------------------------
    v = gap.GapVerdict(absent, gap.PARTIAL, s_abs, [], layer=1)
    raises("G1 PRESENT with no quoted line halts",
           lambda: gap.adjudicate(_StubLLM('```json\n{"verdict":"PRESENT","reason":"x",'
                                           '"quoted_code":"","searched_for":[]}\n```'),
                                  PROMPTS, v, idx), contains="without quoting")
    v2 = gap.GapVerdict(absent, gap.PARTIAL, s_abs, [], layer=1)
    raises("G2 ABSENT with nothing searched-for halts",
           lambda: gap.adjudicate(_StubLLM('```json\n{"verdict":"ABSENT","reason":"x",'
                                           '"quoted_code":"","searched_for":[]}\n```'),
                                  PROMPTS, v2, idx), contains="searched_for")
    v3 = gap.GapVerdict(absent, gap.PARTIAL, s_abs, [], layer=1)
    raises("G3 a fabricated quotation halts",
           lambda: gap.adjudicate(_StubLLM('```json\n{"verdict":"PRESENT","reason":"x",'
                                           '"quoted_code":"const totallyInventedSymbol=42;",'
                                           '"searched_for":[]}\n```'),
                                  PROMPTS, v3, idx), contains="does not appear")

    raises("G4 an empty observable_signature halts the Analyst",
           lambda: feat.run_analyst(
               _StubLLM('```json\n[{"id":"x","name":"x","observable_signature":{}}]\n```'),
               PROMPTS, [feat.Feature("x", "x", "2", "NICE", "ui")], ""),
           contains="empty observable_signature")

    # A max_tokens cutoff arrives looking like an ordinary response — the shared
    # LLM layer never inspects stop_reason. This is the guard that names it as
    # truncation instead of letting it die downstream as "no JSON payload",
    # which is how it presented the first time and cost a live run.
    raises("G5 a max_tokens truncation is named as truncation, not bad JSON",
           lambda: feat.run_analyst(
               _StubLLM('```json\n[\n  {\n    "id": "verb-walk",\n    "name": "Walk",\n'
                        '    "observable_signature": {"identifiers": ["moveStep"'),
               PROMPTS, [feat.Feature("x", "x", "2", "NICE", "ui")], ""),
           contains="TRUNCATED")

    # The batching that makes the truncation unlikely in the first place.
    ck("G6 the Analyst batches — 30 features is not one request",
       len([None for i in range(0, 30, feat.ANALYST_BATCH)]) > 1,
       f"ANALYST_BATCH={feat.ANALYST_BATCH} -> "
       f"{len(range(0, 30, feat.ANALYST_BATCH))} calls for 30 features")

    # ---- H. the cross-check can actually disagree --------------------------
    claimed = mk("faux", "Faux system", identifiers=["definitelyNotInThisFile"])
    claimed.gdd_claimed_status = "Built"
    cv = gap.GapVerdict(claimed, gap.ABSENT, 0.0, [])
    gap.cross_check([cv])
    ck("H1 'Built' + ABSENT is recorded as a disagreement",
       cv.disagrees_with_gdd and cv.gdd_expected == gap.PRESENT, "")
    agree = mk("ok", "OK", identifiers=["selfTest"])
    agree.gdd_claimed_status = "Built"
    av = gap.GapVerdict(agree, gap.PRESENT, 1.0, [])
    gap.cross_check([av])
    ck("H2 'Built' + PRESENT is not a disagreement", not av.disagrees_with_gdd, "")

    # ---- I. the ranking ----------------------------------------------------
    fs2, _, _ = feat.extract_deterministic(gdd)
    for f in fs2:
        f.signature = feat.Signature(identifiers=[f.id.replace("-", "")])
    vs = [gap.GapVerdict(f, gap.ABSENT, 0.0, []) for f in fs2]
    scores = priority.rank(vs)
    win = priority.select(scores)
    ck("I1 the narrated opening wins the ranking",
       win is not None and "narrated" in win.feature.name.lower(),
       f"winner={win.feature.id if win else None} at {win.total:+.2f}")
    ck("I2 it wins from the NICE tier, not from tier weight",
       win.feature.tier == "NICE" and win.term("tier") == 1.0,
       f"tier={win.feature.tier}, tier term {win.term('tier'):+.1f}")
    ck("I3 the gate term is what carries it",
       win.term("gate") == 10.0, f"gate {win.term('gate'):+.1f} = 2 criteria x 5.0")
    ck("I4 the §3 stop rule is WAIVED for it by the carve-out",
       win.term("stop") == 0.0, next(t.detail for t in win.terms if t.name == "stop")[:80])

    endscreen = next((s for s in scores if "endscreen" in s.feature.name.lower()), None)
    ck("I5 the stop rule still penalises a non-gating NICE item",
       endscreen is not None and endscreen.term("stop") == priority.W_STOP,
       f"{endscreen.feature.id} stop {endscreen.term('stop'):+.1f}" if endscreen else "not found")
    ck("I6 the win is not a coin toss", priority.margin(scores) >= 3.0,
       f"margin {priority.margin(scores)}")
    ck("I7 a PRESENT feature is never selectable",
       not priority.score_one(gap.GapVerdict(built, gap.PRESENT, 1.0, [])).selectable, "")

    # ---- J. the patch validator, against the real build --------------------
    src = bb.read_bb(BUILD_TARGET, "selftest")
    before = generate.assertions_in(src)
    ck("J1 the committed build carries 11 assertions", len(before) == 11, f"{len(before)}")

    from builder.fixtures import _PROGRAMMER_PATCH
    patch = generate.Patch(**{k: v for k, v in _PROGRAMMER_PATCH.items()})
    patched, gained, (npass, nfail) = generate.validate(src, patch)
    ck("J2 the fixture patch applies and parses (node --check)",
       len(generate.assertions_in(patched)) == 13, f"11 -> {len(generate.assertions_in(patched))}")
    ck("J3 every original assertion survives",
       all(a in generate.assertions_in(patched) for a in before), f"{len(gained)} new")
    ck("J9 the PATCHED BUILD RUNS and its self-test is green",
       npass == 13 and nfail == 0, f"headless: {npass} PASS / {nfail} FAIL")

    def bad(**kw):
        base = dict(_PROGRAMMER_PATCH)
        base.update(kw)
        return lambda: generate.validate(src, generate.Patch(**base))

    raises("J4 an anchor that is not in the file is rejected",
           bad(anchor="function thisLineDoesNotExist(){}"),
           want=generate.PatchInvalid, contains="does not appear")
    raises("J5 an ambiguous anchor is rejected",
           bad(anchor="  }"), want=generate.PatchInvalid, contains="ambiguous")
    raises("J6 a patch that adds no assertion is rejected",
           bad(edits=[], selftest_insert=""),
           want=generate.PatchInvalid, contains="no new self-test assertion")
    raises("J7 a patch that deletes an existing assertion is rejected",
           bad(edits=[{"anchor": "out.push(['G1 do-nothing -> Apathy loss ~18', ok1===8,",
                       "replacement": "out.push(['REMOVED', ok1===8,"}]),
           want=generate.PatchInvalid, contains="removed or altered")
    raises("J8 JavaScript that does not parse is rejected",
           bad(insert="function broken( { syntax error ]]]"),
           want=generate.PatchInvalid, contains="does not parse")
    # The check that `node --check` cannot make. Anchoring the same valid code
    # BELOW selfTest() puts it in the temporal dead zone: it parses, and the
    # build dies on load. Only executing it finds this.
    raises("J10 a patch that parses but kills the build on load is rejected",
           bad(anchor="function setTip(html){tip.innerHTML=html;}"),
           want=generate.PatchInvalid, contains="threw")
    raises("J11 a patch that leaves the self-test RED is rejected",
           bad(edits=[{"anchor": "  return out;",
                       "replacement": "  out.push(['G12 deliberately false', false, 'x']);\n"
                                      "  return out;"}]),
           want=generate.PatchInvalid, contains="not green")

    # ---- K. the anchor menu ------------------------------------------------
    # The first live Programmer run died twice on anchors that named real
    # functions and invented their bodies, because the model was asked to copy a
    # line from source it had never been shown. The menu removes the freedom;
    # these assert that the menu itself cannot offer an unusable choice.
    cands = generate.anchor_candidates(src)
    st_cands = generate.selftest_anchor_candidates(src)
    st_line, _ = generate.selftest_region(src)

    ck("K1 every menu anchor is verbatim and unique in the real file",
       bool(cands) and all(src.count(ln) == 1 for _, ln in cands + st_cands),
       f"{len(cands)} insertion + {len(st_cands)} self-test candidates")
    ck("K2 no menu anchor is indented or below selfTest()",
       all(ln[:1] not in " \t" for _, ln in cands)
       and all(n - 1 < st_line for n, _ in cands),
       f"selfTest() at line {st_line + 1}; a `const` below it is in the temporal "
       f"dead zone, an indented one lands inside a body")
    menu_text = " ".join(ln for _, ln in cands)
    ck("K3 the pure-resolver zone survives down-sampling",
       all(w in menu_text for w in ("eraOf", "roadStageFor", "ERA_SLEEPS")),
       "the prompt sends the Programmer here; even sampling alone dropped two of the three")
    ck("K4 every menu anchor survives the validator's own uniqueness check",
       all(_ok(lambda: generate._require_unique(src, ln, "anchor"))
           for _, ln in cands + st_cands),
       "menu and validator agree on what 'unique' means")

    # The two anchors that actually killed the live run, as a named regression.
    for i, fake in enumerate((
        "function roadStageFor(born,now){const age=now-born;"
        "if(age<3)return 0;if(age<8)return 1;return 2;}",
        "function eraOf(sleep_no){if(sleep_no<12)return 'genesis';"
        "if(sleep_no<24)return 'struggle';return 'late';}",
    ), 1):
        ck(f"K5.{i} the live-run hallucination is absent from the file and off the menu",
           src.count(fake) == 0 and fake not in [ln for _, ln in cands],
           f"{fake[:56]}…")

    raises("K6 an off-menu anchor_id halts instead of being taken literally",
           lambda: generate._parse_patch(
               "programmer", {"anchor_id": 999999, "insert": "x"},
               {n: ln for n, ln in cands}, {n: ln for n, ln in st_cands}),
           want=AgentError, contains="not on the menu")

    good_id, good_line = cands[-1]
    st_id, st_line_text = st_cands[-1]
    p_ok = generate._parse_patch(
        "programmer",
        {"anchor_id": good_id, "insert": "x",
         "selftest_anchor_id": st_id, "selftest_insert": "out.push(['G12 x', true, '']);"},
        {n: ln for n, ln in cands}, {n: ln for n, ln in st_cands})
    ck("K7 a menu id resolves to the verbatim line, never to model text",
       p_ok.anchor == good_line and p_ok.selftest_anchor == st_line_text,
       f"anchor_id {good_id} -> {good_line.strip()[:48]!r}")
    ck("K8 the self-test anchor is optional when assertions arrive via edits",
       _ok(lambda: generate._parse_patch(
           "programmer", {"anchor_id": good_id, "insert": "x", "selftest_insert": ""},
           {n: ln for n, ln in cands}, {n: ln for n, ln in st_cands})),
       "the fixture places its assertions with an edit, not an insert")

    # ---- L. every menu anchor is a COMPLETE statement -----------------------
    # The second live Programmer failure. Anchors resolved correctly, then the
    # patch died with `SyntaxError: Unexpected token 'const'` — because six of
    # the eleven self-test anchors were the OPENING line of a multi-line
    # `out.push([...])`, and `const F32={` opens six lines of object literal.
    # Inserting after any of them lands inside a literal.
    ck("L1 every menu anchor is a balanced, complete statement",
       all(generate.is_complete_statement(ln) for _, ln in cands + st_cands),
       f"{len(cands)} insertion + {len(st_cands)} self-test candidates")
    ck("L2 multi-line out.push openers are off the menu",
       not any("G9 era resolver" in ln or "G11 atlas integrity" in ln
               for _, ln in st_cands),
       "G6-G11 span lines; their opening line is not an insertion point")
    ck("L3 `const F32={` is off the menu",
       not any(ln.startswith("const F32=") for _, ln in cands),
       "six lines of object literal")

    # The behavioural proof, not just the heuristic: insert real code after EVERY
    # candidate and require the patched build to parse. This is what would have
    # caught both live failures before they cost a run.
    bad_anchor = []
    for n, ln in cands + st_cands:
        probe = generate.Patch(summary="", rationale="", anchor=ln,
                               insert="const __anchor_probe__ = 1;")
        try:
            generate.check_parses(generate.apply_patch(src, probe))
        except Exception as exc:  # noqa: BLE001
            bad_anchor.append((n, type(exc).__name__, str(exc)[:60]))
    ck("L4 inserting after EVERY menu anchor still parses",
       not bad_anchor,
       f"{len(cands) + len(st_cands)} anchors exercised with a real insert"
       if not bad_anchor else f"broke at {bad_anchor[:3]}")

    # ---- report ------------------------------------------------------------
    failures = [(n, d) for n, ok, d in checks if not ok]
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    print()
    if failures:
        print(f"SELFTEST FAILED — {len(failures)} of {len(checks)} check(s):")
        for n, d in failures:
            print(f"  - {n}  [{d}]")
        return 1
    print(f"SELFTEST PASSED — {len(checks)} assertions. The GDD parses, the status "
          f"column is withheld from detection, the vendored bundle is excluded from "
          f"the scan, the ranking reproduces the §3 stop rule and its carve-out, and "
          f"the patch validator rejects every way of breaking the build's self-test.")
    return 0


# ==========================================================================
# RUN
# ==========================================================================

def main() -> int:
    ap = argparse.ArgumentParser(description="uhta goal-oriented coding agent (A5)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--selftest", action="store_true",
                   help="deterministic checks only. No API key, no API calls.")
    g.add_argument("--mock-llm", action="store_true",
                   help="run end to end on canned fixtures. Proves orchestration, not findings.")
    ap.add_argument("--feature", default=None,
                    help="override the prioritiser and build this feature id")
    ap.add_argument("--top", type=int, default=12, help="rows to print from the ranking")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--node", default="node", help="node binary for the parse check")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    mode = "mock" if args.mock_llm else "live"
    run_id = args.run_id or f"builder-{time.strftime('%Y%m%d-%H%M%S')}-{mode}"
    bb = Blackboard(run_id, root=REPO)
    bb.log(f"# uhta builder — {run_id}\n\nGoal-oriented coding agent (Assignment 5). "
           f"Mode: **{mode}**.\n")

    llm = BuilderMockLLM() if args.mock_llm else build_llm("live", REPO / "tests" / "fixtures")
    p = BuilderRun(bb=bb, llm=llm, prompts_dir=PROMPTS, mode=mode,
                   node_bin=args.node, top_n=args.top, force_feature=args.feature)
    try:
        p.run()
        assemble.write_all(p)
        p.write_manifest()
    except AgentError as exc:
        print(f"\nPIPELINE HALT: {exc}\n", file=sys.stderr)
        print(f"See out/{run_id}/FAILED.md", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        bb.write_failed("pipeline", "unhandled", traceback.format_exc())
        print(f"\nPIPELINE HALT: {exc}\nSee out/{run_id}/FAILED.md", file=sys.stderr)
        return 1

    print(f"\n{'='*72}")
    print(f"SELECTED  {p.chosen.feature.id} — {p.chosen.feature.name}")
    print(f"          score {p.chosen.total:+.2f}, margin {priority.margin(p.scores)}")
    print(f"BUILT     {len(p.patch.insert.splitlines())} lines, "
          f"new assertions: {', '.join(p.new_assertions)}")
    dis = gap.disagreements(p.verdicts)
    print(f"GAPS      {sum(1 for v in p.verdicts if v.is_gap)} of {len(p.verdicts)} features"
          f" · {len(dis)} disagreement(s) with the GDD's own status column")
    print(f"ARTIFACTS out/{run_id}/  (PRIORITY.md · GAP-REPORT.md · FEATURES.md · "
          f"GENERATED.md · patch.diff · uhta-slice.patched.html)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
