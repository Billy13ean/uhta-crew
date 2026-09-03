"""Red-Teamer — the attack surface, in prose and in machine-readable form.

Input:  the Keeper's packet + the selected variant + the Designer's rationale.
Output: `attacks-vN.md` (for the Director) and `attacks.json` (for the machine).

`attacks.json` is the load-bearing half and the reason this agent cannot be
removed. It is the Playtester's arm list: each probe names a bot policy from a
fixed whitelist, a seed list, a sleep cap, a pole, and a falsifiable invariant.
The Playtester runs exactly these arms and nothing else. Delete this agent and
the Playtester has nothing to execute — the pipeline halts at stage 5 naming
`red-teamer` rather than quietly falling back to a baseline sweep and emitting a
metrics file that reads like evidence for a variant it never tested.

The prose file is not decoration either: it carries the *intent* behind each
probe, which is what the Playtester reads to turn a number into a verdict.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..llm import LLMCall
from . import AgentError, json_blocks, markdown_block

PROMPT_VERSION = "red-teamer v4 (crew port)"

ALLOWED_BOTS = {
    "bot_do_nothing", "bot_wait_once", "bot_walk_one", "bot_throughput",
    "make_flamer", "run_tyrant", "run_campaign_v3", "run_siege", "run_selfburn",
    "run_campaign_v3_audit",   # 2026-09-03: the 3.10-stat audit shim (policy_shims.py) — runner
}                              # and prompt knew it; this validator was the missed third copy
SAFETY_BOTS = {"bot_do_nothing", "run_selfburn", "bot_wait_once", "bot_walk_one"}
MAX_PROBES = 8


def _validate_attacks_json(data, agent: str, seeds: list[int]) -> dict:
    if not isinstance(data, dict) or "probes" not in data:
        raise AgentError(agent, "attacks.json must be an object with a 'probes' list.")
    probes = data.get("probes")
    if not isinstance(probes, list) or not probes:
        raise AgentError(agent, "attacks.json 'probes' must be a non-empty list.")
    cleaned = []
    for i, p in enumerate(probes[:MAX_PROBES]):
        if not isinstance(p, dict):
            raise AgentError(agent, f"probe #{i} is not an object.")
        bot = p.get("bot")
        if bot not in ALLOWED_BOTS:
            raise AgentError(
                agent,
                f"probe {p.get('id', i)} names bot '{bot}', which the harness cannot "
                f"run. Allowed: {', '.join(sorted(ALLOWED_BOTS))}.",
            )
        if not str(p.get("invariant", "")).strip():
            raise AgentError(agent, f"probe {p.get('id', i)} has no 'invariant'.")
        s = p.get("seeds")
        if not isinstance(s, list) or not s or not all(isinstance(x, int) for x in s):
            s = list(seeds)
        cleaned.append({
            "id": str(p.get("id") or f"P{i+1}"),
            "attack_id": str(p.get("attack_id") or ""),
            "name": str(p.get("name") or ""),
            "bot": bot,
            "seeds": s[:40],
            "max_sleeps": int(p.get("max_sleeps") or 25),
            "poles": p.get("poles") or [-1, 1],
            "player_pole": int(p.get("player_pole") or 1),
            "args": p.get("args") or {},
            "invariant": str(p["invariant"]).strip(),
            "falsification_metric": str(p.get("falsification_metric") or ""),
            "severity_if_confirmed": str(p.get("severity_if_confirmed") or "TUNING"),
        })
    if not any(c["bot"] in SAFETY_BOTS for c in cleaned):
        raise AgentError(
            agent,
            "attacks.json contains no safety-regression probe. At least one probe "
            "must use a passive control (bot_do_nothing / run_selfburn / "
            "bot_wait_once / bot_walk_one): a ruleset that breaks the passive "
            "baseline is broken regardless of how it handles clever play.",
        )
    data["probes"] = cleaned
    return data


def run_red_teamer(bb, llm, ctx, selected_variant: str) -> dict:
    agent = "red-teamer"
    # --- HARD DEPENDENCIES ---
    bb.require(ctx.packet_name, agent, "keeper-b1")
    bb.require(selected_variant, agent, "mechanic-designer")
    bb.require(ctx.rationale_name, agent, "mechanic-designer")

    packet = bb.read(ctx.packet_name, agent, "keeper-b1")
    variant_json = bb.read(selected_variant, agent, "mechanic-designer")
    rationale = bb.read(ctx.rationale_name, agent, "mechanic-designer")

    prompt = (ctx.prompts_dir / "red-teamer.md").read_text(encoding="utf-8")
    system, _, template = prompt.partition("## SYSTEM")
    user = (template
            .replace("{{CONTEXT_PACKET}}", packet)
            .replace("{{VARIANT_NAME}}", selected_variant)
            .replace("{{CHOSEN_VARIANT_JSON}}", variant_json)
            .replace("{{DESIGNER_RATIONALE}}", rationale)
            .replace("{{SEED_LIST}}", json.dumps(ctx.seeds)))

    out = llm.complete(LLMCall(
        agent=agent,
        system="You are the Red-Teamer for uhta. " + system.strip()[:400],
        user=user, temperature=0.2, max_tokens=16000,
    ))

    md = markdown_block(out)
    blocks = json_blocks(out)
    if not blocks:
        raise AgentError(
            agent,
            "response contained no ```json fence. attacks.json is mandatory: it is "
            "the Playtester's arm list, and without it there is nothing to execute.",
        )
    parsed = None
    err = ""
    for b in reversed(blocks):
        try:
            cand = json.loads(b)
        except json.JSONDecodeError as exc:
            err = str(exc)
            continue
        if isinstance(cand, dict) and "probes" in cand:
            parsed = cand
            break
    if parsed is None:
        raise AgentError(agent, f"no parseable attacks.json object found ({err}).")

    parsed["target"] = parsed.get("target") or selected_variant
    parsed = _validate_attacks_json(parsed, agent, ctx.seeds)

    if len(md) < 300 or "##" not in md:
        raise AgentError(agent, f"attacks markdown is implausibly thin ({len(md)} chars).")
    if getattr(llm, "name", "") == "mock":
        md = llm.FIXTURE_BANNER + "\n" + md

    bb.write(ctx.attacks_md_name, md + "\n", agent)
    bb.write(ctx.attacks_json_name, json.dumps(parsed, indent=2) + "\n", agent)
    bb.note(agent, f"specified {len(parsed['probes'])} probe(s): "
                   + ", ".join(f"{p['id']}:{p['bot']}" for p in parsed["probes"]))
    return parsed
