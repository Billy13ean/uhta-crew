"""story.py — the loose storyline, the openings, and which picture goes where.

A run is a SNAPSHOT IN TIME (Director ruling, 2026-08-21): the era is rolled
at the start — nomad camps, villages, or Victorian towns — and never moves.
The cast is that era's descendants of the six nomads (cast.py). The player is
dealt one of them; they do not choose.

Three acts over four nights (twelve watches), then an epilogue:

  Act I   UNDER THE SHADOW  (turns 1-3, before the first dawn)
          The world is grey. The band sits below the ridge with a fire that
          went out. Something tall stands on the far ridge with a white light
          at its chest. Nobody agrees what it is. (In later eras: it has not
          been seen in living memory, and the old stories turn out to be true.)
  Act II  THE COLOUR        (from the first dawn)
          The white flame takes a colour — hope or fear, rolled per
          playthrough — and the being comes down. Its acts land on the band
          every watch. The two Standing Ones pull from the ridge and the
          marsh. The player's choices decide who stays, who breaks, who
          follows whom.
  Act III THE FOG           (when one colour passes 0.55 of the band)
          Uhtcearu's grief condenses on the winner. The shepherded stall;
          the stragglers go grey.
  EPILOGUE at the fourth dawn, or earlier if you break, stop moving, or
          end up alone — and it ends on THE CHOICE: the fork in this
          playthrough the DM puts back to the player as a question.
"""
from __future__ import annotations

from . import art, world, cast

ACTS = {
    1: ("UNDER THE SHADOW", "The sky is grief. The fire is out. Something stands on the far ridge."),
    2: ("THE COLOUR", "The flame has a colour now, and the tall one is near."),
    3: ("THE FOG", "Grief has come down on the winners. The shepherded stall; the stragglers go grey."),
}

ERA_OPENERS = {
    "nomad camps": "It is the time of the camps. Nothing has been built that outlasts a season.",
    "villages": "It is the time of the villages. The fork has walls now, and a well, and the old stories about the ridge are told to children as stories.",
    "Victorian towns": "It is the time of the towns. Fork Town has a clocktower and a reservoir and chimneys that do not sleep, and nobody living has seen the tall one.",
}

OPENINGS = {
    # ---- nomad camps ----------------------------------------------------------
    "ila": (
        "You are Ila. You carry the water, which means you are the one who knows "
        "how little there is. The skins are two-thirds river and one-third lie, and "
        "nobody has noticed yet because nobody is looking at anything. The fire at "
        "the dry fork went out some time ago and no one relit it. Wystan is talking "
        "to himself about a river. Brand is sharpening a spear that is already "
        "broken. Tate is sitting a little apart, looking at the ridge, where "
        "something tall has been standing since before the light came."
    ),
    "wystan": (
        "You are Wystan, and you are the only one left who remembers the sky "
        "being anything but this. There was a river. You have stopped saying so. "
        "The young ones sit around a fire that went out before any of them were "
        "born, and they do not notice it is out. Ila rations the water with a "
        "face you recognise from your own mother. On the far ridge something tall "
        "has been standing all night with a white light where a heart would be, "
        "and you are the only one who has looked at it for longer than a breath."
    ),
    "brand": (
        "You are Brand. The spear is cracked because you put it through a man "
        "from the ridge camp a season ago, and Oswy saw, and neither of you has "
        "said a word about it since. The others think it was a boar. The fire at "
        "the dry fork is out and you are the one who should relight it and you "
        "have not. Hild is singing under her breath, which she does when she is "
        "afraid. On the far ridge there is a tall thing with a white light at its "
        "chest. It has not moved. You have counted."
    ),
    "hild": (
        "You are Hild. You are singing your mother's song under your breath, "
        "which you do when you are afraid, and you have been afraid for a year, "
        "since she walked up the ridge toward the red one and did not come back. "
        "The band sits around a dead fire at the dry fork. Wystan is the only one "
        "who ever listens to the song. Tate is looking at the ridge. There is "
        "something tall up there with a white light in it, and it has been "
        "standing where your mother went."
    ),
    "oswy": (
        "You are Oswy. You watch the ridge because someone has to, and because "
        "you have been up there, close, closer than anyone knows, and looked at "
        "the Red Standing One's face, and you keep going back. Your brother Brand "
        "cracked his spear on a man and you saw it and you carry that too. The "
        "fire at the fork is out. The others are grey and do not know it. And "
        "tonight the ridge has something new on it: a tall shape with a white "
        "light in its chest, and it is not the red one, and it does not move."
    ),
    "tate": (
        "You are Tate. Nobody claims you, which means nobody tells you to stop "
        "looking at things, so you look. You saw the tall one three nights ago, "
        "before anyone, and said so, and Oswy laughed and Brand told you to sit "
        "down. Now it is there for everyone to see, on the far ridge, with a "
        "white light where a chest should be. Ila gave you the last of the good "
        "water this morning and told you not to tell. The fire is out. It has "
        "always been out, as far as you know."
    ),
    # ---- villages -------------------------------------------------------------
    "ilse": (
        "You are Ilse. You keep the well, which means you are the one who knows "
        "the water is going bitter at the bottom and the ration you draw is "
        "short by a cup, and has been for a month, and no one has said a word. "
        "The fork village sits under the ridge with its shutters closed against "
        "nothing. Wyn is telling the river story to no one. Bram is at the forge "
        "with a hammer he does not use. Teg, whom you feed, is on the wall "
        "looking up at the ridge, where something tall has been standing since "
        "before the light, exactly where the children's stories said it once stood."
    ),
    "wyn": (
        "You are Wyn, and you are the last one who keeps the story your "
        "grandmother kept: a river where the road is, and a sky that was not "
        "this sky. You have stopped telling it because the children laugh. The "
        "village is grey in the way a village can be grey — roofs mended, well "
        "drawn, nobody looking up. Ilse draws the ration with a face you know "
        "from the story. On the ridge above the shrine something tall has been "
        "standing all night with a white light in its chest, and it is the "
        "thing from the story, and you are the only one who knows that."
    ),
    "bram": (
        "You are Bram. The hammer is split because you brought it down on a man "
        "from the ridge shrine who came to the forge door to preach, and Osric "
        "saw, and neither of you has spoken of it. The village thinks it split "
        "on iron. Hedda is humming at the loom, which she does when she is "
        "afraid. The shrine bell has not rung since. On the ridge above it, a "
        "tall shape with a white light at its chest has not moved all night. "
        "You have counted."
    ),
    "hedda": (
        "You are Hedda. You are humming your mother's tune at the loom, which "
        "you do when you are afraid, and you have been afraid for two winters, "
        "since she went up the ridge road to the shrine and stayed. Wyn is the "
        "only one who ever listens to the tune. Teg is on the wall looking up. "
        "There is something tall on the ridge above the shrine with a white "
        "light in it, standing where your mother went."
    ),
    "osric": (
        "You are Osric. You walk the ridge road at night because someone has "
        "to, and because you have stood at the shrine door and looked at the "
        "Red Standing One's face, and you keep going back. Your brother Bram "
        "split his hammer on a man and you saw it and you carry that too. The "
        "village sleeps grey and does not know it. And tonight the ridge has "
        "something on it that is not the shrine and not the red one: a tall "
        "shape with a white light in its chest, and it does not move."
    ),
    "teg": (
        "You are Teg. Nobody claims you, except that the well-keeper feeds you, "
        "which is not the same. Nobody tells you to stop looking at things, so "
        "you look. You saw the tall one on the ridge three nights ago, before "
        "anyone, and said so, and were sent to bed for lying. Now it is there "
        "for everyone, above the shrine, with a white light where a chest "
        "should be. Ilse gave you the good water this morning and told you not "
        "to tell."
    ),
    # ---- Victorian towns ------------------------------------------------------
    "ada": (
        "You are Ada Waterman, clerk at the reservoir works, which means you "
        "are the one who knows the intake is silting and the level you write "
        "in the book each morning is a hand higher than the water. Six weeks "
        "now. Fork Town wakes grey under its chimneys. Eadwin is lighting lamps "
        "nobody needs. Bram Spearing is at the mill gate with a mallet he does "
        "not swing. Kit, who sleeps under the clocktower, is standing in the "
        "square looking up past the ridge works, where something tall has been "
        "standing since before the light — a thing from stories nobody tells "
        "any more."
    ),
    "eadwin": (
        "You are Eadwin Rivers, the lamplighter, and your name is a river that "
        "ran where the mill race runs now. You are the last one who knows the "
        "sky was once another colour, and you have stopped telling anyone. The "
        "town is grey in the way a town can be grey — trams running, books "
        "kept, nobody looking up. Ada Waterman keeps the reservoir book with a "
        "face you recognise from somewhere older than the town. And above the "
        "ridge works, all night, a tall shape with a white light in its chest "
        "has stood without moving, and it is the thing from before the town, "
        "and you are the only one who knows that."
    ),
    "bram_s": (
        "You are Bram Spearing, foreman, and the mallet is cracked because you "
        "brought it down on a man from the ridge works who came to the mill "
        "gate, and your brother Osbert saw, and neither of you has spoken of "
        "it. The hands think it cracked on a wedge. Hester is humming at the "
        "loom-line, which she does when she is afraid. Above the ridge works a "
        "tall shape with a white light at its chest has not moved all night. "
        "You have counted."
    ),
    "hester": (
        "You are Hester Singer. You are humming your mother's tune at the "
        "loom-line, which you do when you are afraid, and you have been afraid "
        "since the morning she took the ridge tram up to the works and did not "
        "take it down. Eadwin is the only one who ever listens to the tune. Kit "
        "is in the square looking up. Above the works there is something tall "
        "with a white light in it, standing where your mother went."
    ),
    "osbert": (
        "You are Osbert Spearing, night watchman. Your rounds end at the ridge "
        "works gate, where the Red Standing One stands under the lamps, and you "
        "have gone in past the gate more than once, closer than anyone knows, "
        "and you keep going back. Your brother Bram cracked his mallet on a man "
        "and you saw it and you carry that too. The town sleeps grey and does "
        "not know it. And tonight, above the works, there is a tall shape with "
        "a white light in its chest that is not the red one, and it does not "
        "move."
    ),
    "kit": (
        "You are Kit. Nobody claims you; you sleep under the clocktower and "
        "nobody tells you to stop looking at things, so you look. You saw the "
        "tall one over the chimneys three nights ago, before anyone, and said "
        "so, and were cuffed for it. Now it is there for everyone, above the "
        "ridge works, with a white light where a chest should be. Ada Waterman "
        "gave you clean water from the works this morning and told you not to "
        "tell."
    ),
}


ZEALOT_OPENING = {
    "you": {
        "hope": ("And something happened to you a while ago that did not happen to the others: you stopped moving. "
                 "Whatever the grey does to them, it does not do to you any more, and they have noticed. "
                 "When you sit, they sit nearer. When you look up, they look up. They are waiting for you to say what this is."),
        "fear": ("And something happened to you a while ago that did not happen to the others: you stopped moving. "
                 "Whatever the grey does to them, it does not do to you any more, and they have noticed. "
                 "When you stand, they go quiet. When you look at one of them, that one looks away first. "
                 "They are waiting for you to say what to do about the ridge, and they will do it."),
    },
    "other": {
        "hope": "{name} stopped moving a while ago — the grey does not take {name} the way it takes the rest — and the others sit a little nearer to {name} than to anyone, without saying why.",
        "fear": "{name} stopped moving a while ago — the grey does not take {name} the way it takes the rest — and the others go quiet when {name} stands, without saying why.",
    },
}


def opening(L: dict) -> str:
    text = ERA_OPENERS[L["world"]["era"]] + "\n\n" + OPENINGS[L["meta"]["perspective"]]
    z = L["meta"].get("seated_zealot")
    if z:
        if z["id"] == L["meta"]["perspective"]:
            text += "\n\n" + ZEALOT_OPENING["you"][z["pole"]]
        else:
            text += "\n\n" + ZEALOT_OPENING["other"][z["pole"]].format(name=cast.first_name(L["band"][z["id"]]["name"]))
    text += "\n\n" + opening_press(L)
    return text


def beat_guidance(L: dict) -> str:
    """What the narrator should be leaning on this turn — a nudge, not a script."""
    W = L["world"]
    t = L["meta"]["turn"]
    act = L["meta"]["act"]
    era = W["era"]
    g = [f"The era is {era} and it never changes in this story: {ERA_OPENERS[era]} Dress every scene in it — {W['places']['structures']}, {W['places']['road']}, {W['places']['water']} — and never in another era's furniture."]
    if act == 1:
        g.append("Act I. Keep the world grey and quiet. The being is FAR and has no colour; it is rumour and a light. Do not let it touch anyone yet.")
        if era != "nomad camps":
            g.append("In this era the tall one has not been seen in living memory; the old stories are turning out to be true and nobody wants them to be.")
        if t == 1:
            g.append("First turn: establish the dead fire (or the cold hearth), the ridge, who is where. End on the band noticing the tall shape.")
        if t == world.RULES["turns_per_day"]:
            g.append("Dusk of the first day. Let the band argue about what to do about the ridge. The vigil comes next.")
    elif act == 2:
        g.append(f"Act II. The flame is {world.POLE_COLOUR[W['being_tint']]} and the being is near. Its act this watch is in the ledger — make it land on bodies, not on scenery.")
        if W["being_tint"] == "fear":
            g.append("Fear is the easy path: it breaks and coerces. Let the band get sharp, quick, suspicious. Fear's converts are many and shallow.")
        else:
            g.append("Hope is the hard path: it must convert, slowly, and wins by patience. Let the band soften by inches and resent it. Hope's converts are few and arrive already deep.")
    else:
        g.append(f"Act III. The fog is down on the {W['grief_front']['on']} side. Inside it nobody deepens; the unshepherded go grey. Grief takes the stragglers; the shepherded stand. Make the fog a presence, not weather.")
    return " ".join(g)


def lineage_note(L: dict) -> str:
    """For the narrator's eyes only: who descends from whom, and the habit that
    repeats. The rule is SUBTLETY — the callback is something a perceptive
    player notices, never something the prose points at."""
    P = L["player"]
    lines = [f"- {P['name']} ({P['line']}'s line): {P['habit']}; carries {P['heirloom'] or 'nothing now — gave it away'}"]
    for n in L["band"].values():
        extra = f"; also holds {', '.join(n['carried'])}" if n.get("carried") else ""
        lines.append(f"- {n['name']} ({n['line']}'s line): {n['habit']}; carries {n['heirloom']}{extra}")
    z = L["meta"].get("seated_zealot")
    zl = ""
    if z:
        who = L["player"] if z["id"] == L["meta"]["perspective"] else L["band"][z["id"]]
        if z["id"] == L["meta"]["perspective"]:
            zl = (f"\nTHE ONE WHO STOPPED MOVING IS YOU. {who['name']} is {z['pole']} all the way through and the grey no longer takes them. Never use the word 'zealot' in the prose — not for anyone. The others look to {who['name']} to lead; "
                  f"what {who['name']} does, they do. Show it in how they arrange themselves, wait for a word, copy a gesture. "
                  f"{'Hope' if z['pole']=='hope' else 'Fear'} is what {who['name']} induces: "
                  f"{'steadiness, inclusion, patience' if z['pole']=='hope' else 'watchfulness, coercion, the quick obedience of the frightened'}.")
        else:
            zl = (f"\nTHE ONE WHO STOPPED MOVING: {who['name']} is {z['pole']} all the way through and the grey no longer takes them. Never use the word 'zealot' in the prose — not for anyone. Show it: stillness, certainty, "
                  f"the way people sit nearer or further, and what {who['name']} induces in them — "
                  f"{'steadiness, inclusion, patience' if z['pole']=='hope' else 'watchfulness, coercion, the quick obedience of the frightened'}. "
                  f"If {who['name']} is not present or is burned, they are not here and do not speak.")
    return (
        "LINEAGE — for you only. Each person carries a habit their bloodline has carried since the camps. "
        "Let the habit show in what they DO (a hand on a water skin, a tune under the breath, a look up the ridge road), "
        "never in what you SAY about it: no 'like her grandmother', no 'as her line always has', no family names explained. "
        "Each also carries an OBJECT handed down their line and re-made for this age. Let it be touched, turned, set down, handed over — never explained, never called an heirloom, never given a history. "
        "A perceptive player should be able to notice it across playthroughs; an inattentive one should never be told.\n"
        + "\n".join(lines) + zl + "\n\n" + heirloom_lock(L)
    )


def heirloom_lock(L: dict) -> str:
    """THE DIAGRAM (Director, 2026-08-23). One object per bloodline, locked.
    Built from the LIVE ledger so a handed-on object moves its row's hands —
    the table is the truth of this run, not the truth of the era."""
    rows = []
    for line, holder, obj in _heirloom_rows(L):
        rows.append(f"  {line:<8}| {obj:<62}| {holder}")
    return (
        "THE OBJECTS ARE LOCKED — one per bloodline, never interchanged, never merged, never described in another's hands:\n\n"
        "  line    | the object of that line, in this age                          | in whose hands NOW\n"
        "  --------|---------------------------------------------------------------|-------------------\n"
        + "\n".join(rows) + "\n\n"
        "HARD RULES: an object appears ONLY in the hands the table names. Never let another person hold, touch-as-owner, "
        "or be described with an object that is not theirs. If two objects would appear in one sentence, keep each with its own carrier. "
        "The ONLY way an object changes hands is the ledger recording it handed on — and then the NEW hands are the only correct hands. "
        "A habit stays with its line even when the object has moved."
    )


def _heirloom_rows(L: dict):
    """(line, holder-description, object-text) for every bloodline, from the live ledger."""
    P = L["player"]
    everyone = [("you", P)] + [(pid, n) for pid, n in L["band"].items()]
    rows = []
    for line in cast.HEIRLOOMS:
        obj = cast.heirloom(line, L["world"]["era"])
        holders = []
        for pid, person in everyone:
            own = person.get("heirloom") or ""
            carried = " ".join(person.get("carried") or [])
            if obj == own or (person.get("line") == line and person.get("heirloom")):
                holders.append(f"{person['name']}{' (the player — their own)' if pid == 'you' else ''}")
            elif obj in carried or (obj and any(obj[:24] in c for c in (person.get('carried') or []))):
                holders.append(f"{person['name']} (handed on to them; it is theirs now)")
        if not holders:
            giver = next((per['name'] for _, per in everyone if per.get('line') == line), line)
            holders.append(f"nobody present — {giver} gave it away or it is gone")
        rows.append((line, "; ".join(holders), obj))
    return rows


ERA_ART = {"nomad camps": "camp_grey", "villages": "village", "Victorian towns": "victorian"}


def pick_art(L: dict, action: dict | None, logs: list[str], ending: str | None) -> list[str]:
    """Which pictures accompany this turn. The ledger decides, not the model."""
    W = L["world"]
    picks = []
    if ending:
        return {
            "burned": ["burned"], "zealot": ["zealot_red" if L["player"]["emotion"] < 0 else "zealot_green"],
            "alone": ["fog" if W["grief_front"]["active"] else ERA_ART[W["era"]]], "dawn": ["dawn"],
        }[ending]
    joined = "\n".join(logs)
    slept = "SLEEP —" in joined
    if action and action.get("verb") == "follow_zealot":
        picks.append("zealot_red" if W["camp"] == W["places"]["red"] else "zealot_green")
    if " BROKE " in joined:
        picks.append("burned")
    last = W.get("being_last_act") or {}
    v = last.get("verb")
    if not slept:
        if last.get("distance") == "far":
            if L["meta"]["turn"] == 1:
                picks.append(ERA_ART[W["era"]])
            picks.append("being_far")
        else:
            picks.append({"Flame": "flame", "Roar": "roar", "Beacon": "beacon", "Raze": "raze",
                          "Walk": "being_near", "Wait": "being_near"}.get(v, "being_near"))
    else:
        picks.append("vigil")
        if "THE FIRST DAWN" in joined:
            picks.append("being_near")
        elif "GRIEF FRONT" in joined or W["grief_front"]["active"]:
            picks.append("fog")
    seen, out = set(), []
    for p in picks:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out[:2]


def opening_art(L: dict) -> list[str]:
    return ["title", ERA_ART[L["world"]["era"]]]


def render_art(keys: list[str]) -> list[str]:
    return [art.ALL[k] for k in keys if k in art.ALL]


# ---------------------------------------------------------------------------
# THE PRESS — every section ends on something the player must react to.
# (Director's rule, 2026-08-21: "they need something to react to for the
# 'what do you do?' — a scenario. The hopeful should act hopeful. The fearful
# should act fearful.") The situation is chosen in code from the ledger, so it
# is always true to who is present and what colour they are; the narrator
# renders it in its own words and must end the turn on it.
# ---------------------------------------------------------------------------
import random as _random

BEHAVIOUR = {
    "grey":            "does not look up; answers late or not at all; declines to choose; sits where they sat",
    "tentative hope":  "offers small things — water, a place nearer the warmth, a half-joke; looks at the ridge with curiosity more than dread; wants you to come and see",
    "devout hope":     "steadies the others; includes the one left out; is patient to the point of stubbornness; puts themselves between the frightened and the thing they fear",
    "unmoving hope":   "is still and certain; does not argue; people sit nearer without being asked; wants you to stay, to hold, to wait it out together",
    "tentative fear":  "flinches; checks the way out; asks quick questions and does not wait for answers; keeps the fire or the wall at their back",
    "devout fear":     "coerces; accuses; wants someone to blame or someone to obey; talks about the ridge as the only safe place; counts who is with them",
    "unmoving fear":   "is still and watchful; people go quiet when they stand; wants obedience, not agreement; wants to know who is not with them",
    "burned":          "frozen, grey, ringed in the colour they carried; does not speak, does not look; the others step around them",
}

PRESS = {
    "grey": [
        "{name} has not moved since the light came. You are holding {water}, and {name} has not asked for it, and will not.",
        "{name} is looking at the ground between their feet. When you say their name they take a long moment to look up, and then look down again.",
    ],
    "tentative hope": [
        "{name} holds something out to you — {offer} — and nods toward the ridge. 'Come and look. It hasn't moved. It isn't coming for us.'",
        "{name} crouches beside you. 'If we went up together,' {name} says, 'just to the first rocks. Just to see. Would you?'",
    ],
    "devout hope": [
        "{name} has got {other} sitting up and drinking, and now turns to you. 'We stay together tonight. All of us. Say it with me so they hear it.'",
        "{name} puts a hand flat on your chest, not hard. 'You're going to do something. I can see it. Whatever it is, take me with you.'",
    ],
    "unmoving hope": [
        "{name} has not spoken all watch, and the others have drifted to sit nearer. Now {name} looks at you, only you, and waits. They are all waiting for what you will say.",
    ],
    "tentative fear": [
        "{name} grabs your arm. 'What was that. Did you hear it. We should go. We should go now — tell me we should go.'",
        "{name} has backed up against {wall} and will not come to the fire. 'You go first,' {name} says. 'You. Then I'll know.'",
    ],
    "devout fear": [
        "{name} stands over you. 'The ridge is the only place it can't reach. Everyone who's coming is coming now. Are you with us, or are you with {other}?'",
        "{name} points at {other}. '{other_first} has been lying to all of us. You know it. Say it, or I'll say what you've been hiding.'",
    ],
    "unmoving fear": [
        "{name} stands, and the talk stops. {name} looks at each of them and then at you, and says nothing, and the silence is a question with your name in it.",
    ],
    "burned": [
        "{other} kneels beside {name}, who has not blinked since it happened, and looks up at you. 'Do something. You're the one who can. Do something.'",
    ],
    "alone": [
        "There is no one left at the fire but you. The ridge is there. The marsh is there. The flame is {flame}. Nobody is going to ask you anything again.",
    ],
    "you_lead": [
        "They have stopped talking and are looking at you. Not at the ridge. At you. {name} says, quietly, 'Tell us what we do.'",
        "{name} brings you {water} before you ask for it, and stays crouched there, waiting. Behind {name} the rest have gone quiet. Whatever you do next, they will do too.",
    ],
}

OFFERS = {
    "nomad camps": ["a strip of dried meat", "the last warm stone from the ashes", "a hand up"],
    "villages": ["a heel of bread", "a cup from the well", "a hand up"],
    "Victorian towns": ["a twist of tobacco", "a tin cup of something hot", "a hand up"],
}
WALLS = {"nomad camps": "the rocks", "villages": "the wall", "Victorian towns": "the mill gate"}
WATER_THING = {"nomad camps": "the water skin", "villages": "the well-bucket", "Victorian towns": "the tin cup"}


def _state(n: dict) -> str:
    if n["burned"]:
        return "burned"
    return world.describe(n["emotion"])


def pick_press(L: dict) -> dict:
    """Choose who presses you this watch and how. Deterministic per seed+turn."""
    rng = _random.Random(f"{L['meta']['seed']}:{L['meta']['turn']}")
    era = L["world"]["era"]
    present = [(pid, n) for pid, n in L["band"].items() if n["present"] and n["alive"]]
    if not present:
        return {"who": None, "state": "alone", "text": rng.choice(PRESS["alone"]).format(flame=world.POLE_COLOUR[L["world"]["being_tint"]])}
    P = L["player"]
    # weight: the seated one, the burned, strong feelings, and anyone whose trust is at an extreme press hardest
    def weight(n):
        w = 1.0 + abs(n["emotion"]) / 4
        if n.get("zealot"): w += 3
        if n["burned"]: w += 2
        if abs(n["trust"]) >= 2: w += 1
        return w
    pid, n = rng.choices(present, weights=[weight(n) for _, n in present])[0]
    others = [m for q, m in present if q != pid] or [n]
    other = rng.choice(others)
    if P.get("zealot") and not P["burned"] and rng.random() < 0.6:
        state = "you_lead"
    else:
        state = _state(n)
    tmpl = rng.choice(PRESS[state])
    text = tmpl.format(
        name=cast.first_name(n["name"]), other=cast.first_name(other["name"]), other_first=cast.first_name(other["name"]),
        water=WATER_THING[era], offer=rng.choice(OFFERS[era]), wall=WALLS[era],
        flame=world.POLE_COLOUR[L["world"]["being_tint"]],
    )
    return {"who": pid, "state": state, "text": text}


def behaviour_block(L: dict) -> str:
    rows = []
    P = L["player"]
    rows.append(f"- {P['name']} (you): {_state(P)} — {BEHAVIOUR[_state(P)]}")
    for n in L["band"].values():
        if n["present"] and n["alive"]:
            st = _state(n)
            rows.append(f"- {n['name']}: {st} — {BEHAVIOUR[st]}")
    return ("BEHAVIOUR — each person acts their colour, every time they appear. The hopeful act hopeful; the fearful act fearful; the grey barely act. "
            "Never describe a frightened person as calm or a hopeful one as sour. Their colour is in the ledger; their conduct must match it:\n" + "\n".join(rows))


def press_block(press: dict) -> str:
    return ("THE PRESS — the turn MUST end on this, rendered in your own words as its own final short paragraph, and the very last sentence must be a question or a demand put to you "
            "(something you have to answer with what you do next). Keep it concrete: a person, an act toward you, a thing they want. Here it is:\n" + press["text"])


def opening_press(L: dict) -> str:
    """The opening ends on a press too, templated (no model call before the first turn)."""
    return pick_press(L)["text"]
