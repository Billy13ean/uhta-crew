"""`--mock-llm` backend. NO API CALLS, NO DESIGN WORK.

It exists to prove the orchestration executes end to end without a key, exactly
as `crew/llm.py::MockLLM` does for the rules crew. Everything it returns is
canned or mechanically derived from the prompt it was handed, every artifact a
mock run produces is banner-stamped, and none of it is evidence about the
codebase.

The Programmer fixture is a real, valid patch against the committed build —
anchored on lines that exist, adding assertions that genuinely test the two rules
GDD §1 states about the narrated opening. That is deliberate: a mock that emits
something the validator would reject proves nothing about the validator.
"""
from __future__ import annotations

import json
import re

from crew.llm import BaseLLM

_FEATURE_LINE = re.compile(r"^- id=(\S+) · name=(.+?) · gdd_section=(\S+)", re.MULTILINE)
_CTX_LINE = re.compile(r"^\s*\d+ \| (.+)$", re.MULTILINE)


# --------------------------------------------------------------------------
# the narrated-opening patch — hand-authored, valid against the real build
# --------------------------------------------------------------------------

_NARRATION_INSERT = """
/* ---------- narrated teaching opening (GDD §1) — builder patch ----------------
   "A narrator names each verb the first time you use it; the words end
   permanently at your first Sleep." Two rules, and guide() satisfies neither: it
   tracks four categories of progress rather than per-VERB first use, and it never
   stops. Both resolvers below are PURE functions of (verb, spoken, sleep_no) so
   the headless self-test can gate them without Phaser, the same way eraOf() and
   roadStageFor() are gated. Presentation only — no sim state is written. */
const NARRATION={
  walk:'you move, and the ground remembers',
  flame:'you give them warmth',
  roar:'you give them fear',
  beacon:'you leave a light that does not sleep',
  raze:'you take what they made',
  wait:'you do nothing, and they feel it',
  sleep:'the words end here'};
const narrationOpen=(sleepNo)=>sleepNo===0;   // §1: permanently, not "until dismissed"
function narrationFor(verb,spoken,sleepNo){
  if(!narrationOpen(sleepNo))return null;     // after the first Sleep: silent forever
  if(!(verb in NARRATION))return null;
  if(spoken.has(verb))return null;            // first use only — per verb, not per category
  return NARRATION[verb];
}
"""

_NARRATION_ASSERTIONS = """  // ---- narration (GDD §1): per-verb first use, and a permanent stop at the first Sleep ----
  {
    const spoken=new Set();
    const a=narrationFor('flame',spoken,0); spoken.add('flame');
    const b=narrationFor('flame',spoken,0);
    const c=narrationFor('roar',spoken,0);
    out.push(['G12 narration: names each verb on FIRST use only', !!a&&b===null&&!!c,
      `flame#1 ${a?'spoke':'silent'}, flame#2 ${b?'spoke':'silent'}, roar#1 ${c?'spoke':'silent'}`]);
    const d=narrationFor('beacon',new Set(),1);
    const e=narrationFor('walk',new Set(),9);
    out.push(['G13 narration: words end PERMANENTLY at the first Sleep',
      d===null&&e===null&&narrationOpen(0)&&!narrationOpen(1),
      `after sleep 1 ${d===null?'silent':'spoke'}; after sleep 9 ${e===null?'silent':'spoke'}`]);
  }
"""

_PROGRAMMER_PATCH = {
    "summary": "Adds the narrated teaching opening's two GDD-specified rules as pure "
               "resolvers, and gates both with new self-test assertions.",
    "rationale": "Anchored above selfTest(), beside eraOf() and roadStageFor(), because selfTest() runs inline partway down this file and anything declared below it is in the temporal dead zone when the assertions execute. GDD §1 states two things about the opening: the narrator names each "
                 "verb the first time it is used, and the words end permanently at the "
                 "first Sleep. guide() satisfies neither — it keys off four progress "
                 "flags rather than per-verb first use, and it never stops. The "
                 "resolvers are pure functions of (verb, spoken, sleep_no) so the "
                 "headless self-test can gate them the way it already gates eraOf() "
                 "and roadStageFor(); nothing here writes sim state.",
    "anchor": "function eraOf(s){return s>=ERA_SLEEPS[1]?2:s>=ERA_SLEEPS[0]?1:0;}",
    "insert": _NARRATION_INSERT,
    "edits": [{
        "anchor": "  return out;",
        "replacement": _NARRATION_ASSERTIONS + "  return out;",
        "why": "the new assertions have to run before selfTest returns its results array",
    }],
    "selftest_anchor": "",
    "selftest_insert": "",
    "assertion_names": ["G12 narration: names each verb on FIRST use only",
                        "G13 narration: words end PERMANENTLY at the first Sleep"],
}


# --------------------------------------------------------------------------

def _analyst(user: str) -> str:
    """A signature per supplied feature, derived mechanically from its name."""
    feats = []
    for fid, name, section in _FEATURE_LINE.findall(user):
        words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if len(w) > 2]
        camel = words[0] + "".join(w.capitalize() for w in words[1:]) if words else fid
        feats.append({
            "id": fid, "name": name.strip(), "gdd_section": section, "kind": "system",
            "description": f"[fixture] {name.strip()}",
            "observable_signature": {
                "identifiers": list(dict.fromkeys(words + ["_".join(words), camel]))[:6],
                "constants": [], "rules_key_paths": ["world." + "_".join(words)] if words else [],
                "strings": words[:2],
            },
        })
    return "```json\n" + json.dumps(feats, indent=1) + "\n```"


def _gap(user: str) -> str:
    found = re.search(r"\*\*Signature elements FOUND in the source:\*\* (.+)", user)
    missing = re.search(r"\*\*Signature elements NOT found:\*\* (.+)", user)
    found_s = (found.group(1).strip() if found else "(none)")
    lines = [l for l in _CTX_LINE.findall(user) if l.strip()]
    if found_s != "(none)" and lines:
        quote = max(lines, key=len)[:150]
        body = {"verdict": "PARTIAL",
                "reason": "[fixture] some of the signature matched; a mock run does not "
                          "read code and this verdict is not evidence.",
                "quoted_code": quote, "searched_for": []}
    else:
        body = {"verdict": "ABSENT",
                "reason": "[fixture] nothing in the signature matched the indexed source.",
                "quoted_code": "",
                "searched_for": [s.strip() for s in
                                 (missing.group(1) if missing else "").split(",") if s.strip()][:8]
                                or ["(fixture)"]}
    return "```json\n" + json.dumps(body, indent=1) + "\n```"


class BuilderMockLLM(BaseLLM):
    """Resolves a canned response per agent role. Never contacts an API."""

    def __init__(self, logger=None):
        self.logger = logger
        self.calls = 0

    def complete(self, call) -> str:
        self.calls += 1
        agent = (call.agent or "").lower()
        if agent.startswith("analyst"):
            return _analyst(call.user)
        if agent.startswith("gap"):
            return _gap(call.user)
        if agent.startswith("programmer"):
            return "```json\n" + json.dumps(_PROGRAMMER_PATCH, indent=1) + "\n```"
        raise RuntimeError(f"no builder fixture for agent {call.agent!r}")
