"""Layer 1 of the mini-game Evaluator — the deterministic design gate. No LLM.

A candidate is a design DOCUMENT (JSON), so the gate checks structure and
buildability — the things a schema can decide — before any model judges the
design. Each check is named C1..C6 and traceable to a stated rule:

    C1 SCHEMA          every required field present and non-empty
    C2 VALID-SLOT      encounter/pole match a real slot
    C3 BUILDABLE-INPUT controls ⊆ the slice's actual input vocabulary — a
                       design needing inputs the build does not have cannot
                       be built into it
    C4 REAL-STAKES     outcome effects ⊆ the sim's outcome vocabulary — the
                       RPG-minigame integration rule ('stakes wired to the
                       main loop') made mechanical
    C5 WORDLESS        no interface/text vocabulary in the player-facing
                       fields — GDD: 'no interface, no text, only your body
                       and theirs'
    C6 SHORT           field length caps — an encounter is 'a short,
                       wordless, diegetic exchange', and a design nobody can
                       hold in their head will not be built small enough to
                       finish

This module also carries the slice ANCHOR extraction for the build stage:
three anchored patterns, not a scan (the A5 vendored-Phaser lesson) — the
pure-logic anchor, the self-test anchor, and the hook anchor — plus the
patch post-checks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .spec import ALLOWED_INPUTS, OUTCOME_EFFECTS, SLOT_SPECS

REQUIRED_FIELDS = ["id", "encounter", "pole", "name", "premise", "loop",
                   "signals", "controls", "outcome_win", "outcome_fail",
                   "effects", "why_fun", "pattern_source", "gdd_quote"]

#: Interface/text vocabulary banned from the PLAYER-FACING fields (premise,
#: loop, signals, outcomes). Meta fields (why_fun, pattern_source) may use
#: these words to talk ABOUT the design.
BANNED_UI_TOKENS = [
    "hud", "menu", "text", "label", "labels", "button", "buttons", "prompt",
    "tooltip", "dialog", "dialogue", "caption", "subtitle", "tutorial",
    "score display", "scoreboard", "counter", "meter bar", "progress bar",
    "words", "written", "font", "icon", "arrow indicator", "cursor",
]
_UI_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in BANNED_UI_TOKENS) + r")\b",
    re.IGNORECASE)

MAX_FIELD_WORDS = 130     # per player-facing field
MAX_NAME_CHARS = 48

PLAYER_FACING = ["premise", "loop", "signals", "outcome_win", "outcome_fail"]

_VALID = {(s.encounter, s.pole) for s in SLOT_SPECS}


@dataclass
class Finding:
    source: str      # "deterministic" | "llm"
    check: str
    detail: str
    quoted_chunk: str = ""

    def render(self) -> str:
        chunk = f' — chunk: "{self.quoted_chunk}"' if self.quoted_chunk else ""
        return f"[{self.source}] {self.check}: {self.detail}{chunk}"


_TOKEN_RE_CACHE: dict[tuple, "re.Pattern"] = {}


def _token_re(tokens: list[str]) -> "re.Pattern":
    key = tuple(tokens)
    if key not in _TOKEN_RE_CACHE:
        _TOKEN_RE_CACHE[key] = re.compile(
            r"\b(" + "|".join(re.escape(t) for t in key) + r")\b",
            re.IGNORECASE)
    return _TOKEN_RE_CACHE[key]


def run_design_checks(cand: dict, canon=None) -> list[Finding]:
    # The constants in this module are the authored BASELINE (asserted
    # equal to canon/rules.json in --selftest). The gate enforces the
    # EFFECTIVE canon: an AMENDED vocabulary or cap applies here; a
    # REPEALED check (C5/C6 are repealable) is skipped — and the skip is
    # logged in the run's CANON-IN-FORCE.md, never silent.
    if canon is None:
        from crew.canon import get_canon
        canon = get_canon()
    f: list[Finding] = []

    def _empty(k: str) -> bool:
        v = cand.get(k)
        if isinstance(v, list):
            return len(v) == 0
        return not str(v or "").strip()

    missing = [k for k in REQUIRED_FIELDS if _empty(k)]
    if missing:
        f.append(Finding("deterministic", "C1 SCHEMA",
                         f"missing/empty field(s): {', '.join(missing)}"))
        return f  # nothing downstream is meaningful on a broken schema

    def _slot_norm(v: str) -> str:
        return str(v).strip().lower().replace(" ", "-").replace("_", "-")

    if (_slot_norm(cand["encounter"]), _slot_norm(cand["pole"])) not in _VALID:
        f.append(Finding(
            "deterministic", "C2 VALID-SLOT",
            f"({cand['encounter']!r}, {cand['pole']!r}) is not one of the six "
            f"GDD encounter slots {sorted(_VALID)}"))

    allowed_inputs = canon.param("mg-allowed-inputs", "allowed_inputs",
                                 ALLOWED_INPUTS)
    controls = cand.get("controls") or []
    bad = [c for c in controls if c not in allowed_inputs]
    if not controls or bad:
        f.append(Finding(
            "deterministic", "C3 BUILDABLE-INPUT",
            f"controls {bad or '(none)'} not in the slice's input vocabulary "
            f"{allowed_inputs} — a design this build cannot receive input for "
            f"cannot be built into it"))

    outcome_effects = canon.param("mg-outcome-effects", "outcome_effects",
                                  OUTCOME_EFFECTS)
    effects = cand.get("effects") or []
    bad = [e for e in effects if e not in outcome_effects]
    if not effects or bad:
        f.append(Finding(
            "deterministic", "C4 REAL-STAKES",
            f"effects {bad or '(none)'} not in the sim's outcome vocabulary "
            f"{outcome_effects} — stakes must pay in the main loop's real "
            f"currencies"))

    if canon.enforced("mg-c5-wordless"):
        tokens = canon.param("mg-c5-wordless", "banned_tokens",
                             BANNED_UI_TOKENS)
        ui_re = _token_re(tokens)
        for field in PLAYER_FACING:
            m = ui_re.search(str(cand[field]))
            if m:
                f.append(Finding(
                    "deterministic", "C5 WORDLESS",
                    f"field '{field}' contains interface vocabulary "
                    f"{m.group(0)!r} — 'no interface, no text, only your "
                    f"body and theirs'"))
                break

    if canon.enforced("mg-c6-short"):
        max_name = canon.param("mg-c6-short", "max_name_chars",
                               MAX_NAME_CHARS)
        max_words = canon.param("mg-c6-short", "max_field_words",
                                MAX_FIELD_WORDS)
        if len(str(cand["name"])) > max_name:
            f.append(Finding("deterministic", "C6 SHORT",
                             f"name is {len(str(cand['name']))} chars "
                             f"(cap {max_name})"))
        else:
            for field in PLAYER_FACING:
                n = len(str(cand[field]).split())
                if n > max_words:
                    f.append(Finding(
                        "deterministic", "C6 SHORT",
                        f"field '{field}' is {n} words (cap {max_words}) — "
                        f"'a short, wordless, diegetic exchange'"))
                    break

    return f


# ---------------------------------------------------------------------------
# Build-stage anchors and patch post-checks (the A5 contract, three anchors)
# ---------------------------------------------------------------------------

#: Anchored patterns, not a scan: each is a line known to exist exactly once
#: in the authored code (asserted by --selftest against the real build).
#: Contract v3 has FIVE anchors. The frame and input anchors exist because
#: of the second Director playtest: a three-anchor patch had no seat in the
#: per-frame loop, so the generated encounter could only advance one tick
#: per verb click — mechanically alive, perceptually nonexistent.
LOGIC_ANCHOR_RE = re.compile(
    r"function teachingFor\(verb,sleep_no,spoken\)\{[^\n]*\}")
SELFTEST_ANCHOR_RE = re.compile(
    r"  out\.push\(\['G5 road allegiance erodes enemy crossing'[^\n]*\);")
HOOK_ANCHOR_RE = re.compile(
    r"    else SIM\.act\(kind,SIM\.player_pos\.slice\(\),SIM\.player_pole,cost\);")
#: Inside drawWorld(), immediately after the per-frame graphics clears —
#: code inserted here runs EVERY FRAME, with `this.overlay` (an existing
#: Graphics object, just cleared) available to draw into. No object leaks.
FRAME_ANCHOR_RE = re.compile(re.escape(
    "    const g=this.world; g.clear(); this.ui.clear(); "
    "this.overlay.clear(); this.poolN=0; this.terrN=0; this.pool32N=0;"))
#: The first line of onClick — an early-return guard here lets the encounter
#: OWN the pointer while it is active, so feeding the flame does not also
#: fire the Flame verb.
INPUT_ANCHOR_RE = re.compile(re.escape("  onClick(p){"))

G_ASSERT_RE = re.compile(r"\['(G\d+)")

ANCHOR_NAMES = ("logic", "frame", "input", "selftest", "hook")


class BuildAnchorError(RuntimeError):
    pass


def extract_anchors(html: str) -> dict[str, str]:
    """The five anchor lines, verbatim from the real build. Each must occur
    exactly once — an ambiguous anchor is a patch applied somewhere you did
    not look."""
    out: dict[str, str] = {}
    for name, rx in (("logic", LOGIC_ANCHOR_RE),
                     ("frame", FRAME_ANCHOR_RE),
                     ("input", INPUT_ANCHOR_RE),
                     ("selftest", SELFTEST_ANCHOR_RE),
                     ("hook", HOOK_ANCHOR_RE)):
        hits = rx.findall(html)
        if len(hits) != 1:
            raise BuildAnchorError(
                f"{name} anchor matched {len(hits)} time(s) (need exactly 1). "
                f"The build has drifted from what this pipeline was verified "
                f"against — re-run --selftest and update checks.py.")
        out[name] = hits[0]
    return out


def brace_balanced(code: str) -> bool:
    """Fallback parse sanity when node is unavailable: braces/brackets/parens
    balance outside of strings. Not a parser, and labelled as such wherever
    its verdict is recorded."""
    depth = {"{": 0, "[": 0, "(": 0}
    close = {"}": "{", "]": "[", ")": "("}
    in_str: str | None = None
    comment: str | None = None   # "line" | "block"
    esc = False
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        if comment == "line":
            if ch == "\n":
                comment = None
            i += 1
            continue
        if comment == "block":
            if ch == "*" and i + 1 < n and code[i + 1] == "/":
                comment = None
                i += 2
                continue
            i += 1
            continue
        if esc:
            esc = False
            i += 1
            continue
        if in_str:
            if ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue
        if ch == "/" and i + 1 < n and code[i + 1] in "/*":
            comment = "line" if code[i + 1] == "/" else "block"
            i += 2
            continue
        if ch in "'\"`":
            in_str = ch
        elif ch in depth:
            depth[ch] += 1
        elif ch in close:
            depth[close[ch]] -= 1
            if depth[close[ch]] < 0:
                return False
        i += 1
    return not in_str and comment != "block" \
        and all(v == 0 for v in depth.values())


def apply_patch(html: str, anchors: dict[str, str],
                blocks: dict[str, str]) -> str:
    """Insert each block immediately after its named anchor. Caller runs
    check_patch() on the result before anything is written."""
    out = html
    for name in ANCHOR_NAMES:
        if name not in blocks:
            continue
        block = str(blocks[name]).rstrip("\n")
        out = out.replace(anchors[name], anchors[name] + "\n" + block, 1)
    return out


def check_patch(original: str, patched: str) -> dict[str, bool]:
    checks = {
        "all_preexisting_assertions_survive":
            G_ASSERT_RE.findall(original) == G_ASSERT_RE.findall(patched),
        "adds_at_least_one_M_assertion":
            bool(re.search(r"\['M\d+", patched))
            and not re.search(r"\['M\d+", original),
        "grew": len(patched) > len(original),
    }
    return checks
