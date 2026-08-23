"""cast.py — three snapshots in time, one bloodline each way.

Director's rules (2026-08-21): a run never shifts era — it is a snapshot. The
era is rolled at the start (one of three). The player does not choose who they
are; they are dealt one of the cast and replay hoping to be dealt the same
person again. Later casts are DESCENDANTS of the six nomads, and each carries
a habit that repeats in the new context — the callback is for the perceptive
player to notice, never for the narrator to announce.

Six lines, one habit each:
  ila    — thins the water and tells no one the source is failing
  wystan — remembers what was before the grief, and has stopped saying so
  brand  — the broken weapon, broken on a person; a brother saw
  hild   — the mother's song under the breath; the mother went up to the red
  oswy   — goes to look at the Red Standing One, closer than anyone knows
  tate   — unclaimed; saw the tall one first and was not believed

Each entry: id (unique per era), line (ancestor id), name, role, emotion,
private (their secret), habit (the callback, for the narrator's eyes only),
trusts/doubts (another id in the same cast).
"""
from __future__ import annotations

ERAS = ["nomad camps", "villages", "Victorian towns"]

# where the two Standing Ones stand, dressed for the era (they themselves never change)
PLACES = {
    "nomad camps":     {"camp": "the dry fork below the ridge", "red": "the ridge camp",   "green": "the low marsh",
                        "structures": "lean-tos", "road": "packed earth", "water": "the skins"},
    "villages":        {"camp": "the fork village, under the ridge", "red": "the ridge shrine", "green": "the marsh hall",
                        "structures": "houses", "road": "cobbles", "water": "the well"},
    "Victorian towns": {"camp": "Fork Town, under the ridge works", "red": "the ridge works", "green": "the marsh gardens",
                        "structures": "mill sheds", "road": "paver stone", "water": "the reservoir"},
}

CASTS = {
    "nomad camps": {
        "ila":    {"line": "ila",    "name": "Ila",    "role": "carries the water skins",            "emotion": 1,
                   "private": "Ila has been watering the skins down for days and has told no one the spring is failing.",
                   "habit": "thins what everyone drinks and carries the failing source alone",
                   "trusts": "tate", "doubts": "brand"},
        "wystan": {"line": "wystan", "name": "Wystan", "role": "the eldest; remembers a river",       "emotion": -2,
                   "private": "Wystan remembers the sky before it was grief, and has stopped saying so because nobody believes him.",
                   "habit": "remembers what was before and has given up saying it",
                   "trusts": "hild", "doubts": "oswy"},
        "brand":  {"line": "brand",  "name": "Brand",  "role": "the hunter with the cracked spear",   "emotion": -4,
                   "private": "Brand cracked the spear on a man from the ridge camp, not on an animal. Oswy saw.",
                   "habit": "a broken weapon, broken on a person, and a brother who saw",
                   "trusts": "oswy", "doubts": "wystan"},
        "hild":   {"line": "hild",   "name": "Hild",   "role": "sings under her breath when afraid",  "emotion": 2,
                   "private": "Hild's song is her mother's, and her mother walked into the ridge camp a year ago and did not come back.",
                   "habit": "the mother's song under the breath; the mother went up to the red",
                   "trusts": "wystan", "doubts": "brand"},
        "oswy":   {"line": "oswy",   "name": "Oswy",   "role": "Brand's brother; watches the ridge",  "emotion": 0,
                   "private": "Oswy has seen the Red Standing One up close and has been going back to look.",
                   "habit": "goes up to look at the Red Standing One, closer than anyone knows",
                   "trusts": "brand", "doubts": "ila"},
        "tate":   {"line": "tate",   "name": "Tate",   "role": "the child nobody claims",             "emotion": 0,
                   "private": "Tate was the first to see the tall one, three nights ago, and was not believed.",
                   "habit": "unclaimed; saw the tall one first and was not believed",
                   "trusts": "ila", "doubts": "oswy"},
    },
    "villages": {
        "ilse":   {"line": "ila",    "name": "Ilse",   "role": "keeps the well",                       "emotion": 1,
                   "private": "Ilse has been drawing the well-ration short for a month and has told no one the water is going bitter at the bottom.",
                   "habit": "thins what everyone drinks and carries the failing source alone",
                   "trusts": "teg", "doubts": "bram"},
        "wyn":    {"line": "wystan", "name": "Wyn",    "role": "the old one; keeps a story of a river", "emotion": -2,
                   "private": "Wyn's grandmother's story had a river in it and a sky that was not this one, and Wyn has stopped telling it because the children laugh.",
                   "habit": "remembers what was before and has given up saying it",
                   "trusts": "hedda", "doubts": "osric"},
        "bram":   {"line": "brand",  "name": "Bram",   "role": "the smith with the split hammer",      "emotion": -4,
                   "private": "Bram split the hammer on a man from the ridge shrine who came down to preach, not on iron. Osric saw.",
                   "habit": "a broken weapon, broken on a person, and a brother who saw",
                   "trusts": "osric", "doubts": "wyn"},
        "hedda":  {"line": "hild",   "name": "Hedda",  "role": "hums at the loom when afraid",         "emotion": 2,
                   "private": "Hedda's tune is her mother's, and her mother went up to the ridge shrine two winters ago and stayed.",
                   "habit": "the mother's song under the breath; the mother went up to the red",
                   "trusts": "wyn", "doubts": "bram"},
        "osric":  {"line": "oswy",   "name": "Osric",  "role": "Bram's brother; walks the ridge road at night", "emotion": 0,
                   "private": "Osric has stood at the shrine door and looked at the Red Standing One's face, and goes back when the village sleeps.",
                   "habit": "goes up to look at the Red Standing One, closer than anyone knows",
                   "trusts": "bram", "doubts": "ilse"},
        "teg":    {"line": "tate",   "name": "Teg",    "role": "the foundling the well-keeper feeds",   "emotion": 0,
                   "private": "Teg saw the tall one on the ridge three nights ago, before anyone, and was sent to bed for lying.",
                   "habit": "unclaimed; saw the tall one first and was not believed",
                   "trusts": "ilse", "doubts": "osric"},
    },
    "Victorian towns": {
        "ada":    {"line": "ila",    "name": "Ada Waterman",   "role": "clerk at the reservoir works",  "emotion": 1,
                   "private": "Ada has been writing the reservoir level a hand higher than it is for six weeks, and has told no one the intake is silting.",
                   "habit": "thins what everyone drinks and carries the failing source alone",
                   "trusts": "kit", "doubts": "bram_s"},
        "eadwin": {"line": "wystan", "name": "Eadwin Rivers",  "role": "the old lamplighter",           "emotion": -2,
                   "private": "Eadwin's family name is a river that ran where the mill race runs now, and he has stopped telling anyone the sky was once another colour.",
                   "habit": "remembers what was before and has given up saying it",
                   "trusts": "hester", "doubts": "osbert"},
        "bram_s": {"line": "brand",  "name": "Bram Spearing",  "role": "the foreman with the cracked mallet", "emotion": -4,
                   "private": "Bram cracked the mallet on a man from the ridge works who came to the gate, not on a wedge. Osbert saw.",
                   "habit": "a broken weapon, broken on a person, and a brother who saw",
                   "trusts": "osbert", "doubts": "eadwin"},
        "hester": {"line": "hild",   "name": "Hester Singer",  "role": "hums at the loom-line when afraid", "emotion": 2,
                   "private": "Hester's tune is her mother's, and her mother took the ridge tram up to the works one morning and did not take it down.",
                   "habit": "the mother's song under the breath; the mother went up to the red",
                   "trusts": "eadwin", "doubts": "bram_s"},
        "osbert": {"line": "oswy",   "name": "Osbert Spearing", "role": "Bram's brother; the night watchman", "emotion": 0,
                   "private": "Osbert's rounds end at the ridge works gate, where the Red Standing One stands under the lamps, and he has gone in past the gate more than once.",
                   "habit": "goes up to look at the Red Standing One, closer than anyone knows",
                   "trusts": "bram_s", "doubts": "ada"},
        "kit":    {"line": "tate",   "name": "Kit",            "role": "the foundling who sleeps under the clocktower", "emotion": 0,
                   "private": "Kit saw the tall one over the chimneys three nights ago, before anyone, and was cuffed for it.",
                   "habit": "unclaimed; saw the tall one first and was not believed",
                   "trusts": "ada", "doubts": "osbert"},
    },
}


# The heirlooms: one object per bloodline, handed down and re-made for each
# age. Never explained in the prose; a hand goes to it, that is all.
HEIRLOOMS = {
    "ila":    {"nomad camps": "a water skin with a red stitch along the seam",
               "villages": "the well-bucket's handle, wrapped in old leather with a red stitch",
               "Victorian towns": "a leather flask, cracked and re-stitched in red thread"},
    "wystan": {"nomad camps": "a smooth grey river-stone, worn by a river nobody else remembers",
               "villages": "a smooth grey river-stone, kept in a pocket and turned when thinking",
               "Victorian towns": "a smooth grey river-stone on the lamplighter's watch-chain"},
    "brand":  {"nomad camps": "the cracked spear, its head bound with sinew",
               "villages": "the split hammer, its head an old spearhead re-forged",
               "Victorian towns": "the cracked mallet, banded with iron that was once something sharper"},
    "hild":   {"nomad camps": "a bone comb with three teeth missing, her mother's",
               "villages": "a bone comb with three teeth missing, her mother's",
               "Victorian towns": "a bone comb with three teeth missing, worn in the hair at the loom-line"},
    "oswy":   {"nomad camps": "a strip of red cloth taken from the ridge, kept folded small",
               "villages": "a strip of red cloth, faded, sewn inside the collar",
               "Victorian towns": "a strip of red cloth tied round the watchman's lamp handle"},
    "tate":   {"nomad camps": "a white feather found the night the tall one was first seen",
               "villages": "a white feather, kept flat in a fold of cloth",
               "Victorian towns": "a white feather, pressed between two pieces of tin"},
}


# Distinctive, era-independent words for each line's object. Shared by the
# narrator's LOCKED-OBJECTS diagram (story.lineage_note) and the deterministic
# heirloom gate (style_gate.heirloom_gate) — one vocabulary, two enforcers.
# Director ruling 2026-08-23: the objects are locked to their lines; the DM
# had been interchanging them between bloodlines in live play.
HEIRLOOM_MARKS = {
    "ila":    ["water skin", "water-skin", "well-bucket", "bucket", "flask", "red stitch", "re-stitched"],
    "wystan": ["river-stone", "river stone", "grey stone"],
    "brand":  ["spear", "hammer", "mallet"],
    "hild":   ["bone comb", "comb"],
    "oswy":   ["red cloth", "strip of cloth", "strip of red"],
    "tate":   ["feather"],
}


def heirloom(line: str, era: str) -> str:
    return HEIRLOOMS[line][era]


def first_name(name: str) -> str:
    return name.split()[0]


def deal(rng) -> tuple[str, str]:
    """Roll the era and the person. The player does not choose."""
    era = rng.choice(ERAS)
    pid = rng.choice(sorted(CASTS[era]))
    return era, pid
