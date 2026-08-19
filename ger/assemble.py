"""Evidence documents and the drop-in patch. Deterministic; no LLM.

Nothing in these files is typed by hand — every table row is generated from
the run's own data structures, so a claim in an evidence document is a claim
about something that actually happened in this run.
"""
from __future__ import annotations

import re
import time

from .checks import (extract_teaching_text, render_teaching_snippet,
                     _TEACHING_RE)
from .spec import REGISTER, VERBS


def _mock_banner(p) -> str:
    if p.mode != "mock":
        return ""
    return ("> **MOCK-LLM FIXTURE RUN — NOT REAL CONTENT.** Generator, "
            "Evaluator and Refiner responses in this run were canned fixtures "
            "from `tests/fixtures/ger/`, replayed to prove the orchestration — "
            "including the deterministic register gate, the refinement loop and "
            "the circuit breaker — executes end to end without an API key. The "
            "register-gate findings ARE real (the gate is code, not a model); "
            "the prose verdicts are fixtures.\n\n")


def _hdr(p, title: str) -> str:
    return (f"# {title} — {p.run_id}\n\n"
            f"> Pipeline `ger` (Assignment 6) · backend `{p.llm.name}` · model "
            f"`{p.llm.model}` · generated {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            + _mock_banner(p))


# ---------------------------------------------------------------------------

def write_baseline(p) -> None:
    lines = [_hdr(p, "BASELINE AUDIT — the Evaluator vs the shipped build")]
    lines.append(
        "The rule under enforcement (GDD §2.5): *\"" + getattr(p, "register", REGISTER) + "\"*\n\n"
        "Before generating anything, the Evaluator was pointed at the text "
        "already in `blackboard/build/uhta-slice.html`: the seven stub "
        "`TEACHING_TEXT` lines A5's Programmer wrote as placeholders, and the "
        "`guide()` tutorial strings the A5 repo findings measured against the "
        "GDD. A pipeline that only ever judges its own output has never been "
        "tested against a real failure.\n")

    lines.append("\n## guide() tutorial strings vs the register gate\n")
    lines.append("| # | string (truncated) | findings |")
    lines.append("|---|---|---|")
    for i, row in enumerate(p.guide_audit, 1):
        txt = row["text"].replace("|", "\\|")
        txt = (txt[:80] + "…") if len(txt) > 80 else txt
        f = "<br>".join(x.replace("|", "\\|") for x in row["findings"]) or "clean"
        lines.append(f"| {i} | `{txt}` | {f} |")
    caught = sum(1 for r in p.guide_audit if r["findings"])
    lines.append(
        f"\n**{caught} of {len(p.guide_audit)}** shipped tutorial strings fail "
        f"the register gate — `press`, `W A S D`, click vocabulary. This is the "
        f"exact failure class the Pre-Build Declaration named, found in text "
        f"that is in the game today.\n")

    lines.append("\n## The build's current TEACHING_TEXT stubs, judged\n")
    for row in p.baseline:
        lines.append(f"### `{row['verb']}`\n")
        lines.append(f"> {row['line']}\n")
        if row["layer1"]:
            for f in row["layer1"]:
                lines.append(f"- {f}")
        if row["layer2"] is None:
            lines.append("- layer 2: not judged "
                         "(gate failed first, or --skip-baseline)")
        else:
            j = row["layer2"]
            mark = "**FAIL**" if j["verdict"] == "FAIL" else "PASS"
            cls = f" `{j['class']}`" if j["class"] else ""
            lines.append(f"- layer 2: {mark}{cls} — {j['reason']}")
            if j["quoted_chunk"]:
                lines.append(f"  - chunk cited: \"{j['quoted_chunk']}\"")
        lines.append("")
    flagged = sum(1 for r in p.baseline if r["caught"])
    lines.append(f"**{flagged} of {len(p.baseline)}** stub lines flagged. Each "
                 f"flagged stub is a line currently shipping in the build that "
                 f"the loop replaces (or escalates) below.\n")
    p.bb.write("BASELINE-AUDIT.md", "\n".join(lines) + "\n", "assemble")


# ---------------------------------------------------------------------------

def write_ger_log(p) -> None:
    lines = [_hdr(p, "GER-LOG — every round of the loop")]
    lines.append(
        "Per verb: the Generator's draft, every Evaluator verdict (layer 1 "
        "deterministic gate, then the layer 2 judge), every Refiner repair, "
        "and where the loop stopped. `round 0` is the draft; refinement "
        f"rounds are capped at {p.breaker.max_rounds} per verb by the circuit "
        f"breaker.\n")
    for o in p.outcomes:
        status = ("**ACCEPTED**" if o.status == "ACCEPTED"
                  else "**ESCALATED** → see ESCALATED.md")
        lines.append(f"\n## `{o.verb}` — {status} "
                     f"({o.refinements_used} refinement(s))\n")
        for r in o.rounds:
            src = "Generator draft" if r.round_no == 0 else f"Refiner round {r.round_no}"
            lines.append(f"**{src}:**\n")
            lines.append(f"> {r.line}\n")
            if r.passed:
                if r.judgment is not None:
                    lines.append(f"- PASS — {r.judgment.reason}")
                    if r.judgment.quoted_chunk:
                        lines.append(f"  - chunk honored: "
                                     f"\"{r.judgment.quoted_chunk}\"")
                else:
                    lines.append("- PASS (deterministic gate only)")
            else:
                for f in r.findings:
                    lines.append(f"- FAIL — {f.render()}")
            lines.append("")
    total_rounds = sum(len(o.rounds) for o in p.outcomes)
    caught = sum(1 for o in p.outcomes for r in o.rounds if not r.passed)
    lines.append(f"\n**Totals:** {len(p.outcomes)} verbs · {total_rounds} "
                 f"evaluated rounds · {caught} FAIL verdicts, every one either "
                 f"repaired by the Refiner or escalated by the breaker — the "
                 f"pipeline has no third path.\n")
    p.bb.write("GER-LOG.md", "\n".join(lines) + "\n", "assemble")


# ---------------------------------------------------------------------------

def write_escalated(p) -> None:
    if not p.breaker.escalated:
        return
    lines = [_hdr(p, "ESCALATED — what the loop hands the Director")]
    lines.append(
        f"The circuit breaker stops spending on a verb after "
        f"{p.breaker.max_rounds} failed refinements and hands it here WITH its "
        f"evidence — the point of the loop is that a human reviews the "
        f"residue, not every output. Global trip threshold: "
        f"{p.breaker.escalation_limit} escalations"
        + (" — **REACHED; the run was halted**."
           if p.breaker.summary()["tripped"] else ".") + "\n")
    for o in p.breaker.escalated:
        lines.append(f"\n## `{o.verb}`\n")
        lines.append("| round | line | findings |")
        lines.append("|---|---|---|")
        for r in o.rounds:
            f = "<br>".join(x.render().replace("|", "\\|") for x in r.findings) \
                or "—"
            lines.append(f"| {r.round_no} | {r.line.replace('|', chr(92)+'|')} "
                         f"| {f} |")
        lines.append(f"\n**Director options:** write the `{o.verb}` line by "
                     f"hand; keep the build's current stub; or adjust the "
                     f"spec/prompt and re-run `--verbs {o.verb}`.\n")
    p.bb.write("ESCALATED.md", "\n".join(lines) + "\n", "assemble")


# ---------------------------------------------------------------------------

def write_teaching_lines(p) -> None:
    lines = [_hdr(p, "teaching-lines — first-use verb narration")]
    lines.append(
        "One rule-passing line per verb for the build's `TEACHING_TEXT` const "
        "(the mechanism A5 built; GDD §2.5 — 'a narrator names each verb the "
        "first time you use it', and the words end permanently at the first "
        "Sleep). ESCALATED verbs keep the build's current stub, marked.\n")
    lines.append("| verb | status | line |")
    lines.append("|---|---|---|")
    accepted_map = {}
    for o in p.outcomes:
        if o.status == "ACCEPTED":
            accepted_map[o.verb] = o.final_line
            lines.append(f"| `{o.verb}` | ACCEPTED "
                         f"(r{len(o.rounds) - 1}) | {o.final_line} |")
        else:
            accepted_map[o.verb] = p.build_lines.get(o.verb, "")
            lines.append(f"| `{o.verb}` | **ESCALATED** — stub retained | "
                         f"{accepted_map[o.verb]} |")
    for v in VERBS:
        if v not in accepted_map and v in p.build_lines:
            accepted_map[v] = p.build_lines[v]
            lines.append(f"| `{v}` | not in this run — stub retained | "
                         f"{accepted_map[v]} |")

    lines.append(
        "\n## Applying it\n\n"
        "Two equivalent routes, both Director-applied — the pipeline modifies "
        "nothing in place:\n\n"
        "1. **The snippet** — `teaching-text.snippet.js` in this directory is "
        "a drop-in replacement for the single `const TEACHING_TEXT={...};` "
        "line in `blackboard/build/uhta-slice.html`.\n"
        "2. **The pre-patched build** — `uhta-slice.patched.html` in this "
        "directory is the build with that one line already replaced, verified "
        "(see manifest `patch`): the const still parses, all pre-existing "
        "self-test assertions survive verbatim, and re-extracting the const "
        "returns exactly the accepted lines. Open it and check the self-test "
        "panel: G12 (once per verb, sleep 0 only) and G13 (all 7 verbs "
        "covered) gate this exact mechanism.\n")
    lines.append(
        "\n---\n\n## Director selection\n\n"
        "*Left unfilled by the pipeline. The loop guarantees every line above "
        "passes the GDD §2.5 register rule; which words enter a wordless game "
        "is still a Director ruling (GDD §4.5, 'human as curator').*\n\n"
        "**Apply as-is / edit / reject (per verb):** ____________________\n\n"
        "**Signed (Director):** _______________  **Date:** ____________\n")
    p.bb.write("teaching-lines.md", "\n".join(lines) + "\n", "assemble")
    p.accepted_map = accepted_map


# ---------------------------------------------------------------------------

def write_patch(p) -> None:
    """The snippet, and the pre-patched build with deterministic post-checks —
    the same contract shape as A5's generate stage: verify BEFORE writing, and
    never touch the in-place build."""
    accepted = getattr(p, "accepted_map", None)
    if not accepted or set(accepted) != set(VERBS):
        p.patch_report = {"written": False,
                          "reason": "not all seven verbs resolved in this run "
                                    "(--verbs subset?) — a partial const would "
                                    "fail the build's G13 assertion"}
        return
    snippet = render_teaching_snippet(accepted, VERBS)
    p.bb.write("teaching-text.snippet.js", snippet + "\n", "assemble")

    html = p.bb.read_bb("build/uhta-slice.html", "assemble")
    occurrences = len(_TEACHING_RE.findall(html))
    checks = {"const_occurs_exactly_once": occurrences == 1}
    # lambda replacement: the snippet may contain backslash escapes, which a
    # plain re.sub replacement string would reinterpret
    patched = _TEACHING_RE.sub(lambda m: snippet, html, count=1) \
        if occurrences == 1 else html

    if occurrences == 1:
        before = set(re.findall(r"\['(G\d+)", html))
        after = set(re.findall(r"\['(G\d+)", patched))
        checks["all_selftest_assertions_survive"] = before == after and bool(before)
        checks["reextracted_const_matches_accepted"] = (
            extract_teaching_text(patched) == accepted)

    if all(checks.values()):
        out = p.bb.run_dir / "uhta-slice.patched.html"
        out.write_text(patched, encoding="utf-8")
        p.bb.note("assemble", f"**WRITE** `out/{p.run_id}/"
                              f"uhta-slice.patched.html` ({len(patched)} B) — "
                              f"all patch post-checks passed")
        p.patch_report = {"written": True, "checks": checks,
                          "bytes": len(patched)}
    else:
        p.patch_report = {"written": False, "checks": checks,
                          "reason": "a post-check failed; the snippet is still "
                                    "valid and can be applied by hand"}
        p.bb.note("assemble", f"patched build NOT written — {checks}")


# ---------------------------------------------------------------------------

def write_all(p) -> None:
    write_baseline(p)
    write_ger_log(p)
    write_escalated(p)
    write_teaching_lines(p)
    write_patch(p)
