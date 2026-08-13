"""Evidence documents, generated from the run — never typed.

Same rule the A3 Playtester's board follows and the A4 evidence documents follow:
static framing prose is written by a human, every number and every verdict is
injected from the run, and blocks that came from execution are marked so a reader
can tell which sentences are claims and which are results.
"""
from __future__ import annotations

from .gap import PRESENT, PARTIAL, ABSENT, disagreements
from .priority import selectable, margin

INJECTED = "*[injected from this run]*"


def _mode_banner(p) -> str:
    if p.mode == "mock":
        return ("> **THIS RUN USED `--mock-llm`.** Every model-authored field below "
                "came from a canned fixture in `tests/fixtures/builder/`, not from a "
                "model. It demonstrates that the orchestration executes end to end "
                "without an API key. It is not evidence about the codebase.\n\n")
    return ""


# --------------------------------------------------------------------------

def features_md(p) -> str:
    rows = "\n".join(
        f"| `{f.id}` | {f.name} | §{f.gdd_section} | {f.tier} | {f.kind} | "
        f"{f.signature.weight()} | {f.source} |"
        for f in sorted(p.features, key=lambda x: (x.tier, x.id))
    )
    excl = "\n".join(f"| `{e.key}` | {e.heading} | {e.reason} |"
                     for e in p.corpus_exclusions)
    return (
        f"# FEATURES — the inventory read out of the GDD\n\n{_mode_banner(p)}"
        f"Source: `blackboard/gdd/uhta-gdd-v0.9.9-condensed.md`. The verb table, the "
        f"build-order tiers and the acceptance criteria were parsed deterministically; "
        f"the `observable_signature` on each feature — what the code would look like if "
        f"the feature existed — is the Analyst's, and is the only part of this stage a "
        f"model produced.\n\n"
        f"**{len(p.features)} features.** {INJECTED}\n\n"
        f"| id | name | § | tier | kind | signature size | from |\n|---|---|---|---|---|---|---|\n{rows}\n\n"
        f"## Acceptance criteria (§4)\n\n"
        + "\n".join(f"- **{c.number}.** {c.text} — *{c.status}*" for c in p.criteria)
        + f"\n\n## Corpus scope — {len(p.corpus_exclusions)} chunk(s) excluded, each with a reason\n\n"
        f"`BUILDER_POLICY` is not `CORPUS_POLICY`. The content pipeline wanted game "
        f"material only, because it was writing prose a player reads. This pipeline also "
        f"needs §3 and §4 — the build order and the acceptance test — because those are "
        f"the criteria the build decision is made against. Same corpus, two policies, "
        f"because the consumer differs.\n\n"
        f"| chunk | heading | reason |\n|---|---|---|\n{excl}\n"
    )


def gap_report_md(p) -> str:
    counts = {v: sum(1 for x in p.verdicts if x.verdict == v)
              for v in (PRESENT, PARTIAL, ABSENT)}
    dis = disagreements(p.verdicts)

    def block(v):
        head = (f"### `{v.feature.id}` — **{v.verdict}** "
                f"(layer {v.layer}, score {v.score:.2f}, signature {v.found_ratio()})\n\n"
                f"{v.feature.name} — §{v.feature.gdd_section}. {v.reason}\n\n")
        if v.quoted_code:
            head += f"Evidence, quoted from the source:\n\n```js\n{v.quoted_code}\n```\n\n"
        if v.searched_for:
            head += f"Searched for and did not find: `{'`, `'.join(v.searched_for[:8])}`\n\n"
        if v.disagrees_with_gdd:
            head += (f"> **Disagrees with the GDD.** §3 reports this feature as "
                     f"*{v.feature.gdd_claimed_status}*, which implies "
                     f"{v.gdd_expected}. The scan found {v.verdict}.\n\n")
        return head

    gaps = [v for v in p.verdicts if v.is_gap]
    scan = p.index.stats()
    excl_rows = "\n".join(
        f"| `{e.path}` | {e.line} | {e.chars:,} | {e.rule} | {e.reason} |"
        for e in p.index.exclusions[:12])

    return (
        f"# GAP REPORT — the GDD against the codebase\n\n{_mode_banner(p)}"
        f"**{counts[PRESENT]} present · {counts[PARTIAL]} partial · {counts[ABSENT]} absent** "
        f"across {len(p.verdicts)} features. {len(p.adjudicated)} went to layer-2 "
        f"adjudication. {INJECTED}\n\n"
        f"## The cross-check — {len(dis)} disagreement(s) with the GDD's own status column\n\n"
        f"The detector never sees §3's Built/Unbuilt column. `Feature.for_detection()` "
        f"withholds it, and `--selftest` asserts the withholding. The two readings are "
        f"therefore independent, and this section is where they differ — which is the "
        f"only evidence available that this pipeline reads a codebase rather than a "
        f"status column. An agent that had merely read that column could not disagree "
        f"with it.\n\n"
        + ("".join(block(v) for v in dis) if dis
           else "*No disagreements this run: the codebase matches what §3 claims about it.*\n\n")
        + f"## Gaps found\n\n" + ("".join(block(v) for v in gaps) if gaps else "*none*\n\n")
        + f"## Scan scope\n\n"
        f"Indexed **{scan['symbols']} symbols**, {scan['literals']} string literals and "
        f"{scan['key_paths']} ruleset key paths. `SCAN_POLICY` excluded "
        f"**{scan['excluded_regions']} region(s), {scan['excluded_chars']:,} characters** "
        f"— overwhelmingly the vendored Phaser bundle. That exclusion is the code-side "
        f"twin of the content pipeline's §4.5 exclusion: §4.5 was cut because indexing "
        f"it let the Writer retrieve the answer instead of writing one, and Phaser is cut "
        f"because indexing it makes every feature look already built.\n\n"
        f"| file | line | chars | rule | reason |\n|---|---|---|---|---|\n{excl_rows}\n"
    )


def priority_md(p) -> str:
    sel = selectable(p.scores)
    rows = []
    for i, s in enumerate(p.scores, 1):
        t = {x.name: x.value for x in s.terms}
        flag = "" if s.selectable else " *(present — not a gap)*"
        rows.append(
            f"| {i} | `{s.feature.id}`{flag} | {s.feature.tier} | {s.verdict.verdict} | "
            f"{t['gate']:+.1f} | {t['tier']:+.1f} | {t['dep']:+.1f} | {t['cost']:+.1f} | "
            f"{t['stop']:+.1f} | **{s.total:+.2f}** |")
    win = p.chosen
    terms = "\n".join(f"- **{x.name}** `{x.value:+.2f}` — {x.detail}" for x in win.terms)

    return (
        f"# PRIORITY — what to build first, and the arithmetic that decided it\n\n"
        f"{_mode_banner(p)}"
        f"No model produced this ranking. Every term is computed in "
        f"`builder/priority.py` and printed below, so it can be recomputed by hand.\n\n"
        f"```\nscore =  5.0 · (§4 criteria this feature blocks)\n"
        f"       +       tier weight   (CORE 4 · PASS 1 3 · PASS 2 2 · NICE 1 · PROPOSED 0 · CUT −2)\n"
        f"       +  1.5 if no unmet dependency, −3.0 if gated on the stranger test\n"
        f"       −  0.5 · estimated size\n"
        f"       −  4.0 if below the CORE/PASS-1 line AND not unblocking a §4 criterion\n```\n\n"
        f"| # | feature | tier | scan | gate | tier | dep | cost | stop | total |\n"
        f"|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        f"## Selected: `{win.feature.id}` — {win.feature.name} {INJECTED}\n\n"
        f"{terms}\n\n"
        f"**Total {win.total:+.2f}**, winning by **{margin(p.scores)}** over the "
        f"next buildable item"
        + (f" (`{sel[1].feature.id}`, {sel[1].total:+.2f})" if len(sel) > 1 else "")
        + ".\n\n"
        f"### Why this is not the obvious answer\n\n"
        f"`{win.feature.id}` sits in the **{win.feature.tier}** tier — "
        f"{'the lowest positive tier weight in the table' if win.feature.tier == 'NICE' else 'not the top tier'}. "
        f"On build-order value alone it would lose to anything above it. It wins on the "
        f"`gate` term: it blocks §4 "
        f"criteri{'on' if len(win.feature.blocks_criteria) == 1 else 'a'} "
        f"{', '.join(str(c) for c in win.feature.blocks_criteria)}, and §4 is the "
        f"acceptance test the entire project is paused on.\n\n"
        f"The `stop` term is what makes that legal rather than merely appealing. GDD §3 "
        f"forbids building anything below the CORE/PASS-1 line until a stranger has "
        f"played the loop — *except work that unblocks a §4 criterion, which is the gate "
        f"rather than a violation.* The agent evaluates that carve-out and waives the "
        f"−4.0 penalty. Every other sub-line feature keeps it.\n\n"
        f"So the ranking reproduces the Director's own written stop rule, from the rule's "
        f"text rather than from its conclusion.\n"
    )


def generated_md(p) -> str:
    f, patch = p.chosen.feature, p.patch
    edits = ("\n".join(f"- replaced `{e.get('anchor','')[:90]}` — {e.get('why','')}"
                       for e in patch.edits) or "- none")
    repairs = ("\n".join(f"- {r}" for r in p.repair_log)
               or "- none — the first patch passed every check")
    return (
        f"# GENERATED — {f.name}\n\n{_mode_banner(p)}"
        f"## What the agent built {INJECTED}\n\n{patch.summary}\n\n{patch.rationale}\n\n"
        f"| | |\n|---|---|\n"
        f"| feature | `{f.id}` — {f.name} (§{f.gdd_section}, {f.tier}) |\n"
        f"| gap verdict | {p.chosen.verdict.verdict} (layer {p.chosen.verdict.layer}) |\n"
        f"| priority score | {p.chosen.total:+.2f}, margin {margin(p.scores)} |\n"
        f"| inserted after | `{patch.anchor[:80]}` |\n"
        f"| lines added | {len(patch.insert.splitlines())} |\n"
        f"| new assertions | {', '.join(p.new_assertions) or '—'} |\n"
        f"| repair round-trips | {len(p.repair_log)} of 1 permitted |\n\n"
        f"## Existing behaviour this patch changes\n\n{edits}\n\n"
        f"## Deterministic checks, all passed before anything was written\n\n"
        f"1. the anchor appears exactly once in the target\n"
        f"2. every pre-existing self-test assertion survives verbatim\n"
        f"3. at least one new assertion was added — a feature that cannot be asserted "
        f"has not been finished\n"
        f"4. the patched script parses (`node --check`)\n\n"
        f"### Repair log\n\n{repairs}\n\n"
        f"## Applying it\n\n"
        f"The in-place build was **not** modified. This run wrote "
        f"`uhta-slice.patched.html` and `patch.diff` into its own directory; the "
        f"Director applies them. The rules crew stops at a blank `## Ruling` and the "
        f"content pipeline stops at an unfilled `## Director selection` — this pipeline "
        f"stops here, for the same reason.\n\n"
        f"```bash\n"
        f"cp out/{p.bb.run_id}/uhta-slice.patched.html blackboard/build/uhta-slice.html\n"
        f"# then open it and read the self-test panel, bottom left\n```\n\n"
        f"## Director verification\n\n"
        f"- [ ] the patched build loads and the self-test panel reads all PASS\n"
        f"- [ ] the feature does what §{f.gdd_section} describes\n"
        f"- [ ] the new assertions fail if the feature is removed\n"
    )


def write_all(p) -> None:
    p.bb.write("FEATURES.md", features_md(p), "assemble")
    p.bb.write("GAP-REPORT.md", gap_report_md(p), "assemble")
    p.bb.write("PRIORITY.md", priority_md(p), "assemble")
    p.bb.write("GENERATED.md", generated_md(p), "assemble")
