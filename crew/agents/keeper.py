"""Keeper — Modes B1 and B2. GDD §3.1, contract §3.2.

B1 opens the run: it assembles the context packet that is the Mechanic Designer's
only view of canon. B2 closes it: it diffs the selected variant and its evidence
against CANON and writes `contradictions-runN.md` in the six-heading schema.

The Keeper is the reason the crew is a pipeline and not a pile. Nothing
downstream reads `CANON.md` directly — the Designer sees canon only through the
packet, so a bad cut is a design defect with a name and a file. And nothing
reaches the Director without a diff stapled to it.

Both modes run at temperature 0. A Keeper that paraphrases canon has failed.
"""
from __future__ import annotations

from pathlib import Path

from ..llm import LLMCall
from . import AgentError, fenced_blocks, markdown_block

PROMPT_VERSION = "keeper v2 (crew port)"

RULING_BLOCK = """

---

## Ruling

*Left blank by the crew. This block is the Director's, and only the Director's
(CANON-process.md ruling 1: "flags never gate, but they do block silence" — a
`CONTRADICTS-LOCKED` flag cannot be closed by omission, and "no ruling" is not a
state a commit can be in).*

**Class answered:** _(the flag class this ruling addresses, or `n/a` if CLEAN)_

**Verdict:** _(exactly one of)_ `UPHOLD` | `AMEND` | `DEFER`

- `UPHOLD` — canon stands; the output is revised or discarded.
- `AMEND`  — canon changes; the Keeper transcribes the new line into `CANON.md`
             with this run number as provenance, tagged AMEND in
             `Delta from vN-1`.
- `DEFER`  — the conflict becomes a named GDD §6 open question.

**CANON line added (AMEND only):**

**Signed (Director):** _______________  **Date:** ____________
"""


# ---- the packet contract (added after crew-021217) ------------------------
# That live run's Keeper reply carried no ```markdown fence, so extraction
# fell through to "first unlabelled fence" — which was a 507-byte grief_front
# JSON excerpt, not the packet. The gate (len > 400) passed it, and the
# Mechanic Designer spent six refusal-retries on a prompt built from a
# fragment. The packet is located by its own contract now, not by fence luck.

PACKET_H1 = "# Context packet"
PACKET_HEADINGS = [
    "## CANON digest",
    "## Canon lines this run touches",
    "## Relevant specification excerpts",
    "## The baseline ruleset and what may move",
    "## Open questions in scope for this run",
    "## Excluded from this packet",
    "## Assumptions",
]


def extract_packet(out: str) -> str | None:
    """The packet, located by its H1. Prefers a fenced block containing it
    (any label), falls back to the raw text from the H1 onward."""
    for b in fenced_blocks(out):
        if PACKET_H1 in b:
            return b.strip()
    i = out.find(PACKET_H1)
    if i != -1:
        return out[i:].strip()
    return None


def packet_findings(packet: str | None) -> list[str]:
    """Every way the packet can fail its own output contract, named."""
    if packet is None:
        return [f"no '{PACKET_H1}' heading anywhere in the response"]
    f = []
    if len(packet) < 400:
        f.append(f"implausibly short ({len(packet)} chars)")
    missing = [h for h in PACKET_HEADINGS if h not in packet]
    if missing:
        f.append("missing required section(s): " + ", ".join(missing))
    return f


def _sections(prompt_text: str, mode: str) -> str:
    """Return the prompt with the non-active mode's section removed.

    The two modes share a SYSTEM block and diverge below; sending both halves
    doubles the prompt and invites the model to answer the wrong one.
    """
    b1_marker = "## MODE B1 — Assemble a context packet"
    b2_marker = "## MODE B2 — Contradiction diff"
    if b1_marker not in prompt_text or b2_marker not in prompt_text:
        return prompt_text
    head, rest = prompt_text.split(b1_marker, 1)
    b1_body, b2_body = rest.split(b2_marker, 1)
    if mode == "B1":
        return head + b1_marker + b1_body
    return head + b2_marker + b2_body


def run_keeper_b1(bb, llm, ctx) -> Path:
    """Stage 1. Reads the seeded blackboard; writes the Designer's packet."""
    agent = "keeper-b1"
    canon = bb.read_bb("CANON.md", agent)
    canon_proc = bb.read_bb("CANON-process.md", agent)
    gdd = bb.read_bb(f"gdd/{ctx.gdd_name}", agent)
    baseline = bb.read_bb(f"rules/{ctx.baseline_name}", agent)

    prompt = _sections(Path(ctx.prompts_dir / "keeper.md").read_text(encoding="utf-8"), "B1")
    system, _, template = prompt.partition("## SYSTEM")
    user = (
        template
        .replace("{{CANON_DIGEST}}", canon)
        .replace("{{CANON_PROCESS}}", canon_proc)
        .replace("{{RUN_PURPOSE}}", ctx.goal)
        .replace("{{QUESTION_SET}}", ctx.question_set)
        .replace("{{BASELINE_NAME}}", ctx.baseline_name)
        .replace("{{BASELINE_RULES_JSON}}", baseline)
        .replace("{{GDD_SECTIONS}}", gdd)
    )
    sys_prompt = "You are the Keeper for uhta. " + system.strip()[:400]
    out = llm.complete(LLMCall(
        agent=agent, system=sys_prompt,
        user=user, temperature=0.0, max_tokens=12000,
    ))
    packet = extract_packet(out)
    findings = packet_findings(packet)
    if findings:
        # One repair round, then halt — same budget as every other seat.
        bb.note(agent, "packet failed its structural contract ("
                       + "; ".join(findings) + ") — **one repair round**")
        repair = (
            "\n\n### REPAIR — your previous response did not deliver the "
            "packet.\nFindings:\n"
            + "".join(f"- {f}\n" for f in findings)
            + "\nEmit ONLY the context packet, inside a single ```markdown "
              "fence, starting at the `# Context packet` heading, with every "
              "required `##` section present. No prose before or after the "
              "fence.")
        out = llm.complete(LLMCall(
            agent=agent, system=sys_prompt,
            user=user + repair, temperature=0.0, max_tokens=12000,
        ))
        packet = extract_packet(out)
        findings = packet_findings(packet)
        if findings:
            raise AgentError(
                agent, "packet failed its structural contract twice: "
                       + "; ".join(findings)
                       + " — a Designer briefed by this packet designs from "
                         "a fragment (crew-021217).")
    if getattr(llm, "name", "") == "mock":
        packet = llm.FIXTURE_BANNER + "\n" + packet
    return bb.write(ctx.packet_name, packet + "\n", agent)


def run_keeper_b2(bb, llm, ctx) -> Path:
    """Stage 6. Requires the selected variant (Designer) and metrics (Playtester)."""
    agent = "keeper-b2"
    bb.require(ctx.selected_variant_name, agent, "mechanic-designer")
    bb.require(ctx.metrics_name, agent, "playtester")
    bb.require(ctx.attacks_md_name, agent, "red-teamer")

    canon = bb.read_bb("CANON.md", agent)
    canon_proc = bb.read_bb("CANON-process.md", agent)
    variant = bb.read(ctx.selected_variant_name, agent, "mechanic-designer")
    metrics = bb.read(ctx.metrics_name, agent, "playtester")
    attacks = bb.read(ctx.attacks_md_name, agent, "red-teamer")

    prompt = _sections(Path(ctx.prompts_dir / "keeper.md").read_text(encoding="utf-8"), "B2")
    system, _, template = prompt.partition("## SYSTEM")
    user = (
        template
        .replace("{{CANON_DIGEST}}", canon)
        .replace("{{CANON_PROCESS}}", canon_proc)
        .replace("{{RUN_PURPOSE}}", ctx.goal)
        .replace("{{SELECTED_VARIANT_JSON}}", variant)
        .replace("{{METRICS}}", metrics)
        .replace("{{ATTACKS}}", attacks)
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system="You are the Keeper for uhta. " + system.strip()[:400],
        user=user, temperature=0.0, max_tokens=8000,
    ))
    report = markdown_block(out)
    if "## Coherence verdict" not in report:
        raise AgentError(
            agent,
            "report is missing the '## Coherence verdict' heading required by the "
            "GDD §3.2 six-heading schema. Got headings: "
            + ", ".join(l.strip() for l in report.splitlines() if l.startswith("##"))[:400],
        )
    if "## Ruling" in report:
        report = report.split("## Ruling")[0].rstrip()
    if getattr(llm, "name", "") == "mock":
        report = llm.FIXTURE_BANNER + "\n" + report
    return bb.write(ctx.contradictions_name, report + RULING_BLOCK, agent)
