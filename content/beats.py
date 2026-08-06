"""The beats this pipeline exists to fill, and the gap each one closes.

Three content types, sixteen beats. None of these is a demonstration topic
invented to show a pipeline working — each names a hole in uhta that the game
cannot ship with, cited to the GDD line that says so.

Every beat carries **two** queries, not one. That is the GDD §4.5 retrieval
rule, and it exists because the first hand-run retrieved only the experience
section and produced lines that would sit unchanged in any god-game about hope
and fear:

    query_mechanic   the consequence — the verb's own §2.2 row, the system that
                     actually fires. This is what makes a line belong to *this*
                     game.
    query_experience what the player is meant to understand or feel at this
                     moment.

`--ab` runs one beat both ways (naive single-query top-1 vs this two-query
union) and has the same Critic judge both sets. That comparison is the Voice
Judgment evidence: the retrieval tweak is measured, not asserted.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Beat:
    id: str
    type: str            # narration | era-flavor | endscreen
    label: str
    brief: str           # what this line has to do
    query_mechanic: str
    query_experience: str

    @property
    def queries(self) -> list[str]:
        return [self.query_mechanic, self.query_experience]


CONTENT_TYPES = {
    "narration": {
        "title": "Teacher narration — the opening cycle",
        "file": "narration-lines.md",
        "gap": (
            "uhta is wordless after the first dawn, and the one narrated cycle "
            "has never been written. GDD §2.8 criteria 1 and 3 are **Blocked** on "
            "exactly this: a stranger cannot reach their first Sleep without being "
            "told what the keys do, and cannot name the two things they can make "
            "people feel. §2.7 lists the narrated opening as NICE #1 and as the "
            "only unbuilt item that currently blocks the Definition of Playable. "
            "This is not thin content — it is absent content on the critical path."
        ),
        "register": (
            "Short, declarative, second person. Names the verb and states its "
            "consequence. Instrumentation, not lore — §2.5: 'short declarative "
            "lines, no mythology'."
        ),
    },
    "era-flavor": {
        "title": "Era and settlement flavor — the three eras",
        "file": "era-flavor.md",
        "gap": (
            "GDD §2.3 locks the division of labor — 'landscape tint communicates "
            "feeling; era art communicates time' — and §2.6 ships era progression "
            "(Nomad/Tribal → Village → Victorian at sleeps 6 and 14) as built. The "
            "art exists; the words that tell an art pass what a settlement in each "
            "era *is* do not. §4.5 names 'era-transition and settlement flavor "
            "across three eras' as one of the three content gaps. Without it the "
            "eras are dress changes with no stated meaning."
        ),
        "register": (
            "Third person, present tense, concrete and physical. Describes what "
            "is visible in the world, never what it symbolises. No numbers."
        ),
    },
    "endscreen": {
        "title": "Endscreen candidates",
        "file": "endscreen-candidates.md",
        "gap": (
            "GDD §6 carries the endscreen as an **open question the Director has "
            "not ruled on**: can the outcome be delivered wordlessly, with a text "
            "card demoted to a post-image epilogue, and does the teacher's voice "
            "return once at the very end? §2.7 lists the wordless endscreen as "
            "NICE #2. The run currently ends on a readout. These are candidates "
            "for a ruling, and are marked UNRULED throughout."
        ),
        "register": (
            "The teacher's voice returning once, after a whole game of silence. "
            "Short. States what the player did, not what it means."
        ),
    },
}

_EXP_OPENING = (
    "first cycle tutorial disguised as myth teacher narrator speaks names each "
    "verb as first used states consequence plainly short declarative no mythology "
    "cave white flame two paths shadows"
)
_EXP_WAKE = (
    "waking emotional centerpiece generation passed world moved on its own "
    "landscape same but different roads harden tribes built land turned"
)
_EXP_ERA = (
    "waking landscape roads harden tribes stopped wandering and built devotion "
    "reads as architecture land turned green and growing sharp and industrial ash"
)
_EXP_END = (
    "victory your color crossing the whole map until the sky turns defeat grey "
    "closing in player shrunk back into the cave both endings seen coming"
)

BEATS: list[Beat] = [
    # ---------------- narration: the opening cycle (8) ----------------
    Beat("n1", "narration", "The cave — the undetermined flame",
         "The player's first moment. Say what the flame is and that nothing about "
         "it is decided yet. Must not promise that either path is the good one.",
         "player alignment flame Fear red Neutral white Hope green nothing locks "
         "the flame cave choice sets only the starting tint re-tints continuously",
         _EXP_OPENING),

    Beat("n2", "narration", "First Walk — the ground remembers",
         "Names Walk and states its consequence: the tile you cross becomes a road "
         "that carries your color and that people will travel.",
         "Walk stamina per tile every tile walked becomes a compacted road NPCs "
         "traverse faster roads carry your color allegiance leash",
         _EXP_OPENING),

    Beat("n3", "narration", "First Flame — it applies what you feel",
         "Names Raise/wave the flame. The load-bearing fact: it applies the flame's "
         "*current* alignment, so it is not a heal — it is whatever you currently are.",
         "Raise wave the flame clears fog locally applies the flame's current "
         "alignment to NPCs in radius grows with Ascension",
         _EXP_OPENING),

    Beat("n4", "narration", "First Roar — whatever you intend",
         "Names Roar. Must carry the unconditional clause: everyone who witnesses it "
         "is frightened regardless of the flame's color. A line that would read the "
         "same in a Hope run has failed.",
         "Roar shatters a line of tiles NPCs within witness radius take an "
         "unconditional Fear push regardless of flame color out-of-radius free",
         _EXP_OPENING),

    Beat("n5", "narration", "First Wait — inaction is an action",
         "Names Wait. The consequence: withholding teaches the people watching that "
         "you do not matter, and pushes them toward apathy.",
         "Wait do nothing free ends an encounter deliberate non-response witnessed "
         "inaction pushes nearby NPCs toward Apathy no action is neutral",
         _EXP_OPENING),

    Beat("n6", "narration", "The found basin — the beacon that gives strength",
         "Names the discoverable beacon. Consequence: it reveals the region and it "
         "gives the player strength that persists.",
         "light a beacon permanent aura radiates the flame's current color every "
         "generation tick discoverable ruined basin reveal stamina bonus",
         _EXP_OPENING),

    Beat("n7", "narration", "First Sleep — where you lie down matters",
         "Names Sleep. Two consequences: a whole generation passes, and the sleeping "
         "body keeps radiating for every tick of it. Where, not just when.",
         "Sleep ends the cycle advances one generation positional the sleeping body "
         "radiates the flame's emotion over a radius for every tick",
         _EXP_OPENING),

    Beat("n8", "narration", "First waking — and the last words",
         "The final narrated line. A generation has passed and the world moved "
         "without the player. It is also the moment the narration stops for good.",
         "generational sleep time only advances while the player sleeps contagion "
         "resolves tribes wander population grows landscape tint shifts",
         _EXP_WAKE),

    # ---------------- era-settlement flavor (5) ----------------
    Beat("e1", "era-flavor", "Era 1 — Nomad / Tribal",
         "What a settlement looks like in the first era, and what its people wear. "
         "Physical description only; the land itself never ages.",
         "era progression nomad tribal dress hood staffs satchels camps settling "
         "rule walled camp open settlement structures landscape tint feeling",
         _EXP_ERA),

    Beat("e2", "era-flavor", "Transition — Nomad into Village",
         "The moment the world visibly ages for the first time. What changed since "
         "the player last looked, in physical terms.",
         "era progression village sleep thresholds derived from sleep count NPC "
         "dress coif settlement structures villages roads compacted earth paver stone",
         _EXP_WAKE),

    Beat("e3", "era-flavor", "Era 2 — Village",
         "The middle era. Settlements have permanence; the roads the player walked "
         "are now stone.",
         "village era settlement structures roads paver stone after one generation "
         "allegiance colors green Hope red Fear ruins scar tissue",
         _EXP_ERA),

    Beat("e4", "era-flavor", "Transition — Village into Victorian",
         "The second and last visible ageing. Clocktowers and smoking factories "
         "arrive; the people are wearing top hats.",
         "Victorian town clocktowers smoking factories top hat canes garment folds "
         "era art communicates time base land art never ages",
         _EXP_WAKE),

    Beat("e5", "era-flavor", "Ruins — what a burned-out settlement leaves",
         "The forensic image the GDD calls the game's signature: grey people "
         "standing still in the place they built when they believed.",
         "ruins abandoned structures remain scar tissue burned-out settlement grey "
         "people standing still in the place they built when they believed burnout",
         _EXP_ERA),

    # ---------------- endscreen candidates (3) ----------------
    Beat("s1", "endscreen", "Win — the sky turns your color",
         "The unification win. Says what the player did to specific people, not what "
         "it symbolises. UNRULED — a candidate for a Director ruling, not a decision.",
         "win unification threshold contagion-dominant held across a generation no "
         "living opposing zealot player replaces Uhtcearu as the sky",
         _EXP_END),

    Beat("s2", "endscreen", "Loss — the grey closes in",
         "The apathy loss. The thesis line is that your own excess feeds Uhtcearu; "
         "the endscreen has to land that without accusing the player. UNRULED.",
         "loss your actions stop mattering apathy soft grey plus burned passes the "
         "dominance threshold grey retakes the map player shrunk back into the cave",
         _EXP_END),

    Beat("s3", "endscreen", "The teacher returns — one last line",
         "GDD §6: 'the teacher's voice returning once, at the very end, is a "
         "candidate the Director has not ruled on.' This is that candidate. UNRULED.",
         "tone mournful mythic wordless after the first dawn one voice spent in the "
         "first cycle never heard again the silence afterward is itself a statement",
         _EXP_END),
]


def beats_of(kind: str) -> list[Beat]:
    return [b for b in BEATS if b.type == kind]


AB_BEAT_ID = "n4"  # the Roar — the beat the GDD's own worked example uses
