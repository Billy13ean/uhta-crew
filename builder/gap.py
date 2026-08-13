"""Stage 3 — detect gaps. Two layers, plus a cross-check that can embarrass the GDD.

LAYER 1 is deterministic. Each feature's `observable_signature` is probed against
the code index and scored by how much of it was found. Cheap, reproducible, and
it decides most features outright.

LAYER 2 is a model, and only for the features layer 1 could not decide: a
PARTIAL, a thin-signature ABSENT, or a PRESENT that only just cleared the line.
It receives the feature and the actual source lines around the nearest hits, and
it must SHOW its verdict:

    PRESENT / PARTIAL  ->  must quote a real code line
    ABSENT             ->  must list what it searched for and did not find

A verdict that shows neither raises `AgentError` and halts the run. That is the
Critic's guarantee from the content pipeline, transplanted: a catch shown, not
claimed. `content/agents/critic.py` refuses to write a rejection without a
repair; this refuses to write a verdict without evidence.

THE CROSS-CHECK is the reason any of this is worth doing. §3's table self-reports
Built / Unbuilt. The detector never sees that column — `Feature.for_detection()`
withholds it — so the two are independent, and every disagreement between them is
a finding. An agent that had merely read the status column could not possibly
disagree with it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from crew.llm import LLMCall

from . import AgentError, parse_json_payload
from .codescan import CodeIndex, Hit
from .features import Feature

PROMPT_VERSION = "gap-adjudicator v1 (builder pipeline)"
TEMPERATURE = 0.0

PRESENT, PARTIAL, ABSENT = "PRESENT", "PARTIAL", "ABSENT"
VALID_VERDICTS = {PRESENT, PARTIAL, ABSENT}

#: How much each kind of trace counts. Identifiers dominate because a feature
#: that exists has a name; rules key paths matter almost as much in this project,
#: where a whole system can be present as data the build reads at boot.
WEIGHTS = {"identifiers": 0.45, "rules_key_paths": 0.25, "constants": 0.18, "strings": 0.12}

PRESENT_AT = 0.60
ABSENT_BELOW = 0.15
#: A PRESENT this close to the line, or an ABSENT resting on this few traces, is
#: not a confident answer — send it to layer 2 rather than reporting it as one.
UNSURE_PRESENT_BELOW = 0.72
THIN_SIGNATURE = 4


@dataclass
class Evidence:
    category: str
    needle: str
    found: bool
    hits: list[Hit] = field(default_factory=list)
    excerpt: str = ""

    def as_dict(self) -> dict:
        return {"category": self.category, "needle": self.needle, "found": self.found,
                "hits": [str(h) for h in self.hits[:3]], "excerpt": self.excerpt}


@dataclass
class GapVerdict:
    feature: Feature
    verdict: str
    score: float
    evidence: list[Evidence]
    layer: int = 1
    reason: str = ""
    quoted_code: str = ""
    searched_for: list[str] = field(default_factory=list)
    disagrees_with_gdd: bool = False
    gdd_expected: str = ""

    @property
    def is_gap(self) -> bool:
        return self.verdict in (PARTIAL, ABSENT)

    def found_ratio(self) -> str:
        f = sum(1 for e in self.evidence if e.found)
        return f"{f}/{len(self.evidence)}"

    def as_dict(self) -> dict:
        return {
            "id": self.feature.id, "name": self.feature.name,
            "verdict": self.verdict, "score": round(self.score, 3), "layer": self.layer,
            "found": self.found_ratio(), "reason": self.reason,
            "quoted_code": self.quoted_code, "searched_for": self.searched_for,
            "gdd_claimed_status": self.feature.gdd_claimed_status,
            "gdd_expected": self.gdd_expected,
            "disagrees_with_gdd": self.disagrees_with_gdd,
            "evidence": [e.as_dict() for e in self.evidence],
        }


# --------------------------------------------------------------------------
# layer 1 — deterministic probe
# --------------------------------------------------------------------------

def probe(feature: Feature, idx: CodeIndex) -> tuple[float, list[Evidence]]:
    sig = feature.signature
    buckets = {
        "identifiers": sig.identifiers,
        "constants": sig.constants,
        "rules_key_paths": sig.rules_key_paths,
        "strings": sig.strings,
    }
    evidence: list[Evidence] = []
    total_w = 0.0
    score = 0.0

    for cat, needles in buckets.items():
        if not needles:
            continue
        total_w += WEIGHTS[cat]
        found_n = 0
        for needle in needles:
            if cat == "rules_key_paths":
                ok = idx.has_key_path(needle)
                hits = [Hit("rules", 1)] if ok else []
            elif cat == "strings":
                hits = idx.find_literal(needle)
                ok = bool(hits)
            else:
                hits = idx.find_symbol(needle)
                ok = bool(hits)
            found_n += 1 if ok else 0
            evidence.append(Evidence(
                cat, needle, ok, hits,
                idx.excerpt(hits[0]) if hits and cat != "rules_key_paths" else "",
            ))
        score += WEIGHTS[cat] * (found_n / len(needles))

    return (score / total_w if total_w else 0.0), evidence


def classify(score: float) -> str:
    if score >= PRESENT_AT:
        return PRESENT
    if score < ABSENT_BELOW:
        return ABSENT
    return PARTIAL


def needs_adjudication(v: GapVerdict) -> bool:
    if v.verdict == PARTIAL:
        return True
    if v.verdict == ABSENT and v.feature.signature.weight() < THIN_SIGNATURE:
        return True
    if v.verdict == PRESENT and v.score < UNSURE_PRESENT_BELOW:
        return True
    return False


def detect_layer1(features: list[Feature], idx: CodeIndex) -> list[GapVerdict]:
    out = []
    for f in features:
        score, ev = probe(f, idx)
        out.append(GapVerdict(f, classify(score), score, ev, layer=1,
                              reason="deterministic signature probe"))
    return out


# --------------------------------------------------------------------------
# layer 2 — adjudication
# --------------------------------------------------------------------------

def _context(v: GapVerdict, idx: CodeIndex, max_lines: int = 24) -> str:
    """The real source around the traces that DID hit — never a summary."""
    seen, parts = set(), []
    for e in v.evidence:
        if not e.found:
            continue
        for h in e.hits[:2]:
            if (h.path, h.line) in seen or h.path == "rules":
                continue
            seen.add((h.path, h.line))
            rows = idx.lines.get(h.path) or []
            lo, hi = max(1, h.line - 2), min(len(rows), h.line + 2)
            body = "\n".join(f"{n:>6} | {rows[n - 1][:160]}" for n in range(lo, hi + 1))
            parts.append(f"--- {h.path} (matched {e.needle!r} at line {h.line}) ---\n{body}")
            if len(parts) >= max_lines // 4:
                break
        if len(parts) >= max_lines // 4:
            break
    return "\n\n".join(parts) if parts else "(no signature element matched anywhere in the indexed source)"


def _load_prompt(prompts_dir) -> str:
    text = (prompts_dir / "gap-adjudicator.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def adjudicate(llm, prompts_dir, v: GapVerdict, idx: CodeIndex,
               agent_label: str | None = None) -> GapVerdict:
    agent = agent_label or f"gap-{v.feature.id}"
    template = _load_prompt(prompts_dir)
    d = v.feature.for_detection()
    missing = [e.needle for e in v.evidence if not e.found]
    user = (template
            .replace("{{FEATURE_NAME}}", d["name"])
            .replace("{{GDD_SECTION}}", d["gdd_section"])
            .replace("{{DESCRIPTION}}", d["description"])
            .replace("{{SIGNATURE_FOUND}}", ", ".join(e.needle for e in v.evidence if e.found) or "(none)")
            .replace("{{SIGNATURE_MISSING}}", ", ".join(missing) or "(none)")
            .replace("{{LAYER1_VERDICT}}", f"{v.verdict} (score {v.score:.2f})")
            .replace("{{CODE_CONTEXT}}", _context(v, idx)))
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Gap Adjudicator for uhta's goal-oriented coding "
                "agent. You decide whether a designed feature is present in the "
                "source you are shown, and you must show the evidence for your "
                "answer rather than assert it."),
        user=user, temperature=TEMPERATURE, max_tokens=2000,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, dict):
        raise AgentError(agent, f"expected a JSON object, got {type(payload).__name__}")

    verdict = str(payload.get("verdict", "")).strip().upper()
    if verdict not in VALID_VERDICTS:
        raise AgentError(agent, f"verdict={payload.get('verdict')!r} is not one of "
                                f"{sorted(VALID_VERDICTS)}")
    quoted = str(payload.get("quoted_code") or "").strip()
    searched = [str(s) for s in (payload.get("searched_for") or [])]
    reason = str(payload.get("reason") or "").strip()

    # THE structural guarantee for this stage.
    if verdict in (PRESENT, PARTIAL) and not quoted:
        raise AgentError(
            agent,
            f"feature {v.feature.id!r} was judged {verdict} without quoting a code "
            f"line. A verdict that something EXISTS must point at the line where "
            f"it exists — otherwise the gap report is the model's recollection of "
            f"the codebase rather than a reading of it.",
        )
    if verdict == ABSENT and not searched:
        raise AgentError(
            agent,
            f"feature {v.feature.id!r} was judged ABSENT with an empty "
            f"searched_for. A claim that something is missing has to name what "
            f"was looked for, or it cannot be checked or reproduced.",
        )
    if quoted:
        # An invented quote is the one failure this stage must not permit: it
        # would look exactly like evidence. Verify it against the actual bytes.
        norm = re.sub(r"\s+", " ", quoted).strip()
        haystacks = ("\n".join(rows) for rows in idx.lines.values())
        if not any(norm in re.sub(r"\s+", " ", h) for h in haystacks):
            raise AgentError(
                agent,
                f"feature {v.feature.id!r}: the quoted line does not appear in any "
                f"indexed source file. Quoted: {quoted[:160]!r}. A fabricated "
                f"quotation is worse than no evidence, because it reads as proof.",
            )

    v.verdict, v.layer, v.reason = verdict, 2, reason
    v.quoted_code, v.searched_for = quoted, searched
    return v


# --------------------------------------------------------------------------
# the cross-check
# --------------------------------------------------------------------------

def _expected_from_claim(status: str) -> str:
    s = (status or "").strip().lower()
    if not s:
        return ""
    if s.startswith("built"):
        return PRESENT
    if s.startswith("unbuilt") or s.startswith("out") or "unbuilt" in s:
        return ABSENT
    return ""


def cross_check(verdicts: list[GapVerdict]) -> list[GapVerdict]:
    """Compare each independent verdict against §3's self-reported status.

    Run AFTER detection, never before. PARTIAL counts as disagreeing with a
    'Built' claim — that is the interesting case, and it is exactly what the
    narrated opening turns out to be.
    """
    for v in verdicts:
        exp = _expected_from_claim(v.feature.gdd_claimed_status)
        v.gdd_expected = exp
        if not exp:
            continue
        if exp == PRESENT:
            v.disagrees_with_gdd = v.verdict != PRESENT
        else:
            v.disagrees_with_gdd = v.verdict == PRESENT
    return verdicts


def disagreements(verdicts: list[GapVerdict]) -> list[GapVerdict]:
    return [v for v in verdicts if v.disagrees_with_gdd]
