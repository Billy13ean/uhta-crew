"""agent.py — the Dungeon Master, in two halves, on the Claude API.

  INTERPRETER  reads what the player typed and returns a structured action
               (a forced tool call against a JSON schema). Temperature 0.
               It decides WHAT you did; it never decides what it DID — the
               rules in world.py do that.
  NARRATOR     is handed the ledger, the delta log (what the rules say just
               happened), the durable facts, and the act guidance, and writes
               the turn. It may not contradict the ledger; the style gate and
               the consistency gate check the prose in code and send it back
               once with findings if it fails.

Sole third-party dependency: `anthropic`. Model from $SONDER_MODEL (default
claude-sonnet-4-6). MockDM replays rule-based interpretations and templated
prose so the whole engine runs with no key — it proves the plumbing, not the
judgement, and every mock turn is stamped as such.
"""
from __future__ import annotations

import json
import os
import re

from . import world, story, style_gate

DEFAULT_MODEL = "claude-sonnet-4-6"


class DMError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# prompts
# ---------------------------------------------------------------------------
WORLD_BIBLE = """You are the Dungeon Master of SONDER, a text adventure set in the world of *uhta* (ūhta: the last part of the night, before dawn).

THE WORLD, AS CANON HAS IT
- The sky is grief. Uhtcearu, the world's god, is in mourning, and his grief is the gravity: left alone, every feeling in every person slides back toward grey. Apathy is what he leaves behind. He has no colour and fights for none; he drowns the board in grey. His active form is a grey fog that condenses on whichever colour is winning.
- People sit on one scale: deep Fear at one end (red), grey Apathy in the middle, deep Hope at the other (green). Four bands: grey, tentative, devout, zealot. Zealots have stopped moving entirely and now move others. Where a person sits is legible on sight: the colour they carry, how they stand, whether they follow anyone.
- Two caps: nobody moves more than one step at a time, and too much of the same pressure at once BREAKS a person — they freeze grey, ringed in the colour they carried. The burned do not speak. Only the opposite feeling can bring them back, and it costs more than the conversion would have.
- A tall, unnamed, kaiju-scale being has woken: the counterpoint to Uhtcearu, in the musical sense — a second voice, not predisposed to oppose grief with light. It carries a white flame that is genuinely undetermined until the first dawn, when it takes a colour. Its seven acts are Walk (where it steps the earth packs into a road of its colour), Flame (pushes everyone near toward its colour), Roar (pure Fear on everyone who hears it, whatever its colour), Beacon (lights one of the five old ruined basins; the light does not go out), Raze (tears structures out of the ground; Fear), Wait (witnessed inaction pulls toward grey), Sleep.
- Fear is the easy path: it breaks and coerces; many converts, every one shallow. Hope is the hard path: it must convert, wins by patience and depth; few converts, and they arrive already deep.
- The two founding zealots: the Red Standing One at the ridge camp, the Green Standing One at the low marsh. They are era-invariant and unnamed beyond that. Whoever goes to them is pulled hard.
- The world has three ages — nomad camps, then villages, then Victorian towns with clocktowers and smoking factories; roads age from compacted earth to paver stone. A story of SONDER happens inside ONE of them and never leaves it: a night passing is a night, not an age. Zealots, the burned and the being look the same in every age.
- The people of later ages descend from the six nomads of the first, and carry their habits. You are told the lineage privately; you never state it.
- Grief takes the stragglers; the shepherded stand.

THE STYLE (the uhta style guide — enforced by code after you write)
- Mournful, mythic, restrained. The comps are Journey and Gris, not epic fantasy. No enthusiasm, no triumph, no cheer, even when hope wins.
- Consequence over spectacle: land on what changed for people, not on how impressive anything is.
- Canonical nouns only: the god is Uhtcearu (never "the gods"); the being is unnamed ("the tall one", "the being", "it"); the flame is the white flame until it has a colour; poles are Hope and Fear; grey zero is Apathy; the frozen are the burned; the founders are the Standing Ones.
- The word "zealot" is never written in the story. The people who have stopped moving are shown by what they do and how others arrange themselves around them — never named as a kind of thing.
- No game-economy words: no mana, XP, karma, morale, sanity, stats, levels, quests, inventory, stamina.
- No interface language: no press, click, button, menu, screen, HUD, keys, commands. Never mention turns, ledgers or rules. Never write a number as digits, and never spell out counts of sleeps, steps or believers.
- No exclamation marks. Ever.
- People may speak, briefly, in short plain lines — they are nomads in a world that has mostly stopped talking. The player is addressed as "you".
- Length: two or three SHORT paragraphs, about a hundred and fifty words, with a hard ceiling of two hundred — if in doubt, cut the middle paragraph, never the press; the last paragraph is always THE PRESS — a person doing something toward you and wanting something, ending on a question or a demand. Plain prose, no headings, no lists, no markdown.

THE CONTRACT
- The ledger is the truth. You narrate what it says happened and nothing it says did not. If the log says Ila moved from grey to tentative fear, then Ila is afraid now, visibly. If it says Brand broke, he is frozen and silent from here on. If someone stayed behind at the fork, they are not here and cannot speak.
- React to the whole history, not the last line: a person you abandoned remembers it; a promise you kept is felt; a secret you confessed changes how the doubters look at you; trust in the ledger is what people show you.
- Do not invent new named people, places or events. Do not advance the plot yourself; the world's act this watch is given to you.
"""

INTERPRET_SYSTEM = """You are the action interpreter for a text adventure. The player is one person in a small nomad band. Read what they typed and record it as ONE structured action using the tool. Be literal about intent; do not narrate, do not moralise, do not invent. Ordinary camp work (gathering wood, looking for food, mending, walking the road, lying down to sleep) is verb "wait" — it moves nobody — but the summary must still say what they did, plainly and in the world ("Tate went looking for firewood"), never meta-commentary like "no action was recorded". A question to the band is verb "speak" with target null and the question as the summary. Only pure nonsense is "wait" with the summary "did nothing". If they name a person, map it to that person's id. If they name the marsh or the Green Standing One, target is green_standing; the ridge or the Red Standing One, red_standing — regardless of tone. Tone is the emotional colour of the act: "hope" if it comforts, steadies, includes, trusts; "fear" if it threatens, coerces, excludes, abandons, or is done out of dread; otherwise "neutral"."""

ACTION_TOOL = {
    "name": "record_action",
    "description": "Record the player's action for this watch.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verb": {"type": "string", "enum": list(world.ACTION_VERBS)},
            "target": {"type": ["string", "null"], "description": "id of the person acted on, or 'red_standing' / 'green_standing' for follow_zealot, or null"},
            "tone": {"type": "string", "enum": ["hope", "fear", "neutral"]},
            "promise": {"type": ["string", "null"], "description": "if verb is promise: what was promised, in a few words"},
            "gives_heirloom": {"type": "boolean", "description": "true only if the player hands their own carried object (named in the prompt) to the target person for keeps"},
            "summary": {"type": "string", "description": "one past-tense line, third person, naming the player by name: what they did"},
        },
        "required": ["verb", "target", "tone", "summary"],
    },
}


def interpret_user(L: dict, text: str) -> str:
    present = [f"- {pid}: {n['name']}, who {n['role']}" + ("" if n["present"] else f" [NOT HERE: {n['where']}]") + (" [BURNED, frozen]" if n["burned"] else "") + (f" [has stopped moving; {n['pole']} all through; the others follow them]" if n.get("zealot") else "")
               for pid, n in L["band"].items()]
    verbs = "\n".join(f"- {v}: {d}" for v, d in world.ACTION_VERBS.items())
    return (
        f"The player is {L['player']['name']} (who {L['player']['role']}).\n"
        f"People (id: name):\n" + "\n".join(present) +
        f"\nZealots: red_standing (the Red Standing One, ridge camp), green_standing (the Green Standing One, low marsh).\n"
        f"The being: 'the tall one' — use verb approach_being; it is not a person id.\n\n"
        f"Verbs:\n{verbs}\n\n"
        f"The player's private secret (for 'confess'): {L['player']['private']}\n"
        f"The player carries: {L['player']['heirloom'] or 'nothing now (already given away)'} — set gives_heirloom=true only if they hand it to someone for keeps.\n\n"
        f"The player typed:\n\"\"\"{text}\"\"\""
    )


def narrate_user(L: dict, player_text: str, action: dict, logs: list[str], retry_findings: list[dict] | None, press: dict | None = None) -> str:
    act_title, act_line = story.ACTS[L["meta"]["act"]]
    view = world.ledger_view(L)
    view.pop("history", None)
    compact = {
        "turn": L["meta"]["turn"], "watch": L["world"]["watch"], "sleeps": L["world"]["sleeps"],
        "era": L["world"]["era"], "camp": L["world"]["camp"],
        "being": {"tint": L["world"]["being_tint"], "distance": L["world"]["being_distance"],
                  "last_act": L["world"]["being_last_act"], "basins_lit": len(L["world"]["beacons"])},
        "grief_front": L["world"]["grief_front"],
        "you": {k: L["player"][k] for k in ("name", "role", "emotion", "band", "pole", "burned", "burned_colour", "zealot", "heirloom")},
        "band": {pid: {k: n.get(k) for k in ("name", "emotion", "band", "pole", "burned", "burned_colour", "trust", "present", "where", "zealot", "heirloom", "carried")}
                 for pid, n in L["band"].items()},
        "promises": L["promises"], "betrayals": L["betrayals"], "loyalties": L["loyalties"][-6:],
    }
    parts = [
        f"ACT {L['meta']['act']} — {act_title}. {act_line}",
        f"GUIDANCE: {story.beat_guidance(L)}",
        "",
        story.lineage_note(L),
        "",
        "THE LEDGER (truth; numbers are for you, never for the prose):",
        json.dumps(compact, ensure_ascii=False, indent=1),
        "",
        "DURABLE FACTS (never contradict these):",
        "\n".join(f"- {f}" for f in L["facts"][-18:]) or "- (none yet)",
        "",
        "RECENT HISTORY:",
        "\n".join(f"- {h}" for h in L["history"][-5:]) or "- (the story begins)",
        "",
        f"THE PLAYER TYPED: \"{player_text}\"",
        f"INTERPRETED AS: {action.get('summary', '')}  (verb={action.get('verb')}, target={action.get('target')}, tone={action.get('tone')})",
        "",
        "WHAT THE RULES SAY HAPPENED THIS WATCH (narrate all of it, in this order: the player's act and its consequences, then the being's act, then the night if there was one):",
        "\n".join(f"- {x}" for x in logs),
        "",
        story.behaviour_block(L),
    ]
    if press:
        parts += ["", story.press_block(press)]
    if retry_findings:
        parts += ["", "YOUR PREVIOUS DRAFT WAS REJECTED BY THE STYLE GATE. Fix every finding below and rewrite the whole turn:",
                  style_gate.findings_text(retry_findings)]
    parts += ["", "Write the turn now. Prose only."]
    return "\n".join(parts)


def epilogue_user(L: dict, ending: str) -> str:
    why = {
        "burned": f"{L['player']['name']} broke under too much of the same colour and is frozen grey, ringed in {L['player']['burned_colour']}. The burned do not speak; the story ends from outside them.",
        "zealot": f"{L['player']['name']} stopped moving. They are {world.POLE_COLOUR[L['player']['pole']]} all the way through now, and the grey will not take them, and they will move others.",
        "alone": f"Everyone has left or is gone. {L['player']['name']} is alone at {L['world']['camp']}.",
        "dawn": "The fourth dawn. The story ends here, wherever everyone stands.",
    }[ending]
    band = "\n".join(
        f"- {n['name']}: {world.describe(n['emotion']) if not n['burned'] else 'burned (' + n['burned_colour'] + ')'}"
        f", trust {n['trust']:+d}, {'here' if n['present'] else n['where']}"
        for n in L["band"].values())
    return (
        f"EPILOGUE. {why}\n\n"
        f"The flame's colour: {world.POLE_COLOUR[L['world']['being_tint']]}. Era: {L['world']['era']}. "
        f"Fog: {'down' if L['world']['grief_front']['active'] else 'not down'}. "
        f"You: {world.describe(L['player']['emotion']) if not L['player']['burned'] else 'burned'}.\n"
        f"Where everyone ended:\n{band}\n\n"
        f"Promises: {json.dumps(L['promises'], ensure_ascii=False)}\nBetrayals: {json.dumps(L['betrayals'], ensure_ascii=False)}\n"
        f"Facts:\n" + "\n".join(f"- {f}" for f in L["facts"][-14:]) +
        "\n\nWrite the epilogue: one paragraph, the teacher's voice returning once at the very end, "
        "mournful, exact about who ended where and what the player's choices cost or kept. "
        "Then a single closing line that names, without numbers, what the world will look like a generation on. No exclamation marks, no digits."
    )


def telling_user(L: dict, ending: str) -> str:
    """The Sonder engine's output: this person's experience, told as the game
    would tell it to another player — third person, past tense, Register B.
    No 'you' (F4 applies here: the teacher's voice is not in this). This is
    what gets banked and, one day, shown when the being converts someone."""
    P = L["player"]
    tint = L["world"]["being_tint"]
    who = "nobody" if tint == "drift" else world.POLE_COLOUR[tint]
    band = "; ".join(
        f"{n['name']} ended {('burned, ringed in ' + n['burned_colour']) if n['burned'] else world.describe(n['emotion'])}"
        + ("" if n["present"] else f" ({n['where']})") for n in L["band"].values())
    return (
        f"Write THE TELLING: the story of {P['name']} (who {P['role']}) as it will be told, later, to a stranger — "
        f"a god who is {who if who != 'nobody' else 'white'}-flamed, passing through, who will never meet {P['name']} and will only hear this.\n\n"
        f"The being's colour was {who}. {P['name']}'s ending: {ending}. "
        f"{P['name']} ended {('burned, ringed in ' + str(P['burned_colour'])) if P['burned'] else world.describe(P['emotion'])}.\n"
        f"The others: {band}.\n"
        f"Promises: {json.dumps(L['promises'], ensure_ascii=False)}. Betrayals: {json.dumps(L['betrayals'], ensure_ascii=False)}.\n"
        f"What happened, in order:\n" + "\n".join(f"- {h}" for h in L["history"][-16:]) + "\n"
        f"Facts:\n" + "\n".join(f"- {f}" for f in L["facts"][-14:]) +
        f"\nThe era is {L['world']['era']}; the telling stays in it."
        "\n\nRules for the telling: THIRD PERSON ONLY — never 'you', never 'I'. Past tense. Four to six sentences, under ninety words. Do not end on a question; the question is put separately. "
        "Name the person, say what the flame was to them, say one thing they did that mattered and what it cost or kept, and end on where they stand now. "
        "Mournful, exact, no moral. No digits, no exclamation marks, no interface words. Plain prose, nothing else."
    )


CHOICE_TOOL = {
    "name": "record_choice",
    "description": "Name the one fork in this playthrough worth putting back to a stranger as a question.",
    "input_schema": {
        "type": "object",
        "properties": {
            "turn": {"type": "integer", "description": "the watch where the fork was"},
            "did": {"type": "string", "description": "what the person did, one plain clause, third person, past tense"},
            "could_have": {"type": "string", "description": "the other road they did not take, one plain clause"},
            "question": {"type": "string", "description": "the question put to a stranger, second person is allowed here, one sentence ending in a question mark, no digits, no exclamation marks, in the uhta register — e.g. 'Ila drank the good water herself. Would you have given it to the child?'"},
        },
        "required": ["turn", "did", "could_have", "question"],
    },
}

CHOICE_SYSTEM = """You read one finished playthrough of SONDER and find THE CHOICE: the single fork where what this person did mattered most to someone else — water drunk or shared, a promise kept or dropped, a secret told or held, a brother struck or stood with, a road taken to the ridge or the marsh, a runner followed or left. Prefer a fork with a real cost on both sides over a dramatic one. If the person mostly waited, the fork is the thing they did not do. Put it back to a stranger as ONE question in the uhta register: plain, mournful, no moral, no digits, no exclamation marks. Use the tool."""


def choice_user(L: dict, beats: list[dict]) -> str:
    rows = "\n".join(f"- watch {b['turn']}: {b['did']} -> {'; '.join(b['became']) or 'nothing moved'}" for b in beats)
    return (
        f"{L['player']['name']}, who {L['player']['role']}. Era: {L['world']['era']}. The flame was {world.POLE_COLOUR[L['world']['being_tint']]}. Ending: {L['meta']['ended']}.\n"
        f"Private truth: {L['player']['private']} (told: {L['player']['private_told']}).\n"
        f"Promises: {json.dumps(L['promises'], ensure_ascii=False)}\nBetrayals: {json.dumps(L['betrayals'], ensure_ascii=False)}\n"
        f"What they did, watch by watch:\n{rows}\n\nFacts:\n" + "\n".join(f"- {f}" for f in L["facts"][-14:])
    )


# ---------------------------------------------------------------------------
# backends
# ---------------------------------------------------------------------------
class LiveDM:
    name = "live"

    def __init__(self, model: str | None = None):
        try:
            import anthropic
        except ImportError as e:
            raise DMError("the `anthropic` package is not installed: pip install -r requirements.txt") from e
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise DMError("ANTHROPIC_API_KEY is not set (put it in .env) — or run with --mock, which makes no calls")
        self.model = model or os.environ.get("SONDER_MODEL") or DEFAULT_MODEL
        self.client = anthropic.Anthropic(api_key=key)
        self.calls = 0
        self.in_tokens = 0
        self.out_tokens = 0

    def _count(self, resp):
        self.calls += 1
        u = getattr(resp, "usage", None)
        if u:
            self.in_tokens += getattr(u, "input_tokens", 0) or 0
            self.out_tokens += getattr(u, "output_tokens", 0) or 0

    def interpret(self, L: dict, text: str) -> dict:
        resp = self.client.messages.create(
            model=self.model, max_tokens=400, temperature=0,
            system=INTERPRET_SYSTEM, tools=[ACTION_TOOL],
            tool_choice={"type": "tool", "name": "record_action"},
            messages=[{"role": "user", "content": interpret_user(L, text)}])
        self._count(resp)
        for b in resp.content:
            if getattr(b, "type", "") == "tool_use":
                a = dict(b.input)
                if a.get("verb") not in world.ACTION_VERBS:
                    a["verb"] = "wait"
                return a
        raise DMError("interpreter returned no tool call")

    def _text(self, system: str, user: str, max_tokens: int = 700, temperature: float = 0.6) -> str:
        resp = self.client.messages.create(
            model=self.model, max_tokens=max_tokens, temperature=temperature,
            system=system, messages=[{"role": "user", "content": user}])
        self._count(resp)
        if getattr(resp, "stop_reason", None) == "refusal":
            raise DMError("the model refused this turn (stop_reason=refusal); try rephrasing")
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()

    def narrate(self, L: dict, player_text: str, action: dict, logs: list[str], retry: list[dict] | None = None, press: dict | None = None) -> str:
        return self._text(WORLD_BIBLE, narrate_user(L, player_text, action, logs, retry, press))

    def epilogue(self, L: dict, ending: str) -> str:
        return self._text(WORLD_BIBLE, epilogue_user(L, ending), max_tokens=600)

    def telling(self, L: dict, ending: str) -> str:
        return self._text(WORLD_BIBLE, telling_user(L, ending), max_tokens=400, temperature=0.5)

    def choice(self, L: dict, beats: list[dict]) -> dict:
        resp = self.client.messages.create(
            model=self.model, max_tokens=400, temperature=0.3,
            system=CHOICE_SYSTEM, tools=[CHOICE_TOOL],
            tool_choice={"type": "tool", "name": "record_choice"},
            messages=[{"role": "user", "content": choice_user(L, beats)}])
        self._count(resp)
        for b in resp.content:
            if getattr(b, "type", "") == "tool_use":
                return dict(b.input)
        raise DMError("the choice call returned no tool call")


class MockDM:
    """No API. Keyword interpreter + templated prose. Proves the engine, not the DM."""
    name = "mock"
    model = "mock (no API calls)"
    calls = in_tokens = out_tokens = 0

    KEYWORDS = [
        ("confess", ["confess", "the truth", "admit", "secret", "what i did"]),
        ("promise", ["promise", "swear", "i will always", "i won't leave"]),
        ("abandon", ["abandon", "leave him", "leave her", "leave them", "leave tate", "leave brand", "without"]),
        ("strike", ["strike", "hit", "punch", "stab", "kill", "attack"]),
        ("threaten", ["threaten", "warn him", "warn her", "or else", "menace", "shut", "keep quiet"]),
        ("withhold", ["refuse", "withhold", "keep the water", "hoard", "turn away", "ignore", "take ", "steal", "for myself"]),
        ("tend", ["tend", "care for", "hold him", "hold her", "nurse", "warm him", "warm her"]),
        ("follow_zealot", ["ridge camp", "red standing", "the red one", "marsh", "green standing", "the green one"]),
        ("approach_being", ["tall one", "the being", "flame", "walk toward it", "approach it", "go to it"]),
        ("flee", ["run", "flee", "escape", "hide"]),
        ("share", ["share", "give", "water", "food", "offer"]),
        ("stand_with", ["stand with", "stay with", "comfort", "protect", "shield", "sit with", "hold"]),
        ("speak", ["say", "tell", "ask", "talk", "speak", "sing", "story", "\""]),
        ("wait", ["wait", "nothing", "sleep", "watch", "sit"]),
    ]
    FEAR_WORDS = ["threat", "afraid", "fear", "run", "kill", "hit", "leave", "abandon", "refuse", "red", "ridge", "or else"]
    HOPE_WORDS = ["comfort", "hold", "share", "give", "promise", "stay", "protect", "song", "sing", "green", "marsh", "warm", "truth"]

    def interpret(self, L: dict, text: str) -> dict:
        low = text.lower()
        verb = "wait"
        for v, keys in self.KEYWORDS:
            if any(k in low for k in keys):
                verb = v
                break
        target = None
        for pid, n in L["band"].items():
            if n["name"].lower() in low or pid in low:
                target = pid
                break
        if verb == "follow_zealot":
            target = "red_standing" if ("ridge" in low or "red" in low) else "green_standing"
        if verb in ("tend", "stand_with", "share", "withhold", "threaten", "strike", "abandon", "promise") and not target:
            target = next((pid for pid, n in L["band"].items() if n["present"]), None)
        tone = "neutral"
        if any(w in low for w in self.HOPE_WORDS):
            tone = "hope"
        if any(w in low for w in self.FEAR_WORDS):
            tone = "fear"
        if verb in ("stand_with", "share", "tend", "promise") and tone == "neutral":
            tone = "hope"
        if verb in ("strike", "threaten", "abandon", "withhold", "flee") and tone == "neutral":
            tone = "fear"
        gives = bool(target) and any(w in low for w in ("give", "hand", "pass")) and any(w in low for w in ("skin", "stone", "spear", "hammer", "mallet", "comb", "cloth", "feather", "flask", "bucket", "it to"))
        return {"verb": verb, "target": target, "tone": tone, "gives_heirloom": gives,
                "promise": text[:60] if verb == "promise" else None,
                "summary": f"{L['player']['name']} {verb.replace('_', ' ')}" + (f" ({L['band'][target]['name']})" if target in L["band"] else "")}

    def narrate(self, L, player_text, action, logs, retry=None, press=None):
        # templated, digit-free so the real style gate has nothing to say about the fixture
        lines = ["[mock DM — templated prose, no model; the deltas below are the rules' own words]"]
        for x in logs:
            x = re.sub(r"\s*trust -> ([+-]?)\d+", lambda m: " trust " + ("grew" if m.group(1) != "-" else "fell"), x)
            x = re.sub(r"\(\d+/\d+\)", "", x)
            x = re.sub(r"\d+(\.\d+)?", "some", x)
            lines.append(x.replace("!", ""))
        if press:
            lines.append("")
            lines.append(press["text"] + ("" if press["text"].rstrip().endswith("?") else " What do you do?"))
        return "\n".join(lines)

    def epilogue(self, L, ending):
        return f"[mock DM] The story ended: {ending}. You are {world.describe(L['player']['emotion'])}."

    def choice(self, L, beats):
        b = next((x for x in beats if x["verb"] in ("share", "withhold", "abandon", "promise", "confess", "strike", "follow_zealot", "stand_with")), beats[-1] if beats else {"turn": 0, "did": "did nothing"})
        return {"turn": b.get("turn", 0), "did": b.get("did", ""), "could_have": "done otherwise",
                "question": f"[mock DM] {b.get('did', 'They did nothing')}. Would you have done otherwise?"}

    def telling(self, L, ending):
        P = L["player"]
        col = world.POLE_COLOUR[L["world"]["being_tint"]]
        state = ("burned, ringed in " + str(P["burned_colour"])) if P["burned"] else world.describe(P["emotion"])
        return (f"[mock DM] {P['name']}, who {P['role']}, saw the flame turn {col}. "
                f"{P['name']} ended {state}. The telling is templated here; a live run writes the real one.")


def build_dm(mock: bool, model: str | None = None):
    return MockDM() if mock else LiveDM(model)
