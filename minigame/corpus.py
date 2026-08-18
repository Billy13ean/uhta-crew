"""The mini-game pipeline's corpus — a PER-DOCUMENT policy, and why.

A4's CORPUS_POLICY scopes by top-level section NUMBER, which works when every
document numbers its sections the same way. This corpus cannot reuse it: it
mixes GDD v0.9.9 (where §3 is the build order and §4 the Definition of
Playable — both things a mini-game recommender NEEDS) with v0.9.7-full
(where §3 is the AI architecture and §4 the technical strategy — both things
no player-facing design should retrieve). The same number means opposite
things in the two bindings, so the policy here is keyed by (document,
section), with a recorded reason per cut — the A5 BUILDER_POLICY lesson,
taken one step further.

Three documents, three roles:

    uhta-gdd-v0.9.9-condensed.md   the ONLY GDD with the encounter table.
                                   §1–§4 in (summary, mechanics+encounters,
                                   tiers+stop rule, playability); §5–§8 out
                                   (pipeline material).
    uhta-gdd-v0.9.7-full.md        §2.x only — the mechanical detail the
                                   condensed doc compresses (verb costs,
                                   burnout, systems). Everything else out,
                                   including §4.5 for A4's original reason.
    research/minigame-patterns.md  the seeded design-patterns reference —
                                   all in. It is the recommender half of the
                                   corpus; it contains no uhta canon and the
                                   Evaluator's EXCEEDS-SCOPE class polices
                                   the boundary.
"""
from __future__ import annotations

from content.retriever import Chunk, Exclusion, chunk_markdown

CORPUS_FILES = {
    "uhta-gdd-v0.9.9-condensed.md": "gdd/uhta-gdd-v0.9.9-condensed.md",
    "uhta-gdd-v0.9.7-full.md": "gdd/uhta-gdd-v0.9.7-full.md",
    "minigame-patterns.md": "research/minigame-patterns.md",
}

MINIGAME_POLICY = {
    "name": "minigame per-doc policy v1",
    "rationale": (
        "v0.9.9 and v0.9.7 number their sections differently — §3/§4 are "
        "game material in one and pipeline material in the other — so this "
        "policy is keyed by (document, top-level section), not by number "
        "alone."
    ),
    "per_doc": {
        "uhta-gdd-v0.9.9-condensed.md": {
            "include": {"1", "2", "3", "4"},
            "reasons_exclude": {
                "5": "§5 is the AI architecture — pipeline material.",
                "6": "§6 is technical strategy and token budgets — pipeline "
                     "material.",
                "7": "§7 is revision provenance.",
                "8": "§8 is open-questions process notes; the design content "
                     "it references lives in §2–§4, which are indexed.",
            },
        },
        "uhta-gdd-v0.9.7-full.md": {
            "include": {"2"},
            "reasons_exclude": {
                "*": "only §2 (mechanics detail) is indexed from the full "
                     "v0.9.7 binding; its §3–§7 are that document's pipeline "
                     "material, and §4.5 in particular carries the "
                     "Director's hand-written worked example (the A4 "
                     "exclusion, upheld).",
            },
        },
        "minigame-patterns.md": {
            "include": "*",
            "reasons_exclude": {},
        },
    },
    "exclude_front_matter": "version preambles and seeding notes describe "
                            "the documents, not the game or the patterns.",
}


def build_minigame_corpus(docs: dict[str, str]) -> tuple[list[Chunk],
                                                         list[Exclusion],
                                                         list[Chunk]]:
    all_chunks: list[Chunk] = []
    for name, text in docs.items():
        all_chunks.extend(chunk_markdown(text, name))

    kept: list[Chunk] = []
    dropped: list[Exclusion] = []
    for c in all_chunks:
        rules = MINIGAME_POLICY["per_doc"].get(c.doc)
        if rules is None:
            dropped.append(Exclusion(c.key, c.heading,
                                     f"document '{c.doc}' is not in the "
                                     f"per-doc policy", c.words))
            continue
        if c.top_level == "front-matter":
            dropped.append(Exclusion(c.key, c.heading,
                                     MINIGAME_POLICY["exclude_front_matter"],
                                     c.words))
            continue
        inc = rules["include"]
        if inc == "*" or c.top_level in inc:
            kept.append(c)
            continue
        reason = rules["reasons_exclude"].get(
            c.top_level, rules["reasons_exclude"].get(
                "*", f"top-level '{c.top_level}' not on the include list "
                     f"for {c.doc}"))
        dropped.append(Exclusion(c.key, c.heading, reason, c.words))
    return all_chunks, dropped, kept
