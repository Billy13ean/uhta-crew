"""style_gate.py — the uhta style guide, applied to every line the DM writes.

Carried over from the A7 Style Guide Agent (style/STYLEGUIDE.md): the rules
that can be checked by code are checked by code, before anyone reads the
prose. Findings are returned, never silently fixed; the DM gets one retry
with the findings quoted, and if it still fails the turn ships with the
findings attached so the log is honest about it.

Rules enforced here (IDs match the style guide):
  F2  no numerals in game text — digits, and spelled-out counts of sim values
  F3  no exclamation marks (the deterministic face of T1, mournful restraint)
  V1  canonical proper nouns only — the god is Uhtcearu, never "the gods"
  V2  the emotion vocabulary is closed — no mana / XP / karma / morale / sanity
  V3  no interface language — press, click, menu, HUD, key names
  Z1  the word "zealot" is never written in the story (Director, 2026-08-21)
  F1  length: narration <= 190 words (POLICY for a DM turn; the guide's
      Register B limit is per line, a DM turn is a paragraph or two)
Register note: Register B forbids second person, but a Dungeon Master
addresses the player. sonder's prose is ruled (by the Director, 2026-08-21)
as "people may speak; the teacher's 'you' is allowed" — so F4 is NOT applied.
Consistency (not a style rule, but checked here because it is the same
shape): nobody who is absent, burned or dead may be quoted speaking.
"""
from __future__ import annotations

import re

from . import cast as _cast

MAX_WORDS = 240   # live calibration 2026-08-21: with the press the model lands 210-260; the prompt asks for 150, hard 200

FORBIDDEN_NOUNS = {
    "V1": [r"\bthe (old )?gods\b", r"\bpantheon\b", r"\bgoddess\b", r"\bthe god of\b"],
    "V2": [r"\bmana\b", r"\bxp\b", r"\bexperience points?\b", r"\bkarma\b",
           r"\balignment points?\b", r"\bmorale\b", r"\bsanity\b", r"\bhit points?\b",
           r"\bhp\b", r"\bstamina\b", r"\blevel(led|ed)? up\b", r"\bquest\b",
           r"\binventory\b"],
    "Z1": [r"\bzealots?\b"],   # Director's rule 2026-08-21: their actions tell what they are
    "V3": [r"\bpress\b", r"\bclick\b", r"\bbutton\b", r"\bmenu\b", r"\bscreen\b",
           r"\bhud\b", r"\bwasd\b", r"\bkeyboard\b", r"\btype\s+['\"]?/", r"\bcommand\b",
           r"\bstat(s|istics)?\b", r"\bledger\b", r"\bturn \d+\b"],
}

SPELLED = r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty|thirty|forty|fifty|hundred)\s+(sleeps?|generations?|steps?|points?|turns?|believers?|converts?|followers?|tribes?|factories|towns?)\b"


def run_gate(text: str) -> list[dict]:
    f = []
    if re.search(r"\d", text):
        f.append({"rule": "F2", "detail": "digits: " + ", ".join(sorted(set(re.findall(r"\d+", text)))[:5])})
    m = re.search(SPELLED, text, re.I)
    if m:
        f.append({"rule": "F2", "detail": f"spelled-out sim quantity: '{m.group(0)}'"})
    if "!" in text:
        f.append({"rule": "F3", "detail": "exclamation mark"})
    for rule, pats in FORBIDDEN_NOUNS.items():
        for p in pats:
            m = re.search(p, text, re.I)
            if m:
                f.append({"rule": rule, "detail": f"'{m.group(0)}'"})
    words = len(text.split())
    if words > MAX_WORDS:
        f.append({"rule": "F1", "detail": f"{words} words > {MAX_WORDS}"})
    return f


def press_gate(text: str) -> list[dict]:
    """S1 — every section ends on something to react to: the last sentence is a question or a demand."""
    t = text.rstrip().rstrip('"”\'’')
    if t.endswith("?"):
        return []
    last = re.split(r"(?<=[.?!])\s+", t)[-1] if t else ""
    if re.search(r"\b(tell|say|choose|decide|come|stay|go|give|answer|swear|look at me|with us|or not)\b", last, re.I) and len(last.split()) <= 18:
        return []
    return [{"rule": "S1", "detail": "the turn does not end on a press — no question or demand put to the player in the last sentence"}]


def consistency_gate(text: str, ledger: dict) -> list[dict]:
    """Absent or burned people do not speak. Departed people are not 'here'."""
    f = []
    for pid, n in ledger["band"].items():
        name = n["name"]
        speaks = re.search(
            rf"({name}\s+(says?|said|asks?|asked|whispers?|whispered|answers?|answered|calls?|called|mutters?|muttered|sings?|sang|tells?|told|laughs?|laughed|shouts?|shouted|replies|replied)\b"
            rf"|[“\"][^”\"]{{2,}}[”\"],?\s+{name}\s+(says?|said|asks?|asked|whispers?|whispered|answers?|answered)\b)",
            text)
        if speaks and (not n["present"] or not n["alive"]):
            f.append({"rule": "CONSISTENCY", "detail": f"{name} is quoted speaking but is not here ({n.get('where') or 'gone'})"})
        if speaks and n["burned"]:
            f.append({"rule": "CONSISTENCY", "detail": f"{name} is quoted speaking but is burned — the burned are frozen and do not speak"})
        if not n["present"] and re.search(rf"{name}\s+(is|stands|sits|kneels)\s+(here|beside|next to|with you)", text):
            f.append({"rule": "CONSISTENCY", "detail": f"{name} is described as present but left ({n.get('where')})"})
    P = ledger["player"]
    if P["burned"] and re.search(r"\byou (say|said|ask|asked|whisper|shout|tell|told)\b", text):
        f.append({"rule": "CONSISTENCY", "detail": "you are burned and frozen; you do not speak"})
    return f


def findings_text(findings: list[dict]) -> str:
    return "\n".join(f"- {x['rule']}: {x['detail']}" for x in findings)


def second_person(text: str) -> list[dict]:
    """F4 — for the telling only: Register B, no 'you', no 'I'."""
    f = []
    m = re.search(r"\b(you|your|yours|yourself)\b", text, re.I)
    if m:
        f.append({"rule": "F4", "detail": f"second person in a Register B telling: '{m.group(0)}'"})
    m = re.search(r"\b(I|I'm|I've|my|mine|we|our)\b", text)
    if m:
        f.append({"rule": "F4", "detail": f"first person in a Register B telling: '{m.group(0)}'"})
    return f


def _first(name: str) -> str:
    return name.split()[0].lower()


def heirloom_gate(text: str, L: dict, gave_line: str | None = None) -> list[dict]:
    """L1 (Director, 2026-08-23): the objects are locked to their lines.

    Precision pass 2026-08-24, after the first live session produced four false
    positives against prose that was in fact correct:
      * marks match on WORD BOUNDARIES ('spear' no longer fires inside the
        surname 'Spearing');
      * if the object's LEGITIMATE holder is named anywhere in the window, the
        mention PASSES — a nearer pronoun or bystander name is not a claim of
        ownership when the true carrier is right there in the sentence;
      * the window is ±160 chars (holders are often a clause away);
      * on the turn an object is handed on (gave_line), the GIVER's hands are
        still legal for that object — the prose of a handover rightly shows it
        leaving them, while the ledger already shows the receiver.
    A finding now means: a non-holder is named near the object and its real
    carrier is nowhere in the passage. That is the interchange the rule exists
    to stop. Findings feed the same review-before-post loop, right holder named."""
    P = L["player"]
    everyone = [("you", P)] + list(L["band"].items())
    # who legitimately holds each line's object RIGHT NOW
    holders: dict[str, set[str]] = {}
    for line in _cast.HEIRLOOM_MARKS:
        hs = set()
        for pid, person in everyone:
            own = (person.get("heirloom") or "").lower()
            carried = " ".join(person.get("carried") or []).lower()
            marks = _cast.HEIRLOOM_MARKS[line]
            if any(m in own for m in marks) or any(m in carried for m in marks):
                hs.add(_first(person["name"]))
                if pid == "you":
                    hs.update({"you", "your", "yours"})
        if gave_line == line:                      # handover turn: the giver's hands are still legal
            hs.add(_first(P["name"])); hs.update({"you", "your", "yours"})
        holders[line] = hs
    all_names = {_first(per["name"]) for _, per in everyone} | {"you", "your", "yours"}
    low = text.lower()
    findings: list[dict] = []
    flagged = set()
    for line, marks in _cast.HEIRLOOM_MARKS.items():
        for mark in marks:
            for m in re.finditer(r"\b" + re.escape(mark) + r"\b", low):
                lo, hi = max(0, m.start() - 160), min(len(low), m.end() + 160)
                window = low[lo:hi]
                names_here = {nm for nm in all_names
                              if re.search(r"\b" + re.escape(nm) + r"\b", window)}
                if not names_here:
                    continue                       # scenery — no hands claimed
                if names_here & holders.get(line, set()):
                    continue                       # the true carrier is in the passage — right hands
                best = sorted(names_here)[0]
                key = (line, best)
                if key in flagged:
                    continue
                flagged.add(key)
                rightful = ", ".join(sorted(h for h in holders.get(line, set()) if h not in {"you", "your", "yours"})) or "nobody (it was given away or is gone)"
                findings.append({"rule": "L1", "detail":
                    f"'{mark}' is {line}'s line's object and the ledger puts it in {rightful}'s hands — "
                    f"the prose puts it nearest to '{best}'. Objects are locked to their lines; "
                    f"re-narrate with each object in its own carrier's hands."})
    return findings
