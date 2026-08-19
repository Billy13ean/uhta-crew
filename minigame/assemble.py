"""Evidence documents for both phases. Deterministic; no LLM; nothing typed
by hand."""
from __future__ import annotations

import json
import time


def _mock_banner(p) -> str:
    if p.mode != "mock":
        return ""
    return ("> **MOCK-LLM FIXTURE RUN — NOT REAL DESIGN WORK.** Designer, "
            "Judge, Refiner and Programmer responses were canned fixtures "
            "from `tests/fixtures/minigame/`, replayed to prove the "
            "orchestration — the design gate, the loop, the breaker, the "
            "human gate and the patch contract — executes end to end. The "
            "design-gate findings and patch post-checks ARE real (they are "
            "code); the designs and verdicts are fixtures.\n\n")


def _hdr(p, title: str) -> str:
    return (f"# {title} — {p.run_id}\n\n"
            f"> Pipeline `minigame` (Assignment 6 #2) · backend `{p.llm.name}` "
            f"· model `{p.llm.model}` · generated "
            f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n" + _mock_banner(p))


def _render_design(d: dict) -> list[str]:
    out = []
    out.append(f"**{d.get('name', '?')}** — `{d.get('id')}` "
               f"({d.get('encounter')}/{d.get('pole')})\n")
    for k, label in (("premise", "Premise"), ("loop", "Loop"),
                     ("signals", "Diegetic signals"),
                     ("outcome_win", "On success"),
                     ("outcome_fail", "On failure"),
                     ("why_fun", "Why fun"),
                     ("pattern_source", "Pattern"),
                     ("gdd_quote", "GDD grounding")):
        v = str(d.get(k, "")).strip()
        if v:
            out.append(f"- **{label}:** {v}")
    out.append(f"- **Controls:** {', '.join(d.get('controls', []))}")
    out.append(f"- **Effects:** {', '.join(d.get('effects', []))}")
    return out


def write_propose(p) -> None:
    # ---- the candidates document + the gate ----
    lines = [_hdr(p, "MINIGAME-CANDIDATES — encounter mini-games, "
                     "awaiting a ruling")]
    lines.append(
        "One design per encounter slot survived the GER loop (Generator -> "
        "two-layer Evaluator -> Refiner, circuit breaker on the residue). "
        "**Nothing has been built.** GDD §3's stop rule gates encounter "
        "BUILDS on the stranger test; this run spent tokens on design, and "
        "the build stage below cannot run without your typed selection — "
        "the gate is structural.\n")
    for o in p.outcomes:
        d = p.accepted.get(o.verb)
        lines.append(f"\n## `{o.verb}` — "
                     + ("ACCEPTED" if o.status == "ACCEPTED"
                        else "**ESCALATED** (see MG-ESCALATED.md; cannot be "
                             "selected)"))
        if d:
            r = o.rounds[-1]
            lines.extend(_render_design(d))
            if r.judgment is not None:
                lines.append(f"- **Judge:** PASS — {r.judgment.reason}")
                if r.judgment.quoted_chunk:
                    lines.append(f"  - chunk honored: "
                                 f"\"{r.judgment.quoted_chunk}\"")
    lines.append(
        "\n---\n\n## Director selection — the human gate\n\n"
        "*The pipeline stops here by construction. To build ONE selected "
        "design (a minimal playable slice under the A5 patch contract):*\n\n"
        "```\npython3 run_minigame.py --build --select <id> --from-run "
        f"{p.run_id}\n```\n\n"
        f"Selectable ids: {', '.join(sorted(p.accepted)) or '(none)'}\n\n"
        "**Selected:** ____________  **Rejected because:** ____________\n\n"
        "**Signed (Director):** _______________  **Date:** ____________\n")
    p.bb.write("MINIGAME-CANDIDATES.md", "\n".join(lines) + "\n", "assemble")

    # ---- the Director's dashboard: the gate as a checklist ----
    from .dashboard import DASHBOARD_NAME, render_dashboard
    cards = []
    for o in p.outcomes:
        d = p.accepted.get(o.verb)
        if d:
            c = dict(d)
            c["status"] = "ACCEPTED"
            last = o.rounds[-1]
            if last.judgment is not None:
                c["judge_reason"] = last.judgment.reason
                c["judge_chunk"] = last.judgment.quoted_chunk
            cards.append(c)
        else:
            cards.append({"id": o.verb, "name": o.verb, "status": "ESCALATED",
                          "premise": "Escalated by the circuit breaker — see "
                                     "MG-ESCALATED.md for the evidence."})
    p.bb.write(DASHBOARD_NAME,
               render_dashboard(p.run_id, cards, p.canon.summary()),
               "assemble")

    # ---- machine-readable gate artifact the build stage reads ----
    p.bb.write("CANDIDATES.json", json.dumps({
        "run_id": p.run_id, "mode": p.mode,
        "accepted": [p.accepted[k] for k in sorted(p.accepted)],
        "escalated": [o.verb for o in p.breaker.escalated],
    }, ensure_ascii=False, indent=2) + "\n", "assemble")

    # ---- the loop log ----
    lines = [_hdr(p, "MG-GER-LOG — every round of the loop")]
    for o in p.outcomes:
        status = ("**ACCEPTED**" if o.status == "ACCEPTED"
                  else "**ESCALATED**")
        lines.append(f"\n## `{o.verb}` — {status} "
                     f"({o.refinements_used} refinement(s))\n")
        for r in o.rounds:
            src = ("Designer draft" if r.round_no == 0
                   else f"Refiner round {r.round_no}")
            lines.append(f"**{src}:**\n")
            try:
                name = json.loads(r.line).get("name", "?")
            except Exception:  # noqa: BLE001
                name = "?"
            lines.append(f"> design: *{name}*\n")
            if r.passed:
                if r.judgment is not None:
                    lines.append(f"- PASS — {r.judgment.reason}")
                    if r.judgment.quoted_chunk:
                        lines.append(f"  - chunk honored: "
                                     f"\"{r.judgment.quoted_chunk}\"")
                else:
                    lines.append("- PASS (design gate only)")
            else:
                for f in r.findings:
                    lines.append(f"- FAIL — {f.render()}")
            lines.append("")
    p.bb.write("MG-GER-LOG.md", "\n".join(lines) + "\n", "assemble")

    # ---- escalations ----
    if p.breaker.escalated:
        lines = [_hdr(p, "MG-ESCALATED — what the loop hands the Director")]
        lines.append(
            f"After {p.breaker.max_rounds} failed refinements a slot is "
            f"escalated with its full history; "
            f"{p.breaker.escalation_limit} escalations trip the run.\n")
        for o in p.breaker.escalated:
            lines.append(f"\n## `{o.verb}`\n")
            lines.append("| round | design | findings |")
            lines.append("|---|---|---|")
            for r in o.rounds:
                try:
                    name = json.loads(r.line).get("name", "?")
                except Exception:  # noqa: BLE001
                    name = "?"
                f = "<br>".join(x.render().replace("|", "\\|")
                                for x in r.findings) or "—"
                lines.append(f"| {r.round_no} | {name} | {f} |")
            lines.append(f"\n**Director options:** design `{o.verb}` by "
                         f"hand; drop the slot; or adjust the spec and "
                         f"re-run `--slots {o.verb}`.\n")
        p.bb.write("MG-ESCALATED.md", "\n".join(lines) + "\n", "assemble")


def write_build(p, design: dict, patch: dict) -> None:
    lines = [_hdr(p, "MINIGAME-BUILD — the selected design, built")]
    lines.append("## What was built\n")
    lines.extend(_render_design(design))

    if p.instructions.get("first_use_line"):
        lines.append(
            "\n## The Instructor's line (Writer's seat, GDD §5)\n\n"
            f"> {p.instructions['first_use_line']}\n\n"
            "Displays once, when the encounter first begins on sleep 0 — "
            "inside the game's narrated window; register-gated by the same "
            "checks as the verb narration.\n")
    if p.presentation:
        lines.append("\n## The Presenter's spec (Aesthetic Director's seat)\n")
        for k in ("attention_cue", "entry_transition", "exit_transition",
                  "feedback_win", "feedback_fail"):
            v = str(p.presentation.get(k, "")).strip()
            if v:
                lines.append(f"- **{k}:** {v}")
        vh = p.presentation.get("visual_hierarchy") or []
        if vh:
            lines.append("- **visual_hierarchy:** "
                         + " → ".join(str(x) for x in vh))
        sm = p.presentation.get("signal_map") or {}
        for state, visual in sm.items():
            lines.append(f"  - *{state}* → {visual}")

    lines.append(
        "\n## Finding it in play\n\n"
        "- **Director test hook:** open the build with `#mg` in the URL "
        "(e.g. `uhta-slice.html#mg`) — the encounter force-arms from the "
        "start of play, regardless of spawn luck.\n"
        "- **Normal play:** the attention cue above, then the trigger "
        "condition in the design; the entry transition pauses the world.\n")
    lines.append("\n## The patch\n")
    lines.append("| | |\n|---|---|")
    for k, v in p.build_report.items():
        lines.append(f"| {k} | `{v}` |")
    def _n(key: str) -> str:
        v = str(patch.get(key, "") or "")
        return f"{len(v.splitlines())} line(s)" if v.strip() else "(omitted)"

    lines.append(
        "\n### Inserted at the five anchors (contract v3)\n\n"
        f"1. **logic** (top level): {_n('logic_block')}\n"
        f"2. **frame** (inside drawWorld — the per-frame seat where the "
        f"encounter lives): {_n('frame_line')}\n"
        f"3. **input** (onClick guard — the encounter owns the pointer): "
        f"{_n('input_line')}\n"
        f"4. **self-test**: {_n('selftest_block')} — the M-assertions gate "
        f"the pure logic\n"
        f"5. **hook** (verb-trigger arming assist, optional): "
        f"{_n('hook_line')}\n")
    if str(patch.get("notes", "")).strip():
        lines.append(f"\n**Programmer notes:** {patch['notes']}\n")
    lines.append(
        "\n## Applying it (Director)\n\n"
        "```\ncopy blackboard\\build\\uhta-slice.html "
        "blackboard\\build\\uhta-slice.pre-mg.html\n"
        f"copy out\\{p.run_id}\\uhta-slice.minigame.patched.html "
        "blackboard\\build\\uhta-slice.html\n```\n\n"
        "Open the build: the self-test panel must show every G-assertion "
        "AND the new M-assertion(s) green. Then play to the encounter and "
        "judge the thing no container can: whether it feels like the GDD's "
        "sentence. **GDD §3's stop rule still applies to committing this to "
        "the canonical slice** — building it was gated on your selection; "
        "shipping it is gated on the stranger test, and that ruling is "
        "yours.\n"
        "\n## Director verification\n\n"
        "- [ ] panel all green, including M-assertions\n"
        "- [ ] the encounter triggers where the design says\n"
        "- [ ] wordless in play — no text appeared\n"
        "- [ ] the two poles would not play the same game\n")
    p.bb.write("MINIGAME-BUILD.md", "\n".join(lines) + "\n", "assemble")
