"""The six encounter slots (three types x two poles), and the rules.

Each brief quotes the GDD v0.9.9 §2 encounter table's own design intent for
that slot — the Generator elaborates a buildable mini-game from it, it does
not invent the slot. Three retrieval queries per brief (an extension of the
§4.5 two-chunk rule): the encounter design itself, the supporting mechanics,
and a mini-game pattern from the seeded research corpus.
"""
from __future__ import annotations

from dataclasses import dataclass

#: The rule the Evaluator enforces, quoted from GDD v0.9.9 §2 (Encounters):
ENCOUNTER_RULES = (
    "GDD §2, Encounters: when you meet a group directly the simulation pauses "
    "and you play a short, wordless, diegetic exchange — 'no interface, no "
    "text, only your body and theirs'. 'This is the only time you act on "
    "individuals rather than a population', and 'the two poles never play the "
    "same game': Hope plays patience, depth, few (converts arrive devout); "
    "Fear plays speed, force, many (converts are shallow). A design that "
    "needs a HUD, a label, or a word has failed; a design whose Hope and "
    "Fear versions are the same game reskinned has failed."
)

#: The only inputs the slice has. A design that needs anything else cannot be
#: built into this build and fails deterministically (checks.py C3).
ALLOWED_INPUTS = ["wasd-move", "mouse-move", "left-click", "right-click",
                  "space", "e-key"]

#: The outcome vocabulary — every effect a mini-game may pay out in, each an
#: existing notion in the sim. A design paying in a currency the game does
#: not have fails deterministically (checks.py C4). This is the RPG-minigame
#: integration principle ('stakes wired to the main loop') made mechanical.
OUTCOME_EFFECTS = ["convert_devout", "convert_shallow", "burnout",
                   "drift_apathy", "stamina_gain", "stamina_loss",
                   "resistance_drop", "story_spreads", "no_effect"]


@dataclass
class SlotSpec:
    id: str              # e.g. "first-contact-hope"
    encounter: str       # first-contact | vigil | holding
    pole: str            # hope | fear
    label: str
    brief: str           # the GDD's own design intent for this slot, quoted
    query_encounter: str
    query_mechanics: str
    query_pattern: str

    @property
    def queries(self) -> list[str]:
        return [self.query_encounter, self.query_mechanics, self.query_pattern]


_Q_ENC_FIRST = ("first contact unaligned nomad band encounter simulation "
                "pauses wordless diegetic exchange no interface only your "
                "body and theirs individuals")
_Q_ENC_VIGIL = ("the vigil moment of Sleep every generation believers hang "
                "in the dark encounter wordless diegetic")
_Q_ENC_HOLD = ("the holding pressing a rooted settlement eras encounter "
               "roads resistance wordless diegetic")

SLOT_SPECS: list[SlotSpec] = [
    SlotSpec(
        "first-contact-hope", "first-contact", "hope",
        "First contact — Hope: steady the flame",
        "GDD: 'They approach in a wavering ring and commit only if the flame "
        "is steady when they arrive. Too bright and they break; too dim and "
        "they drift. The correct move is usually to do less. Few converts, "
        "and they arrive already devout.'",
        _Q_ENC_FIRST,
        "flame current alignment burnout break too much same pressure "
        "converts devout tentative bands",
        "threshold fight steady hold continuous quantity band too hard "
        "snaps ease off slips do less"),
    SlotSpec(
        "first-contact-fear", "first-contact", "fear",
        "First contact — Fear: the scatter",
        "GDD: 'You roar, the band breaks, and you have a handful of strides "
        "to cut off the runners. Everyone you head off turns; everyone who "
        "escapes carries the story outward. Many converts, every one of them "
        "shallow.'",
        _Q_ENC_FIRST,
        "Roar unconditional Fear push witnesses shallow converts story "
        "spreads outward nomad band scatter",
        "interception cutoff chase geometry escape lines cannot catch "
        "everyone runners"),
    SlotSpec(
        "vigil-hope", "vigil", "hope",
        "The vigil — Hope: the weaving",
        "GDD: 'Your believers hang in the dark and you trace lines between "
        "them with your last stamina. Completed chains become channels "
        "belief travels while you are gone; longer chains reach further and "
        "are harder to hold.'",
        _Q_ENC_VIGIL,
        "Sleep generation passes sleeping body radiates contagion channels "
        "belief travels stamina last",
        "path tracing drawn line constraint speed turn limits line is the "
        "artifact longer harder"),
    SlotSpec(
        "vigil-fear", "vigil", "fear",
        "The vigil — Fear: the watch",
        "GDD: 'Your believers are points of light and the dark presses in. "
        "You shield what you can and you cannot shield everything. Fear's "
        "version is triage — choosing who to abandon before dawn.'",
        _Q_ENC_VIGIL,
        "grief front grey drift apathy unshepherded believers stall "
        "shepherded stand sleeps dark",
        "triage protect what you can guaranteed loss allocation attention "
        "choosing what to lose"),
    SlotSpec(
        "holding-hope", "holding", "hope",
        "The holding — Hope: the procession",
        "GDD: 'Roads are the only way in. Converts fall in behind you as you "
        "walk and the line breaks if you move too fast or turn too sharply; "
        "whoever is still with you at the heart converts a resident.'",
        _Q_ENC_HOLD,
        "roads carry your color allegiance rooted tribe resists except "
        "along your own roads settlement",
        "procession follow the leader escort line intact too fast too "
        "sharply tail detaches leader discipline"),
    SlotSpec(
        "holding-fear", "holding", "fear",
        "The holding — Fear: the breaking",
        "GDD: 'Resistance shows as a ring. Strike where it is thinnest — but "
        "each strike hardens the arc beside it, so winning means finding the "
        "collapsing sequence before your stamina runs out.'",
        _Q_ENC_HOLD,
        "Raze fear spike settlement resistance stamina budget faction "
        "fights breaks opponents burnout",
        "weak point sequencing collapsing order strike hardens neighbours "
        "order of strikes resources"),
]

SLOT_IDS = [s.id for s in SLOT_SPECS]


def spec_for(slot_id: str) -> SlotSpec:
    for s in SLOT_SPECS:
        if s.id == slot_id:
            return s
    raise KeyError(f"no SlotSpec for {slot_id!r} — known: {SLOT_IDS}")
