"""A7 spec — the machine half of STYLEGUIDE.md.

Rule IDs here must appear verbatim in STYLEGUIDE.md (asserted at selftest),
so the prose artifact and the enforced spec cannot drift apart silently.
"""
from pathlib import Path
import hashlib

STYLE_DIR = Path(__file__).resolve().parent
GUIDE_PATH = STYLE_DIR / "STYLEGUIDE.md"

RULE_IDS = [
    # tone
    "T1", "T2", "T3", "T4",
    # vocabulary & lore
    "V1", "V2", "V3", "V4",
    # format & length (deterministic)
    "F1", "F2", "F3", "F4", "F5",
]

CONSTRAINT_TYPES = {
    "TONE": ["T1", "T2", "T3", "T4"],
    "VOCAB": ["V1", "V2", "V3", "V4"],
    "FORMAT": ["F1", "F2", "F3", "F4", "F5"],
}

# Deterministic-cap policy (STYLEGUIDE.md §3): any F-finding caps score at:
DET_SCORE_CAP = 6
ACCEPT_SCORE = 9           # accept at 9+ (STYLEGUIDE.md §3): every rule
                           # honored, at most a craft note. 10 = no note at
                           # all. Calibrated after live run a7-live, where a
                           # 10-only bar escalated three gate-clean 8-9/10
                           # lines and tripped the breaker.
MAX_REFINEMENTS = 2        # per item, then ESCALATED  (A6 breaker policy)
ESCALATION_LIMIT = 3       # run trips after this many escalations

# Register limits (F1)
REG_A_MAX_CHARS, REG_A_MAX_WORDS = 120, 24
REG_B_MAX_CHARS, REG_B_MAX_SENTENCES = 160, 2

# ---------------------------------------------------------------------------
# The run's item set.
#
# kind "era"      — genuine content: the named GDD §4.2 gap (three eras).
# kind "sabotage" — the A7 rubric's before/after demos: the generator is
#                   *instructed to produce wrong content* in a named violation
#                   class, so the Evaluator must catch it and the Refiner fix
#                   it with no human in the loop.
# ---------------------------------------------------------------------------
ITEMS = [
    {
        "id": "era-nomad", "kind": "era", "register": "B",
        "brief": ("One flavor line for the Nomad era: scattered grey wanderers, "
                  "camps not yet settled, the fog, the grief-sky. What the world "
                  "is before anyone builds."),
    },
    {
        "id": "era-village", "kind": "era", "register": "B",
        "brief": ("One flavor line for the Village era: tribes have settled and "
                  "built, roads harden from compacted earth toward paver stone, "
                  "allegiance colors the land."),
    },
    {
        "id": "era-victorian", "kind": "era", "register": "B",
        "brief": ("One flavor line for the Victorian era: towns with clocktowers "
                  "and smoking factories, the world aged by what was believed. "
                  "Tone must still be mournful — time passing under a grieving sky."),
    },
    {
        "id": "demo-tone", "kind": "sabotage", "register": "B",
        "violation_class": "TONE",
        "brief": ("Write an EXCITED, TRIUMPHANT announcement celebrating the "
                  "player's amazing new village. Use exclamation marks. Be "
                  "enthusiastic like a mobile-game level-up toast."),
    },
    {
        "id": "demo-vocab", "kind": "sabotage", "register": "B",
        "violation_class": "VOCAB",
        "brief": ("Write a line about the town prospering because the old gods "
                  "are pleased, mentioning the mana the settlers earn and telling "
                  "the player to press E to enter the village."),
    },
    {
        "id": "demo-format", "kind": "sabotage", "register": "B",
        "violation_class": "FORMAT",
        "brief": ("Write a long, detailed, multi-sentence status report about "
                  "the era transition, quoting the exact numbers: 14 sleeps "
                  "elapsed, 3 factories built, 42 believers, addressed to 'you'."),
    },
]


def guide_text() -> str:
    return GUIDE_PATH.read_text(encoding="utf-8")


def guide_sha() -> str:
    return hashlib.sha256(GUIDE_PATH.read_bytes()).hexdigest()[:16]


def guide_integrity() -> list[str]:
    """Every rule ID and every constraint type name must appear in the guide."""
    text = guide_text()
    missing = [rid for rid in RULE_IDS if f"{rid} " not in text and f"{rid}·" not in text
               and f"{rid} ·" not in text and rid + "–" not in text and rid not in text]
    for ct in CONSTRAINT_TYPES:
        if ct not in ("TONE", "VOCAB", "FORMAT"):
            missing.append(ct)
    return missing
