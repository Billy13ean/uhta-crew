"""The seven verbs, and what each verb's line must do.

One spec per key in the build's `TEACHING_TEXT` const — the target is the
mechanism A5 shipped, so the verb list IS the build's verb list, asserted
against the real file in --selftest. Six of the seven reuse the A4 narration
beats' two-query retrieval pairs verbatim (content/beats.py n2–n7); Raze is
new, because A4 had no raze beat — the mechanism A5 built covers all seven
verbs and the content pipeline only ever wrote six of them. That mismatch is
itself a finding this pipeline exists to close.

Every query pair follows the GDD §4.5 two-chunk rule: one query for the
mechanical consequence (the verb's own §2.2 row), one for the experience.
"""
from __future__ import annotations

from dataclasses import dataclass

#: The register rule the Evaluator enforces, quoted from the corpus the
#: Writer is grounded in (GDD §2.5, restated as A4's narration register):
#: "Short, declarative, second person. Names the verb and states its
#: consequence. Instrumentation, not lore — 'short declarative lines, no
#: mythology'." Plus §2.3's display rule: the player never sees a number.
REGISTER = (
    "Short, declarative, second person. Names the verb and states its "
    "consequence. Instrumentation, not lore — GDD §2.5: 'short declarative "
    "lines, no mythology'. No interface language: this is a wordless game's "
    "one narrated cycle, not a tutorial overlay — the narrator names what "
    "the being DOES, never which key the player presses. No numbers (§2.3, "
    "banded display)."
)

_EXP_OPENING = (
    "first cycle tutorial disguised as myth teacher narrator speaks names each "
    "verb as first used states consequence plainly short declarative no mythology "
    "cave white flame two paths shadows"
)
_EXP_WAKE = (
    "waking emotional centerpiece generation passed world moved on its own "
    "landscape same but different roads harden tribes built land turned"
)


@dataclass
class VerbSpec:
    verb: str            # the TEACHING_TEXT key in the build
    label: str
    brief: str           # what this line has to do (the Generator's contract)
    query_mechanic: str  # the verb's own §2.2 row / the system that fires
    query_experience: str

    @property
    def queries(self) -> list[str]:
        return [self.query_mechanic, self.query_experience]


VERB_SPECS: list[VerbSpec] = [
    VerbSpec(
        "walk", "Walk — the ground remembers",
        "Names Walk and states its consequence: the tile you cross becomes a "
        "road that carries your color and that people will travel.",
        "Walk stamina per tile every tile walked becomes a compacted road NPCs "
        "traverse faster roads carry your color allegiance leash",
        _EXP_OPENING),
    VerbSpec(
        "flame", "Flame — it applies what you feel",
        "Names the flame. The load-bearing fact: it applies the flame's "
        "*current* alignment, so it is not a heal — it is whatever you "
        "currently are.",
        "Raise wave the flame clears fog locally applies the flame's current "
        "alignment to NPCs in radius grows with Ascension",
        _EXP_OPENING),
    VerbSpec(
        "roar", "Roar — whatever you intend",
        "Names Roar. Must carry the unconditional clause: everyone who "
        "witnesses it is frightened regardless of the flame's color. A line "
        "that would read the same in a Hope run has failed.",
        "Roar shatters a line of tiles NPCs within witness radius take an "
        "unconditional Fear push regardless of flame color out-of-radius free",
        _EXP_OPENING),
    VerbSpec(
        "wait", "Wait — inaction is an action",
        "Names Wait. The consequence: withholding teaches the people watching "
        "that you do not matter, and pushes them toward apathy.",
        "Wait do nothing free ends an encounter deliberate non-response witnessed "
        "inaction pushes nearby NPCs toward Apathy no action is neutral",
        _EXP_OPENING),
    VerbSpec(
        "beacon", "Beacon — the light that works without you",
        "Names the beacon. Consequence: a permanent aura that radiates the "
        "flame's color every generation, even while you sleep.",
        "light a beacon permanent aura radiates the flame's current color every "
        "generation tick discoverable ruined basin reveal stamina bonus",
        _EXP_OPENING),
    VerbSpec(
        "raze", "Raze — Fear's hammer",
        "Names Raze. Consequence per its §2.2 row: it destroys a settlement, "
        "forcibly unsettles the tribe, and pushes a massive Fear spike onto "
        "witnesses. It is Fear's hammer — a line that reads gentle has failed.",
        "Raze destroys a settlement forcibly unsettles the tribe massive Fear "
        "spike onto witnesses Fear's hammer against entrenchment cost scales "
        "with devotion",
        _EXP_OPENING),
    VerbSpec(
        "sleep", "Sleep — where you lie down matters",
        "Names Sleep. Two consequences: a whole generation passes, and the "
        "sleeping body keeps radiating for every tick of it. Where, not just "
        "when.",
        "Sleep ends the cycle advances one generation positional the sleeping body "
        "radiates the flame's emotion over a radius for every tick",
        _EXP_WAKE),
]

VERBS = [s.verb for s in VERB_SPECS]


def spec_for(verb: str) -> VerbSpec:
    for s in VERB_SPECS:
        if s.verb == verb:
            return s
    raise KeyError(f"no VerbSpec for {verb!r} — known: {VERBS}")
