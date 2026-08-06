#!/usr/bin/env python3
"""uhta content pipeline — Assignment 4, dynamic content pipeline. Entry point.

Generates the game's TEXT — the teacher's narration for the opening cycle, era
and settlement flavor, endscreen candidates — from uhta's own GDD read as a RAG
corpus. Separate program from `run_crew.py`, which produces the game's NUMBERS.

Three run modes:

    python3 run_content.py                  live. Calls the Anthropic API.
                                            Model: $CREW_MODEL (default claude-sonnet-4-5).
                                            Key:   $ANTHROPIC_API_KEY.

    python3 run_content.py --selftest       NO API CALLS. Asserts the deterministic
                                            half: chunking, the corpus policy, BM25
                                            ranking with real numbers, the two-chunk
                                            rule, and every halt guard in the Critic.
                                            Exits 0 on success.

    python3 run_content.py --mock-llm       NO API CALLS. Full pipeline with canned
                                            fixtures from tests/fixtures/content/.
                                            Proves the orchestration runs; produces
                                            NO real content.

Useful flags: --candidates N (per beat, default 6), --beats n4,e1 (subset),
--run-id NAME.

See README-A4.md in any completed run directory for what it produced and why.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from crew.agents import AgentError  # noqa: E402
from crew.blackboard import Blackboard, MissingArtifactError  # noqa: E402
from crew.llm import LLMCall  # noqa: E402
from content.agents.critic import run_critic  # noqa: E402
from content.agents.writer import run_writer  # noqa: E402
from content.beats import AB_BEAT_ID, BEATS, CONTENT_TYPES  # noqa: E402
from content.orchestrator import ContentOrchestrator  # noqa: E402
from content.pipeline import CORPUS_FILES, ContentPipeline  # noqa: E402
from content.retriever import (SCORE_THRESHOLD, Retriever, Selection,  # noqa: E402
                               build_corpus, chunk_markdown)

BANNER = "=" * 74


class _ScriptedLLM:
    """Returns a fixed string. Used only by --selftest, to drive the Critic's
    halt guards without an API key. Never used by a real run."""
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
    print("uhta content pipeline — SELFTEST (no API key required, no API calls)")
    print(BANNER)
    failures: list[str] = []
    run_id = f"content-selftest-{time.strftime('%Y%m%d-%H%M%S')}"
    bb = Blackboard(run_id, root=ROOT, quiet=True)

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    # ---- 1. chunking ----
    print("\n[1/5] Chunking — one ### subsection is one chunk (GDD §4.5)")
    for name, rel in CORPUS_FILES.items():
        check(f"seeded corpus file present: {name}", bb.bb_path(rel).exists())
    docs = {n: bb.read_bb(r, "selftest") for n, r in CORPUS_FILES.items()}
    full = chunk_markdown(docs["uhta-gdd-v0.9.7-full.md"], "uhta-gdd-v0.9.7-full.md")
    secs = {c.section for c in full}
    check("the full GDD splits into its numbered subsections",
          {"2.2", "2.3", "2.5", "4.5"} <= secs, f"{len(full)} chunks")
    abridged = chunk_markdown(docs["uhta-gdd-v0.9.7-abridged.md"],
                              "uhta-gdd-v0.9.7-abridged.md")
    fenced = [c for c in abridged if c.heading.startswith(("Change under review",
                                                           "Coherence verdict",
                                                           "Cross-file impact"))]
    check("headings inside fenced code blocks are NOT treated as sections",
          not fenced,
          "the abridged §3.2 embeds a report skeleton whose lines start with ##; "
          f"{len(fenced)} leaked" if fenced else
          "the abridged §3.2 embeds a report skeleton whose lines start with ##")

    # ---- 2. corpus policy ----
    print("\n[2/5] Corpus policy — game material in, pipeline material out")
    all_chunks, dropped, kept = build_corpus(docs)
    kept_keys = {c.key for c in kept}
    check("policy actually removed §3 (AI architecture)",
          not any(c.top_level == "3" for c in kept),
          f"{sum(1 for d in dropped if d.key.split('#')[1].startswith('3'))} §3 chunk(s) dropped")
    check("policy actually removed §4 (technical strategy)",
          not any(c.top_level == "4" for c in kept))
    check("policy actually removed §7 (provenance)",
          not any(c.top_level == "7" for c in kept))
    check("policy actually removed CANON-process.md",
          not any(c.doc == "CANON-process.md" for c in kept))
    check("§4.5 — the Director's own worked narration example — is NOT indexed",
          "uhta-gdd-v0.9.7-full.md#4.5" not in kept_keys,
          "a Writer handed it would return the Director's line, not write one")
    check("version front matter / changelog is NOT indexed",
          not any(c.top_level == "front-matter" for c in kept))
    check("the game's own material IS indexed",
          {"uhta-gdd-v0.9.7-full.md#2.2", "uhta-gdd-v0.9.7-full.md#2.3",
           "uhta-gdd-v0.9.7-full.md#2.5"} <= kept_keys)
    check("every exclusion carries a reason",
          all(d.reason.strip() for d in dropped), f"{len(dropped)} exclusions")
    print(f"         corpus: {len(kept)} chunks / {sum(c.words for c in kept):,} words IN · "
          f"{len(dropped)} chunks / {sum(d.words for d in dropped):,} words OUT")

    # ---- 3. BM25 ranking ----
    print("\n[3/5] BM25 retrieval — real ranking, real numbers")
    r = Retriever(kept)
    check("IDF is non-negative for every term in the vocabulary",
          all(r.idf(t) >= 0 for t in r._df), f"{len(r._df)} terms")

    roar_q = ("Roar shatters a line of tiles NPCs within witness radius take an "
              "unconditional Fear push regardless of flame color")
    roar = r.rank(roar_q)
    check("a Roar query ranks the §2.2 verb table FIRST",
          roar[0].chunk.section == "2.2" and roar[0].chunk.doc.endswith("full.md"),
          f"bm25 {roar[0].score:.2f} vs {roar[1].score:.2f} for the runner-up "
          f"(§{roar[1].chunk.section})")

    burn_q = ("burnout overdose threshold frozen value save opposing valence timer "
              "sleeps")
    burn = r.rank(burn_q)
    check("a burnout query ranks the §2.3 systems block FIRST",
          burn[0].chunk.section == "2.3",
          f"bm25 {burn[0].score:.2f}")

    controls = {
        "sourdough": "sourdough bread starter hydration baking oven temperature crumb",
        "tax filing": "quarterly tax filing deadline depreciation schedule invoice payroll",
    }
    for label, q in controls.items():
        sel = r.select(q, max_chunks=2)
        best = r.rank(q)[0].score
        check(f"off-topic control ('{label}') retrieves NOTHING",
              not sel.selected,
              f"best chunk scored {best:.2f} against a threshold of {SCORE_THRESHOLD}")

    # ---- 4. the two-chunk rule ----
    print("\n[4/5] The GDD §4.5 two-chunk rule")
    thin = 0
    for b in BEATS:
        if len(r.select_multi(b.queries).selected) < 2:
            thin += 1
    check("every beat retrieves two chunks", thin == 0,
          f"{len(BEATS)} beats, {thin} thin")
    ab = next(b for b in BEATS if b.id == AB_BEAT_ID)
    arm_a = r.select(ab.query_experience, max_chunks=1)
    arm_b = r.select_multi(ab.queries)
    a_keys = {x.chunk.key for x in arm_a.selected}
    b_keys = {x.chunk.key for x in arm_b.selected}
    check("the A/B arms genuinely differ (the tweak is a real change)",
          a_keys != b_keys and a_keys < b_keys,
          f"naive={sorted(x.chunk.section for x in arm_a.selected)} ⊂ "
          f"two-chunk={sorted(x.chunk.section for x in arm_b.selected)}")
    check("every beat names the gap it fills",
          all(CONTENT_TYPES[b.type]["gap"].strip() for b in BEATS),
          f"{len(CONTENT_TYPES)} content types")

    # ---- 5. halt guards ----
    print("\n[5/5] Halt guards — the Critic cannot record a rejection it did not repair")
    beat = ab
    ct = CONTENT_TYPES[beat.type]
    cands = ["a line", "another line"]

    def critic_with(payload: str):
        return run_critic(_ScriptedLLM(payload), ROOT / "prompts", beat, arm_b,
                          cands, ct, agent_label="critic-selftest")

    guards = [
        ("a FAIL with no correction HALTS",
         '```json\n[{"index":1,"verdict":"PASS","class":null,"quoted_chunk":"x","reason":"r","correction":null},'
         '{"index":2,"verdict":"FAIL","class":"GENERIC","quoted_chunk":"x","reason":"r","correction":null}]\n```',
         "correction"),
        ("a FAIL with an unknown flag class HALTS",
         '```json\n[{"index":1,"verdict":"PASS","class":null,"quoted_chunk":"x","reason":"r","correction":null},'
         '{"index":2,"verdict":"FAIL","class":"VIBES","quoted_chunk":"x","reason":"r","correction":"fixed"}]\n```',
         "not one of"),
        ("a FAIL that quotes no chunk HALTS",
         '```json\n[{"index":1,"verdict":"PASS","class":null,"quoted_chunk":"x","reason":"r","correction":null},'
         '{"index":2,"verdict":"FAIL","class":"GENERIC","quoted_chunk":"","reason":"r","correction":"fixed"}]\n```',
         "without quoting"),
        ("a verdict count that does not match the candidates HALTS",
         '```json\n[{"index":1,"verdict":"PASS","class":null,"quoted_chunk":"x","reason":"r","correction":null}]\n```',
         "Every candidate must be judged"),
        ("an unparseable response HALTS",
         "here are my thoughts, no json at all", "no JSON payload"),
    ]
    for name, payload, needle in guards:
        try:
            critic_with(payload)
            check(name, False, "no exception raised")
        except AgentError as exc:
            check(name, needle in str(exc), str(exc).split(":", 1)[-1].strip()[:90])

    try:
        run_writer(_ScriptedLLM("[]"), ROOT / "prompts", beat,
                   Selection("q", [], []), ct, 3, agent_label="writer-selftest")
        check("generating from an EMPTY retrieval HALTS", False, "no exception raised")
    except AgentError as exc:
        check("generating from an EMPTY retrieval HALTS",
              "no chunks above the score threshold" in str(exc),
              "placeholder-lore prevention")

    try:
        bb.require("rag-trace-that-was-never-produced.md", "assemble", "generation")
        check("a missing upstream artifact halts naming its producer", False)
    except MissingArtifactError as exc:
        check("a missing upstream artifact halts naming its producer",
              "generation" in str(exc) and "assemble" in str(exc))

    total = len(failures)
    print("\n" + BANNER)
    if failures:
        print(f"SELFTEST FAILED — {total} check(s): " + "; ".join(failures))
        print(BANNER)
        return 1
    print("SELFTEST PASSED — chunking, corpus policy, BM25 ranking, the two-chunk")
    print("rule, and every halt guard. No API key, no API calls, no model.")
    print(BANNER)
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="uhta content pipeline (Retriever, Writer, Critic) — Assignment 4.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--selftest", action="store_true",
                   help="no API calls; assert retrieval accuracy and every halt guard")
    g.add_argument("--mock-llm", action="store_true",
                   help="no API calls; full pipeline on canned fixtures (NOT content)")
    ap.add_argument("--candidates", type=int, default=6,
                    help="candidates the Writer produces per beat (default 6)")
    ap.add_argument("--beats", default=None,
                    help="comma-separated beat ids to run (default: all 16)")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--drop-agent", default=None,
                    choices=list(ContentOrchestrator.DROPPABLE),
                    help="REMOVE an agent from the dispatch sequence. The run is "
                         "expected to HALT with a named error at the first stage "
                         "that needs the missing artifact. This is the role-clarity "
                         "demonstration, shown rather than asserted. Exit code 1 on "
                         "the halt is the PASSING result.")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    mode = "mock" if args.mock_llm else "live"
    print(BANNER)
    print(f"uhta content pipeline — {'MOCK-LLM' if mode == 'mock' else 'LIVE'} run")
    if mode == "mock":
        print("MOCK MODE: no API calls. Writer and Critic responses are canned")
        print("fixtures from tests/fixtures/content/. This proves the pipeline")
        print("executes; it produces NO real content. Retrieval is still real.")
    print(BANNER)

    from crew.llm import LLMError, LiveLLM
    try:
        if mode == "mock":
            from content.fixtures import ContentMockLLM
            llm = ContentMockLLM(ROOT / "tests" / "fixtures" / "content")
        else:
            llm = LiveLLM()
    except LLMError as exc:
        print(f"\nSTARTUP FAILED: {exc}\n")
        return 1

    beat_filter = [b.strip() for b in args.beats.split(",")] if args.beats else None
    if beat_filter:
        known = {b.id for b in BEATS}
        unknown = [b for b in beat_filter if b not in known]
        if unknown:
            print(f"\nUnknown beat id(s): {', '.join(unknown)}. "
                  f"Known: {', '.join(sorted(known))}\n")
            return 1

    if args.drop_agent:
        print(f"\n--drop-agent {args.drop_agent}: this agent will NOT be dispatched.")
        print("EXPECTED RESULT: the pipeline halts with a clear error naming it, and")
        print("exits 1. A completed run here would be the failure.\n")

    p = ContentPipeline(llm, mode, ROOT, run_id=args.run_id,
                        n_candidates=args.candidates, beat_filter=beat_filter,
                        drop_agent=args.drop_agent)
    llm.logger = p.bb.log
    rc = p.run()
    print(f"\nRun directory: out/{p.run_id}/")
    for f in sorted(p.bb.run_dir.iterdir()):
        if f.is_file():
            print(f"  {f.name}  ({f.stat().st_size} B)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
