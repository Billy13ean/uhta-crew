"""Mechanic Designer — 2-3 rules variants + a rationale table. GDD §3.1.

Input: the Keeper's packet (required — this agent never reads CANON directly) and
the ratified baseline JSON.
Output: `rules-vN-{A,B,C}.json` and `designer-rationale.md`.

Between this agent and everything downstream sits the deterministic validation
gate (`crew/validate.py`). It runs here, in this module, because a variant that
does not load is not a design proposal — it is a syntax error wearing one, and
the Red-Teamer should never see it. On failure the Designer gets exactly ONE
repair round-trip carrying the validator's own error text; a second failure
aborts the run (GDD §3.5, "validation happens before anything is compiled or
imported").
"""
from __future__ import annotations

import json
from pathlib import Path

from ..llm import LLMCall
from ..validate import ValidationResult, Validator
from . import AgentError, json_blocks
import copy

PROMPT_VERSION = "mechanic-designer v3 (crew port)"
LETTERS = ["A", "B", "C", "D"]

GAME_FRAMING = (
    "You are working on *uhta*, a fictional single-player browser video game "
    "about emotional contagion, built as a student capstone project. Every term "
    "below — NPC, tribe, convert, grief, burnout, wear, siege, zealot — names a "
    "simulated entity or a numeric state variable inside that game's simulation. "
    "Your task is game balance tuning: choosing numbers for a JSON configuration "
    "file that a browser build loads at boot. Nothing here describes, models, or "
    "is intended to apply to real people.\n\n"
)

def _extract_variants(text: str, agent: str) -> list[tuple[str, str]]:
    blocks = json_blocks(text)
    if not blocks:
        raise AgentError(
            agent,
            "response contained no fenced ```json block. The Designer must emit "
            "each variant as a complete rules file in its own json fence.",
        )
    out: list[tuple[str, str]] = []
    for i, b in enumerate(blocks):
        letter = LETTERS[i] if i < len(LETTERS) else f"X{i}"
        try:
            data = json.loads(b)
            v = str(data.get("meta", {}).get("variant", "")).strip().upper()
            if v and len(v) <= 2:
                letter = v
        except json.JSONDecodeError:
            pass  # the validator will report the parse failure properly
        out.append((letter, b))
    # de-duplicate letters, preserving order
    seen: set[str] = set()
    fixed: list[tuple[str, str]] = []
    for letter, b in out:
        L = letter
        k = 0
        while L in seen:
            k += 1
            L = f"{letter}{k}"
        seen.add(L)
        fixed.append((L, b))
    return fixed[:3]


def _rationale(text: str) -> str:
    """Everything that is not a json fence — the rationale table and notes."""
    import re
    stripped = re.sub(r"```json.*?```", "\n_(variant JSON emitted to its own file)_\n",
                      text, flags=re.DOTALL | re.IGNORECASE)
    return stripped.strip()

def _deep_merge(base, delta, prefix="", dropped=None):
    """Overlay delta onto base ONLY where the baseline already defines the path
    and the types agree. The baseline is the schema (crew/validate.py), so a
    variant cannot introduce a key the reference simulator has never seen --
    that is what failed check (c). `meta.*` is exempt: the harness never reads
    it, and it carries the variant's provenance."""
    if dropped is None:
        dropped = []
    permissive = prefix.startswith("meta")
    if isinstance(base, dict) and isinstance(delta, dict):
        out = copy.deepcopy(base)
        for k, v in delta.items():
            p = f"{prefix}{k}"
            if k in out:
                out[k] = _deep_merge(out[k], v, p + ".", dropped)
            elif permissive:
                out[k] = copy.deepcopy(v)
            else:
                dropped.append(f"{p} (not in baseline)")
        return out
    numeric = isinstance(base, (int, float)) and isinstance(delta, (int, float))
    if permissive or numeric or isinstance(base, type(delta)) or isinstance(delta, type(base)):
        return copy.deepcopy(delta)
    dropped.append(
        f"{prefix.rstrip('.')} (type {type(base).__name__} -> {type(delta).__name__})"
    )
    return copy.deepcopy(base)


def _changed_paths(base, merged, prefix=""):
    out = []
    if isinstance(base, dict) and isinstance(merged, dict):
        for k in merged:
            p = f"{prefix}{k}"
            if k not in base:
                out.append(f"{p} (new)")
            else:
                out.extend(_changed_paths(base[k], merged[k], p + "."))
    elif base != merged:
        out.append(f"{prefix.rstrip('.')}: {base!r} -> {merged!r}")
    return out


def _complete_variant(baseline_obj, body, letter, agent, bb):
    """The model proposes a DELTA over the ratified baseline. Code applies it.
    Untouched parameters cannot drift and invented parameters cannot enter."""
    try:
        delta = json.loads(body)
    except json.JSONDecodeError:
        return body
    if not isinstance(delta, dict):
        return body
    dropped: list[str] = []
    merged = _deep_merge(baseline_obj, delta, "", dropped)
    changed = _changed_paths(baseline_obj, merged)
    bb.note(agent, f"variant {letter}: merged onto baseline — "
                   f"{len(changed)} path(s) changed: "
                   + "; ".join(changed[:8]) + (" …" if len(changed) > 8 else ""))
    if dropped:
        bb.note(agent, f"variant {letter}: {len(dropped)} proposed path(s) DROPPED "
                       f"(not in the ratified baseline): "
                       + "; ".join(dropped[:8]) + (" …" if len(dropped) > 8 else ""))
    return json.dumps(merged, indent=2)

def run_mechanic_designer(bb, llm, ctx, validator: Validator) -> dict:
    agent = "mechanic-designer"
    # --- HARD DEPENDENCY: the Keeper's packet. No packet, no run. ---
    bb.require(ctx.packet_name, agent, "keeper-b1")
    packet = bb.read(ctx.packet_name, agent, "keeper-b1")

    prompt = (ctx.prompts_dir / "mechanic-designer.md").read_text(encoding="utf-8")
    _, _, body = prompt.partition("## SYSTEM")
    system, marker, rest = body.partition("## CONTEXT PACKET")
    template = marker + rest

    def build_user(repair: str) -> str:
        return (template
                .replace("{{CONTEXT_PACKET}}", packet)
                .replace("{{QUESTION_SET}}", ctx.question_set)
                .replace("{{REPAIR_BLOCK}}", repair))

    attempts: list[dict] = []
    repair_block = ""
    baseline_obj = json.loads(bb.read_bb(f"rules/{ctx.baseline_name}", agent))
    for attempt in (1, 2):
        out = llm.complete(LLMCall(
            agent=agent if attempt == 1 else f"{agent}-repair",
            system=GAME_FRAMING + system.strip(),
            user=build_user(repair_block), temperature=0.2, max_tokens=48000,
        ))
        variants = _extract_variants(out, agent)
        bb.note(agent, f"emitted {len(variants)} variant block(s) on attempt {attempt}: "
                       f"{', '.join(v for v, _ in variants)}")

        results: list[ValidationResult] = []
        for letter, body in variants:
            name = ctx.variant_name(letter)
            dest = bb.path(name)
            body = _complete_variant(baseline_obj, body, letter, agent, bb)
            res = validator.validate_text(body, letter, dest)
            results.append(res)
            bb.note("validation-gate", f"{res.summary()} -> `{name}`")
            if not res.ok:
                bb.note("validation-gate", f"  reason: {res.error.splitlines()[0][:200]}")
            else:
                # only a passing variant is recorded on the blackboard ledger as a
                # real artifact; a failing one is left on disk for the repair
                # round-trip but is never handed downstream.
                bb._record("write", "out", dest, agent, dest.read_bytes())

        attempts.append({
            "attempt": attempt,
            "variants": [
                {"variant": r.variant, "path": Path(r.path).name, "ok": r.ok,
                 "checks": r.checks, "error": r.error[:2000], "smoke": r.smoke}
                for r in results
            ],
        })

        valid = [r for r in results if r.ok]
        if valid:
            rationale = _rationale(out)
            if getattr(llm, "name", "") == "mock":
                rationale = llm.FIXTURE_BANNER + "\n" + rationale
            bb.write(ctx.rationale_name, rationale + "\n", agent)
            for r in results:
                if not r.ok:
                    Path(r.path).unlink(missing_ok=True)
            bb.write("validation.json",
                     json.dumps({"gate": "deterministic", "baseline": ctx.baseline_name,
                                 "required_key_paths": len(validator.required),
                                 "attempts": attempts,
                                 "accepted": [r.variant for r in valid]}, indent=2) + "\n",
                     "validation-gate")
            return {"valid": valid, "all": results, "attempts": attempts}

        if attempt == 1:
            errs = "\n\n".join(f"### Variant {r.variant}\n{r.error}" for r in results)
            repair_block = (
                "## REPAIR ROUND-TRIP — YOUR PREVIOUS OUTPUT FAILED THE VALIDATION GATE\n\n"
                "A deterministic validator ran your variants against the ratified "
                "baseline before any downstream agent saw them. Every variant failed. "
                "The exact errors are below. Re-emit ALL variants as COMPLETE rules "
                "files fixing these errors. This is your only repair attempt: a second "
                "failure aborts the run.\n\n" + errs + "\n"
            )
            bb.note("validation-gate",
                    "ALL variants invalid — dispatching ONE repair round-trip to the "
                    "Mechanic Designer with the validator's error text.")

    bb.write("validation.json",
             json.dumps({"gate": "deterministic", "baseline": ctx.baseline_name,
                         "required_key_paths": len(validator.required),
                         "attempts": attempts, "accepted": []}, indent=2) + "\n",
             "validation-gate")
    detail = "; ".join(
        f"{r['variant']}: {r['error'].splitlines()[0] if r['error'] else 'unknown'}"
        for r in attempts[-1]["variants"]
    )
    raise AgentError(
        agent,
        "no variant passed the deterministic validation gate after one repair "
        f"round-trip. The run is aborted rather than sending an unloadable ruleset "
        f"to the Red-Teamer and Playtester. Last errors: {detail}",
    )
