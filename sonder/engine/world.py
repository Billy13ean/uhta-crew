"""world.py — the facts ledger and the rules that move it.

No LLM in this file. Everything here is deterministic: the ledger is a plain
dict (serialised as JSON every turn), and `apply_action` / `world_tick` /
`sleep` are the only functions that change it. The model never edits the
ledger directly — it proposes a structured action, the rules decide what that
action did, and the narrator is handed the result. That split is what makes
the state tracking trustworthy: a hallucinated consequence cannot reach the
ledger because the ledger is not written from prose.

The numbers are the game's own where they exist (GDD §2, rules-v3.9.1-C):
the -12..+12 scale, the four bands, the one-step-per-tick cap, Flame +/-2.0,
Roar 2.8 of Fear on every witness, Wait 0.5 toward Apathy, grief decay toward
zero every Sleep, peer contagion, burnout under too much same-colour pressure,
and the save that only the opposite feeling can perform. Where the prototype
needed a constant the GDD does not fix (how a mortal's acts weigh, era
thresholds in sleeps), it is declared in RULES below and marked POLICY.
"""
from __future__ import annotations

import copy
import json
import random

SCALE_MIN, SCALE_MAX = -12, 12

RULES = {
    "step_cap": 1,               # canon: nobody moves more than one step per tick
    "flame_push": 2.0,           # canon: toward the being's tint, r3
    "roar_fear_push": 2.8,       # canon: unconditional Fear on all witnesses, r6
    "wait_apathy_pull": 0.5,     # canon: witnessed inaction pulls toward grey
    "beacon_aura": 0.35,         # canon: per tick, in the being's colour
    "raze_fear_spike": 2.5,      # canon
    "grief_decay_per_sleep": 1,  # canon: Uhtcearu — everyone slides toward zero
    "peer_contagion": 0.1,       # canon: per same-direction neighbour
    "peer_contagion_cap": 0.7,   # canon
    "zealot_pull": 2.0,          # canon: a zealot pulls hardest
    "burn_threshold": 4.5,       # POLICY: same-colour pressure >= this in one tick breaks a devout person
    "save_tends_needed": 2,      # POLICY: opposite-colour tending, twice, lifts a burn
    "mortal_act_push": 0.8,      # POLICY: a mortal's act on its target
    "mortal_witness_push": 0.4,  # POLICY: ...and on whoever watches
    "strike_fear_push": 1.2,     # POLICY
    "turns_per_day": 3,          # POLICY: three watches, then the vigil
    "grief_front_dominance": 0.55,  # canon: fires past 0.55 dominance, on the winner
    "grief_front_sleeps": 3,     # canon
    "story_turns": 12,           # POLICY: four days, then the epilogue
    "seated_zealot_chance": 0.6, # POLICY: chance a run has a zealot among the cast (maybe you)
    "seated_zealot_pull": 0.6,   # POLICY: a cast zealot's pull on everyone present, every watch
    "zealot_lead_factor": 2.0,   # POLICY: a zealot player's acts weigh double — they look to you to lead
}

POLE_COLOUR = {"hope": "green", "fear": "red", "grey": "grey", "drift": "white"}


def band_of(e: int) -> str:
    a = abs(e)
    if a >= 12:
        return "zealot"
    if a >= 8:
        return "devout"
    if a >= 3:
        return "tentative"
    return "grey"


def pole_of(e: int) -> str:
    if e >= 3:
        return "hope"
    if e <= -3:
        return "fear"
    return "grey"


def describe(e: int) -> str:
    """Human words for a position. 'zealot' is never said in the story — the
    Director's rule: their actions tell what they are — so the band reads as
    'unmoving' in anything a player or the narrator might see."""
    b = band_of(e)
    if b == "grey":
        return "grey"
    if b == "zealot":
        return f"unmoving {pole_of(e)}"
    return f"{b} {pole_of(e)}"


# -- the band -----------------------------------------------------------------
# The casts live in cast.py: three eras, six bloodlines, set backstories.
# In uhta nobody is named on screen; a DM that cannot say who was abandoned
# cannot track a betrayal, so the prototype names them.
from . import cast as _cast

BAND = _cast.CASTS["nomad camps"]      # kept for callers that want the root cast
ZEALOTS = {
    "red_standing":   {"name": "the Red Standing One",   "pole": "fear", "emotion": -12},
    "green_standing": {"name": "the Green Standing One", "pole": "hope", "emotion": 12},
}


def new_ledger(perspective: str | None = None, seed: int = 7, era: str | None = None) -> dict:
    """Deal a playthrough. Era and person are rolled from the seed unless forced
    (forcing is for tests and the --as/--era flags; the page never offers it)."""
    rng = random.Random(seed)
    rolled_era, rolled_pid = _cast.deal(rng)
    if era is None and perspective is not None:   # a forced person implies their era
        era = next((e for e, c in _cast.CASTS.items() if perspective in c), rolled_era)
    era = era or rolled_era
    if era not in _cast.CASTS:
        raise ValueError(f"unknown era {era!r}; one of {list(_cast.CASTS)}")
    castd = _cast.CASTS[era]
    perspective = perspective or (rolled_pid if rolled_pid in castd else sorted(castd)[0])
    if perspective not in castd:
        raise ValueError(f"unknown perspective {perspective!r} for {era}; one of {list(castd)}")
    places = _cast.PLACES[era]
    me = castd[perspective]
    npcs = {}
    for pid, m in castd.items():
        if pid == perspective:
            continue
        trust = 1 if pid == me["trusts"] else (-1 if pid == me["doubts"] else 0)
        npcs[pid] = {
            "name": m["name"], "role": m["role"], "line": m["line"], "habit": m["habit"],
            "heirloom": _cast.heirloom(m["line"], era), "heirloom_from": None,
            "emotion": m["emotion"], "band": band_of(m["emotion"]), "pole": pole_of(m["emotion"]),
            "burned": False, "burned_colour": None, "tends": 0,
            "trust": trust,          # -3 .. +3 toward you
            "present": True,         # still with you
            "where": None,           # if not present: where they went
            "alive": True,
        }
    zealots = copy.deepcopy(ZEALOTS)
    zealots["red_standing"]["where"] = places["red"]
    zealots["green_standing"]["where"] = places["green"]
    L = {
        "meta": {"seed": seed, "turn": 0, "era": era, "perspective": perspective,
                 "player_name": me["name"], "ended": None, "act": 1},
        "player": {
            "name": me["name"], "role": me["role"], "line": me["line"], "habit": me["habit"],
            "heirloom": _cast.heirloom(me["line"], era), "heirloom_from": None, "heirloom_given_to": None,
            "emotion": me["emotion"], "band": band_of(me["emotion"]), "pole": pole_of(me["emotion"]),
            "burned": False, "burned_colour": None, "tends": 0,
            "private": me["private"], "private_told": False,
        },
        "band": npcs,
        "zealots": zealots,
        "world": {
            "sleeps": 0, "era": era, "watch": "first light",
            "camp": places["camp"], "home": places["camp"], "places": places,
            "roads": [], "beacons": [],
            "being_tint": "drift",       # white until the first dawn
            "being_distance": "far",     # far -> near
            "being_seen_verbs": [],
            "being_last_act": None,
            "grief_front": {"active": False, "sleeps_left": 0, "on": None},
            "dominance": {"hope": 0.0, "fear": 0.0, "grey": 1.0},
        },
        "facts": [],      # durable facts the narrator may never contradict
        "promises": [],   # {"to", "what", "turn", "kept": None|True|False}
        "betrayals": [],  # {"of", "what", "turn"}
        "loyalties": [],  # {"to", "what", "turn"}
        "history": [],    # one past-tense line per turn
        "_roll": rng.random(),   # decides the being's colour at the first dawn
    }
    L["facts"].append(f"You are {me['name']}, who {me['role']}. It is the time of {era}.")
    L["facts"].append(f"{me['name']} carries {L['player']['heirloom']}.")

    # A seated zealot (Director ruling 2026-08-21): sometimes one of the cast
    # has already stopped moving — and sometimes it is you, and the others
    # look to you to lead. Who, and which colour, is rolled from the seed.
    L["player"]["zealot"] = False
    L["player"]["started_zealot"] = False
    for n in npcs.values():
        n["zealot"] = False
    if rng.random() < RULES["seated_zealot_chance"]:
        seat = rng.choice([perspective] + sorted(npcs))
        base = castd[seat]["emotion"]
        pole = "hope" if base > 0 else ("fear" if base < 0 else rng.choice(["hope", "fear"]))
        e = 12 if pole == "hope" else -12
        who = L["player"] if seat == perspective else npcs[seat]
        who.update({"zealot": True, "emotion": e, "band": "zealot", "pole": pole})
        L["meta"]["seated_zealot"] = {"id": seat, "pole": pole}
        if seat == perspective:
            L["player"]["started_zealot"] = True
            for n in npcs.values():
                n["trust"] = min(3, n["trust"] + 1)
            L["facts"].append(f"{me['name']} stopped moving some time ago — the grey does not take {me['name']} — and is {pole} all the way through. The others look to {me['name']} to lead.")
        else:
            L["facts"].append(f"{who['name']} stopped moving some time ago — the grey does not take {who['name']} — and is {pole} all the way through. The others arrange themselves around {who['name']}.")
    else:
        L["meta"]["seated_zealot"] = None
    return L


# -- pressure -------------------------------------------------------------------
def _apply_pressure(person: dict, pressure: float, log: list, who: str) -> None:
    """The two caps that make this a game instead of a slider (GDD §2)."""
    if not person.get("alive", True) or person["burned"]:
        return
    e = person["emotion"]
    same_colour = (pressure > 0 and e >= 8) or (pressure < 0 and e <= -8)
    if same_colour and abs(pressure) >= RULES["burn_threshold"]:
        person["burned"] = True
        person["burned_colour"] = pole_of(e)
        person["zealot"] = False
        person["emotion"] = 0
        person["band"], person["pole"] = "grey", "grey"
        log.append(f"{who} BROKE under {abs(pressure):.1f} of the same colour — frozen grey, ringed in {person['burned_colour']}")
        return
    if person.get("zealot") and abs(e) >= 12:
        return  # a zealot has stopped moving; only breaking moves them (above)
    step = 0
    if abs(pressure) >= 0.5:
        step = 1 if pressure > 0 else -1
    ne = max(SCALE_MIN, min(SCALE_MAX, e + step))
    if ne != e:
        person["emotion"] = ne
        ob, nb = band_of(e), band_of(ne)
        person["band"], person["pole"] = nb, pole_of(ne)
        if ob != nb or abs(ne) == 12:
            log.append(f"{who}: {describe(e)} -> {describe(ne)}")


def _tend(person: dict, tone: str, log: list, who: str) -> None:
    """The save: only the opposite feeling brings the burned back (GDD §2.3)."""
    if tone != "neutral" and tone != person["burned_colour"]:
        person["tends"] += 1
        if person["tends"] >= RULES["save_tends_needed"]:
            person["burned"] = False
            person["emotion"] = 3 if tone == "hope" else -3
            person["band"], person["pole"] = band_of(person["emotion"]), pole_of(person["emotion"])
            log.append(f"{who} came back — tentative {tone}; the ring of {person['burned_colour']} is gone")
            person["burned_colour"] = None
        else:
            log.append(f"{who} was tended with {tone} ({person['tends']}/{RULES['save_tends_needed']}) — still frozen")
    else:
        log.append(f"{who} was tended with the colour that broke them — nothing moved")


# -- the player's action -------------------------------------------------------
ACTION_VERBS = {
    "stand_with":     "side with, comfort, shield or defend someone (tone decides the colour)",
    "share":          "give water, food, warmth, a story, a name",
    "withhold":       "refuse, hoard, turn away from someone",
    "threaten":       "menace or intimidate someone",
    "strike":         "violence against someone",
    "abandon":        "leave someone behind, or break a promise to them",
    "tend":           "care for someone who is burned/frozen",
    "follow_zealot":  "go up to the Red Standing One (the ridge) or out to the Green Standing One (the marsh)",
    "approach_being": "walk toward the tall one and its flame",
    "flee":           "run — from the being, the fog, the camp",
    "speak":          "talk, ask, tell, confess (tone decides the colour; target optional)",
    "promise":        "bind yourself to someone with words",
    "confess":        "tell the band your private secret",
    "wait":           "do nothing, watch, sleep it off",
}


def _present(L: dict) -> list:
    return [i for i, n in L["band"].items() if n["present"] and n["alive"]]


def apply_action(L: dict, action: dict) -> list:
    """Apply an interpreted player action. Returns the delta log (strings)."""
    log = []
    verb = action.get("verb", "wait")
    tone = action.get("tone", "neutral")
    if tone not in ("hope", "fear", "neutral"):
        tone = "neutral"
    target = action.get("target")
    P = L["player"]
    name = P["name"]
    t = L["meta"]["turn"]
    sign = {"hope": 1, "fear": -1, "neutral": 0}[tone]
    lead = RULES["zealot_lead_factor"] if P.get("zealot") else 1.0   # they look to you
    push = RULES["mortal_act_push"] * sign * lead
    witness = RULES["mortal_witness_push"] * sign * lead
    present = _present(L)
    tgt = L["band"].get(target) if target in L["band"] else None
    if tgt and not tgt["present"]:
        log.append(f"{tgt['name']} is not here ({tgt['where']}); the act found no one")
        tgt = None
        if verb in ("stand_with", "share", "withhold", "threaten", "strike", "abandon", "tend", "promise"):
            verb = "wait"

    if P["burned"]:
        log.append(f"{name} is burned — frozen grey; nothing was done")
        return log

    # handing on the heirloom: an object goes from your line into theirs
    if action.get("gives_heirloom") and tgt and P.get("heirloom"):
        obj = P["heirloom"]
        tgt["heirloom_from"] = name
        tgt.setdefault("carried", []).append(obj)
        P["heirloom_given_to"] = target
        P["heirloom"] = None
        tgt["trust"] = min(3, tgt["trust"] + 2)
        log.append(f"{name} gave {tgt['name']} {obj}; trust -> {tgt['trust']:+d}")
        L["facts"].append(f"Turn {t}: {name} gave {tgt['name']} {obj}. {tgt['name']} has it now; {name} does not.")
        L["loyalties"].append({"to": target, "what": f"gave {obj}", "turn": t})

    if verb in ("stand_with", "share", "speak", "promise") and tgt:
        if tgt["burned"]:
            _tend(tgt, tone, log, tgt["name"])
        else:
            _apply_pressure(tgt, push, log, tgt["name"])
        tgt["trust"] = min(3, tgt["trust"] + 1)
        log.append(f"{tgt['name']} trust -> {tgt['trust']:+d}")
        for i in present:
            if i != target:
                _apply_pressure(L["band"][i], witness, log, L["band"][i]["name"])
        _apply_pressure(P, push * 0.5, log, name)
        if verb == "promise":
            what = action.get("promise") or action.get("summary") or "a promise"
            L["promises"].append({"to": target, "what": what, "turn": t, "kept": None})
            L["facts"].append(f"Turn {t}: {name} promised {tgt['name']}: {what}")
        elif verb == "stand_with":
            L["loyalties"].append({"to": target, "what": action.get("summary", ""), "turn": t})
            L["facts"].append(f"Turn {t}: {name} stood with {tgt['name']}")
        elif verb == "share":
            L["loyalties"].append({"to": target, "what": "shared", "turn": t})
            L["facts"].append(f"Turn {t}: {name} shared with {tgt['name']}")

    elif verb == "speak" and not tgt:
        for i in present:
            _apply_pressure(L["band"][i], witness, log, L["band"][i]["name"])
        _apply_pressure(P, push * 0.5, log, name)

    elif verb == "confess":
        if not P["private_told"]:
            P["private_told"] = True
            L["facts"].append(f"Turn {t}: {name} told the band the truth: {P['private']}")
            log.append("the secret is out; the band heard it")
            for i in present:
                n = L["band"][i]
                # the truth lands differently on those who doubted you
                n["trust"] = max(-3, min(3, n["trust"] + (1 if n["trust"] >= 0 else -1)))
                _apply_pressure(n, witness if sign else -0.5, log, n["name"])
        else:
            log.append("the band already knows; nothing new was said")

    elif verb == "tend" and tgt:
        if tgt["burned"]:
            _tend(tgt, tone, log, tgt["name"])
        else:
            _apply_pressure(tgt, push, log, tgt["name"])
        tgt["trust"] = min(3, tgt["trust"] + 1)
        L["loyalties"].append({"to": target, "what": "tended", "turn": t})
        L["facts"].append(f"Turn {t}: {name} tended {tgt['name']}")

    elif verb in ("withhold", "threaten") and tgt:
        _apply_pressure(tgt, -RULES["mortal_act_push"], log, tgt["name"])
        tgt["trust"] = max(-3, tgt["trust"] - 1)
        log.append(f"{tgt['name']} trust -> {tgt['trust']:+d}")
        for i in present:
            if i != target:
                _apply_pressure(L["band"][i], -RULES["mortal_witness_push"], log, L["band"][i]["name"])
        _apply_pressure(P, -0.5, log, name)
        L["facts"].append(f"Turn {t}: {name} {'threatened' if verb == 'threaten' else 'turned away from'} {tgt['name']}")

    elif verb == "strike" and tgt:
        _apply_pressure(tgt, -RULES["strike_fear_push"], log, tgt["name"])
        tgt["trust"] = -3
        for i in present:
            if i != target:
                _apply_pressure(L["band"][i], -RULES["strike_fear_push"] * 0.5, log, L["band"][i]["name"])
                L["band"][i]["trust"] = max(-3, L["band"][i]["trust"] - 1)
        _apply_pressure(P, -1.0, log, name)
        L["betrayals"].append({"of": target, "what": "struck", "turn": t})
        L["facts"].append(f"Turn {t}: {name} struck {tgt['name']}; everyone saw")

    elif verb == "abandon" and tgt:
        tgt["trust"] = -3
        _apply_pressure(tgt, -1.0, log, tgt["name"])
        L["betrayals"].append({"of": target, "what": action.get("summary", "abandoned"), "turn": t})
        L["facts"].append(f"Turn {t}: {name} abandoned {tgt['name']}")
        for p in L["promises"]:
            if p["to"] == target and p["kept"] is None:
                p["kept"] = False
                L["facts"].append(f"Turn {t}: the promise to {tgt['name']} ('{p['what']}') was broken")
        for i in present:
            if i != target:
                _apply_pressure(L["band"][i], -0.5, log, L["band"][i]["name"])
                L["band"][i]["trust"] = max(-3, L["band"][i]["trust"] - 1)
        _apply_pressure(P, -0.5, log, name)

    elif verb == "follow_zealot":
        # the named target wins; tone decides only when no Standing One was named.
        # (Live finding, session ila-260820-220654-45f5: "go to the low marsh" with tone=fear
        #  was sent to the ridge by the old tone-first rule, and the ledger wrote a fact the
        #  interpreter's summary contradicted. The fact won downstream — the telling put Ila
        #  before the Red Standing One. Fixed here; see README §5.)
        if target in ("red_standing", "green_standing"):
            z = target
        else:
            z = "red_standing" if tone == "fear" else "green_standing"
        Z = L["zealots"][z]
        zs = 1 if Z["pole"] == "hope" else -1
        _apply_pressure(P, RULES["zealot_pull"] * zs, log, name)
        L["world"]["camp"] = Z["where"]
        L["facts"].append(f"Turn {t}: {name} went to {Z['where']} and stood before {Z['name']}")
        for i in present:
            n = L["band"][i]
            if n["trust"] >= 1:
                _apply_pressure(n, RULES["zealot_pull"] * 0.5 * zs, log, n["name"])
            else:
                n["present"] = False
                n["where"] = f"stayed behind at {L['world']['home']}"
                log.append(f"{n['name']} did not follow — stayed behind")
                L["facts"].append(f"Turn {t}: {n['name']} stayed behind when {name} went to {Z['where']}")

    elif verb == "approach_being":
        W = L["world"]
        tint = W["being_tint"]
        if W["being_distance"] == "far":
            log.append("the tall one is still far; walking toward it brought it no nearer")
            L["facts"].append(f"Turn {t}: {name} set out toward the tall one and could not reach it")
        elif tint == "drift":
            log.append("the white flame is undetermined; it warmed, it did not push")
            L["facts"].append(f"Turn {t}: {name} walked up to the tall one; the flame was still white")
        else:
            _apply_pressure(P, RULES["flame_push"] * (1 if tint == "hope" else -1), log, name)
            L["facts"].append(f"Turn {t}: {name} walked into the {POLE_COLOUR[tint]} flame")

    elif verb == "flee":
        _apply_pressure(P, -0.5, log, name)
        L["facts"].append(f"Turn {t}: {name} ran")
        for i in present:
            n = L["band"][i]
            if n["trust"] <= -1:
                n["trust"] = max(-3, n["trust"] - 1)

    else:  # wait
        for i in present:
            n = L["band"][i]
            if n["emotion"]:
                _apply_pressure(n, -RULES["wait_apathy_pull"] if n["emotion"] > 0 else RULES["wait_apathy_pull"], log, n["name"])
        log.append(f"{name} waited; witnessed inaction pulls toward grey")

    # promises are kept by deed
    if verb in ("stand_with", "share", "tend") and tgt:
        for p in L["promises"]:
            if p["to"] == target and p["kept"] is None and p["turn"] < t:
                p["kept"] = True
                L["facts"].append(f"Turn {t}: the promise to {tgt['name']} ('{p['what']}') was kept")
    return log


# -- the world's own move ------------------------------------------------------
# Act I (turns 1-3): the being is far. Rumour, tremor, a light. No pressure.
FAR_SCRIPT = [
    ("Walk",  "far off, the ground shook in a slow rhythm and a line of packed earth appeared across the flat"),
    ("Wait",  "it stood on the far ridge with a white light at its chest and did not move for the whole watch"),
    ("Flame", "at dusk the white light rose and fell, rose and fell, too far to warm anyone"),
]
# From the first dawn the being is near and has a colour.
NEAR_SCRIPT = {
    "hope": [
        ("Walk",   "it came down off the ridge; where it stepped the earth packed into a road and greened at the edges"),
        ("Flame",  "it knelt at the edge of the camp and the green flame came down over everyone"),
        ("Beacon", "it set something burning in one of the old ruined basins, and the light did not go out"),
        ("Wait",   "it sat in the basin light and did nothing, and everyone watched it do nothing"),
        ("Flame",  "the flame again, lower, nearer"),
        ("Walk",   "it walked the road again; the road darkened green"),
        ("Flame",  "the flame, a third time, steady"),
        ("Wait",   "it waited"),
        ("Beacon", "a second basin lit"),
    ],
    "fear": [
        ("Walk",   "it came down off the ridge; where it stepped the earth packed into a road and reddened at the edges"),
        ("Roar",   "it roared; the sound carved a line in the ground toward the marsh and everyone who heard it flinched"),
        ("Flame",  "it knelt at the edge of the camp and the red flame came down over everyone"),
        ("Raze",   "it tore the {structures} out of the ground"),
        ("Wait",   "it stood in the wreck and did nothing, and everyone watched it do nothing"),
        ("Roar",   "it roared again, from nearer"),
        ("Beacon", "it set something burning in one of the old ruined basins; the light was red and did not go out"),
        ("Flame",  "the flame again, lower, nearer"),
        ("Raze",   "it tore the ground again"),
    ],
}


def world_tick(L: dict) -> list:
    """The being acts once per watch. Returns the delta log."""
    log = []
    W = L["world"]
    t = L["meta"]["turn"]
    tint = W["being_tint"]
    if W["being_distance"] == "far":
        verb, line = FAR_SCRIPT[(t - 1) % len(FAR_SCRIPT)]
        W["being_last_act"] = {"verb": verb, "line": line, "turn": t, "distance": "far"}
        if verb not in W["being_seen_verbs"]:
            W["being_seen_verbs"].append(verb)
        log.append(f"the being (far): {verb} — {line}")
        _seated_pull(L, log)
        return log

    sgn = 1 if tint == "hope" else -1
    script = NEAR_SCRIPT[tint]
    verb, line = script[(t - RULES["turns_per_day"] - 1) % len(script)]
    line = line.format(structures=W["places"]["structures"])
    present = [L["band"][i] for i in _present(L)]
    everyone = present + [L["player"]]
    names = [n["name"] for n in present] + [L["player"]["name"]]

    if verb == "Walk":
        W["roads"].append({"turn": t, "colour": POLE_COLOUR[tint]})
    elif verb == "Flame":
        for p, nm in zip(everyone, names):
            _apply_pressure(p, RULES["flame_push"] * sgn, log, nm)
    elif verb == "Roar":
        for p, nm in zip(everyone, names):
            _apply_pressure(p, -RULES["roar_fear_push"], log, nm)
    elif verb == "Raze":
        for p, nm in zip(everyone, names):
            _apply_pressure(p, -RULES["raze_fear_spike"], log, nm)
    elif verb == "Beacon":
        W["beacons"].append({"turn": t, "colour": POLE_COLOUR[tint]})
        L["facts"].append(f"Turn {t}: a basin was lit {POLE_COLOUR[tint]} and has not gone out")
    elif verb == "Wait":
        for p, nm in zip(everyone, names):
            if p["emotion"]:
                _apply_pressure(p, -RULES["wait_apathy_pull"] if p["emotion"] > 0 else RULES["wait_apathy_pull"], log, nm)

    if verb not in W["being_seen_verbs"]:
        W["being_seen_verbs"].append(verb)
    W["being_last_act"] = {"verb": verb, "line": line, "turn": t, "distance": "near"}
    log.insert(0, f"the being: {verb} — {line}")

    if W["beacons"]:
        for p, nm in zip(everyone, names):
            _apply_pressure(p, RULES["beacon_aura"] * sgn * len(W["beacons"]), log, nm)
    _seated_pull(L, log)
    return log


def _seated_pull(L: dict, log: list) -> None:
    """A zealot among the cast moves the people around them, every watch."""
    present = [L["band"][i] for i in _present(L)]
    everyone = present + [L["player"]]
    names = [n["name"] for n in present] + [L["player"]["name"]]
    for z in everyone:
        if z.get("zealot") and not z["burned"]:
            zs = 1 if z["emotion"] > 0 else -1
            for p, nm in zip(everyone, names):
                if p is not z:
                    _apply_pressure(p, RULES["seated_zealot_pull"] * zs, log, nm)


def sleep(L: dict) -> list:
    """The vigil. A night passes: grief, contagion, the fog. Never the era."""
    log = ["SLEEP — the vigil; a night passes"]
    W = L["world"]
    W["sleeps"] += 1
    s = W["sleeps"]
    present = [L["band"][i] for i in _present(L)]
    everyone = present + [L["player"]]
    names = [n["name"] for n in present] + [L["player"]["name"]]

    # The first dawn decides the being's colour. Canon: counterpoint, not
    # opposite — the white flame is undetermined. POLICY: the roll made at the
    # start of the playthrough decides it, so every perspective meets a
    # different world and nobody can steer the god.
    if W["being_tint"] == "drift":
        W["being_tint"] = "hope" if L["_roll"] >= 0.5 else "fear"
        W["being_distance"] = "near"
        log.append(f"THE FIRST DAWN: the white flame took a colour — {POLE_COLOUR[W['being_tint']]}; the being came down off the ridge")
        L["facts"].append(f"Sleep {s}: the flame stopped being white. It is {POLE_COLOUR[W['being_tint']]} now, and the tall one is near.")
        L["meta"]["act"] = 2

    fog = W["grief_front"]["active"]
    at_zealot = W["camp"] in (z["where"] for z in L["zealots"].values())
    for p, nm in zip(everyone, names):
        if p["burned"]:
            continue
        others = [q["emotion"] for q in everyone if q is not p]
        same = sum(1 for o in others if o * p["emotion"] > 0) if p["emotion"] else 0
        pull = min(RULES["peer_contagion_cap"], RULES["peer_contagion"] * same)
        if pull and p["emotion"]:
            _apply_pressure(p, pull * (1 if p["emotion"] > 0 else -1), log, nm)
        held = abs(p["emotion"]) >= 8 and at_zealot
        if fog and held:
            continue  # canon: inside the front grief exactly cancels the pull — a stall
        if p["emotion"] != 0:
            _apply_pressure(p, -RULES["grief_decay_per_sleep"] if p["emotion"] > 0 else RULES["grief_decay_per_sleep"], log, nm)

    # The era never moves: a run is a snapshot in time (Director ruling, 2026-08-21).

    n = len(everyone)
    hope = sum(1 for p in everyone if p["emotion"] >= 3 and not p["burned"]) / n
    fear = sum(1 for p in everyone if p["emotion"] <= -3 and not p["burned"]) / n
    W["dominance"] = {"hope": round(hope, 2), "fear": round(fear, 2), "grey": round(1 - hope - fear, 2)}
    gf = W["grief_front"]
    if gf["active"]:
        gf["sleeps_left"] -= 1
        if gf["sleeps_left"] <= 0:
            gf["active"] = False
            log.append("the fog lifted")
            L["facts"].append(f"Sleep {s}: the grey fog lifted")
    else:
        winner = "hope" if hope >= RULES["grief_front_dominance"] else ("fear" if fear >= RULES["grief_front_dominance"] else None)
        if winner:
            gf.update({"active": True, "sleeps_left": RULES["grief_front_sleeps"], "on": winner})
            L["meta"]["act"] = 3
            log.append(f"GRIEF FRONT: the fog condensed on the {winner} camp")
            L["facts"].append(f"Sleep {s}: a grey fog came down on the camp. Inside it nobody deepens, and the unshepherded go grey.")

    W["watch"] = "first light"
    L["history"].append(f"Night {s}: " + "; ".join(log[1:4]))
    return log


WATCHES = ["first light", "high sun", "dusk"]


def advance_turn(L: dict) -> None:
    L["meta"]["turn"] += 1
    L["world"]["watch"] = WATCHES[(L["meta"]["turn"] - 1) % RULES["turns_per_day"]]


def night_falls(L: dict) -> bool:
    return L["meta"]["turn"] % RULES["turns_per_day"] == 0


def check_end(L: dict) -> str | None:
    P = L["player"]
    if P["burned"]:
        return "burned"
    if abs(P["emotion"]) >= 12 and not P.get("started_zealot"):
        return "zealot"
    if not _present(L):
        return "alone"
    if L["meta"]["turn"] >= RULES["story_turns"]:
        return "dawn"
    return None


def ledger_view(L: dict) -> dict:
    v = copy.deepcopy(L)
    v.pop("_roll", None)
    return v


def dumps(L: dict) -> str:
    return json.dumps(ledger_view(L), indent=2, ensure_ascii=False)


def diff(before: dict, after: dict, path: str = "") -> list:
    """Flat list of 'path: old -> new' for everything that changed."""
    out = []
    if isinstance(before, dict) and isinstance(after, dict):
        for k in sorted(set(before) | set(after)):
            if k.startswith("_"):
                continue
            out += diff(before.get(k, "∅"), after.get(k, "∅"), f"{path}.{k}" if path else k)
    elif isinstance(before, list) and isinstance(after, list):
        if len(after) > len(before):
            for item in after[len(before):]:
                out.append(f"{path} += {json.dumps(item, ensure_ascii=False)}")
        elif before != after:
            out.append(f"{path}: {json.dumps(before, ensure_ascii=False)} -> {json.dumps(after, ensure_ascii=False)}")
    elif before != after:
        out.append(f"{path}: {json.dumps(before, ensure_ascii=False)} -> {json.dumps(after, ensure_ascii=False)}")
    return out
