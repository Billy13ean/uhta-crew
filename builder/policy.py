"""Two scoping policies, each with a recorded reason per cut.

`content/retriever.py` established the pattern for prose: `CORPUS_POLICY` keeps
the GDD's game material and drops its account of the pipeline, and every dropped
chunk is listed with a reason rather than quietly absent. That policy found a
real defect — GDD §4.5 carries the Director's own hand-written narration example,
and indexing it let the Writer retrieve the answer instead of writing one.

This module is the same idea applied twice more, because this pipeline reads two
things the content pipeline never did: a different slice of the GDD, and source
code.

--------------------------------------------------------------------------
1. BUILDER_POLICY — why CORPUS_POLICY cannot be reused
--------------------------------------------------------------------------

`CORPUS_POLICY` scopes by top-level section number, and those numbers are
v0.9.7's. The current GDD is v0.9.9, which RENUMBERS:

    §        v0.9.7                    v0.9.9
    3        AI architecture           Build order — core, then nice
    4        Technical strategy        Definition of Playable
    5        —                         AI Architecture
    6        —                         Technical Strategy

Reusing it unchanged would exclude exactly the two sections this pipeline runs
on — §3 supplies the tier weights and the stop rule, §4 supplies the acceptance
criteria that drive the gate term — while including §5 and §6, which are
pipeline material.

The deeper reason is not numbering. The two pipelines want opposite things from
the same document. The content pipeline wanted game material ONLY, because it was
writing prose a player reads; a narration line grounded in the agent roster would
be about the pipeline. This pipeline wants game material PLUS the project's own
build-order and acceptance sections, because it is deciding what to build next
and those sections are the decision's criteria.

Same corpus, two policies, because the consumer differs.

--------------------------------------------------------------------------
2. SCAN_POLICY — the code-side analogue of the §4.5 exclusion
--------------------------------------------------------------------------

`blackboard/build/uhta-slice.html` vendors Phaser 3 inline: one line, 1,181,901
characters of minified library. Phaser defines thousands of identifiers,
including `Scene`, `World`, `Tween`, `Text`, `Zone` and `Wander`. A symbol scan
that indexes it finds evidence for nearly any feature the GDD names, and every
gap comes back PRESENT.

That is the same failure mode as §4.5, one level down. In both cases the corpus
contains something that silently defeats the pipeline's purpose, and in both
cases it is findable only by looking at the actual bytes rather than trusting the
file's description.

So vendored and minified regions are excluded by an explicit rule, with a reason
recorded per exclusion and the whole thing asserted by `--selftest`.
"""
from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------
# 1. corpus scope
# --------------------------------------------------------------------------

BUILDER_POLICY = {
    "name": "build-decision material v1",
    "gdd_version": "0.9.9",
    "rationale": (
        "This pipeline decides what to build next. That decision is made against "
        "the game's design (what the game is supposed to be) AND against the "
        "project's own build order and acceptance test (what counts as next, and "
        "what counts as done). The content pipeline excluded the latter because "
        "prose a player reads must not be grounded in project process; this "
        "pipeline requires it, because process is the decision criteria."
    ),
    "include_top_level": {
        "1": "Summary — the tone contract and the design stance. §1 is where the "
             "narrated opening's spec actually lives: 'a narrator names each verb "
             "the first time you use it; the words end permanently at your first "
             "Sleep.'",
        "2": "Game Mechanics — the verb table, the systems, the antagonist, the "
             "win/loss check. The feature inventory's main source.",
        "3": "Build order — the CORE/PASS-1/PASS-2/NICE/PROPOSED/CUT tiers and "
             "the stop rule. Supplies the tier weight and the stop-rule term.",
        "4": "Definition of Playable — the six acceptance criteria. Supplies the "
             "gate term, which is the term that decides the ranking.",
        "8": "Logic gaps and open questions — names what is unresolved, which is "
             "how a feature gets marked dependency-blocked rather than merely "
             "unbuilt.",
    },
    "exclude_top_level": {
        "5": "§5 is the AI-architecture / agent roster — how the game is built, "
             "not what is in it and not how the build order is decided. A feature "
             "extracted from the roster would be an agent, not a game feature.",
        "6": "§6 is technical strategy, verification layers and token budget. It "
             "describes the pipeline's own economics; nothing in it is a feature "
             "the slice could be missing.",
        "7": "§7 is revision provenance — a record of which Assignment-1 note "
             "landed where. Document history, not game material.",
    },
    "exclude_docs": {
        "CANON-process.md": "Process canon — Keeper escalation, report discipline, "
                            "artifact counts. Governs how the project runs.",
    },
    "exclude_front_matter": (
        "Version preamble. Describes what changed between GDD revisions, not what "
        "is true in the world or what remains to be built."
    ),
}

# --------------------------------------------------------------------------
# 2. code scope
# --------------------------------------------------------------------------

#: A source line longer than this is not authored source. The slice's own
#: hand-written lines top out around 750 characters (the `F` frame-index map);
#: the Phaser bundle is a single line of 1,181,901. Any threshold in that gap
#: separates them, and 2000 leaves an order of magnitude of headroom on the
#: authored side.
VENDOR_LINE_CHARS = 2000

#: Preambles that identify a minified vendor bundle regardless of line length.
VENDOR_SIGNATURES = (
    "!function(t,e){",
    "!function(e,t){",
    "/*! For license information",
    "(function(global,factory)",
    "typeof exports===\"object\"&&typeof module",
)

#: Embedded asset payloads. Base64 is not code, and a 50KB atlas string would
#: otherwise dominate every string-literal probe.
DATA_URI_PREFIX = "data:image/"

SCAN_POLICY = {
    "name": "authored-source-only v1",
    "rationale": (
        "A symbol index over a vendored library reports PRESENT for nearly every "
        "feature the GDD names, because a game framework necessarily defines "
        "Scene, World, Tween, Zone and Wander. Excluding it is not tidiness — it "
        "is the difference between a gap detector that reads the codebase and one "
        "that reports whatever the framework happens to be called."
    ),
    "rules": {
        "vendor_line": f"a single line longer than {VENDOR_LINE_CHARS} characters",
        "vendor_signature": "a line opening with a known minified-bundle preamble",
        "data_uri": "a base64 `data:image/...` payload — an embedded asset, not code",
    },
}


@dataclass
class ScanExclusion:
    """One excluded region of one file, with the reason it was cut."""
    path: str
    line: int
    chars: int
    rule: str
    reason: str

    def as_dict(self) -> dict:
        return {
            "path": self.path, "line": self.line, "chars": self.chars,
            "rule": self.rule, "reason": self.reason,
        }


def classify_line(text: str) -> tuple[str, str] | None:
    """Return `(rule, reason)` if this line must be excluded, else None."""
    stripped = text.lstrip()
    for sig in VENDOR_SIGNATURES:
        if stripped.startswith(sig):
            return (
                "vendor_signature",
                f"line opens with the minified-bundle preamble {sig!r}; this is a "
                f"vendored library, and indexing it would make every feature "
                f"appear already implemented",
            )
    if DATA_URI_PREFIX in text and "base64," in text:
        return (
            "data_uri",
            "line embeds a base64 `data:image/...` payload — an art asset, not "
            "authored code; its characters are not identifiers",
        )
    if len(text) > VENDOR_LINE_CHARS:
        return (
            "vendor_line",
            f"line is {len(text):,} characters, above the {VENDOR_LINE_CHARS:,} "
            f"authored-source threshold; the longest hand-written line in this "
            f"build is under 800",
        )
    return None


def policy_summary() -> dict:
    """Both policies, for the manifest and the generated evidence documents."""
    return {"corpus": BUILDER_POLICY, "scan": SCAN_POLICY}
