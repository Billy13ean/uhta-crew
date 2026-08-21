#!/usr/bin/env python3
"""sonder — a text adventure in the world of uhta, run by a Claude Dungeon Master.

  python sonder.py                       serve the terminal at http://127.0.0.1:8765 (live DM; needs ANTHROPIC_API_KEY)
  python sonder.py --mock                same, no API calls (templated DM; proves the engine, not the judgement)
  python sonder.py --cli                 play in this terminal instead of the browser
  python sonder.py --script scripts/loyal.txt [--seed 7]
                                         replay a scripted playthrough, log it to sessions/
  python sonder.py --batch 6 [--mock]    run six scripted playthroughs (scripts\*.txt × fresh seeds), then --compile
  python sonder.py --compile [--include-mock]
                                         fold every finished playthrough in sessions/ into bank/sonder-bank.{json,js}
  python sonder.py --selftest            rules + gate + mock engine assertions, no key

Each playthrough rolls an era (camps / villages / Victorian towns) and deals you one of that era's six —
descendants of the six nomads. You do not choose. (--as / --era force a deal for testing only.)
The ledger is written to sessions/<id>/ every turn.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import world, story, style_gate, agent  # noqa: E402
from engine.session import Session  # noqa: E402


def load_env():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------------------------------------------------------------------------
def selftest() -> int:
    n = 0

    def ok(cond, msg):
        nonlocal n
        n += 1
        if not cond:
            print(f"SELFTEST FAILED at #{n}: {msg}")
            sys.exit(1)

    # the deal: three eras, six people each, never chosen — rolled from the seed
    from engine import cast
    ok(set(cast.CASTS) == {"nomad camps", "villages", "Victorian towns"}, "three eras")
    for era, c in cast.CASTS.items():
        ok(len(c) == 6 and {m["line"] for m in c.values()} == set(cast.CASTS["nomad camps"]), f"{era}: six people, one per bloodline")
        for pid, m in c.items():
            ok(m["trusts"] in c and m["doubts"] in c, f"{era}/{pid}: trusts/doubts point into the cast")
            ok(pid in story.OPENINGS and story.OPENINGS[pid].startswith(f"You are {m['name']}"), f"{era}/{pid}: has an opening")
            L = world.new_ledger(pid, seed=1)
            ok(L["world"]["era"] == era and L["player"]["name"] == m["name"] and pid not in L["band"] and len(L["band"]) == 5, f"{pid}: dealt into {era}")
            ok(L["player"]["habit"] == cast.CASTS["nomad camps"][m["line"]]["habit"], f"{pid}: carries {m['line']}'s habit")
    eras, people = set(), set()
    for sd in range(40):
        L = world.new_ledger(seed=sd)
        eras.add(L["world"]["era"]); people.add(L["meta"]["perspective"])
    ok(len(eras) == 3 and len(people) >= 12, f"the roll reaches every era and most people (eras {len(eras)}, people {len(people)})")
    # a seated zealot: sometimes one of the cast, sometimes you; pinned, pulls others, can still break
    seats = {"none": 0, "you": 0, "other": 0}
    for sd in range(60):
        L = world.new_ledger(seed=sd)
        z = L["meta"]["seated_zealot"]
        seats["none" if not z else ("you" if z["id"] == L["meta"]["perspective"] else "other")] += 1
    ok(all(v > 0 for v in seats.values()), f"the seat rolls all three ways: {seats}")
    Lz = next(world.new_ledger(seed=sd) for sd in range(60) if (world.new_ledger(seed=sd)["meta"]["seated_zealot"] or {}).get("id") == world.new_ledger(seed=sd)["meta"]["perspective"])
    ok(Lz["player"]["zealot"] and abs(Lz["player"]["emotion"]) == 12 and world.check_end(Lz) is None, "a zealot player does not end the story on turn zero")
    ok(all(n["trust"] >= 0 for n in Lz["band"].values()) , "they look to you: trust starts no lower than even")
    world.advance_turn(Lz); lg = world.world_tick(Lz)
    ok(any("->" in x for x in lg) or all(abs(n["emotion"]) >= 1 for n in Lz["band"].values()), "a zealot's pull moves the people around them every watch")
    zp = {"emotion": 12, "band": "zealot", "pole": "hope", "burned": False, "burned_colour": None, "alive": True, "tends": 0, "zealot": True}
    world._apply_pressure(zp, -2.8, [], "z")
    ok(zp["emotion"] == 12, "a zealot has stopped moving: a roar does not move them")
    world._apply_pressure(zp, 5.0, [], "z")
    ok(zp["burned"] and not zp["zealot"], "...but too much of their own colour still breaks them")

    # the colour is undetermined until the first dawn, then fixed by the roll
    L = world.new_ledger("ila", seed=3)
    ok(L["world"]["being_tint"] == "drift", "white flame at start")
    rolls = set()
    for sd in range(12):
        Ls = world.new_ledger("ila", seed=sd)
        Ls["meta"]["turn"] = 3
        world.sleep(Ls)
        rolls.add(Ls["world"]["being_tint"])
    ok(rolls == {"hope", "fear"}, "both colours are reachable across seeds")
    # a snapshot in time: four nights, the era never moves
    L = world.new_ledger("ilse", seed=2)
    for _ in range(4):
        L["meta"]["turn"] += 3
        world.sleep(L)
    ok(L["world"]["era"] == "villages" and L["world"]["sleeps"] == 4, "the era never shifts across nights")

    # heirlooms: one object per bloodline, re-made per age, and it can be handed on
    for era_h, c in cast.CASTS.items():
        for pid, m in c.items():
            ok(cast.heirloom(m["line"], era_h), f"{era_h}/{pid}: has an heirloom")
    Lh = world.new_ledger("ila", seed=1)
    ok("red stitch" in Lh["player"]["heirloom"] and "river-stone" in Lh["band"]["wystan"]["heirloom"], "heirlooms dealt with the person")
    world.advance_turn(Lh)
    world.apply_action(Lh, {"verb": "share", "target": "tate", "tone": "hope", "gives_heirloom": True, "summary": "Ila gave Tate the skin"})
    ok(Lh["player"]["heirloom"] is None and Lh["band"]["tate"]["carried"] and Lh["band"]["tate"]["heirloom_from"] == "Ila", "the object changes hands")
    ok(any("has it now" in f for f in Lh["facts"]), "the handing-on is a fact")

    # the two caps
    p = {"emotion": 0, "band": "grey", "pole": "grey", "burned": False, "burned_colour": None, "alive": True, "tends": 0}
    log = []
    world._apply_pressure(p, 5.0, log, "x")
    ok(p["emotion"] == 1, "step cap: +5.0 moves one step")
    p["emotion"] = 9
    world._apply_pressure(p, 5.0, log, "x")
    ok(p["burned"] and p["emotion"] == 0 and p["burned_colour"] == "hope", "burnout: same-colour overload on the devout breaks them")
    world._tend(p, "hope", log, "x")
    ok(p["burned"], "same-colour tending does nothing")
    world._tend(p, "fear", log, "x"); world._tend(p, "fear", log, "x")
    ok(not p["burned"] and p["emotion"] == -3, "the save: opposite colour, twice")

    # actions write facts the narrator must honour
    L = world.new_ledger("brand", seed=5)
    world.advance_turn(L)
    world.apply_action(L, {"verb": "promise", "target": "hild", "tone": "hope", "promise": "I will not leave you", "summary": "Brand promised Hild"})
    ok(any("promised Hild" in f for f in L["facts"]), "promise recorded as a fact")
    world.advance_turn(L)
    world.apply_action(L, {"verb": "abandon", "target": "hild", "tone": "fear", "summary": "Brand left Hild"})
    ok(L["promises"][0]["kept"] is False, "abandoning the person breaks the promise")
    ok(L["band"]["hild"]["trust"] == -3 and L["betrayals"], "betrayal tracked, trust floored")
    ok(any("was broken" in f for f in L["facts"]), "broken promise is a fact")
    ok(L["band"]["oswy"]["trust"] == 0, "the band saw the abandonment; everyone's trust dropped")
    L["band"]["oswy"]["trust"] = 2
    world.advance_turn(L)
    world.apply_action(L, {"verb": "follow_zealot", "target": "red_standing", "tone": "fear", "summary": "Brand went to the ridge"})
    ok(not L["band"]["hild"]["present"], "those who do not trust you stay behind")
    ok(L["band"]["oswy"]["present"], "those who trust you follow")
    ok(L["world"]["camp"] == L["world"]["places"]["red"], "camp moved")
    Lz = world.new_ledger("ila", seed=1); world.advance_turn(Lz)
    world.apply_action(Lz, {"verb": "follow_zealot", "target": "green_standing", "tone": "fear", "summary": "Ila went to the marsh, afraid"})
    ok(Lz["world"]["camp"] == "the low marsh", "a named Standing One beats the tone (live finding, ila-260820-220654-45f5)")
    # an absent person cannot be acted on
    world.advance_turn(L)
    lg = world.apply_action(L, {"verb": "share", "target": "hild", "tone": "hope", "summary": "Brand shared with Hild"})
    ok(any("is not here" in x for x in lg), "acting on the absent is refused by the rules")

    # the being: far and colourless in Act I, then its acts land
    L = world.new_ledger("tate", seed=2)
    for _ in range(3):
        world.advance_turn(L)
        lg = world.world_tick(L)
        ok(all("->" not in x for x in lg), "Act I: the far being moves nobody")
    lg = world.sleep(L)
    ok(L["world"]["being_distance"] == "near" and L["world"]["being_tint"] in ("hope", "fear"), "first dawn: colour + arrival")
    ok(L["meta"]["act"] == 2, "act advanced")
    world.advance_turn(L)
    world.world_tick(L)
    world.advance_turn(L)
    lg = world.world_tick(L)
    ok(any("->" in x for x in lg) or any(w in " ".join(lg) for w in ("Flame", "Roar")), "Act II: the being's act lands")

    # the grief front fires on the winner, not on nobody
    L = world.new_ledger("hild", seed=9)
    for member in L["band"].values():
        member["emotion"] = 9; member["band"] = "devout"; member["pole"] = "hope"
    L["player"]["emotion"] = 9
    L["meta"]["turn"] = 3
    world.sleep(L)
    ok(L["world"]["grief_front"]["active"] and L["world"]["grief_front"]["on"] == "hope", "fog condenses on the winner")
    L2 = world.new_ledger("hild", seed=9)
    L2["meta"]["turn"] = 3
    world.sleep(L2)
    ok(not L2["world"]["grief_front"]["active"], "no winner, no fog (canon: cannot fire in a do-nothing run)")

    # style gate
    ok(any(f["rule"] == "F2" for f in style_gate.run_gate("You gained 14 points")), "gate: digits")
    ok(any(f["rule"] == "F3" for f in style_gate.run_gate("Run!")), "gate: exclamation")
    ok(any(f["rule"] == "V3" for f in style_gate.run_gate("Press E to open the menu")), "gate: interface words")
    ok(any(f["rule"] == "V1" for f in style_gate.run_gate("The old gods are angry")), "gate: the old gods")
    ok(any(f["rule"] == "V2" for f in style_gate.run_gate("Your morale drops")), "gate: game-economy nouns")
    ok(any(f["rule"] == "Z1" for f in style_gate.run_gate("Brand is a zealot now")), "gate: the word zealot is never written")
    ok(style_gate.press_gate("Ila holds out the skin. Will you take it?") == [], "press gate: a closing question passes")
    ok(style_gate.press_gate("Ila holds out the skin. 'Tell me what to do.'") == [], "press gate: a closing demand passes")
    ok(style_gate.press_gate("The fire stayed out. Everyone slept.") , "press gate: a turn with nothing to react to is flagged")
    # the press is true to the ledger: the fearful act fearful, the hopeful hopeful
    Lp = world.new_ledger("ila", seed=1); Lp["meta"]["turn"] = 1
    for mb in Lp["band"].values():
        mb["emotion"] = -9; mb["band"] = "devout"; mb["pole"] = "fear"
    pr = story.pick_press(Lp)
    ok(pr["state"] == "devout fear" and pr["who"] in Lp["band"], f"press comes from a present person in their colour: {pr['state']}")
    for mb in Lp["band"].values():
        mb["emotion"] = 9; mb["band"] = "devout"; mb["pole"] = "hope"
    ok(story.pick_press(Lp)["state"] == "devout hope", "the same people, hopeful, press hopefully")
    ok("hopeful act hopeful" in story.behaviour_block(Lp), "behaviour block handed to the narrator")
    ok(story.opening(Lp).count("\n\n") >= 2, "the opening ends on a press")
    ok(world.describe(12) == "unmoving hope" and "zealot" not in world.describe(-12), "describe(): no 'zealot' in player-facing words")
    ok(any(f["rule"] == "F2" for f in style_gate.run_gate("Fourteen sleeps passed")), "gate: spelled-out sim quantity")
    ok(style_gate.run_gate("Ila looked at the ridge and said nothing. The fire stayed out.") == [], "gate: clean prose passes")
    L = world.new_ledger("brand", seed=1)
    L["band"]["hild"]["present"] = False; L["band"]["hild"]["where"] = "stayed behind"
    cf = style_gate.consistency_gate('"Come back," Hild said.', L)
    ok(cf and cf[0]["rule"] == "CONSISTENCY", "consistency: the absent do not speak")
    L["band"]["oswy"]["burned"] = True
    ok(style_gate.consistency_gate("Oswy whispers something.", L), "consistency: the burned do not speak")
    ok(style_gate.consistency_gate("Oswy stands frozen, ringed in red.", L) == [], "consistency: describing the burned is fine")

    # the whole engine, mock DM, a full playthrough to the fourth dawn
    import tempfile, json
    with tempfile.TemporaryDirectory() as td:
        quiet_seed = next(sd for sd in range(100) if world.new_ledger("ila", seed=sd)["meta"]["seated_zealot"] is None)
        s = Session(agent.MockDM(), "ila", seed=quiet_seed, log_dir=Path(td), era="nomad camps")
        ok((s.dir / "transcript.md").exists() and (s.dir / "ledger.json").exists(), "session logs created")
        script = ["share the water with Tate", "tell Wystan I believe him about the river", "promise Hild I will not leave her",
                  "walk toward the tall one", "stand with Tate", "wait", "go to the ridge camp", "abandon Hild", "wait",
                  "confess", "stand with Tate", "wait"]
        recs = [s.turn(x) for x in script]
        ok(len(recs) == 12 and recs[-1]["ending"] == "dawn", f"twelve turns to the dawn (got {recs[-1].get('ending')})")
        ok(all((s.dir / f"turn-{i:02d}.json").exists() for i in range(1, 13)), "every turn logged with its ledger")
        ok(any("promised Hild" in f for f in s.L["facts"]) and any("was broken" in f for f in s.L["facts"]), "facts carried across turns")
        ok(recs[2]["diff"] and any("promises +=" in d for d in recs[2]["diff"]), "diff shows the promise landing")
        ok(recs[3]["header"]["act"] == 2 and recs[3]["header"]["tint"] in ("hope", "fear"), "first dawn after turn three")
        ok(all(r["art"] for r in recs), "every turn has art")
        ok(recs[-1]["epilogue"] and recs[-1]["epilogue"].rstrip().endswith("?"), "epilogue ends on the choice — a question")
        ok(recs[-1]["choice"] and recs[-1]["choice"]["question"].endswith("?"), "the choice is recorded")
        ok(recs[-1]["telling"].rstrip().endswith("?"), "the telling ends on the question too")
        ok(recs[-1]["telling"] and (s.dir / "story.json").exists(), "the telling + story.json written at the end")
        st = json.loads((s.dir / "story.json").read_text(encoding="utf-8"))
        ok(st["schema"] == "sonder-story/1" and len(st["beats"]) == 12 and st["flame"] in ("hope", "fear"), "story record shape")
        ok("broke-a-promise" in st["tags"] and "went-to-the-ridge" in st["tags"], f"tags derived from the ledger: {st['tags']}")
        from engine import bank
        b0 = bank.compile(Path(td), Path(td) / "bank", include_mock=False)
        ok(b0["count"] == 0 and b0["skipped"], "mock stories are excluded from the bank by default")
        b1 = bank.compile(Path(td), Path(td) / "bank", include_mock=True)
        ok(b1["count"] == 1 and (Path(td) / "bank" / "sonder-bank.js").read_text(encoding="utf-8").startswith("// generated"), "bank compiles with --include-mock")
        ok(b1["index"]["by_flame"][st["flame"]] == [s.id], "bank indexed by flame")
        ok(style_gate.second_person("You walked into the flame."), "telling gate: second person caught")
        ok(style_gate.second_person("Ila walked into the flame.") == [], "telling gate: third person passes")
        # the ended session refuses more turns
        ok(s.turn("anything")["kind"] == "ended", "ended session stays ended")
        # every person in every era plays to the end without error
        for era_c in cast.CASTS.values():
          for pid in era_c:
            s2 = Session(agent.MockDM(), pid, seed=11, log_dir=Path(td))
            last = None
            for x in ["wait"] * 12:
                last = s2.turn(x)
                if last.get("ending"):
                    break
            ok(last and last.get("ending"), f"{pid}: reaches an ending")
            ok(last["ledger"]["world"]["era"] == s2.L["meta"]["era"], f"{pid}: era held")
    print(f"SELFTEST PASSED — {n} assertions, no API calls")
    return 0


# ---------------------------------------------------------------------------
def strip_tags(s: str) -> str:
    import re
    return re.sub(r"\{/?[a-z]?\}", "", s)


def cli(dm, perspective, seed, script: list[str] | None, era=None):
    s = Session(dm, perspective, seed=seed, era=era)
    print(f"\nsonder — {s.L['world']['era']} — you are {s.L['player']['name']}   [session {s.id}]")
    for a in s.opening["art_text"]:
        print(strip_tags(a))
    print(s.opening["text"], "\n")
    i = 0
    while not s.ended:
        if script is not None:
            if i >= len(script):
                break
            text = script[i]; i += 1
            print(f"> {text}")
        else:
            try:
                text = input(f"[{s.header()['watch']}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print(); break
            if not text:
                continue
            if text in ("/ledger", "/l"):
                print(world.dumps(s.L)); continue
            if text in ("/facts", "/f"):
                print("\n".join(s.L["facts"])); continue
            if text in ("/quit", "/q"):
                break
        rec = s.turn(text)
        print()
        for a in rec["art_text"]:
            print(strip_tags(a))
        print(f"— {rec['header']['act_title']} · {rec['header']['watch']} · sleeps {rec['header']['sleeps']} · you are {rec['header']['you']}")
        print(rec["text"], "\n")
        print("  rules: " + " | ".join(rec["log"]))
        if rec["style_findings"]:
            print("  gate: " + "; ".join(f"{f['rule']} {f['detail']}" for f in rec["style_findings"]))
        if rec["epilogue"]:
            print("\n" + rec["epilogue"])
    print(f"\nlogged to sessions/{s.id}/  (transcript.md, ledger.json, turn-NN.json)")
    if getattr(dm, "calls", 0):
        print(f"API calls: {dm.calls}, tokens in/out: {dm.in_tokens}/{dm.out_tokens}")


def main():
    ap = argparse.ArgumentParser(description="sonder — a text adventure in the world of uhta")
    ap.add_argument("--mock", action="store_true", help="no API calls; templated DM")
    ap.add_argument("--cli", action="store_true", help="play in this terminal")
    ap.add_argument("--script", help="file of player lines, one per turn (implies --cli)")
    ap.add_argument("--as", dest="perspective", default=None, help="TESTING: force the person (an id from engine/cast.py)")
    ap.add_argument("--era", default=None, choices=["nomad camps", "villages", "Victorian towns"], help="TESTING: force the era")
    ap.add_argument("--dev-pick", action="store_true", help="TESTING: let the page choose era/person")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--model", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--compile", action="store_true", help="build bank/sonder-bank.json + .js from sessions/")
    ap.add_argument("--batch", type=int, default=0, help="run N scripted playthroughs back to back (cycling scripts/*.txt, fresh seeds), then compile")
    ap.add_argument("--include-mock", action="store_true", help="--compile: also bank mock-DM stories (templated tellings)")
    ap.add_argument("--include-legacy", action="store_true", help="--compile: also bank pre-ruling stories that have no closing question")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if a.compile:
        from engine import bank
        b = bank.compile(ROOT / "sessions", ROOT / "bank", include_mock=a.include_mock, include_legacy=a.include_legacy)
        print(f"bank: {b['count']} stories ({b['clean_count']} with a gate-clean telling); skipped {len(b['skipped'])}")
        for k, v in b["index"]["by_flame"].items():
            print(f"  flame {k}: {len(v)}")
        for k, v in b["index"]["by_ending"].items():
            print(f"  ending {k}: {len(v)}")
        for sk in b["skipped"][:8]:
            print(f"  - skipped {Path(sk['path']).parent.name}: {sk['why']}")
        print("-> bank/sonder-bank.json, bank/sonder-bank.js")
        sys.exit(0)
    load_env()
    try:
        dm = agent.build_dm(a.mock, a.model)
    except agent.DMError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
    if a.batch:
        import glob, random as _r
        scripts = sorted(glob.glob(str(ROOT / "scripts" / "*.txt")))
        base = a.seed if a.seed is not None else int(time.time()) % 100000
        for i in range(a.batch):
            sc = scripts[i % len(scripts)]
            seed = base + i * 7919
            lines = [l.strip() for l in Path(sc).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
            print(f"\n=== batch {i+1}/{a.batch}: {Path(sc).name}, seed {seed} ===")
            try:
                cli(dm, None, seed, lines, None)
            except Exception as e:  # one bad run must not sink the batch
                print(f"run failed: {type(e).__name__}: {e}")
        from engine import bank
        b = bank.compile(ROOT / "sessions", ROOT / "bank", include_mock=a.mock)
        print(f"\nbank: {b['count']} stories ({b['clean_count']} gate-clean); by flame {dict((k, len(v)) for k, v in b['index']['by_flame'].items())}; by era {dict((k, len(v)) for k, v in b['index']['by_era'].items())}")
        return
    if a.script or a.cli:
        script = None
        if a.script:
            script = [l.strip() for l in Path(a.script).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        cli(dm, a.perspective, a.seed, script, a.era)
        return
    from engine.server import serve
    serve(dm, port=a.port, default_seed=a.seed, open_browser=not a.no_browser, allow_pick=a.dev_pick)


if __name__ == "__main__":
    main()
