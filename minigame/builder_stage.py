"""The build stage — the Programmer agent, on the far side of the human gate.

This stage CANNOT run inside a propose run. It is a separate command whose
required arguments are the Director's ruling (`--select <id> --from-run
<run>`), which makes the human gate structural rather than procedural: there
is no code path from generation to build that does not pass through a person
typing a selection.

The contract is A5's, held at three anchors instead of one:

    logic block     inserted after the pure-resolver region (the teachingFor
                    line) — the mini-game's state, pure logic, overlay and
                    input handling
    selftest block  inserted inside the on-load self-test (after the G5
                    assertion) — at least one new M-numbered assertion on the
                    PURE logic, so the feature is gated by the same mechanism
                    as everything else
    hook line       inserted after the verb-dispatch line — the single line
                    that arms/triggers the encounter from the live sim

Deterministic post-checks before anything is written: every anchor unique;
every pre-existing G-assertion survives verbatim; at least one M-assertion
added; each inserted block parses (node --check when node is present, a
labelled brace-balance fallback when it is not); the patched file grew. Any
failure -> ONE repair round-trip carrying the checker's error text -> a
second failure aborts to FAILED.md. The in-place build is never touched; the
Director applies the patch and verifies the panel in a browser — the
interactive feel of a mini-game is not a check a container can make.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path  # noqa: F401  (used in signatures)

from content.agents import AgentError, parse_json_payload
from crew.llm import LLMCall

from .checks import apply_patch, brace_balanced, check_patch

PROGRAMMER_PV = "minigame-programmer v3 (Assignment 6 #2)"

CONTEXT_LINES = 34   # authored-code lines shown around each anchor

#: payload key -> (anchor name, wrap-for-parse-check). Wrapped blocks are
#: statements that live inside a method body; the logic block is top-level.
#: hook_line is OPTIONAL: it is the arming assist for verb-triggered
#: designs, and a design whose trigger lives in the frame seat (proximity,
#: time) legitimately has nothing to put there — the first v3 live run
#: proved it by omitting the key for exactly that reason.
PATCH_CONTRACT = [
    ("logic_block", "logic", False),
    ("frame_line", "frame", True),
    ("input_line", "input", True),
    ("selftest_block", "selftest", True),
    ("hook_line", "hook", True),
]
PATCH_KEYS = [k for k, _, _ in PATCH_CONTRACT]
REQUIRED_PATCH_KEYS = [k for k in PATCH_KEYS if k != "hook_line"]


def node_available() -> bool:
    return shutil.which("node") is not None


def playwright_available() -> bool:
    if not node_available():
        return False
    try:
        r = subprocess.run(["node", "-e", "require('playwright')"],
                           capture_output=True, timeout=30)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def run_play_probe(root: Path, patched_html: Path,
                   first_use_line: str) -> tuple[dict, list[str], str]:
    """The Playtester's seat for the overlay: drive the candidate build in
    headless Chromium (tools/mg_probe.js) and reject what static checks
    cannot see — page errors, a pre-armed encounter, dead WASD, a missing
    narration line, inhuman tuning, control not returning after resolution.

    Returns (checks, errors, status) where status is RAN or SKIPPED:<why>.
    SKIPPED is recorded, never silent — on a machine without playwright the
    cloud probe run is the evidence."""
    if not playwright_available():
        return {}, [], "SKIPPED: playwright not available on this machine"
    try:
        r = subprocess.run(
            ["node", str(root / "tools" / "mg_probe.js"),
             str(patched_html), first_use_line],
            capture_output=True, text=True, timeout=180)
        payload = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as exc:  # noqa: BLE001
        return ({"probe:ran": False},
                [f"the play-probe itself failed to run: {exc}"], "RAN")
    checks = {f"probe:{k}": v for k, v in payload.get("checks", {}).items()}
    checks["probe:ran"] = True
    errors = []
    if not payload.get("ok"):
        failed = [k for k, v in payload.get("checks", {}).items() if not v]
        detail = json.dumps(payload.get("detail", {}))[:900]
        errors.append(
            "the headless PLAY-PROBE drove your patched build in a real "
            f"browser and it FAILED: {', '.join(failed)}. Probe detail: "
            f"{detail}")
    return checks, errors, "RAN"


def parse_check(name: str, code: str, wrap: bool) -> tuple[bool, str]:
    """Syntax-check one inserted block. Blocks that only make sense inside a
    function body (self-test pushes, the hook) are wrapped for the check."""
    body = f"function __mg_check(out,SIM){{\n{code}\n}}" if wrap else code
    if node_available():
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(body)
            p = fh.name
        try:
            r = subprocess.run(["node", "--check", p], capture_output=True,
                               text=True, timeout=30)
            return r.returncode == 0, (r.stderr.strip()[:400]
                                       or "node --check passed")
        finally:
            Path(p).unlink(missing_ok=True)
    ok = brace_balanced(body)
    return ok, ("brace-balance passed (node unavailable — weaker check, "
                "labelled)" if ok else "brace-balance FAILED (node "
                "unavailable)")


def anchor_context(html: str, anchor: str, lines: int = CONTEXT_LINES) -> str:
    idx = html.find(anchor)
    pre = html[:idx].splitlines()[-lines:]
    post = html[idx:].splitlines()[:lines]
    return "\n".join(pre + post)


def _template(prompts_dir: Path) -> str:
    text = (prompts_dir / "minigame-programmer.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def run_programmer(llm, prompts_dir: Path, design: dict,
                   anchors: dict[str, str], html: str,
                   instructions: dict | None = None,
                   presentation: dict | None = None,
                   repair_error: str | None = None,
                   agent_label: str = "mg-programmer") -> dict:
    user = (
        _template(prompts_dir)
        .replace("{{DESIGN}}", json.dumps(design, ensure_ascii=False, indent=2))
        .replace("{{INSTRUCTIONS}}",
                 json.dumps(instructions or {}, ensure_ascii=False, indent=2))
        .replace("{{PRESENTATION}}",
                 json.dumps(presentation or {}, ensure_ascii=False, indent=2))
        .replace("{{LOGIC_ANCHOR}}", anchors["logic"])
        .replace("{{FRAME_ANCHOR}}", anchors["frame"])
        .replace("{{INPUT_ANCHOR}}", anchors["input"])
        .replace("{{SELFTEST_ANCHOR}}", anchors["selftest"])
        .replace("{{HOOK_ANCHOR}}", anchors["hook"])
        .replace("{{LOGIC_CONTEXT}}", anchor_context(html, anchors["logic"]))
        .replace("{{FRAME_CONTEXT}}", anchor_context(html, anchors["frame"]))
        .replace("{{INPUT_CONTEXT}}", anchor_context(html, anchors["input"]))
        .replace("{{SELFTEST_CONTEXT}}",
                 anchor_context(html, anchors["selftest"]))
        .replace("{{HOOK_CONTEXT}}", anchor_context(html, anchors["hook"]))
        .replace("{{REPAIR}}",
                 ("### REPAIR ROUND — your previous patch failed these "
                  "checks; fix exactly this and resubmit the full payload:\n"
                  + repair_error) if repair_error else "(first attempt)")
    )
    out = llm.complete(LLMCall(
        agent=agent_label,
        system=("You are the Programmer for uhta's mini-game build stage. "
                "You write a minimal playable version of ONE Director-"
                "selected encounter design as an anchored patch to a "
                "working Phaser build. You never rewrite the file; you "
                "insert at the given anchors, and you gate your own work "
                "with new self-test assertions on its pure logic."),
        user=user, temperature=0.2, max_tokens=8000,
    ))
    payload = parse_json_payload(agent_label, out)
    if not isinstance(payload, dict):
        raise AgentError(agent_label, f"expected a JSON patch object, got "
                                      f"{type(payload).__name__}")
    for key in REQUIRED_PATCH_KEYS:
        if not str(payload.get(key, "") or "").strip():
            raise AgentError(agent_label,
                             f"patch payload missing '{key}' — only "
                             f"hook_line is optional")
    return payload


def _norm_text(s: str) -> str:
    """Alphanumerics only, lowercased — so a JS-escaped or re-quoted copy of
    a line still matches its source."""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def build_and_check(html: str, anchors: dict[str, str], patch: dict,
                    instructions: dict | None = None) -> tuple[str, dict,
                                                               list[str]]:
    """Apply and post-check. Returns (patched, checks, errors)."""
    errors: list[str] = []
    checks: dict[str, bool] = {}

    present = [(k, n, w) for k, n, w in PATCH_CONTRACT
               if str(patch.get(k, "") or "").strip()]
    for key, _, wrap in present:
        ok, detail = parse_check(key, str(patch[key]), wrap)
        checks[f"parse:{key}"] = ok
        if not ok:
            errors.append(f"{key} failed the parse check: {detail}")

    patched = apply_patch(html, anchors,
                          {name: str(patch[key])
                           for key, name, _ in present})
    post = check_patch(html, patched)
    checks.update(post)
    if not post["all_preexisting_assertions_survive"]:
        errors.append("a pre-existing G-assertion did not survive verbatim")
    if not post["adds_at_least_one_M_assertion"]:
        errors.append("no new M-numbered self-test assertion was added — a "
                      "feature that cannot be asserted has not been finished "
                      "(put out.push(['M1 ...', <bool>, '...']); in "
                      "selftest_block)")
    if not post["grew"]:
        errors.append("the patched file did not grow")
    checks["whole_file_brace_balance"] = brace_balanced(
        str(patch["logic_block"]))

    # ---- v2/v3: the findings from the Director playtests ----
    inserted = "\n".join(str(patch.get(k, "") or "") for k in PATCH_KEYS)

    # The v2 deadlock class, banned by name: the v2 live patch assigned
    # `transitioning=true` on encounter start and had no path that cleared
    # it — onKey and update() both gate on that flag, so WASD and rendering
    # froze permanently ("the slice is broken"). Inserted code may READ the
    # flag, never write it.
    import re as _re
    m = _re.search(r"(?<![.\w])transitioning\s*=(?!=)", inserted)
    checks["never_writes_transitioning"] = m is None
    if m:
        errors.append(
            "inserted code ASSIGNS `transitioning` — the build's onKey and "
            "update() both gate on that flag, and an encounter that sets it "
            "and dies (or forgets to clear it) freezes WASD and rendering "
            "permanently. Read it if you need to; never write it — dim and "
            "pause via your own MG state instead")
    checks["director_test_hook"] = "location.hash" in inserted
    if not checks["director_test_hook"]:
        errors.append("no Director test hook — the inserted code must check "
                      "location.hash for 'mg' and force-arm the encounter, "
                      "so verification never depends on spawn luck (put "
                      "e.g. if(location.hash.indexOf('mg')>=0){...} in "
                      "logic_block)")
    if instructions and str(instructions.get("first_use_line", "")).strip():
        want = _norm_text(str(instructions["first_use_line"]))
        checks["first_use_line_present"] = want in _norm_text(inserted)
        if not checks["first_use_line_present"]:
            errors.append("the Instructor's first_use_line is not in the "
                          "patch — it must be displayed once, via the "
                          "existing tip/teaching mechanism, when the "
                          "encounter first begins on sleep 0")
    return patched, checks, errors
