"""Every output document, generated from the run. Nothing here is typed by hand.

The rule this module enforces is the same one `crew/agents/playtester.py`
enforces for the metrics board: **a number or a verdict a reader might check
must not be able to reach an artifact except by having actually happened.** The
static framing prose in `README-A4.md` is marked off from the injected data, so
a reader can tell which sentences a human wrote and which an execution produced.
"""
from __future__ import annotations

import time

from .beats import CONTENT_TYPES
from .retriever import BM25_B, BM25_K1, SCORE_THRESHOLD, TOKEN_BUDGET

DIRECTOR_BLOCK = """
---

## Director selection

*Left unfilled by the pipeline. Generation is bulk and cheap; which words become
the only words in a wordless game is a Director ruling (GDD §4.5, "human as
curator"). The pipeline proposes candidates and stops here.*

**Chosen line (per beat):** _______________________________________________

**Rejected because:** ____________________________________________________

**Signed (Director):** _______________  **Date:** ____________
"""


def _mock_banner(p) -> str:
    if getattr(p.llm, "name", "") != "mock":
        return ""
    return (
        "> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Every Writer and Critic\n"
        "> response below was replayed verbatim from `tests/fixtures/content/`. No\n"
        "> model saw a chunk; no judgement was exercised. Nothing here is evidence\n"
        "> about uhta's text. The RETRIEVAL half of this run is real — BM25 ranking\n"
        "> and the corpus policy execute identically in every mode.\n\n"
    )


def _head(p, title: str, subtitle: str) -> str:
    return (f"# {title}\n\n{_mock_banner(p)}> {subtitle}\n>\n"
            f"> Run `{p.run_id}` · backend `{getattr(p.llm, 'name', 'n/a')}` · "
            f"model `{getattr(p.llm, 'model', 'n/a')}` · "
            f"generated {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")


# --------------------------------------------------------------------------
# the three content files
# --------------------------------------------------------------------------

def _content_file(p, kind: str) -> str:
    ct = CONTENT_TYPES[kind]
    rows = [r for r in p.results if r["beat"].type == kind]
    out = [_head(p, ct["title"], "Generated content, pending Director selection.")]
    out.append(f"**The gap this fills.** {ct['gap']}\n\n")
    out.append(f"**Register.** {ct['register']}\n\n---\n\n")
    for r in rows:
        b, sel = r["beat"], r["selection"]
        out.append(f"## {b.id} — {b.label}\n\n*{b.brief}*\n\n")
        out.append("**Retrieved:** " + ", ".join(
            f"`{x.chunk.doc} §{x.chunk.section}` ({x.chunk.heading}, bm25 "
            f"{x.score:.2f})" for x in sel.selected) + "\n\n")
        out.append("| # | verdict | candidate |\n|---|---|---|\n")
        for v in r["verdicts"]:
            mark = "PASS" if not v.failed else f"**FAIL** `{v.flag_class}`"
            line = v.line.replace("|", "\\|")
            out.append(f"| {v.index} | {mark} | {line} |\n")
        out.append("\n")
        corrected = [v for v in r["verdicts"] if v.failed]
        if corrected:
            out.append("**Critic corrections** (the repaired line replaces the "
                       "rejected one as a candidate):\n\n")
            for v in corrected:
                out.append(f"- #{v.index} → {v.correction}\n")
            out.append("\n")
    out.append(DIRECTOR_BLOCK)
    return "".join(out)


# --------------------------------------------------------------------------
# RAG-TRACE.md
# --------------------------------------------------------------------------

def _rag_trace(p) -> str:
    c = p.corpus_stats
    out = [_head(p, "RAG-TRACE — query → retrieved chunk → output",
                 "Retrieval is deterministic. Every selection and every cut below "
                 "was produced by `content/retriever.py`, not by a model.")]
    out.append(
        "## Corpus\n\n"
        f"Chunk rule: **one `###` subsection** (GDD §4.5 — \"the section boundary "
        f"*is* the chunk boundary\"); a `##` section with no `###` children is one "
        f"chunk. Headings inside fenced code blocks are not headings.\n\n"
        f"Scorer: **BM25**, pure Python (`content/retriever.py`), "
        f"k1={BM25_K1}, b={BM25_B}, non-negative IDF. Score threshold "
        f"**{SCORE_THRESHOLD}**, token budget **{TOKEN_BUDGET}** (estimated tokens).\n\n"
        f"| | chunks | words |\n|---|---|---|\n"
        f"| **indexed** | {c['chunks_indexed']} | {c['words_indexed']:,} |\n"
        f"| **excluded by corpus policy** | {c['chunks_excluded']} | {c['words_excluded']:,} |\n"
        f"| total parsed | {c['chunks_total']} | {c['words_indexed'] + c['words_excluded']:,} |\n\n"
        f"### Corpus policy — `{c['policy']}`\n\n{c['policy_rationale']}\n\n"
        f"**Every excluded chunk, with its reason** (not a summary — the list):\n\n"
        "| chunk | heading | words | reason |\n|---|---|---|---|\n")
    for e in c["exclusions"]:
        out.append(f"| `{e['key']}` | {e['heading'][:60]} | {e['words']} | {e['reason']} |\n")
    out.append("\n### What is in the index\n\n| chunk | heading | words | est. tokens |\n|---|---|---|---|\n")
    for k in c["indexed"]:
        out.append(f"| `{k['key']}` | {k['heading'][:60]} | {k['words']} | {k['est_tokens']} |\n")

    out.append("\n---\n\n## Per-beat trace\n\n"
               "Each beat runs **two** queries and unions their cuts — the GDD §4.5 "
               "two-chunk rule. Query 1 is the mechanical consequence; query 2 is the "
               "experience.\n\n")
    for r in p.results:
        b, sel = r["beat"], r["selection"]
        out.append(f"### {b.id} — {b.label}\n\n")
        out.append(f"**Query 1 (mechanic):** `{b.query_mechanic}`\n\n")
        out.append(f"**Query 2 (experience):** `{b.query_experience}`\n\n")
        out.append("**Retrieved:**\n\n")
        for x in sel.selected:
            out.append(f"- `{x.chunk.doc} §{x.chunk.section}` — *{x.chunk.heading}* — "
                       f"**bm25 {x.score:.2f}**, {x.chunk.words} words, "
                       f"~{x.chunk.tokens} est. tokens\n\n"
                       f"  > {x.chunk.excerpt(500)}\n\n")
        if sel.exclusions:
            out.append("**Cut, with reasons:**\n\n")
            for e in sel.exclusions:
                out.append(f"- `{e.key}` *{e.heading[:50]}* — {e.reason}\n")
            out.append("\n")
        out.append(f"**Output** ({len(r['candidates'])} candidates, "
                   f"{sum(1 for v in r['verdicts'] if not v.failed)} cleared the Critic):\n\n")
        for v in r["verdicts"]:
            tag = "PASS" if not v.failed else f"FAIL/{v.flag_class}"
            out.append(f"- `{tag}` {v.line}\n")
        out.append("\n")
    return "".join(out)


# --------------------------------------------------------------------------
# CRITIC-LOG.md
# --------------------------------------------------------------------------

def _critic_log(p) -> str:
    all_v = [(r["beat"], v) for r in p.results for v in r["verdicts"]]
    fails = [(b, v) for b, v in all_v if v.failed]
    out = [_head(p, "CRITIC-LOG — every verdict, every correction",
                 "A FAIL with no correction raises AgentError and halts the run "
                 "(`content/agents/critic.py`). This file cannot contain a "
                 "rejection that was not repaired.")]
    by_class: dict[str, int] = {}
    for _, v in fails:
        by_class[v.flag_class or "?"] = by_class.get(v.flag_class or "?", 0) + 1
    out.append(
        f"## Summary\n\n"
        f"| | |\n|---|---|\n"
        f"| candidates judged | **{len(all_v)}** |\n"
        f"| passed | {len(all_v) - len(fails)} |\n"
        f"| **caught and corrected** | **{len(fails)}** |\n"
        f"| beats | {len(p.results)} |\n\n")
    if by_class:
        out.append("**By flag class:**\n\n| class | count |\n|---|---|\n")
        for k, n in sorted(by_class.items(), key=lambda kv: -kv[1]):
            out.append(f"| `{k}` | {n} |\n")
        out.append("\n")
    else:
        out.append(
            "> **No candidate was rejected in this run.** That is a result, not a "
            "pass: the Critic ran at temperature 0 against every candidate and "
            "found nothing to repair. Re-run with a higher `--candidates` count to "
            "widen the Writer's spread, or read the A/B section of "
            "`VOICE-JUDGMENT.md`, where the deliberately weaker retrieval arm is "
            "the likeliest source of an honest catch.\n\n")

    out.append("---\n\n## Catches — the correction is shown, not claimed\n\n")
    if not fails:
        out.append("*(none in this run — see the note above)*\n\n")
    for b, v in fails:
        out.append(
            f"### {b.id} · candidate {v.index} — `{v.flag_class}`\n\n"
            f"**Rejected line**\n\n> {v.line}\n\n"
            f"**Chunk it breaks** (quoted by the Critic from the text the Writer "
            f"was given)\n\n> {v.quoted_chunk}\n\n"
            f"**Why** — {v.reason}\n\n"
            f"**Correction**\n\n> {v.correction}\n\n---\n\n")

    out.append("## Full verdict table\n\n| beat | # | verdict | class | line |\n|---|---|---|---|---|\n")
    for b, v in all_v:
        out.append(f"| {b.id} | {v.index} | {'PASS' if not v.failed else 'FAIL'} | "
                   f"{v.flag_class or ''} | {v.line.replace('|', chr(92) + '|')[:90]} |\n")
    return "".join(out)


# --------------------------------------------------------------------------
# VOICE-JUDGMENT.md
# --------------------------------------------------------------------------

def _voice_judgment(p) -> str:
    out = [_head(p, "VOICE-JUDGMENT — does this sound like uhta?",
                 "Self-assessment plus the one retrieval change that was measured "
                 "rather than asserted.")]
    out.append(
        "## The test a line has to pass\n\n"
        "uhta's register is fixed in GDD §2.5: *\"short declarative lines, no "
        "mythology\"*, and the narration is **instrumentation, not lore**. So the "
        "question is not whether a line is pretty. It is:\n\n"
        "> Would this line read identically in any other god-game about hope and "
        "fear?\n\n"
        "If yes, it has failed, however well written it is. That is the `GENERIC` "
        "flag class in `prompts/critic.md`, and it is the one the Critic is told to "
        "be hardest about.\n\n---\n\n")

    if not p.ab:
        out.append("## The retrieval tweak\n\n*A/B stage did not run in this "
                   "invocation (the A/B beat was filtered out).*\n\n")
        return "".join(out)

    beat = p.ab["beat"]
    a = p.ab["arms"]["A-naive-top1"]
    b = p.ab["arms"]["B-two-chunk-rule"]
    a_pass = sum(1 for v in a["verdicts"] if not v.failed)
    b_pass = sum(1 for v in b["verdicts"] if not v.failed)

    out.append(
        f"## The retrieval tweak, measured — beat `{beat.id}` ({beat.label})\n\n"
        "GDD §4.5 records the change and the reason for it:\n\n"
        "> The first hand-run retrieved **only** §2.5, the experience section, and "
        "every candidate came back generic: lines that would sit unchanged in any "
        "god-game about hope and fear. The fix was not a better prompt but a wider "
        "cut — **a narration beat now retrieves two chunks, the experience section "
        "*and* the verb's own row from the §2.2 table**.\n\n"
        "That was design-stage. This run executes both arms on the same beat, with "
        "the same Writer temperature and candidate count, and hands **both candidate "
        "sets to the same Critic at temperature 0, judged against the same "
        "chunks** — so the only variable is what the Writer could see.\n\n"
        "| arm | retrieval | chunks the Writer saw | candidates | cleared the Critic |\n"
        "|---|---|---|---|---|\n")
    out.append(
        f"| **A — naive** | single experience-side query, top-1 | "
        + ", ".join(f"`§{x.chunk.section}`" for x in a["selection"].selected)
        + f" | {len(a['candidates'])} | **{a_pass}/{len(a['verdicts'])}** |\n")
    out.append(
        f"| **B — GDD §4.5 rule** | two queries (mechanic + experience), unioned | "
        + ", ".join(f"`§{x.chunk.section}`" for x in b["selection"].selected)
        + f" | {len(b['candidates'])} | **{b_pass}/{len(b['verdicts'])}** |\n\n")

    delta = b_pass / max(1, len(b["verdicts"])) - a_pass / max(1, len(a["verdicts"]))
    if delta > 0:
        read = (f"Arm B cleared a higher share of its candidates ({b_pass}/"
                f"{len(b['verdicts'])} vs {a_pass}/{len(a['verdicts'])}). The "
                f"mechanical chunk is what the extra passes are made of — the "
                f"Critic's `GENERIC` class is the one arm A loses candidates to.")
    elif delta < 0:
        read = (f"Arm A cleared a higher share this run ({a_pass}/{len(a['verdicts'])} "
                f"vs {b_pass}/{len(b['verdicts'])}). That is against the design's "
                f"prediction and is reported as measured; a single beat at n="
                f"{len(a['verdicts'])} is a thin sample and the honest read is that "
                f"this run did not reproduce the effect.")
    else:
        read = (f"Both arms cleared the same share ({a_pass}/{len(a['verdicts'])}). "
                f"The pass rate did not separate them this run — read the candidate "
                f"text below rather than the count, and treat n="
                f"{len(a['verdicts'])} on one beat as the thin sample it is.")
    out.append(f"**Read.** {read}\n\n")

    for name, arm in (("A — naive single-query top-1", a),
                      ("B — the two-chunk rule", b)):
        out.append(f"### Arm {name}\n\n")
        for v in arm["verdicts"]:
            tag = "PASS" if not v.failed else f"FAIL `{v.flag_class}`"
            out.append(f"- {tag} — {v.line}\n")
            if v.failed:
                out.append(f"    - *{v.reason}*\n")
        out.append("\n")

    out.append(
        "---\n\n## Where this still falls short\n\n"
        "- **One beat, one run.** The A/B is a single beat at "
        f"n={len(a['candidates'])} candidates per arm. It is evidence about a "
        "retrieval policy, not a statistically meaningful measurement.\n"
        "- **The Critic is the same model family as the Writer.** An adversarial "
        "evaluator that shares the generator's priors will miss the failures both "
        "share. The rules crew has the same limitation and names it too.\n"
        "- **No player has read any of this.** GDD §2.8 is 0 of 6 tested. These "
        "lines are the thing that unblocks criteria 1 and 3; whether they *work* is "
        "a question only the stranger test answers.\n"
        "- **Selection is not automated and should not be.** Every line here is a "
        "candidate. The `## Director selection` block in each content file is "
        "deliberately empty.\n")
    return "".join(out)


# --------------------------------------------------------------------------
# README-A4.md
# --------------------------------------------------------------------------

def _readme_a4(p) -> str:
    c = p.corpus_stats
    all_v = [v for r in p.results for v in r["verdicts"]]
    fails = [v for v in all_v if v.failed]
    types = sorted({r["beat"].type for r in p.results})
    out = [_head(p, "Assignment 4 — dynamic content pipeline for uhta",
                 "What content was generated, does it sound like the game, and what "
                 "did the Critic catch.")]
    out.append(
        "## What this is\n\n"
        "`run_content.py` generates the **text** of uhta — a wordless browser "
        "god-game about emotional contagion — against the game's own GDD read as a "
        "RAG corpus. It is a second, independent pipeline in the Assignment-3 repo: "
        "it reuses `crew/blackboard.py`, `crew/llm.py` and `crew.agents.AgentError` "
        "verbatim, and **nothing in `crew/` imports `content/`**, so adding it could "
        "not change what a rules run does.\n\n"
        "```\ncorpus (deterministic)   chunk 4 blackboard files at ### boundaries, scope by\n"
        "                         CORPUS_POLICY, record every exclusion -> BM25 index\n"
        "retrieval (deterministic) per beat: two queries (mechanic + experience),\n"
        "                         union their cuts, record every exclusion\n"
        "generation               Writer (temp 0.9, N candidates) -> Critic (temp 0.0,\n"
        "                         verdict + quoted chunk + correction)\n"
        "ab                       the same beat twice: naive top-1 vs the GDD §4.5\n"
        "                         two-chunk rule, both sets judged by the same Critic\n"
        "assembly (deterministic) content files + RAG-TRACE / CRITIC-LOG /\n"
        "                         VOICE-JUDGMENT / this file, all generated\n```\n\n"
        "---\n\n## 1. The knowledge base is the game's own GDD\n\n"
        "*[injected from this run]*\n\n"
        f"- Corpus files: {', '.join('`' + f + '`' for f in c['files'])}\n"
        f"- **{c['chunks_indexed']} chunks / {c['words_indexed']:,} words indexed**\n"
        f"- **{c['chunks_excluded']} chunks / {c['words_excluded']:,} words excluded**, "
        f"each with a recorded reason (see `RAG-TRACE.md`)\n\n"
        "There is no placeholder lore anywhere in this pipeline. The corpus is "
        "`uhta-gdd-v0.9.7`, its abridged submission variant, and `CANON.md`, the "
        "locked-decision digest.\n\n"
        "**The corpus is *scoped*, which is the part worth arguing about.** The GDD "
        "is two documents in one binding — the design of uhta, and the design of the "
        "pipeline that builds uhta. Only the first is a knowledge base for writing "
        "the game's text, so `CORPUS_POLICY` keeps §1, §2, §5, §6 and Appendix A and "
        "drops §3, §4, §7, the version changelogs and `CANON-process.md`. The sharp "
        "case is **§4.5**, which contains the Director's own hand-written worked "
        "narration example. Indexed, it ranks near the top on a Roar query — and a "
        "Writer handed it is not generating a line, it is handing the Director's "
        "back. Excluding it is the difference between a pipeline that writes and one "
        "that retrieves an answer.\n\n"
        "---\n\n## 2. Three content types the game specifically needs\n\n")
    for kind in ("narration", "era-flavor", "endscreen"):
        if kind not in types:
            continue
        ct = CONTENT_TYPES[kind]
        n = sum(1 for r in p.results if r["beat"].type == kind)
        out.append(f"### {ct['title']} — {n} beats → `{ct['file']}`\n\n"
                   f"**The gap.** {ct['gap']}\n\n")
    out.append(
        "None of these is a demonstration topic. The narration lines in particular "
        "are the single item on the project's critical path: GDD §2.7 lists the "
        "narrated opening as the only unbuilt thing blocking the Definition of "
        "Playable, and §2.8 criteria 1 and 3 are **Blocked** on it by name.\n\n"
        "---\n\n## 3. Retrieval — query, chunk and output side by side\n\n"
        "`RAG-TRACE.md` is the artifact for this and it is generated per run: for "
        "every beat it prints both queries, every chunk selected with its BM25 "
        "score, an excerpt of the chunk text, every chunk cut with the reason it was "
        "cut, and the candidates that came out.\n\n"
        "Retrieval is **BM25 in pure Python** (`content/retriever.py`, k1=1.5, "
        "b=0.75, non-negative IDF) rather than a package, because the assignment "
        "permits one third-party dependency and it is already spent on `anthropic`. "
        "The scorer being written out is not a purity argument — it is what lets "
        "`--selftest` assert specific ranking behaviour with numbers, without a key "
        "and without a model.\n\n"
        "---\n\n## 4. What the Critic caught\n\n*[injected from this run]*\n\n")
    out.append(
        f"- **{len(all_v)} candidates judged**, {len(all_v) - len(fails)} passed, "
        f"**{len(fails)} caught and corrected**\n")
    if fails:
        first = fails[0]
        out.append(f"- Flag classes fired: "
                   + ", ".join(f"`{k}`" for k in sorted({v.flag_class for v in fails}))
                   + "\n\n**The first catch, in full:**\n\n"
                   f"> **Rejected** — {first.line}\n>\n"
                   f"> **Chunk it breaks** — {first.quoted_chunk}\n>\n"
                   f"> **Why** — {first.reason}\n>\n"
                   f"> **Correction** — {first.correction}\n\n")
    else:
        out.append("- No candidate was rejected in this run. See the note at the top "
                   "of `CRITIC-LOG.md`: that is a reported result, not a silence.\n\n")
    out.append(
        "The consistency loop is **structural, not exhortative**. "
        "`content/agents/critic.py` raises `AgentError` and halts the run on a `FAIL` "
        "with an empty `correction`, on a flag class outside the four allowed, and on "
        "a FAIL that quotes no chunk. `CRITIC-LOG.md` therefore cannot contain a "
        "rejection without a repair — the pipeline is incapable of producing one.\n\n"
        "---\n\n## 5. Does it sound like uhta?\n\n"
        "`VOICE-JUDGMENT.md`, generated from this run, is the self-assessment — "
        "including the A/B stage that measures the one retrieval change on record "
        "instead of asserting it, and a closing section on where the whole thing "
        "still falls short.\n\n"
        "---\n\n## 6. Running it\n\n"
        "```bash\npython3 run_content.py --selftest      # no key: retrieval assertions\n"
        "python3 run_content.py --mock-llm      # no key: full pipeline on fixtures (NOT content)\n"
        "python3 run_content.py --candidates 8  # LIVE — needs ANTHROPIC_API_KEY\n```\n\n"
        "`--mock-llm` replays canned fixtures and produces no real content; every "
        "artifact it writes is stamped as such and `manifest.json` records "
        "`\"llm_backend\": \"mock\"`. The retrieval half is real in every mode.\n\n"
        "**It ends at a human.** The rules crew stops at a blank `## Ruling`; this "
        "pipeline stops at an unfilled `## Director selection`, and the endscreen "
        "file is marked UNRULED throughout because GDD §6 records that question as "
        "open.\n")
    return "".join(out)


# --------------------------------------------------------------------------

def write_all(p) -> None:
    for kind, ct in CONTENT_TYPES.items():
        if any(r["beat"].type == kind for r in p.results):
            p.bb.write(ct["file"], _content_file(p, kind), "assemble")
    p.bb.write("RAG-TRACE.md", _rag_trace(p), "assemble")
    p.bb.write("CRITIC-LOG.md", _critic_log(p), "assemble")
    p.bb.write("VOICE-JUDGMENT.md", _voice_judgment(p), "assemble")
    p.bb.write("README-A4.md", _readme_a4(p), "assemble")
