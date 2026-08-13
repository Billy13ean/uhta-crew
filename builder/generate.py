"""Stage 5 — write the code, then refuse to believe it until it checks out.

The target has a green on-load self-test, which makes it exactly the kind of file
a helpful agent destroys. So the contract is narrow:

  * the model emits an ANCHORED PATCH, never a file. Anchors are exact existing
    lines and must be unique, so "apply the patch" is a mechanical operation with
    no judgement in it.
  * the patch must EXTEND THE SELF-TEST. A feature that cannot be asserted has
    not been finished; every other behaviour in that file is gated this way.
  * five deterministic checks run BEFORE anything is written, and the last one
    is not static — the patched build is EXECUTED headlessly and its own
    acceptance self-test must come back green. On failure the
    validator's own error text goes back for exactly ONE repair round-trip, and a
    second failure aborts to `FAILED.md`. That is the A3 validation gate's shape,
    reused for the same reason: one bounded retry is a typo fixed, and an
    unbounded one is a model arguing with a checker.
  * the in-place build is NOT modified. The patched file is written into the run
    directory and the Director applies it. Like the rules crew's blank `## Ruling`
    and the content pipeline's unfilled `## Director selection`, this pipeline
    ends at a human.
"""
from __future__ import annotations

import difflib
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from crew.llm import LLMCall

from . import AgentError, parse_json_payload, render_chunks

PROMPT_VERSION = "programmer v4 (builder pipeline)"
TEMPERATURE = 0.2

_ASSERTION = re.compile(r"out\.push\(\[\s*'([^']+)'")
_G_NUM = re.compile(r"^G(\d+)\b")
#: Top-level declarations introduced by an insert, for the reachability check.
_DECLARED = re.compile(r"^\s*(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)", re.M)
_SCRIPT = re.compile(r"<script>(.*?)</script>", re.DOTALL)


@dataclass
class Patch:
    summary: str
    rationale: str
    anchor: str
    insert: str
    edits: list[dict] = field(default_factory=list)
    selftest_anchor: str = ""
    selftest_insert: str = ""
    assertion_names: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "summary": self.summary, "rationale": self.rationale,
            "anchor": self.anchor, "edits": self.edits,
            "assertion_names": self.assertion_names,
            "insert_lines": len(self.insert.splitlines()),
            "selftest_insert_lines": len(self.selftest_insert.splitlines()),
        }


class PatchInvalid(Exception):
    """A deterministic check failed. The text is fed back for one repair."""


# --------------------------------------------------------------------------
# apply + validate
# --------------------------------------------------------------------------

def assertions_in(text: str) -> list[str]:
    return _ASSERTION.findall(text)


def _require_unique(original: str, anchor: str, label: str) -> None:
    if not anchor.strip():
        raise PatchInvalid(f"{label} is empty. It must be an exact line from the file.")
    n = original.count(anchor)
    if n == 0:
        raise PatchInvalid(
            f"{label} does not appear in the file. It must be copied verbatim from "
            f"the source you were shown. Got: {anchor[:200]!r}"
        )
    if n > 1:
        raise PatchInvalid(
            f"{label} appears {n} times in the file, so the insertion point is "
            f"ambiguous. Choose a longer, unique line. Got: {anchor[:200]!r}"
        )


def apply_patch(original: str, patch: Patch) -> str:
    """Apply the patch mechanically. Every failure here is a PatchInvalid."""
    _require_unique(original, patch.anchor, "anchor")
    out = original

    for i, e in enumerate(patch.edits, 1):
        a, r = str(e.get("anchor", "")), str(e.get("replacement", ""))
        _require_unique(out, a, f"edits[{i}].anchor")
        out = out.replace(a, r, 1)

    if patch.anchor not in out:
        raise PatchInvalid(
            "an entry in `edits` removed or altered the main `anchor` line, so the "
            "insertion point no longer exists. Anchor on a line your edits leave alone."
        )
    out = out.replace(patch.anchor, patch.anchor + "\n" + patch.insert.rstrip("\n"), 1)

    if patch.selftest_insert.strip():
        _require_unique(out, patch.selftest_anchor, "selftest_anchor")
        out = out.replace(
            patch.selftest_anchor,
            patch.selftest_anchor + "\n" + patch.selftest_insert.rstrip("\n"), 1,
        )
    return out


def check_assertions(original: str, patched: str) -> list[str]:
    """Every original assertion survives, and at least one new one arrives."""
    before, after = assertions_in(original), assertions_in(patched)
    lost = [a for a in before if a not in after]
    if lost:
        raise PatchInvalid(
            f"the patch removed or altered {len(lost)} existing self-test "
            f"assertion(s): {lost[:4]}. Those assertions are the proof that the JS "
            f"port matches the reference simulator tick-for-tick. All {len(before)} "
            f"must still be present, verbatim."
        )
    gained = [a for a in after if a not in before]
    if not gained:
        raise PatchInvalid(
            f"the patch added no new self-test assertion. The build has "
            f"{len(before)} and gates every behaviour through them; an addition "
            f"nobody can check is the one thing that does not belong in this file. "
            f"Add at least one `out.push([...])`."
        )

    # The first live run named its new assertion "G9 teaching text: …" while the
    # build already had "G9 era resolver + era frames in atlas map". Two G9s pass
    # every check above — the strings differ — and leave a self-test nobody can
    # read. The numbers are the file's index; a collision is a defect.
    used = {m.group(1) for m in (_G_NUM.match(a) for a in before) if m}
    clashes = [a for a in gained
               if (m := _G_NUM.match(a)) and m.group(1) in used]
    if clashes:
        nxt = max((int(n) for n in used), default=0) + 1
        raise PatchInvalid(
            f"the new assertion reuses an existing G-number: {clashes}. The build "
            f"already uses {sorted(used, key=int)}. Number yours from G{nxt} "
            f"upward — two assertions with the same number make the self-test "
            f"output unreadable, which is the one thing it exists to be."
        )
    return gained


def check_reachable(patched: str, patch: Patch) -> list[str]:
    """Whatever the patch declares must be USED by the game, not only by its test.

    The first live run produced this, and it passed every other check in this
    module:

        const TEACHING={flame:'You kindle a flame…'};
        function teachingTextFor(sleep_no,verb){…}

    `teachingTextFor` was called from exactly two places — the two self-test
    assertions the same patch added. `guide()` and `setTip` were byte-identical
    to the original. The build was green, the assertion was green, and the player
    saw nothing, because nothing in the render path ever called it.

    A pure resolver plus an assertion that exercises it is a local maximum: it
    satisfies "extend the self-test" at the lowest possible cost and delivers no
    feature. So reachability is a gate. A declaration is reachable when it is
    referenced somewhere that is neither its own definition nor inside
    `selfTest()`.
    """
    declared = _DECLARED.findall(patch.insert)
    if not declared:
        return []

    st_start, st_end = selftest_region(patched)
    lines = patched.splitlines()
    insert_lines = set(patch.insert.splitlines())
    outside = "\n".join(
        ln for i, ln in enumerate(lines)
        if not (st_start <= i <= st_end) and ln not in insert_lines
    )

    reached = [n for n in declared if re.search(rf"\b{re.escape(n)}\b", outside)]
    # ONE entry point is enough. A patch may legitimately declare a lookup table
    # consumed only by its own resolver — `TEACHING` used solely inside
    # `teachingTextFor` is fine, as long as something in the game calls
    # `teachingTextFor`. Requiring every name to be externally referenced
    # rejected that shape, which is the correct one.
    if not reached:
        raise PatchInvalid(
            f"the patch declares {declared} and nothing outside the self-test "
            f"ever calls any of them. That is dead code with a passing test "
            f"attached: the build stays green and the player sees nothing change.\n\n"
            f"Wire it into the running game. `guide()` builds the string that "
            f"`setTip()` renders every frame — splice the narration there with an "
            f"`edits` entry, so the feature reaches the screen and not just the "
            f"assertion. At least one declaration must be reachable from the "
            f"render path."
        )
    return reached


def check_parses(patched: str, node_bin: str = "node") -> None:
    """Extract the authored script and syntax-check it with Node."""
    blocks = _SCRIPT.findall(patched)
    if not blocks:
        raise PatchInvalid("no <script> block survives in the patched file.")
    # Pick the AUTHORED block, not the biggest one. This build vendors Phaser
    # inline, so the largest <script> is 1.18 MB of library — checking that
    # would syntax-check someone else's code and pass every broken patch. The
    # authored block is the one carrying the acceptance self-test.
    authored = [b for b in blocks if "function selfTest()" in b] or \
               [b for b in blocks if "const RULES" in b]
    if not authored:
        raise PatchInvalid(
            "the patched file has no <script> block containing `function "
            "selfTest()`. The acceptance self-test is the build's own gate; a "
            "patch that loses it cannot be verified."
        )
    body = max(authored, key=len)
    if shutil.which(node_bin) is None:
        # Fallback: bracket balance outside strings/comments. Weaker, but a
        # missing Node must not silently downgrade this to no check at all.
        depth = 0
        for ch in body:
            depth += (ch == "{") - (ch == "}")
        if depth != 0:
            raise PatchInvalid(f"braces are unbalanced in the patched script (net {depth:+d}).")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(body)
        tmp = fh.name
    try:
        p = subprocess.run([node_bin, "--check", tmp], capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            err = (p.stderr or p.stdout).strip().splitlines()
            raise PatchInvalid(
                "the patched JavaScript does not parse. Node reported:\n"
                + "\n".join(err[:12])
            )
    finally:
        Path(tmp).unlink(missing_ok=True)


#: Runs the build's own on-load acceptance self-test with a minimal DOM stub.
#: Phaser is absent, which the build already guards for (`if(typeof Phaser!==
#: 'undefined')`), so the sim core and the self-test run and the render layer
#: does not.
_HEADLESS_HARNESS = r"""
const fs=require('fs');
const src=fs.readFileSync(process.argv[2],'utf8');
const blocks=[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const body=blocks.filter(b=>b.includes('function selfTest()')).sort((a,b)=>b.length-a.length)[0];
if(!body){console.error('NO_AUTHORED_BLOCK');process.exit(2);}
let panel='';
const el={set textContent(v){panel=v;},get textContent(){return panel;},set className(v){},style:{}};
global.document={getElementById:()=>el};
global.window=global;
const realLog=console.log;console.log=()=>{};
try{ new Function(body)(); }catch(e){ console.log=realLog; console.error('THREW: '+e.message); process.exit(3); }
console.log=realLog;
process.stdout.write(panel);
"""


def check_selftest_runs(patched: str, node_bin: str = "node") -> tuple[int, int]:
    """EXECUTE the build's acceptance self-test headlessly and require it green.

    `node --check` is a syntax check and nothing more. It passes a patch that
    inserts a `const` into the temporal dead zone of code that runs earlier in
    the file — which is a real way to break this build, because `selfTest()` runs
    inline partway down and the render layer is defined below it.

    So the last check is not static. The patched file is actually run, the
    self-test panel is read back, and every assertion must pass. This is also
    what makes 'were you able to run this in your game?' answerable with evidence
    rather than with hope.
    """
    if shutil.which(node_bin) is None:
        return (-1, -1)                        # reported as skipped, never as passed
    with tempfile.TemporaryDirectory() as d:
        html, js = Path(d) / "patched.html", Path(d) / "harness.js"
        html.write_text(patched, encoding="utf-8")
        js.write_text(_HEADLESS_HARNESS, encoding="utf-8")
        p = subprocess.run([node_bin, str(js), str(html)],
                           capture_output=True, text=True, timeout=300)
    if p.returncode == 3:
        raise PatchInvalid(
            "the patched build THREW while running its on-load self-test:\n  "
            + (p.stderr or "").strip()[:400]
            + "\n\nThe patch is syntactically valid but does not execute. A common "
              "cause in this file: `selfTest()` runs partway down the script, so "
              "anything anchored BELOW it is in the temporal dead zone when the "
              "assertions run. Anchor above `function selfTest()`."
        )
    if p.returncode != 0:
        raise PatchInvalid(f"the headless self-test run failed (exit {p.returncode}): "
                           f"{(p.stderr or p.stdout).strip()[:400]}")
    out = p.stdout
    if "self-test error:" in out:
        # The build wraps its self-test in try/catch, so a load-time exception
        # surfaces as panel text rather than a crash. Catch it explicitly —
        # otherwise it reads as "0 assertions" instead of "the build is dead".
        raise PatchInvalid(
            "the patched build THREW on load. Its self-test panel reads:\n  "
            + out.strip()[:300]
            + "\n\nThe patch parses but does not execute. The usual cause in this "
              "file: `selfTest()` runs inline partway down the script, so anything "
              "anchored BELOW it is in the temporal dead zone when the assertions "
              "run. Anchor above `function selfTest()`."
        )
    npass, nfail = out.count("PASS"), out.count("FAIL")
    if nfail or npass == 0:
        failing = [l.strip() for l in out.splitlines() if "FAIL" in l]
        raise PatchInvalid(
            f"the patched build runs, but its self-test is not green: {npass} PASS / "
            f"{nfail} FAIL.\n  " + "\n  ".join(failing[:6])
            + "\n\nThe build's acceptance self-test gates every behaviour in the "
              "file. A patch that leaves it red has not added a feature; it has "
              "broken the build."
        )
    return npass, nfail


def validate(original: str, patch: Patch, node_bin: str = "node"
             ) -> tuple[str, list[str], tuple[int, int]]:
    # Order is cheapest-and-most-structural first, most-semantic last. You only
    # ask "is this wired into the game" once you know it is valid JavaScript,
    # carries a real assertion, and actually runs green — otherwise a patch that
    # does not parse gets reported as a wiring problem, which sends the repair
    # round-trip after the wrong thing.
    patched = apply_patch(original, patch)
    gained = check_assertions(original, patched)
    check_parses(patched, node_bin)
    result = check_selftest_runs(patched, node_bin)
    check_reachable(patched, patch)
    return patched, gained, result


def unified_diff(original: str, patched: str, path: str) -> str:
    return "".join(difflib.unified_diff(
        original.splitlines(keepends=True), patched.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}", n=3,
    ))


# --------------------------------------------------------------------------
# the Programmer
# --------------------------------------------------------------------------

def _load_prompt(prompts_dir) -> str:
    text = (prompts_dir / "programmer.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def _selftest_context(source: str, limit: int = 70) -> str:
    i = source.find("function selfTest()")
    if i < 0:
        return "(selfTest not found)"
    rows = source[i:].splitlines()[:limit]
    return "\n".join(rows)


# --------------------------------------------------------------------------
# anchor menus — why the model is not allowed to write an anchor
# --------------------------------------------------------------------------
#
# The first live Programmer run failed twice with anchors that looked exactly
# right and did not exist:
#
#   function roadStageFor(born,now){const age=now-born;if(age<3)return 0;...}
#   function eraOf(sleep_no){if(sleep_no<12)return 'genesis';...}
#
# Both name real functions in this build. Neither body is real. The cause was
# structural, not a lapse: `code_context()` shows only the lines the GAP DETECTOR
# matched, and a feature that is genuinely missing matches almost nothing — so
# the Programmer was handed "(the detector matched nothing — this is new ground)"
# and then asked for a line copied verbatim from a file it had never seen.
#
# Raising the context budget would make hallucination less likely. Removing the
# freedom makes it impossible: the model picks an anchor from a numbered menu of
# lines lifted verbatim out of the real source, and returns the NUMBER. An index
# either resolves against the file or is out of range. There is no third option,
# and no amount of plausible-looking JavaScript can fake one.

#: NO leading whitespace. An indented `const` is inside a function or a class
#: body, and inserting a top-level declaration after it is a syntax error — the
#: menu must not be able to offer a choice that cannot work.
_ANCHOR_DECL = re.compile(r"^(?:function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|class\s+\w+)")
_SELFTEST_LINE = re.compile(r"^\s*out\.push\(\[")

#: Anchor lines must be recognisable structure, not a fragment. The lower bound
#: keeps out `};`; the upper keeps out the vendored bundle and the base64 blobs,
#: which SCAN_POLICY already excludes from the index for the same reason.
ANCHOR_MIN_CHARS = 18
ANCHOR_MAX_CHARS = 300

#: Declarations immediately before selfTest() that are never sampled away.
TAIL_ALWAYS = 8


def _strip_strings(s: str) -> str:
    """Drop string literals and line comments, so bracket counting sees code."""
    out, i, quote = [], 0, None
    while i < len(s):
        c = s[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "'\"`":
            quote = c
            i += 1
            continue
        if c == "/" and i + 1 < len(s) and s[i + 1] == "/":
            break
        out.append(c)
        i += 1
    return "".join(out)


def is_complete_statement(line: str) -> bool:
    """True when the line opens nothing it does not also close.

    This is the check that was missing, and it cost a live run. The self-test's
    later assertions are multi-line calls:

        out.push(['G9 era resolver + era frames in atlas map', eras&&missing…,
          `eraOf(0,5,6,13,14)=…`]);

    and `const F32={…}` spans six lines. Anchoring "insert after this line" on
    the FIRST line of either puts the new code INSIDE an array or object
    literal, and the patch dies with `SyntaxError: Unexpected token 'const'` —
    which is what happened, twice, after the anchors themselves were fixed.

    A line that ends balanced is a statement you can safely insert after.
    """
    code = _strip_strings(line)
    if sum((c in "([{") - (c in ")]}") for c in code) != 0:
        return False
    return code.rstrip().endswith((";", "}"))


def _unique_lines(source: str, lines: list[str]) -> set[str]:
    """Lines that occur exactly once, both as a line and as a substring.

    Both tests matter: `_require_unique` checks substring count against the whole
    file, so a line that is unique among lines but appears inside a longer line
    would pass here and fail there.
    """
    freq = Counter(lines)
    return {ln for ln, n in freq.items() if n == 1 and source.count(ln) == 1}


def selftest_region(source: str) -> tuple[int, int]:
    """Line span of `function selfTest()` … its `return out;`."""
    lines = source.splitlines()
    start = next((i for i, l in enumerate(lines) if "function selfTest()" in l), -1)
    if start < 0:
        return (0, 0)
    end = next((i for i in range(start, len(lines)) if lines[i].strip() == "return out;"),
               min(start + 400, len(lines)))
    return (start, end)


def anchor_candidates(source: str, max_n: int = 22) -> list[tuple[int, str]]:
    """Numbered menu of real, unique, top-level lines to insert after."""
    lines = source.splitlines()
    uniq = _unique_lines(source, lines)
    st_start, st_end = selftest_region(source)
    out: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        # ABOVE selfTest() only. selfTest() executes inline immediately after it
        # is defined, so a `const` or `class` anchored below that point is in the
        # temporal dead zone when the assertions run and the build dies on load.
        # The prompt warns about this; the menu simply never offers it.
        if st_start and i >= st_start:
            break
        if not (ANCHOR_MIN_CHARS <= len(ln) <= ANCHOR_MAX_CHARS):
            continue
        if ln not in uniq or not _ANCHOR_DECL.match(ln):
            continue
        if not is_complete_statement(ln):
            continue          # e.g. `const F32={…` — six lines of object literal
        out.append((i + 1, ln))
    if len(out) <= max_n:
        return out
    # The last few declarations before selfTest() are the pure-resolver zone —
    # `eraOf`, `roadStageFor`, `ERA_SLEEPS` — which is where the prompt tells the
    # Programmer to anchor and where a headless-testable addition belongs. Even
    # sampling alone dropped two of those three, so keep the tail whole and
    # sample the rest for coverage.
    keep_tail = min(TAIL_ALWAYS, len(out))
    head, tail = out[:-keep_tail], out[-keep_tail:]
    slots = max_n - keep_tail
    if slots <= 0 or not head:
        return tail
    step = len(head) / slots
    return [head[int(k * step)] for k in range(slots)] + tail


def selftest_anchor_candidates(source: str, max_n: int = 12) -> list[tuple[int, str]]:
    """Menu of real `out.push([...])` assertion lines to append after."""
    lines = source.splitlines()
    uniq = _unique_lines(source, lines)
    start, end = selftest_region(source)
    out = [(i + 1, lines[i]) for i in range(start, min(end + 1, len(lines)))
           if _SELFTEST_LINE.match(lines[i])
           and lines[i] in uniq
           and len(lines[i]) <= ANCHOR_MAX_CHARS
           # G6–G11 are multi-line pushes; anchoring on their opening line
           # inserts into the argument array. Only whole statements qualify.
           and is_complete_statement(lines[i])]
    return out[-max_n:] if len(out) > max_n else out


#: Methods the prompt names as wiring points. An `edits` entry replaces a line
#: rather than inserting after one, so an indented line inside a method body is
#: a legal target here in a way it never is for the insertion anchor.
HOOK_METHODS = ("moveStep(dx,dy){", "tryAct(kind,cost){", "doSleep(){", "guide(){")


def hook_candidates(source: str, per_method: int = 6) -> list[tuple[int, str]]:
    """Menu of real lines inside the render-layer methods, for `edits`.

    The second live run invented `'  constructor(seed,poles){'` for an `edits`
    anchor — the real line is
    `constructor(seed,poles=[-1,-1,1],start='tentative'){`. Exactly the failure
    the insertion menu was built to stop, in the one field that was still free
    text. So `edits` gets a menu too, and after this there is no anchor anywhere
    in the patch contract that the model composes itself.
    """
    lines = source.splitlines()
    uniq = _unique_lines(source, lines)
    out: list[tuple[int, str]] = []
    for sig in HOOK_METHODS:
        start = next((i for i, l in enumerate(lines) if l.strip() == sig.strip()), -1)
        if start < 0:
            continue
        taken = 0
        for i in range(start, min(start + 40, len(lines))):
            ln = lines[i]
            if i > start and re.match(r"^  [A-Za-z_$][\w$]*\s*\(", ln):
                break                      # next method — stop
            if not (ANCHOR_MIN_CHARS <= len(ln) <= ANCHOR_MAX_CHARS):
                continue
            if ln not in uniq or not is_complete_statement(ln):
                continue
            out.append((i + 1, ln))
            taken += 1
            if taken >= per_method:
                break
    return out


def render_menu(cands: list[tuple[int, str]], width: int = 190) -> str:
    if not cands:
        return "(no candidate found — this is a bug in anchor_candidates, not your problem)"
    return "\n".join(f"[{n}] {ln.strip()[:width]}" for n, ln in cands)


def code_context(source: str, verdict, idx, budget: int = 90) -> str:
    """The lines the gap detector actually matched — never a summary of them."""
    seen, parts, used = set(), [], 0
    for e in verdict.evidence:
        if not e.found:
            continue
        for h in e.hits[:2]:
            if h.path == "rules" or (h.path, h.line) in seen or used >= budget:
                continue
            seen.add((h.path, h.line))
            rows = idx.lines.get(h.path) or []
            lo, hi = max(1, h.line - 4), min(len(rows), h.line + 8)
            used += hi - lo
            parts.append(f"--- {h.path}:{lo}-{hi} (matched {e.needle!r}) ---\n"
                         + "\n".join(f"{n:>6} | {rows[n-1][:200]}" for n in range(lo, hi + 1)))
    return "\n\n".join(parts) if parts else "(the detector matched nothing — this is new ground)"


def _pick(agent: str, raw: dict, id_field: str, text_field: str,
          menu: dict[int, str] | None, label: str, required: bool = True) -> str:
    """Resolve an anchor from the menu id, falling back to literal text.

    The id path is the one live runs take: it cannot name a line that is not in
    the file, because the text never comes from the model. The literal path
    stays for the mock fixtures, which predate the menu and exercise the
    validator directly.
    """
    if menu:
        val = raw.get(id_field)
        if val is None and required and not str(raw.get(text_field) or "").strip():
            raise AgentError(
                agent,
                f"no {id_field} given. {label} must be chosen from the numbered "
                f"menu by its id — valid ids: {sorted(menu)}. Writing the line "
                f"out by hand is how the first live run failed twice.",
            )
        if val is not None:
            try:
                key = int(val)
            except (TypeError, ValueError):
                raise AgentError(agent, f"{id_field}={val!r} is not an integer id") from None
            if key not in menu:
                raise AgentError(
                    agent,
                    f"{id_field}={key} is not on the menu. Valid ids: {sorted(menu)}. "
                    f"Ids are line numbers from the real file; you cannot invent one.",
                )
            return menu[key]
    return str(raw.get(text_field) or "")


def _parse_patch(agent: str, raw, anchors: dict[int, str] | None = None,
                 st_anchors: dict[int, str] | None = None,
                 hooks: dict[int, str] | None = None) -> Patch:
    if not isinstance(raw, dict):
        raise AgentError(agent, f"expected a JSON object, got {type(raw).__name__}")
    edits = raw.get("edits") or []
    if not isinstance(edits, list):
        raise AgentError(agent, "`edits` must be an array (possibly empty)")

    # Resolve every edit's anchor from the hook menu. After this no anchor in the
    # patch contract is text the model wrote.
    resolved: list[dict] = []
    for i, e in enumerate(edits, 1):
        if not isinstance(e, dict):
            continue
        e = dict(e)
        e["anchor"] = _pick(agent, e, "anchor_id", "anchor", hooks,
                            f"edits[{i}].anchor")
        resolved.append(e)
    edits = resolved
    return Patch(
        summary=str(raw.get("summary") or "").strip(),
        rationale=str(raw.get("rationale") or "").strip(),
        anchor=_pick(agent, raw, "anchor_id", "anchor", anchors, "The insertion anchor"),
        insert=str(raw.get("insert") or ""),
        edits=edits,
        # Only required when there are assertions to place. A patch may deliver
        # them through `edits` instead — the fixture does — and `apply_patch`
        # already treats the anchor as needed only when selftest_insert is set.
        selftest_anchor=_pick(agent, raw, "selftest_anchor_id", "selftest_anchor",
                              st_anchors, "The self-test anchor",
                              required=bool(str(raw.get("selftest_insert") or "").strip())),
        selftest_insert=str(raw.get("selftest_insert") or ""),
        assertion_names=[str(a) for a in (raw.get("assertion_names") or [])],
    )


def run_programmer(llm, prompts_dir, feature, verdict, selection, source: str, idx,
                   node_bin: str = "node", agent_label: str = "programmer"
                   ) -> tuple[Patch, str, list[str], list[str], tuple[int, int]]:
    """Generate, validate, and allow exactly one repair. Returns
    (patch, patched_source, new_assertions, repair_log, selftest_result)."""
    template = _load_prompt(prompts_dir)
    finding = (f"{verdict.verdict} — {verdict.reason}"
               + (f"\nExisting code, quoted by the detector: {verdict.quoted_code}"
                  if verdict.quoted_code else ""))
    cands = anchor_candidates(source)
    st_cands = selftest_anchor_candidates(source)
    hook_cands = hook_candidates(source)
    anchors = {n: ln for n, ln in cands}
    st_anchors = {n: ln for n, ln in st_cands}
    hooks = {n: ln for n, ln in hook_cands}

    base = (template
            .replace("{{FEATURE_NAME}}", feature.name)
            .replace("{{GDD_REQUIREMENT}}", feature.description)
            .replace("{{GAP_FINDING}}", finding)
            .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection) if selection else "(none)")
            .replace("{{CODE_CONTEXT}}", code_context(source, verdict, idx))
            .replace("{{SELFTEST_CONTEXT}}", _selftest_context(source))
            .replace("{{ANCHOR_MENU}}", render_menu(cands))
            .replace("{{SELFTEST_ANCHOR_MENU}}", render_menu(st_cands))
            .replace("{{HOOK_MENU}}", render_menu(hook_cands)))

    repair_log: list[str] = []
    user = base
    for attempt in (1, 2):
        out = llm.complete(LLMCall(
            agent=agent_label if attempt == 1 else f"{agent_label}-repair",
            system=("You are the Programmer for uhta. You write small, anchored "
                    "patches to a single-file Phaser build whose on-load self-test "
                    "must stay green, and you extend that self-test to cover "
                    "whatever you add."),
            user=user, temperature=TEMPERATURE, max_tokens=8000,
        ))
        patch = _parse_patch(agent_label, parse_json_payload(agent_label, out),
                             anchors, st_anchors, hooks)
        try:
            patched, gained, selftest_result = validate(source, patch, node_bin)
            return patch, patched, gained, repair_log, selftest_result
        except PatchInvalid as exc:
            repair_log.append(f"attempt {attempt}: {exc}")
            if attempt == 2:
                raise AgentError(
                    agent_label,
                    "the patch failed the deterministic checks twice. One repair "
                    "round-trip carrying the validator's own error text is the "
                    "budget; a second failure means the model is arguing with the "
                    "checker rather than fixing the patch.\n\n"
                    + "\n".join(repair_log),
                ) from exc
            user = (base + "\n\n---\n\n## YOUR PREVIOUS ATTEMPT WAS REJECTED\n\n"
                    f"The deterministic validator rejected it:\n\n```\n{exc}\n```\n\n"
                    "Return a corrected patch in the same JSON shape. Fix exactly "
                    "this problem; do not redesign the feature.")
    raise AssertionError("unreachable")
