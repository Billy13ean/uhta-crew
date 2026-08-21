"""bank.py — the Sonder engine: playthroughs become stories the game can tell.

Two layers:

  story_record(session, last_turn)   one playthrough -> sessions/<id>/story.json
      who you were, the flame's colour, every watch as a beat (what you did,
      what it changed, what the being did), the promises/betrayals, the
      ending, the epilogue, and THE TELLING — the third-person retelling the
      DM writes at the end, style-gated for Register B (no 'you').

  compile(sessions_dir, out_dir)     all story.json -> bank/sonder-bank.json
                                                      + bank/sonder-bank.js
      indexed by flame colour, ending and tags, so the slice can ask
      "a fear-flame story about someone who broke" and get one.

The bank is data for a surface the game does not yet have. Canon (GDD §1
Tone, ruled v0.9.2) says the game is wordless after the first dawn; where a
telling appears — on a conversion, in an encounter's text scope under the
2026-08-19 amendment, on the endscreen — is a Director ruling this engine
does not make. It only makes the ruling cheap: the stories are banked,
tagged, gated and ready.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import world

SCHEMA_STORY = "sonder-story/1"
SCHEMA_BANK = "sonder-bank/1"


def _tags(L: dict, ending: str, turns: list[dict]) -> list[str]:
    tags = [f"flame:{L['world']['being_tint']}", f"ending:{ending}", f"who:{L['meta']['perspective']}"]
    verbs = [t["action"].get("verb") for t in turns]
    if L["betrayals"]:
        tags.append("betrayed-someone")
    if any(p["kept"] is False for p in L["promises"]):
        tags.append("broke-a-promise")
    if L["promises"] and all(p["kept"] for p in L["promises"]):
        tags.append("kept-every-promise")
    if "confess" in verbs and L["player"]["private_told"]:
        tags.append("confessed")
    if L["world"]["camp"] == L["world"]["places"]["red"]:
        tags.append("went-to-the-ridge")
    if L["world"]["camp"] == L["world"]["places"]["green"]:
        tags.append("went-to-the-marsh")
    if any(t["action"].get("verb") == "approach_being" and t["header"]["act"] >= 2 for t in turns):
        tags.append("walked-into-the-flame")
    if any("GRIEF FRONT" in "\n".join(t["log"]) for t in turns):
        tags.append("saw-the-fog")
    if any(" BROKE " in "\n".join(t["log"]) for t in turns):
        tags.append("someone-broke")
    if any(n["burned"] for n in L["band"].values()):
        tags.append("left-someone-burned")
    if any(t["action"].get("verb") == "tend" for t in turns):
        tags.append("tended-the-burned")
    if any(t["action"].get("verb") in ("strike",) for t in turns):
        tags.append("struck-someone")
    you = L["player"]
    tags.append("you:" + (("burned-" + str(you["burned_colour"])) if you["burned"] else world.describe(you["emotion"]).replace(" ", "-")))
    tags.append(f"era:{L['world']['era'].replace(' ', '-')}")
    tags.append(f"line:{L['player']['line']}")
    if L["player"].get("heirloom_given_to"):
        tags.append("handed-it-on")
    z = L["meta"].get("seated_zealot")
    if z:
        tags.append("you-were-the-zealot" if z["id"] == L["meta"]["perspective"] else f"zealot-among-you:{z['pole']}")
    return tags


def story_record(session, last: dict) -> dict:
    L = session.L
    beats = []
    for t in session.turns:
        became = [x for x in t["log"] if "->" in x or "BROKE" in x or "did not follow" in x or "came back" in x or "is not here" in x]
        beats.append({
            "turn": t["turn"], "watch": t["header"]["watch"], "act": t["header"]["act"],
            "you_typed": t["player_text"], "did": t["action"].get("summary", ""),
            "verb": t["action"].get("verb"), "tone": t["action"].get("tone"), "target": t["action"].get("target"),
            "became": became,
            "being": (L["world"]["being_last_act"] or {}).get("verb") if t is session.turns[-1] else next((x.split(":")[1].split("—")[0].strip() for x in t["log"] if x.startswith("the being")), None),
            "slept": any(x.startswith("SLEEP") for x in t["log"]),
            "art": t["art"],
            "narration": t["text"],
        })
    you = L["player"]
    return {
        "schema": SCHEMA_STORY,
        "session": session.id,
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dm": last["dm"],
        "seed": L["meta"]["seed"],
        "perspective": {"id": L["meta"]["perspective"], "name": you["name"], "role": you["role"], "line": you["line"], "private": you["private"], "private_told": you["private_told"],
                        "heirloom": you.get("heirloom"), "heirloom_given_to": you.get("heirloom_given_to")},
        "era": L["world"]["era"],
        "flame": L["world"]["being_tint"],
        "ending": last["ending"],
        "final": {
            "you": ("burned, ringed in " + str(you["burned_colour"])) if you["burned"] else world.describe(you["emotion"]),
            "emotion": you["emotion"], "burned": you["burned"],
            "era": L["world"]["era"], "fog": L["world"]["grief_front"]["active"], "camp": L["world"]["camp"],
            "sleeps": L["world"]["sleeps"], "basins_lit": len(L["world"]["beacons"]),
            "dominance": L["world"]["dominance"],
        },
        "band_end": {pid: {"name": n["name"],
                           "state": ("burned, ringed in " + str(n["burned_colour"])) if n["burned"] else world.describe(n["emotion"]),
                           "emotion": n["emotion"], "trust": n["trust"], "present": n["present"], "where": n["where"]}
                     for pid, n in L["band"].items()},
        "promises": L["promises"], "betrayals": L["betrayals"], "loyalties": L["loyalties"],
        "beats": beats,
        "facts": L["facts"],
        "epilogue": last["epilogue"],
        "choice": last.get("choice"),
        "telling": last["telling"],
        "telling_clean": not last["telling_findings"],
        "telling_findings": last["telling_findings"],
        "tags": _tags(L, last["ending"], session.turns),
    }


def compile(sessions_dir: Path, out_dir: Path, include_mock: bool = False) -> dict:
    stories, skipped = [], []
    for p in sorted(sessions_dir.glob("*/story.json")):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # a half-written file must not take the bank down
            skipped.append({"path": str(p), "why": f"unreadable: {e}"})
            continue
        if s.get("schema") != SCHEMA_STORY:
            skipped.append({"path": str(p), "why": "schema"}); continue
        if s["dm"]["backend"] == "mock" and not include_mock:
            skipped.append({"path": str(p), "why": "mock DM — templated telling, excluded by default"}); continue
        if not s.get("telling"):
            skipped.append({"path": str(p), "why": "no telling"}); continue
        stories.append({
            "id": s["session"], "recorded": s["recorded"], "dm": s["dm"]["backend"], "model": s["dm"].get("model", ""),
            "who": s["perspective"], "flame": s["flame"], "ending": s["ending"], "final": s["final"],
            "era": s.get("era"), "tags": s["tags"], "telling": s["telling"], "telling_clean": s["telling_clean"], "choice": s.get("choice"),
            "epilogue": s["epilogue"],
            "beats": [{"turn": b["turn"], "did": b["did"], "became": b["became"], "being": b["being"], "slept": b["slept"], "art": b["art"]} for b in s["beats"]],
            "band_end": s["band_end"], "promises": s["promises"], "betrayals": s["betrayals"],
        })
    index = {"by_flame": {}, "by_ending": {}, "by_who": {}, "by_tag": {}, "by_era": {}, "by_line": {}}
    for s in stories:
        index["by_era"].setdefault(s.get("era") or "?", []).append(s["id"])
        index["by_line"].setdefault(s["who"].get("line", s["who"]["id"]), []).append(s["id"])
        index["by_flame"].setdefault(s["flame"], []).append(s["id"])
        index["by_ending"].setdefault(s["ending"], []).append(s["id"])
        index["by_who"].setdefault(s["who"]["id"], []).append(s["id"])
        for t in s["tags"]:
            index["by_tag"].setdefault(t, []).append(s["id"])
    bank = {"schema": SCHEMA_BANK, "compiled": time.strftime("%Y-%m-%dT%H:%M:%S"), "count": len(stories),
            "clean_count": sum(1 for s in stories if s["telling_clean"]),
            "stories": stories, "index": index, "skipped": skipped}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sonder-bank.json").write_text(json.dumps(bank, indent=1, ensure_ascii=False), encoding="utf-8")
    # a script-tag form, because the slice is one HTML file opened from disk: no fetch, no CORS
    (out_dir / "sonder-bank.js").write_text("// generated by sonder.py --compile — do not edit\nwindow.SONDER_BANK = " +
                                            json.dumps(bank, ensure_ascii=False) + ";\n", encoding="utf-8")
    return bank
