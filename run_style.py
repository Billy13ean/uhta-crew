#!/usr/bin/env python3
"""run_style.py — the A7 Style Guide Agent pipeline for uhta.

Modes (same trio as every pipeline in this repo):
  python3 run_style.py --selftest       no key, no calls
  python3 run_style.py --mock-llm       full loop on fixtures, every path
  python3 run_style.py                  live (~15-30 calls, < $1)

Options: --run-id ID   --escalation-limit N
"""
import argparse, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from style import spec, checks, agents, pipeline, fixtures
from style.llm import MockLLM, LiveLLM, LLMError

OUT = Path(__file__).resolve().parent / "out"


def selftest() -> int:
    n = 0
    def ok(cond, msg):
        nonlocal n
        n += 1
        if not cond:
            print(f"SELFTEST FAILED at #{n}: {msg}")
            sys.exit(1)

    # --- spec / guide integrity ------------------------------------------
    ok(spec.GUIDE_PATH.exists(), "STYLEGUIDE.md present")
    ok(spec.guide_integrity() == [], f"guide/spec drift: {spec.guide_integrity()}")
    ok(len(spec.CONSTRAINT_TYPES) >= 3, ">=3 constraint types (rubric)")
    ok(sum(1 for i in spec.ITEMS if i["kind"] == "sabotage") == 3,
       "exactly 3 sabotage demos (rubric: 3 violation classes)")
    classes = {i["violation_class"] for i in spec.ITEMS if i["kind"] == "sabotage"}
    ok(classes == {"TONE", "VOCAB", "FORMAT"}, "demo classes are distinct")
    ok(len(spec.guide_sha()) == 16, "guide hashes")

    # --- deterministic gate: must catch each seeded failure class --------
    f = checks.run_gate("You gained 14 points!", "B")
    ok(any(x["rule"] == "F2" for x in f), "gate catches digits")
    ok(any(x["rule"] == "F3" for x in f), "gate catches exclamation")
    ok(any(x["rule"] == "F4" for x in f), "gate catches 2nd person in B")
    f = checks.run_gate("Press E to enter the menu", "B")
    ok(any(x["rule"] == "V3" for x in f), "gate flags interface language")
    f = checks.run_gate("The old gods grant mana", "B")
    ok(any(x["rule"] == "V1/V2" for x in f), "gate flags forbidden nouns")
    f = checks.run_gate("Fourteen sleeps have passed", "B")
    ok(any(x["rule"] == "F2" for x in f), "gate catches spelled sim quantities")
    long_b = "One. " * 60
    ok(any(x["rule"] == "F1" for x in checks.run_gate(long_b, "B")),
       "gate catches Register B length")
    ok(checks.run_gate(
        "Where belief took root the tribes stopped walking.", "B") == [],
       "gate passes a clean Register B line")
    ok(checks.caps_score([{"rule": "F2", "detail": ""}]), "F findings cap")
    ok(not checks.caps_score([{"rule": "V3", "detail": ""}]), "V findings don't cap")

    # --- evaluator contract parsing --------------------------------------
    ok(agents.SCORE_RE.search("SCORE: [7/10]").group(1) == "7", "score parse []")
    ok(agents.SCORE_RE.search("score: 10/10").group(1) == "10", "score parse bare")
    ok(agents.SCORE_RE.search("PASS") is None, "binary verdict rejected")
    ok(agents.REPAIR_RE.search("REWRITE: better line"), "repair attempt detected")

    # --- full mock pipeline ----------------------------------------------
    import tempfile, json
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "st"
        rc = pipeline.run(MockLLM(fixtures.script()), run_dir, mock=True)
        ok(rc == 0, "mock pipeline exit 0")
        for name in ["STYLE-LOG.md", "BEFORE-AFTER.md", "candidates.md",
                     "manifest.json", "RUN-LOG.md", "ESCALATED.md"]:
            ok((run_dir / name).exists(), f"artifact {name}")
        man = json.loads((run_dir / "manifest.json").read_text())
        ok(man["items"]["demo-tone"] == "ACCEPTED", "tone demo repaired")
        ok(man["items"]["demo-vocab"] == "ACCEPTED", "vocab demo repaired")
        ok(man["items"]["demo-format"] == "ACCEPTED", "format demo repaired")
        ok(man["items"]["era-victorian"] == "ESCALATED", "escalation path shown")
        ba = (run_dir / "BEFORE-AFTER.md").read_text()
        for cls in ["TONE", "VOCAB", "FORMAT"]:
            ok(f"Violation class: {cls}" in ba, f"before/after covers {cls}")
        ok("SCORE: 2/10" in ba or "SCORE: [2/10]" in ba or "2/10" in ba,
           "scores surfaced in before/after")
        ok("**Signed (Director):** ____" in (run_dir / "candidates.md").read_text(),
           "Director gate unfilled")
        # breaker trip
        run_dir2 = Path(td) / "trip"
        rc2 = pipeline.run(MockLLM(fixtures.script()), run_dir2, mock=True,
                           escalation_limit=1)
        ok(rc2 == 1, "breaker trips at limit 1")
        ok("circuit-breaker" in (run_dir2 / "FAILED.md").read_text(),
           "FAILED.md names the breaker")

    print(f"SELFTEST PASSED — {n} assertions")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mock-llm", action="store_true")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--escalation-limit", type=int,
                    default=spec.ESCALATION_LIMIT)
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    run_id = args.run_id or f"style-{time.strftime('%y%m%d-%H%M%S')}"
    run_dir = OUT / run_id
    try:
        llm = MockLLM(fixtures.script()) if args.mock_llm else LiveLLM()
    except LLMError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
    rc = pipeline.run(llm, run_dir, mock=args.mock_llm,
                      escalation_limit=args.escalation_limit)
    print(f"{'COMPLETED' if rc == 0 else 'FAILED'} — out/{run_id}/")
    sys.exit(rc)


if __name__ == "__main__":
    main()
