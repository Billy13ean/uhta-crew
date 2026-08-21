"""Deterministic format gate — rules F1–F5 of STYLEGUIDE.md.

Runs before the LLM Evaluator on every draft. Findings do not decide the
score; they cap it (spec.DET_SCORE_CAP) and are handed to the Evaluator as
evidence it must fold into its REASON. Code, not judgment — same division of
labor as the A6 register gate.
"""
import re
from . import spec

INTERFACE_WORDS = re.compile(
    r"\b(press|click|button|menu|screen|hud|wasd|keyboard|mouse|hotkey|"
    r"key(s)?\b|stamina bar|tooltip|cursor)\b", re.IGNORECASE)

SPELLED_NUMBERS = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|twenty|thirty|forty|fifty|hundred)\b"
    r"(?=[^.]*\b(sleeps?|ticks?|believers?|factories|followers?|tiles?|"
    r"generations?)\b)", re.IGNORECASE)

FORBIDDEN_NOUNS = re.compile(
    r"\b(mana|xp|karma|morale|sanity|level up|quest|achievement|"
    r"the old gods|the gods)\b", re.IGNORECASE)


def _sentences(line: str) -> int:
    return max(1, len([s for s in re.split(r"[.!?]+", line.strip()) if s.strip()]))


def run_gate(line: str, register: str, item_id: str = "") -> list[dict]:
    """Return a list of findings: {rule, detail}. Empty list = gate clean."""
    findings = []
    line = line.strip()

    # F1 — length
    if register == "A":
        if len(line) > spec.REG_A_MAX_CHARS:
            findings.append({"rule": "F1", "detail":
                f"{len(line)} chars > {spec.REG_A_MAX_CHARS} (Register A)"})
        if len(line.split()) > spec.REG_A_MAX_WORDS:
            findings.append({"rule": "F1", "detail":
                f"{len(line.split())} words > {spec.REG_A_MAX_WORDS} (Register A)"})
    else:
        if len(line) > spec.REG_B_MAX_CHARS:
            findings.append({"rule": "F1", "detail":
                f"{len(line)} chars > {spec.REG_B_MAX_CHARS} (Register B)"})
        if _sentences(line) > spec.REG_B_MAX_SENTENCES:
            findings.append({"rule": "F1", "detail":
                f"{_sentences(line)} sentences > {spec.REG_B_MAX_SENTENCES} (Register B)"})

    # F2 — numerals (digits always; spelled-out only when quantifying sim nouns)
    if re.search(r"\d", line):
        findings.append({"rule": "F2", "detail": "contains digits"})
    m = SPELLED_NUMBERS.search(line)
    if m:
        findings.append({"rule": "F2", "detail":
            f"spelled-out sim quantity: '{m.group(0)}'"})

    # F3 — exclamation marks
    if "!" in line:
        findings.append({"rule": "F3", "detail": "exclamation mark"})

    # F4 — second person in Register B (epilogue-tagged items exempt)
    if register == "B" and item_id != "endscreen-epilogue":
        m = re.search(r"\b(you|your|yours)\b", line, re.IGNORECASE)
        if m:
            findings.append({"rule": "F4", "detail":
                f"second person in Register B: '{m.group(0)}'"})

    # F5 — output shape
    if "\n" in line.strip():
        findings.append({"rule": "F5", "detail": "multiple lines"})
    if line.startswith(("\"", "'", "“", "#", "-", "*")):
        findings.append({"rule": "F5", "detail": "markdown/quote wrapper"})
    if line.rstrip().endswith("..."):
        findings.append({"rule": "F5", "detail": "trailing ellipsis padding"})

    # Deterministic faces of V-rules ride along as evidence (not F-caps —
    # they are reported to the Evaluator, which owns V scoring):
    m = INTERFACE_WORDS.search(line)
    if m:
        findings.append({"rule": "V3", "detail":
            f"interface language: '{m.group(0)}'"})
    m = FORBIDDEN_NOUNS.search(line)
    if m:
        findings.append({"rule": "V1/V2", "detail":
            f"forbidden noun: '{m.group(0)}'"})

    return findings


def caps_score(findings: list[dict]) -> bool:
    """Only F-rules cap the score; V evidence informs the Evaluator."""
    return any(f["rule"].startswith("F") for f in findings)
