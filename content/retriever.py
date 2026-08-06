"""Retrieval for the content pipeline — chunking, corpus scoping, BM25, selection.

Deterministic end to end. No model is involved in deciding what the Writer sees,
which is the point: if a generated line is wrong, the cause is either the prompt
or a retrieval decision that is written down in `RAG-TRACE.md` with a reason.

Three stages, each of which records what it threw away:

  chunk_markdown   one `###` subsection is one chunk (GDD §4.5: "the section
                   boundary IS the chunk boundary"). A `##` section with no
                   `###` children is itself one chunk. Headings inside fenced
                   code blocks are NOT headings — the GDD embeds a report
                   skeleton whose lines start with `##`, and treating those as
                   sections would shred §3.2 into nonsense.

  CORPUS_POLICY    the GDD is two documents in one binding: the design of uhta,
                   and the design of the pipeline that builds uhta. Only the
                   first is a knowledge base for writing the game's text. Every
                   dropped section is recorded with a reason.

  Retriever        BM25 (k1=1.5, b=0.75, non-negative IDF), written out here
                   rather than pulled from a package, because the assignment
                   permits one third-party dependency and it is already spent on
                   `anthropic`. Selection applies the Keeper's Mode-B1 discipline
                   to the scorer: a score threshold, a token budget, duplicate-
                   heading suppression, and an exclusion list.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# tuning constants — all of them appear in RAG-TRACE.md so a reader can check
# a retrieval decision against the number that caused it.
# --------------------------------------------------------------------------

BM25_K1 = 1.5
BM25_B = 0.75

#: A chunk scoring below this is never retrieved, however highly it ranks.
#: Calibrated against two deliberately off-topic control queries in --selftest:
#: both must retrieve NOTHING. A retriever with no floor always returns its
#: best chunk, which for an off-topic query is a confidently wrong one.
SCORE_THRESHOLD = 8.0

#: Per-beat context budget. The GDD's own Keeper cap is 15K tokens for a whole
#: packet; a single narration line needs far less, and a Writer handed the whole
#: corpus is not being retrieved for.
#: §2.3 (Systems) alone is ~4.5K estimated tokens — it is the document's largest
#: subsection and the one most beats need. The budget is set above it so the
#: two-chunk rule can actually fire on a systems query rather than silently
#: degrading to one chunk.
TOKEN_BUDGET = 6000

#: How many ranked-but-rejected chunks RAG-TRACE records individually before
#: collapsing the rest into a counted tail. Not a silent cap: the tail line
#: states how many were dropped and why.
EXCLUSION_DETAIL_LIMIT = 6

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do", "does",
    "for", "from", "has", "have", "how", "in", "into", "is", "it", "its", "of",
    "on", "or", "that", "the", "their", "them", "then", "there", "they", "this",
    "to", "was", "what", "when", "which", "who", "why", "will", "with", "you",
    "your",
}

_WORD_RE = re.compile(r"[a-z0-9_]+")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_HEADING_RE = re.compile(r"^(#{2,3})\s+(.*\S)\s*$")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, stopwords removed. Deterministic and inspectable."""
    return [t for t in _WORD_RE.findall(text.lower()) if t not in _STOPWORDS]


def estimate_tokens(text: str) -> int:
    """~4 chars per token. An estimate, labelled as one everywhere it is used."""
    return max(1, len(text) // 4)


# --------------------------------------------------------------------------
# chunking
# --------------------------------------------------------------------------

@dataclass
class Chunk:
    doc: str            # source file name
    heading: str        # the heading line, without the #s
    level: int          # 2 or 3
    section: str        # "2.5", "3", "A", or "front-matter"
    top_level: str      # "2", "3", "A", "front-matter"
    text: str           # heading + body, verbatim

    @property
    def key(self) -> str:
        return f"{self.doc}#{self.section}"

    @property
    def norm_heading(self) -> str:
        return re.sub(r"[^a-z0-9]+", " ", self.heading.lower()).strip()

    @property
    def tokens(self) -> int:
        return estimate_tokens(self.text)

    @property
    def words(self) -> int:
        return len(self.text.split())

    def excerpt(self, limit: int = 600) -> str:
        body = " ".join(self.text.split())
        return body if len(body) <= limit else body[: limit - 1].rstrip() + "…"


def _section_id(heading: str, level: int, counter: list[int]) -> tuple[str, str]:
    """Return (section, top_level) parsed from the heading text.

    Handles "2.5 Player experience", "5. Identified Logic Gaps",
    "Appendix A — Changelog", and anything unnumbered (falls back to a counter).
    """
    m = re.match(r"^(\d+(?:\.\d+)*)", heading)
    if m:
        sec = m.group(1)
        return sec, sec.split(".")[0]
    m = re.match(r"^Appendix\s+([A-Z])", heading, re.IGNORECASE)
    if m:
        return f"Appendix {m.group(1).upper()}", m.group(1).upper()
    counter[0] += 1
    sec = f"{'sub' if level == 3 else 'sec'}-{counter[0]}"
    return sec, sec


def chunk_markdown(text: str, doc: str) -> list[Chunk]:
    """Split a markdown document into chunks at `###`, falling back to `##`.

    Fenced regions are skipped when looking for headings. A `##` section that
    has `###` children contributes its own preamble as a chunk only when that
    preamble carries real content (>40 words) — otherwise the preamble is just
    a title and belongs to nobody.
    """
    lines = text.splitlines()
    in_fence = False
    heads: list[tuple[int, int, str]] = []  # (line index, level, heading text)
    for i, line in enumerate(lines):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))

    counter = [0]
    chunks: list[Chunk] = []

    if not heads:
        sec, top = _section_id(doc, 2, counter)
        return [Chunk(doc, doc, 2, sec, top, text)]

    # front matter: everything before the first heading
    front = "\n".join(lines[: heads[0][0]]).strip()
    if front:
        chunks.append(Chunk(doc, "front matter", 2, "front-matter", "front-matter", front))

    for idx, (start, level, heading) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        body = "\n".join(lines[start:end]).strip()
        sec, top = _section_id(heading, level, counter)

        if level == 2:
            # Does this ## have ### children before the next ## ?
            has_children = False
            for _, lv, _ in heads[idx + 1:]:
                if lv == 2:
                    break
                if lv == 3:
                    has_children = True
                    break
            if has_children:
                # keep only the preamble (up to the first child), and only if it
                # carries real content rather than being a bare title
                child_start = heads[idx + 1][0]
                body = "\n".join(lines[start:child_start]).strip()
                if len(body.split()) <= 40:
                    continue
        chunks.append(Chunk(doc, heading, level, sec, top, body))

    return chunks


# --------------------------------------------------------------------------
# corpus policy
# --------------------------------------------------------------------------

@dataclass
class Exclusion:
    key: str
    heading: str
    reason: str
    words: int = 0


CORPUS_POLICY = {
    "name": "game-material-only v1",
    "rationale": (
        "The GDD is two documents in one binding — the design of uhta, and the "
        "design of the pipeline that builds uhta. Only the first is a knowledge "
        "base for writing the game's text. A Writer that can read §4.5 is not "
        "generating a narration line; it is handing the Director's own worked "
        "example back."
    ),
    "include_top_level": {"1", "2", "5", "6", "A"},
    "exclude_top_level": {
        "3": "§3 is the AI-architecture / agent-roster section — how the game is "
             "built, not what is in it. A narration line grounded in the crew "
             "roster would be about the pipeline.",
        "4": "§4 is technical strategy, budgets, and the RAG design itself. §4.5 "
             "in particular carries the Director's hand-written worked narration "
             "example; indexing it lets the Writer retrieve the answer instead of "
             "writing one.",
        "7": "§7 is revision provenance — a record of document history, not game "
             "material.",
    },
    "exclude_docs": {
        "CANON-process.md": "Process canon — Keeper escalation, build order, "
                            "artifact counts. Governs how the project runs; "
                            "contains no game material.",
    },
    "exclude_front_matter": "Version preamble / changelog. Describes what changed "
                            "between GDD revisions, not what is true in the world.",
}


def apply_corpus_policy(chunks: list[Chunk]) -> tuple[list[Chunk], list[Exclusion]]:
    kept: list[Chunk] = []
    dropped: list[Exclusion] = []
    for c in chunks:
        if c.doc in CORPUS_POLICY["exclude_docs"]:
            dropped.append(Exclusion(c.key, c.heading,
                                     CORPUS_POLICY["exclude_docs"][c.doc], c.words))
            continue
        if c.top_level == "front-matter":
            dropped.append(Exclusion(c.key, c.heading,
                                     CORPUS_POLICY["exclude_front_matter"], c.words))
            continue
        if c.top_level in CORPUS_POLICY["exclude_top_level"]:
            dropped.append(Exclusion(c.key, c.heading,
                                     CORPUS_POLICY["exclude_top_level"][c.top_level],
                                     c.words))
            continue
        if c.top_level in CORPUS_POLICY["include_top_level"] or c.doc == "CANON.md":
            kept.append(c)
            continue
        dropped.append(Exclusion(
            c.key, c.heading,
            f"top-level section '{c.top_level}' is not on the include list "
            f"{sorted(CORPUS_POLICY['include_top_level'])}", c.words))
    return kept, dropped


# --------------------------------------------------------------------------
# BM25 + selection
# --------------------------------------------------------------------------

@dataclass
class Ranked:
    chunk: Chunk
    score: float


@dataclass
class Selection:
    query: str
    ranked: list[Ranked]
    selected: list[Ranked]
    exclusions: list[Exclusion] = field(default_factory=list)
    max_chunks: int = 2

    @property
    def tokens(self) -> int:
        return sum(r.chunk.tokens for r in self.selected)


class Retriever:
    """BM25 over the policy-scoped chunk set."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._tf: list[dict[str, int]] = []
        self._len: list[int] = []
        df: dict[str, int] = {}
        for c in chunks:
            toks = tokenize(c.text)
            tf: dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            self._tf.append(tf)
            self._len.append(len(toks))
            for t in tf:
                df[t] = df.get(t, 0) + 1
        self._df = df
        self.n = len(chunks)
        self.avgdl = (sum(self._len) / self.n) if self.n else 0.0

    def idf(self, term: str) -> float:
        """Non-negative IDF: ln(1 + (N - df + 0.5)/(df + 0.5)). Never below 0,
        so a term present in every chunk contributes nothing rather than
        subtracting score from a chunk that legitimately contains it."""
        df = self._df.get(term, 0)
        return math.log(1.0 + (self.n - df + 0.5) / (df + 0.5))

    def score(self, query: str, i: int) -> float:
        tf, dl = self._tf[i], self._len[i]
        total = 0.0
        for term in tokenize(query):
            f = tf.get(term, 0)
            if not f:
                continue
            denom = f + BM25_K1 * (1 - BM25_B + BM25_B * (dl / self.avgdl if self.avgdl else 1))
            total += self.idf(term) * (f * (BM25_K1 + 1)) / denom
        return total

    def rank(self, query: str) -> list[Ranked]:
        out = [Ranked(c, self.score(query, i)) for i, c in enumerate(self.chunks)]
        out.sort(key=lambda r: (-r.score, r.chunk.key))
        return out

    def select(self, query: str, max_chunks: int = 2,
               threshold: float = SCORE_THRESHOLD,
               token_budget: int = TOKEN_BUDGET) -> Selection:
        ranked = self.rank(query)
        selected: list[Ranked] = []
        exclusions: list[Exclusion] = []
        seen_headings: set[str] = set()
        used = 0
        tail_below = 0

        for r in ranked:
            c = r.chunk
            if len(selected) >= max_chunks:
                reason = f"max_chunks={max_chunks} already filled (score {r.score:.2f})"
            elif r.score < threshold:
                reason = f"score {r.score:.2f} below threshold {threshold}"
            elif c.norm_heading in seen_headings:
                reason = (f"duplicate heading suppressed — same section already "
                          f"selected from another document (score {r.score:.2f})")
            elif used + c.tokens > token_budget:
                reason = (f"token budget {token_budget} would be exceeded "
                          f"(+{c.tokens} on {used})")
            else:
                selected.append(r)
                seen_headings.add(c.norm_heading)
                used += c.tokens
                continue

            if len(exclusions) < EXCLUSION_DETAIL_LIMIT and r.score >= threshold:
                exclusions.append(Exclusion(c.key, c.heading, reason, c.words))
            elif r.score < threshold:
                tail_below += 1
            elif len(exclusions) < EXCLUSION_DETAIL_LIMIT:
                exclusions.append(Exclusion(c.key, c.heading, reason, c.words))

        if tail_below:
            exclusions.append(Exclusion(
                "—", f"{tail_below} further chunk(s)",
                f"scored below the {threshold} threshold; not listed individually "
                f"(detail limit {EXCLUSION_DETAIL_LIMIT})", 0))
        return Selection(query, ranked, selected, exclusions, max_chunks)


    def select_multi(self, queries: list[str], per_query: int = 1,
                     threshold: float = SCORE_THRESHOLD,
                     token_budget: int = TOKEN_BUDGET) -> Selection:
        """The GDD §4.5 two-chunk rule, implemented as a union of per-query cuts.

        The rule is not "take the top 2 of one query" — that was the failure the
        rule exists to fix. A single blended query ranks the mechanically-dense
        section first and *second*, and the Writer never sees what the moment is
        supposed to feel like. So each facet of the beat gets its own query and
        its own cut, and the results are unioned:

            queries[0]  the mechanical consequence — the verb's own row, the
                        system that fires
            queries[1]  the experience — what the player is meant to understand

        Every chunk a query wanted but did not get is recorded with its reason,
        exactly as in `select`.
        """
        selected: list[Ranked] = []
        exclusions: list[Exclusion] = []
        chosen_keys: set[str] = set()
        seen_headings: set[str] = set()
        used = 0
        all_ranked: list[Ranked] = []

        for qi, q in enumerate(queries):
            ranked = self.rank(q)
            all_ranked.extend(ranked[:3])
            taken = 0
            for r in ranked:
                if taken >= per_query:
                    break
                c = r.chunk
                if r.score < threshold:
                    exclusions.append(Exclusion(
                        c.key, c.heading,
                        f"query {qi + 1} best remaining chunk scored {r.score:.2f}, "
                        f"below threshold {threshold} — this query retrieved nothing",
                        c.words))
                    break
                if c.key in chosen_keys:
                    continue  # already supplied by an earlier query; not a cut
                if c.norm_heading in seen_headings:
                    exclusions.append(Exclusion(
                        c.key, c.heading,
                        f"duplicate heading suppressed — the same section is already "
                        f"selected from another document (score {r.score:.2f})", c.words))
                    continue
                if used + c.tokens > token_budget:
                    exclusions.append(Exclusion(
                        c.key, c.heading,
                        f"token budget {token_budget} would be exceeded "
                        f"(+{c.tokens} est. tokens on {used})", c.words))
                    continue
                selected.append(r)
                chosen_keys.add(c.key)
                seen_headings.add(c.norm_heading)
                used += c.tokens
                taken += 1

        all_ranked.sort(key=lambda r: (-r.score, r.chunk.key))
        return Selection(" | ".join(queries), all_ranked, selected, exclusions,
                         per_query * len(queries))


def build_corpus(docs: dict[str, str]) -> tuple[list[Chunk], list[Exclusion], list[Chunk]]:
    """docs: {filename: text}. Returns (all_chunks, corpus_exclusions, kept)."""
    all_chunks: list[Chunk] = []
    for name, text in docs.items():
        all_chunks.extend(chunk_markdown(text, name))
    kept, dropped = apply_corpus_policy(all_chunks)
    return all_chunks, dropped, kept
