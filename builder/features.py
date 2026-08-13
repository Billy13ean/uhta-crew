"""Stage 1 — read the GDD, produce a feature inventory.

Two passes, in this order and for this reason:

  DETERMINISTIC FIRST. v0.9.9 is unusually machine-readable — the verbs, the
  build-order tiers and the acceptance criteria are all markdown tables. Parsing
  them is exact, free, and reproducible, so nothing that a parser can establish
  is left to a model to assert.

  LLM SECOND, for the one thing a parser cannot do: `observable_signature` —
  what would appear in the code if this feature existed. That is a judgement
  about implementation, it is the field the whole scan stage runs on, and it is
  the only reason this stage needs a model at all.

THE STATUS COLUMN IS NOT AN INPUT. §3's table self-reports Built / Unbuilt.
Feeding that to the gap detector would make this pipeline a table lookup wearing
a codebase scan as a costume. It is parsed, carried as `gdd_claimed_status`, and
withheld from `Feature.for_detection()` — which is what the detector receives.
`--selftest` asserts the withholding. Its only use is the scoreboard cross-check
in `gap.py`, AFTER detection has independently committed to a verdict.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

from crew.llm import LLMCall

from . import AgentError, parse_json_payload

PROMPT_VERSION = "analyst v2 (builder pipeline)"
TEMPERATURE = 0.0

TIER_ORDER = ["CORE", "PASS 1", "PASS 2", "NICE", "PROPOSED", "CUT"]

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD = re.compile(r"[`*_]")
_ENUM = re.compile(r"^\s*\d+[.)]\s*")
_EMDASH_TAIL = re.compile(r"\s+[—–]\s+.*$")


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------

@dataclass
class Signature:
    """What would appear in the code if this feature existed."""
    identifiers: list[str] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)
    rules_key_paths: list[str] = field(default_factory=list)
    strings: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.identifiers or self.constants or self.rules_key_paths or self.strings)

    def weight(self) -> int:
        return (len(self.identifiers) + len(self.constants)
                + len(self.rules_key_paths) + len(self.strings))


@dataclass
class Feature:
    id: str
    name: str
    gdd_section: str
    tier: str                       # CORE | PASS 1 | PASS 2 | NICE | PROPOSED | CUT | UNTIERED
    kind: str                       # mechanic | verb | system | content | ui | unknown
    description: str = ""
    signature: Signature = field(default_factory=Signature)
    gdd_claimed_status: str = ""    # WITHHELD from detection. Cross-check only.
    source: str = "table"           # table | analyst
    blocks_criteria: list[int] = field(default_factory=list)

    def for_detection(self) -> dict:
        """Exactly what the gap detector is allowed to see.

        Note what is absent: `tier`, `gdd_claimed_status`, `blocks_criteria`. The
        detector's only job is to decide whether the code contains this feature.
        Anything that hints at the answer, or at how much the answer matters, is
        withheld — so that a disagreement with §3's status column is real
        evidence and not an echo.
        """
        return {
            "id": self.id,
            "name": self.name,
            "gdd_section": self.gdd_section,
            "kind": self.kind,
            "description": self.description,
            "signature": asdict(self.signature),
        }

    def as_dict(self) -> dict:
        d = asdict(self)
        d["signature"] = asdict(self.signature)
        return d


@dataclass
class Criterion:
    number: int
    text: str
    status: str
    blocked: bool
    blocker_hint: str = ""


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def slugify(name: str) -> str:
    s = _MD.sub("", name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48] or "unnamed"


def clean(cell: str) -> str:
    return _MD.sub("", cell).strip()


def _tables(text: str) -> list[list[list[str]]]:
    """Every markdown table in the document, as rows of cells.

    Fence-aware for the same reason `content/retriever.py` is: the GDD embeds
    fenced blocks whose lines start with characters that otherwise look like
    structure.
    """
    out, cur, in_fence = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue                      # separator row
            cur.append(cells)
        else:
            if len(cur) >= 2:
                out.append(cur)
            cur = []
    if len(cur) >= 2:
        out.append(cur)
    return out


def _split_items(blob: str) -> list[str]:
    """Split a tier's contents cell into individual feature names."""
    for sep in ("·", ";"):
        if sep in blob:
            parts = blob.split(sep)
            break
    else:
        parts = re.split(r",(?![^(]*\))", blob)
    items = []
    for p in parts:
        p = _EMDASH_TAIL.sub("", p)            # drop the commentary after an em dash
        p = _ENUM.sub("", p)
        p = clean(p).rstrip(".").strip()
        p = re.sub(r"\s*\(§[^)]*\)", "", p).strip()
        if p and len(p) > 2:
            items.append(p)
    return items


# --------------------------------------------------------------------------
# deterministic parse
# --------------------------------------------------------------------------

def parse_verbs(text: str) -> list[Feature]:
    """§2's verb table — seven rows of (verb, cost, effect)."""
    feats = []
    for tbl in _tables(text):
        head = [c.lower() for c in tbl[0]]
        if not (len(head) == 3 and head[0] == "verb" and "cost" in head[1]):
            continue
        for row in tbl[1:]:
            if len(row) != 3:
                continue
            name = clean(row[0])
            if not name:
                continue
            feats.append(Feature(
                id=f"verb-{slugify(name)}", name=name, gdd_section="2", tier="UNTIERED",
                kind="verb",
                description=f"Player verb. Cost: {clean(row[1])}. Effect: {clean(row[2])}",
            ))
        break
    return feats


def parse_tiers(text: str) -> tuple[list[Feature], dict[str, str]]:
    """§3's build-order table. Returns (features, {tier: claimed_status})."""
    feats: list[Feature] = []
    statuses: dict[str, str] = {}
    for tbl in _tables(text):
        head = [c.lower() for c in tbl[0]]
        if not (len(head) == 3 and head[0] == "tier" and "status" in head[2]):
            continue
        for row in tbl[1:]:
            if len(row) != 3:
                continue
            m = _BOLD.search(row[0])
            tier = clean(m.group(1) if m else row[0].split("—")[0]).upper()
            tier = tier.replace("PASS1", "PASS 1").replace("PASS2", "PASS 2")
            if tier not in TIER_ORDER:
                continue
            status = clean(row[2])
            statuses[tier] = status
            for item in _split_items(row[1]):
                feats.append(Feature(
                    id=slugify(item), name=item, gdd_section="3", tier=tier,
                    kind="unknown", description=item, gdd_claimed_status=status,
                ))
        break
    return feats, statuses


def parse_criteria(text: str) -> list[Criterion]:
    """§4's Definition of Playable — six numbered acceptance criteria."""
    crits = []
    for tbl in _tables(text):
        head = [c.lower() for c in tbl[0]]
        if not (len(head) == 3 and head[0] == "#" and "criterion" in head[1]):
            continue
        for row in tbl[1:]:
            if len(row) != 3 or not row[0].strip().isdigit():
                continue
            status = clean(row[2])
            blocked = status.lower().startswith("blocked")
            hint = ""
            if blocked:
                m = re.search(r"needs?\s+(?:the\s+)?(.+)$", status, re.IGNORECASE)
                if m:
                    hint = m.group(1).strip().rstrip(".")
            crits.append(Criterion(int(row[0]), clean(row[1]), status, blocked, hint))
        break
    return crits


def link_criteria(features: list[Feature], criteria: list[Criterion]) -> None:
    """Attach `blocks_criteria` to whichever feature a blocked criterion names.

    §4 says 'Blocked — needs the narrated opening'; §3's NICE tier says
    'narrated teaching opening'. The two strings are not equal, so match on
    shared significant words rather than identity, and carry a same-dependency
    criterion forward (criterion 3 reads 'same dependency' and names nothing).
    """
    stop = {"the", "a", "an", "of", "for", "and", "to", "same", "dependency", "needs"}
    last_hit: Feature | None = None
    for c in criteria:
        if not c.blocked:
            continue
        if not c.blocker_hint or "same" in c.blocker_hint.lower():
            if last_hit is not None:
                last_hit.blocks_criteria.append(c.number)
            continue
        want = {w for w in re.findall(r"[a-z]+", c.blocker_hint.lower()) if w not in stop}
        best, best_n = None, 0
        for f in features:
            have = {w for w in re.findall(r"[a-z]+", f.name.lower()) if w not in stop}
            n = len(want & have)
            if n > best_n:
                best, best_n = f, n
        if best is not None and best_n >= 2:
            best.blocks_criteria.append(c.number)
            last_hit = best


def extract_deterministic(gdd_text: str) -> tuple[list[Feature], list[Criterion], dict]:
    """Everything a parser can establish, before any model is asked anything."""
    verbs = parse_verbs(gdd_text)
    tiered, statuses = parse_tiers(gdd_text)
    criteria = parse_criteria(gdd_text)

    # A verb named in a tier row is the same feature as its verb-table row: keep
    # the verb's richer description, take the tier's placement and status.
    by_norm: dict[str, Feature] = {}
    merged: list[Feature] = []
    for f in verbs:
        by_norm[f.name.lower()] = f
        merged.append(f)
    for f in tiered:
        # A single tier cell can name SEVERAL verbs — CORE's is "Flame / Roar /
        # Wait / Sleep + Walk". Claiming only the first left Walk, Roar and Wait
        # untiered, which then collected the stop-rule penalty as though they
        # were optional. Every verb the cell names takes the tier.
        hits = [by_norm[t.lower()] for t in re.findall(r"[A-Za-z]+", f.name)
                if t.lower() in by_norm]
        if hits:
            for h in hits:
                if h.tier == "UNTIERED":
                    h.tier, h.gdd_claimed_status = f.tier, f.gdd_claimed_status
                    h.gdd_section = "2/3"
            continue
        merged.append(f)
        by_norm[f.name.lower()] = f

    link_criteria(merged, criteria)
    meta = {
        "tier_statuses": statuses,
        "verbs_parsed": len(verbs),
        "tier_items_parsed": len(tiered),
        "criteria_parsed": len(criteria),
    }
    return merged, criteria, meta


# --------------------------------------------------------------------------
# the Analyst — the one thing the parser cannot do
# --------------------------------------------------------------------------

def _load_prompt(prompts_dir) -> str:
    text = (prompts_dir / "analyst.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


#: Features per Analyst call, and the ceiling on each response.
#:
#: Two live runs to get these right, and the first fix was the wrong one. Run 1
#: sent all 30 features at once and truncated. Batching at 8 truncated too — at
#: 24,797 characters for eight features, almost exactly what thirty had produced.
#: The size was never proportional to the feature count: prompt v1 said "give
#: several spellings" and "be generous rather than minimal" with no cap on any
#: array, so the model filled the budget whatever it was handed.
#:
#: The real fix is prompt v2, which bounds every list (3–6 identifiers, ≤4
#: constants, ≤4 key paths, ≤3 strings, ≤15-word description). At those caps a
#: feature costs roughly 500–700 characters, so six per call lands near 4,000 —
#: comfortably inside 12,000 tokens with room for a verbose run.
ANALYST_BATCH = 6
ANALYST_MAX_TOKENS = 12000

#: Only the first batch is asked to add features the tables missed. Every batch
#: sees the whole GDD, so asking all of them means all of them independently
#: re-derive the same un-tabled systems — paid for four times and deduped away.
ADD_MISSING_YES = (
    "Additionally: add any feature the GDD describes that the list above is "
    "missing. The tables do not catch everything — §2's prose names systems that "
    "never appear in a table. Give each a new lowercase-hyphen slug as its `id`."
)
ADD_MISSING_NO = (
    "Do NOT add any feature beyond the list above. This is one batch of a larger "
    "inventory; another batch is responsible for the features the tables missed, "
    "and anything you add here is discarded as a duplicate."
)

SYSTEM = ("You are the Analyst for uhta's goal-oriented coding agent. You turn a "
          "game design document into a feature inventory in which every feature "
          "carries the concrete, checkable traces it would leave in source code "
          "if it had been implemented.")


def _check_not_truncated(agent: str, text: str, n_features: int) -> None:
    """Catch a max_tokens truncation HERE, where it is diagnosable.

    `crew/llm.py` returns whatever text it received and never inspects
    `stop_reason`, so a response cut off mid-array arrives looking like a
    response. Downstream it fails as 'no JSON payload', which points at the
    prompt rather than at the length — a misdiagnosis that cost a live run.

    An opening fence with no closing fence is the signature of exactly that.
    Detecting it structurally needs no change to the shared LLM layer, which
    two tagged submissions depend on.
    """
    s = text.strip()
    if not s.startswith("```"):
        return
    if s.count("```") >= 2:
        return
    raise AgentError(
        agent,
        f"the response was TRUNCATED: it opens a ```json fence and never closes "
        f"one, after {len(text):,} characters for {n_features} feature(s). This "
        f"is a max_tokens cutoff (currently {ANALYST_MAX_TOKENS:,}), not a "
        f"malformed prompt — the JSON up to the cut is well-formed. Lower "
        f"ANALYST_BATCH (currently {ANALYST_BATCH}) or raise ANALYST_MAX_TOKENS.",
    )


def run_analyst(llm, prompts_dir, features: list[Feature], sections: str,
                agent_label: str = "analyst") -> list[Feature]:
    """Give every feature an `observable_signature`; add any the tables missed.

    The features are sent WITHOUT tier and WITHOUT the claimed status, for the
    same reason the detector never sees them: a model told a feature is 'NICE —
    unbuilt' will write a signature it expects to miss.

    Batched. Each call carries the full GDD sections but only a slice of the
    feature list, so response size is bounded by ANALYST_BATCH rather than by
    the size of the inventory.
    """
    template = _load_prompt(prompts_dir)
    batches = [features[i:i + ANALYST_BATCH]
               for i in range(0, len(features), ANALYST_BATCH)] or [[]]

    payload: list = []
    for n, batch in enumerate(batches, 1):
        label = agent_label if len(batches) == 1 else f"{agent_label}-{n}of{len(batches)}"
        listing = "\n".join(
            f"- id={f.id} · name={f.name} · gdd_section={f.gdd_section} · from={f.source}"
            for f in batch
        )
        user = (template
                .replace("{{GDD_SECTIONS}}", sections)
                .replace("{{FEATURE_LIST}}", listing)
                .replace("{{ADD_MISSING}}",
                         ADD_MISSING_YES if n == 1 else ADD_MISSING_NO))
        out = llm.complete(LLMCall(
            agent=label, system=SYSTEM, user=user,
            temperature=TEMPERATURE, max_tokens=ANALYST_MAX_TOKENS,
        ))
        _check_not_truncated(label, out, len(batch))
        part = parse_json_payload(label, out)
        if not isinstance(part, list):
            raise AgentError(label,
                             f"expected a JSON array of features, got {type(part).__name__}")
        payload.extend(part)

    # Every batch sees the whole GDD, so two batches can independently propose
    # the same un-tabled feature. First writer wins.
    deduped, seen_ids = [], set()
    for raw in payload:
        rid = str(raw.get("id") or "").strip() if isinstance(raw, dict) else ""
        if rid and rid in seen_ids:
            continue
        if rid:
            seen_ids.add(rid)
        deduped.append(raw)
    payload = deduped

    by_id = {f.id: f for f in features}
    seen: set[str] = set()
    for i, raw in enumerate(payload, 1):
        if not isinstance(raw, dict):
            raise AgentError(agent_label, f"entry {i} is not an object: {raw!r}")
        fid = str(raw.get("id") or "").strip()
        if not fid:
            raise AgentError(agent_label, f"entry {i} has no id")
        sig_raw = raw.get("observable_signature") or {}
        if not isinstance(sig_raw, dict):
            raise AgentError(agent_label,
                             f"entry {i} ({fid}): observable_signature must be an object")
        sig = Signature(
            identifiers=[str(x) for x in sig_raw.get("identifiers", [])][:12],
            constants=[str(x) for x in sig_raw.get("constants", [])][:12],
            rules_key_paths=[str(x) for x in sig_raw.get("rules_key_paths", [])][:12],
            strings=[str(x) for x in sig_raw.get("strings", [])][:8],
        )
        if sig.is_empty():
            # THE structural guarantee for this stage. A feature with no
            # signature cannot be scanned for, so it would silently come back
            # ABSENT — a false gap that looks exactly like a real one.
            raise AgentError(
                agent_label,
                f"feature {fid!r} was returned with an empty observable_signature. "
                f"Every feature must carry at least one identifier, constant, "
                f"rules key path or string literal that would appear in the code "
                f"if it existed — otherwise the scan cannot look for it and it "
                f"reports ABSENT for free.",
            )
        seen.add(fid)
        if fid in by_id:
            f = by_id[fid]
            f.signature = sig
            f.kind = str(raw.get("kind") or f.kind or "unknown")
            if raw.get("description"):
                f.description = str(raw["description"])
        else:
            features.append(Feature(
                id=fid, name=str(raw.get("name") or fid),
                gdd_section=str(raw.get("gdd_section") or "2"),
                tier=str(raw.get("tier") or "UNTIERED").upper(),
                kind=str(raw.get("kind") or "unknown"),
                description=str(raw.get("description") or ""),
                signature=sig, source="analyst",
            ))

    missing = [f.id for f in features if f.signature.is_empty()]
    if missing:
        raise AgentError(
            agent_label,
            f"{len(missing)} table-derived feature(s) came back with no signature "
            f"at all: {missing[:8]}. Every feature in the supplied list must "
            f"appear in the response.",
        )
    return features
