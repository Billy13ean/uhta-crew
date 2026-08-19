"""Layer 1 of the Evaluator — the deterministic register gate. No LLM.

The rule being enforced is the GDD §2.5 narration register — "short,
declarative, second person. Names the verb and states its consequence …
'short declarative lines, no mythology'" — plus §2.3's display rule (the
player never sees a number) and the wordless-tone corollary that interface
language is a register failure. Everything a regex CAN check is checked here,
for free and reproducibly, before any model is consulted; the LLM layer
(ger/evaluator.py) judges only what a regex cannot — mythology, invented
canon, and consequence fidelity to the retrieved chunks.

The no-UI-language check (R2) is not hypothetical. The shipped build's
`guide()` tutorial text says `press W A S D`, `Left-click`, `press space` —
the exact failure the A5 repo findings (§1) measured against the GDD three
ways. This module also carries the extraction helpers that pull `guide()`'s
strings and the `TEACHING_TEXT` const out of the real build, so the same gate
that judges generated lines can be pointed at the shipped ones. That is the
baseline audit: the evaluator catching, in text that is IN the game today,
the failure it exists to keep out.

Extraction is deliberately narrow — two anchored patterns, not a symbol scan —
because the build vendors the entire minified Phaser bundle on one line and a
broad scan over that file finds anything you ask it for (the A5 SCAN_POLICY
lesson, applied).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ---- the numbers, stated where a reader can check them --------------------

#: "Short" made mechanical. The longest line the Director has shipped in
#: TEACHING_TEXT is 76 characters; A4's PASS-verdict narration candidates top
#: out near 110. The gate is set above both so it rejects paragraphs, not
#: style — the LLM layer still judges "short" as register.
MAX_CHARS = 120
MAX_WORDS = 24

#: Interface vocabulary. Any of these words in a narration line means the
#: narrator is instructing a player at a keyboard instead of naming what the
#: being does — guide()'s register, the one the GDD calls out.
BANNED_UI_TOKENS = [
    "press", "click", "clicked", "left-click", "right-click", "key", "keys",
    "keyboard", "button", "buttons", "mouse", "cursor", "scroll", "wasd",
    "spacebar", "hotkey", "hud", "menu", "drag", "hover", "tap", "interface",
    "tutorial",
]
_UI_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in BANNED_UI_TOKENS) + r")\b",
    re.IGNORECASE,
)
_WASD_SPACED_RE = re.compile(r"\bw\s+a\s+s\s+d\b", re.IGNORECASE)

# Canon: the constants above are the authored BASELINE (asserted equal to
# canon/rules.json in --selftest); at run time the checks read EFFECTIVE
# values through the canon bench (crew/canon.py), so an AMENDED cap or a
# REPEALED R2 takes effect without an edit here — and a repeal is logged in
# the run's CANON-IN-FORCE.md, never silent.
_TOKEN_RE_CACHE: dict[tuple, "re.Pattern"] = {}


def _token_re(tokens: list[str]) -> "re.Pattern":
    key = tuple(tokens)
    if key not in _TOKEN_RE_CACHE:
        _TOKEN_RE_CACHE[key] = re.compile(
            r"\b(" + "|".join(re.escape(t) for t in key) + r")\b",
            re.IGNORECASE)
    return _TOKEN_RE_CACHE[key]


@dataclass
class Finding:
    source: str      # "deterministic" | "llm"
    check: str       # e.g. "R2 NO-UI-LANGUAGE" or an LLM flag class
    detail: str      # what failed, quoting the offending fragment
    quoted_chunk: str = ""   # LLM findings cite the GDD chunk; R-checks cite the rule

    def render(self) -> str:
        chunk = f' — chunk: "{self.quoted_chunk}"' if self.quoted_chunk else ""
        return f"[{self.source}] {self.check}: {self.detail}{chunk}"


# ---- the checks -----------------------------------------------------------

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _words(line: str) -> list[str]:
    return [w for w in re.split(r"\s+", line.strip()) if w]


def run_register_checks(line: str, verb: str | None = None,
                        canon=None) -> list[Finding]:
    """Every deterministic register check, each traceable to the rule text.

    `verb=None` runs only the verb-independent checks — used by the baseline
    audit on guide() strings, which are not per-verb lines.
    """
    if canon is None:
        from crew.canon import get_canon
        canon = get_canon()
    line = strip_html(line)
    findings: list[Finding] = []

    if verb is not None:
        stem = re.compile(r"\b" + re.escape(verb) + r"\w*\b", re.IGNORECASE)
        if not stem.search(line):
            findings.append(Finding(
                "deterministic", "R1 NAMES-VERB",
                f"the line never names its verb '{verb}' — GDD §2.5: 'a "
                f"narrator names each verb the first time you use it'"))

    if canon.enforced("ger-no-ui-language"):
        tokens = canon.param("ger-no-ui-language", "banned_tokens",
                             BANNED_UI_TOKENS)
        ui = _token_re(tokens).search(line) or _WASD_SPACED_RE.search(line)
        if ui:
            findings.append(Finding(
                "deterministic", "R2 NO-UI-LANGUAGE",
                f"interface vocabulary {ui.group(0)!r} — the register is the "
                f"narrator naming what the being does, not which key is "
                f"pressed"))

    if canon.enforced("ger-length-caps"):
        max_chars = canon.param("ger-length-caps", "max_chars", MAX_CHARS)
        max_words = canon.param("ger-length-caps", "max_words", MAX_WORDS)
        if len(line) > max_chars or len(_words(line)) > max_words:
            findings.append(Finding(
                "deterministic", "R3 SHORT",
                f"{len(line)} chars / {len(_words(line))} words exceeds the "
                f"gate ({max_chars} chars / {max_words} words) — §2.5: "
                f"'short declarative lines'"))

    if "?" in line or "!" in line:
        findings.append(Finding(
            "deterministic", "R4 DECLARATIVE",
            f"contains {'?' if '?' in line else '!'} — §2.5: 'short "
            f"DECLARATIVE lines'; the narrator states, never asks or exclaims"))

    if re.search(r"\d", line):
        findings.append(Finding(
            "deterministic", "R5 NO-NUMBERS",
            "contains a digit — §2.3 banded display: the player never sees a "
            "number; say 'everyone who hears you', not a radius"))

    if verb is not None and not re.search(r"\byou\b|\byour\b", line, re.IGNORECASE):
        findings.append(Finding(
            "deterministic", "R6 SECOND-PERSON",
            "no 'you'/'your' — the register is second person: the narrator "
            "speaks to the being about what IT does"))

    return findings


# ---- build extraction (for the baseline audit and the snippet patch) ------

_TEACHING_RE = re.compile(r"const TEACHING_TEXT=\{(.*?)\};", re.DOTALL)
_PAIR_RE = re.compile(r"(\w+):'((?:[^'\\]|\\.)*)'")
_GUIDE_MSG_RE = re.compile(r"msg=`([^`]*)`")


class BuildExtractionError(RuntimeError):
    pass


def extract_teaching_text(html: str) -> dict[str, str]:
    """The build's TEACHING_TEXT const, as {verb: line}. Anchored, not scanned."""
    m = _TEACHING_RE.search(html)
    if not m:
        raise BuildExtractionError(
            "const TEACHING_TEXT={...}; not found in the build. Either the "
            "A5 patch was never applied to this copy of uhta-slice.html, or "
            "the const was renamed. The baseline audit and the snippet patch "
            "both target this anchor.")
    pairs = dict(_PAIR_RE.findall(m.group(1)))
    if not pairs:
        raise BuildExtractionError("TEACHING_TEXT matched but no key:'value' "
                                   "pairs parsed — quoting style changed?")
    return {k: v.replace("\\'", "'") for k, v in pairs.items()}


def extract_guide_strings(html: str) -> list[str]:
    """guide()'s instructional template literals. Filtered to those carrying
    <b> markup, which every guide() message has and nothing in the vendored
    Phaser line does — the narrow-anchor rule again."""
    return [s for s in _GUIDE_MSG_RE.findall(html) if "<b>" in s]


def js_escape(line: str) -> str:
    return line.replace("\\", "\\\\").replace("'", "\\'")


def render_teaching_snippet(lines: dict[str, str], order: list[str]) -> str:
    body = ",".join(f"{v}:'{js_escape(lines[v])}'" for v in order)
    return "const TEACHING_TEXT={" + body + "};"
