"""session.py — one playthrough: the loop, the logs, the gate.

Per turn:
  1. INTERPRET   player text -> structured action      (model, temperature 0)
  2. RULES       apply_action, world_tick, maybe sleep  (code)
  3. NARRATE     ledger + deltas -> prose                (model)
  4. GATE        style + consistency checks             (code; one retry)
  5. ART         pictures chosen from the ledger         (code)
  6. LOG         sessions/<id>/turn-NN.json (full ledger, diff, findings),
                 sessions/<id>/transcript.md, sessions/<id>/ledger.json
"""
from __future__ import annotations

import copy
import json
import re
import time
import uuid
from pathlib import Path

from . import world, story, style_gate, art

SESSIONS = Path(__file__).resolve().parent.parent / "sessions"


class Session:
    def __init__(self, dm, perspective: str | None = None, seed: int | None = None, session_id: str | None = None,
                 log_dir: Path | None = None, era: str | None = None):
        self.dm = dm
        seed = int(time.time() * 1000) % 100000 if seed is None else seed
        self.L = world.new_ledger(perspective, seed, era)
        perspective = self.L["meta"]["perspective"]
        self.id = session_id or f"{perspective}-{time.strftime('%y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        self.dir = (log_dir or SESSIONS) / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.turns: list[dict] = []
        self.ended: str | None = None
        opening = story.opening(self.L)
        self._write_ledger()
        with open(self.dir / "transcript.md", "w", encoding="utf-8") as f:
            f.write(f"# sonder — {self.L['player']['name']} — session {self.id}\n\n")
            f.write(f"DM backend: **{dm.name}** ({getattr(dm, 'model', '')}). Seed {seed}. Era: {self.L['world']['era']}. Dealt: {self.L['player']['name']}.\n\n")
            f.write(f"## Opening\n\n{opening}\n\n")
        self.opening = {
            "kind": "opening", "act": 1, "act_title": story.ACTS[1][0],
            "text": opening, "art": story.opening_art(self.L),
            "art_text": story.render_art(story.opening_art(self.L)),
            "ledger": world.ledger_view(self.L),
            "header": self.header(),
        }

    # -- helpers --------------------------------------------------------------
    def header(self) -> dict:
        W = self.L["world"]
        return {
            "act": self.L["meta"]["act"], "act_title": story.ACTS[self.L["meta"]["act"]][0],
            "turn": self.L["meta"]["turn"], "watch": W["watch"], "sleeps": W["sleeps"],
            "era": W["era"], "tint": W["being_tint"], "camp": W["camp"],
            "fog": W["grief_front"]["active"], "you": world.describe(self.L["player"]["emotion"]) if not self.L["player"]["burned"] else "burned",
            "name": self.L["player"]["name"], "ended": self.ended,
        }

    def _write_ledger(self):
        (self.dir / "ledger.json").write_text(world.dumps(self.L), encoding="utf-8")

    def _gate(self, text: str) -> list[dict]:
        return (style_gate.run_gate(text) + style_gate.consistency_gate(text, self.L)
                + style_gate.heirloom_gate(text, self.L))   # L1: objects locked to lines (2026-08-23)

    # -- the turn -------------------------------------------------------------
    def turn(self, player_text: str) -> dict:
        if self.ended:
            return {"kind": "ended", "text": "The story has ended. Start again to be someone else.", "header": self.header()}
        player_text = player_text.strip()[:600]
        before = world.ledger_view(self.L)
        snapshot = copy.deepcopy(self.L)
        try:
            return self._turn(player_text, before)
        except Exception:
            self.L = snapshot  # a failed call must not leave a half-applied watch behind
            raise

    def _turn(self, player_text: str, before: dict) -> dict:
        world.advance_turn(self.L)
        t = self.L["meta"]["turn"]

        action = self.dm.interpret(self.L, player_text)
        logs = [f"you: {action.get('summary', '')}"]
        logs += world.apply_action(self.L, action)
        logs += world.world_tick(self.L)
        slept = False
        if world.night_falls(self.L):
            logs += world.sleep(self.L)
            slept = True
        ending = world.check_end(self.L)

        press = None if ending else story.pick_press(self.L)
        # REVIEW BEFORE POST (Director, 2026-08-23): every draft is gated BEFORE the
        # player sees anything, with up to TWO review passes, and the cleanest draft
        # ships. Findings go to the session log only — never into the page; a reader
        # should feel the story, and the log should carry the honesty.
        text = self.dm.narrate(self.L, player_text, action, logs, press=press)
        findings = self._gate(text) + (style_gate.press_gate(text) if press else [])
        retried = 0
        while findings and retried < 2 and self.dm.name != "mock":
            retried += 1
            text2 = self.dm.narrate(self.L, player_text, action, logs, retry=findings, press=press)
            findings2 = self._gate(text2) + (style_gate.press_gate(text2) if press else [])
            if len(findings2) < len(findings) or (len(findings2) == len(findings) and retried == 1):
                text, findings = text2, findings2

        self.L["history"].append(f"Turn {t} ({self.L['world']['watch'] if not slept else 'dusk, then the vigil'}): {action.get('summary', '')}")
        epilogue = telling = choice = None
        telling_findings = []
        if ending:
            self.ended = ending
            self.L["meta"]["ended"] = ending
            epilogue = self.dm.epilogue(self.L, ending)
            ef = style_gate.run_gate(epilogue)
            if ef and self.dm.name != "mock":
                epilogue = self.dm.epilogue(self.L, ending)  # one more try, then ship
            # THE CHOICE (Director ruling 2026-08-21): every story ends on a question.
            beats = [{"turn": x["turn"], "did": x["action"].get("summary", ""), "verb": x["action"].get("verb"),
                      "became": [y for y in x["log"] if "->" in y or "BROKE" in y or "did not follow" in y]} for x in self.turns]
            beats.append({"turn": t, "did": action.get("summary", ""), "verb": action.get("verb"),
                          "became": [y for y in logs if "->" in y or "BROKE" in y or "did not follow" in y]})
            choice = self.dm.choice(self.L, beats)
            q = (choice.get("question") or "").strip()
            if not q.endswith("?"):
                q = q.rstrip(".") + "?"
            choice["question"] = q
            epilogue = epilogue.rstrip() + "\n\n" + q
            # the Sonder engine's record: the telling, third person, banked for the game
            telling = self.dm.telling(self.L, ending)
            telling_findings = style_gate.run_gate(telling) + style_gate.second_person(telling)
            if telling_findings and self.dm.name != "mock":
                t2 = self.dm.telling(self.L, ending)
                f2 = style_gate.run_gate(t2) + style_gate.second_person(t2)
                if len(f2) <= len(telling_findings):
                    telling, telling_findings = t2, f2
            telling = telling.rstrip() + "\n\n" + q   # the question is the last line the stranger reads
            self.L["history"].append(f"Turn {t}: the story ended — {ending}")

        after = world.ledger_view(self.L)
        delta = world.diff(before, after)
        art_keys = story.pick_art(self.L, action, logs, ending)
        rec = {
            "kind": "turn", "turn": t, "player_text": player_text, "action": action,
            "log": logs, "text": text, "epilogue": epilogue, "ending": ending,
            "telling": telling, "telling_findings": telling_findings, "choice": choice, "press": press,
            "style_findings": findings, "style_retried": retried,
            "art": art_keys, "art_text": story.render_art(art_keys),
            "ledger": after, "diff": delta, "header": self.header(),
            "dm": {"backend": self.dm.name, "model": getattr(self.dm, "model", ""), "calls": getattr(self.dm, "calls", 0)},
        }
        self.turns.append(rec)
        self._log(rec)
        if ending:
            self._write_story(rec)
        return rec

    def _write_story(self, rec: dict):
        """story.json — the Sonder engine's structured record of this playthrough."""
        from . import bank
        story_rec = bank.story_record(self, rec)
        (self.dir / "story.json").write_text(json.dumps(story_rec, indent=2, ensure_ascii=False), encoding="utf-8")
        with open(self.dir / "transcript.md", "a", encoding="utf-8") as f:
            f.write(f"## The choice\n\n{json.dumps(rec['choice'], ensure_ascii=False)}\n\n## The telling (banked for the game)\n\n{rec['telling']}\n\n")
            if rec["telling_findings"]:
                f.write("**telling gate findings:**\n\n" + style_gate.findings_text(rec["telling_findings"]) + "\n\n")

    def _log(self, rec: dict):
        (self.dir / f"turn-{rec['turn']:02d}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_ledger()
        with open(self.dir / "transcript.md", "a", encoding="utf-8") as f:
            f.write(f"## Turn {rec['turn']} — {rec['header']['act_title']} — {rec['header']['watch']}\n\n")
            f.write(f"> **{self.L['player']['name']}:** {rec['player_text']}\n\n")
            f.write(f"*interpreted:* `{json.dumps(rec['action'], ensure_ascii=False)}`\n\n")
            f.write("**rules:**\n\n" + "\n".join(f"- {x}" for x in rec["log"]) + "\n\n")
            f.write(rec["text"] + "\n\n")
            if rec["style_findings"]:
                f.write("**style/consistency findings (shipped with):**\n\n" + style_gate.findings_text(rec["style_findings"]) + "\n\n")
            elif rec["style_retried"]:
                f.write("*style gate: first draft rejected, retry passed.*\n\n")
            f.write("<details><summary>ledger diff</summary>\n\n" + "\n".join(f"- `{d}`" for d in rec["diff"]) + "\n\n</details>\n\n")
            if rec["epilogue"]:
                label = {"zealot": "stopped moving", "dawn": "the fourth dawn"}.get(rec["ending"], rec["ending"])
                f.write(f"## Epilogue — {label}\n\n{rec['epilogue']}\n\n")

    def state(self) -> dict:
        return {"id": self.id, "header": self.header(), "ledger": world.ledger_view(self.L),
                "facts": self.L["facts"], "turns": len(self.turns), "ended": self.ended}
