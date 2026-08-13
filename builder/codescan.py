"""Stage 2 — scan the codebase. No LLM.

Three targets, because in this project a feature can be present as DATA rather
than as code, and missing that is the obvious way a naive detector produces a
false gap:

    blackboard/build/uhta-slice.html   the game — the Phaser build the player runs
    blackboard/rules/rules-*.json      the ratified ruleset; features live here as
                                       key paths, and the build reads them at boot
    blackboard/sim/harness.py          the reference simulator — the executable spec

Everything here is regex and string work over authored source. It is deliberately
not a parser: the output is evidence with a `file:line` attached, which is what
the gap stage quotes, and precision matters less than being able to show the
line. What it is NOT deliberate about is scope — see `policy.SCAN_POLICY`, which
is what keeps 1.18 MB of vendored Phaser out of the index.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .policy import ScanExclusion, classify_line

# --- JS surface -----------------------------------------------------------
_FUNC = re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(")
_CLASS = re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)")
_DECL = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=")
_METHOD = re.compile(r"^\s{2,}([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{")
_PROP = re.compile(r"\bthis\.([A-Za-z_$][\w$]*)\s*=")
_KEY = re.compile(r"([A-Za-z_$][\w$]*)\s*:")
_STR = re.compile(r"'([^'\\\n]{2,80})'|\"([^\"\\\n]{2,80})\"")
# --- Python surface -------------------------------------------------------
_PYDEF = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)")
_PYCLASS = re.compile(r"^\s*class\s+([A-Za-z_]\w*)")


@dataclass(frozen=True)
class Hit:
    path: str
    line: int

    def __str__(self) -> str:
        return f"{self.path}:{self.line}"


@dataclass
class CodeIndex:
    symbols: dict[str, list[Hit]] = field(default_factory=dict)
    literals: dict[str, list[Hit]] = field(default_factory=dict)
    key_paths: set[str] = field(default_factory=set)
    lines: dict[str, list[str]] = field(default_factory=dict)
    exclusions: list[ScanExclusion] = field(default_factory=list)
    scanned: dict[str, dict] = field(default_factory=dict)

    # ---------------- construction ----------------

    def add_symbol(self, name: str, hit: Hit) -> None:
        if len(name) < 2:
            return
        self.symbols.setdefault(name, [])
        if len(self.symbols[name]) < 8:
            self.symbols[name].append(hit)

    def add_literal(self, value: str, hit: Hit) -> None:
        v = value.strip().lower()
        if len(v) < 3:
            return
        self.literals.setdefault(v, [])
        if len(self.literals[v]) < 8:
            self.literals[v].append(hit)

    # ---------------- lookup ----------------

    def find_symbol(self, name: str) -> list[Hit]:
        """Exact, then case-insensitive, then a normalised (case/underscore-free)
        match — `road_born` and `roadBorn` are the same intent expressed twice."""
        if name in self.symbols:
            return self.symbols[name]
        low = name.lower()
        for k, v in self.symbols.items():
            if k.lower() == low:
                return v
        norm = re.sub(r"[^a-z0-9]", "", low)
        if len(norm) < 4:
            return []
        for k, v in self.symbols.items():
            if re.sub(r"[^a-z0-9]", "", k.lower()) == norm:
                return v
        return []

    def find_literal(self, needle: str) -> list[Hit]:
        n = needle.strip().lower()
        if n in self.literals:
            return self.literals[n]
        out: list[Hit] = []
        for k, v in self.literals.items():
            if n in k:
                out.extend(v)
                if len(out) >= 8:
                    break
        return out

    def has_key_path(self, path: str) -> bool:
        p = path.strip().lstrip("$.").replace("[", ".").replace("]", "")
        if p in self.key_paths:
            return True
        return any(kp.endswith("." + p) or kp == p for kp in self.key_paths)

    def excerpt(self, hit: Hit, width: int = 150) -> str:
        rows = self.lines.get(hit.path) or []
        if not (1 <= hit.line <= len(rows)):
            return ""
        return rows[hit.line - 1].strip()[:width]

    def stats(self) -> dict:
        return {
            "symbols": len(self.symbols),
            "literals": len(self.literals),
            "key_paths": len(self.key_paths),
            "excluded_regions": len(self.exclusions),
            "excluded_chars": sum(e.chars for e in self.exclusions),
            "files": self.scanned,
        }


# --------------------------------------------------------------------------
# per-format scanners
# --------------------------------------------------------------------------

def scan_js_like(idx: CodeIndex, rel: str, text: str) -> None:
    """Index authored JS, applying SCAN_POLICY line by line."""
    rows = text.splitlines()
    idx.lines[rel] = rows
    kept = 0
    for n, raw in enumerate(rows, 1):
        verdict = classify_line(raw)
        if verdict is not None:
            rule, reason = verdict
            idx.exclusions.append(ScanExclusion(rel, n, len(raw), rule, reason))
            continue
        kept += 1
        hit = Hit(rel, n)
        for rx in (_FUNC, _CLASS, _DECL, _METHOD, _PROP):
            for m in rx.finditer(raw):
                idx.add_symbol(m.group(1), hit)
        for m in _KEY.finditer(raw):
            idx.add_symbol(m.group(1), hit)
        for m in _STR.finditer(raw):
            idx.add_literal(m.group(1) or m.group(2) or "", hit)
    idx.scanned[rel] = {
        "lines": len(rows), "indexed": kept, "excluded": len(rows) - kept,
    }


def scan_json_rules(idx: CodeIndex, rel: str, text: str) -> None:
    """Walk the ruleset to a flat key-path set.

    This is the A3 validation gate's trick reused: the ratified rules file IS the
    schema, so the key paths are derived from the live file rather than typed
    into this source.
    """
    data = json.loads(text)
    idx.lines[rel] = text.splitlines()

    def walk(node, prefix=""):
        if isinstance(node, dict):
            for k, v in node.items():
                p = f"{prefix}.{k}" if prefix else k
                idx.key_paths.add(p)
                idx.add_symbol(k, Hit(rel, 1))
                walk(v, p)
        elif isinstance(node, list):
            for v in node:
                walk(v, prefix)

    walk(data)
    idx.scanned[rel] = {"key_paths": len(idx.key_paths)}


def scan_python(idx: CodeIndex, rel: str, text: str) -> None:
    rows = text.splitlines()
    idx.lines[rel] = rows
    for n, raw in enumerate(rows, 1):
        hit = Hit(rel, n)
        for rx in (_PYDEF, _PYCLASS):
            m = rx.match(raw)
            if m:
                idx.add_symbol(m.group(1), hit)
        for m in _STR.finditer(raw):
            idx.add_literal(m.group(1) or m.group(2) or "", hit)
    idx.scanned[rel] = {"lines": len(rows)}


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

#: (blackboard-relative path, scanner). Order is the order they appear in the
#: RUN-LOG, which is the order a reader will meet them in.
SCAN_TARGETS: list[tuple[str, str]] = [
    ("build/uhta-slice.html", "js"),
    ("rules/rules-v3.9.1-C.json", "json"),
    ("sim/harness.py", "py"),
]


def build_index(bb, agent: str = "codescan",
                targets: list[tuple[str, str]] | None = None) -> CodeIndex:
    """Read every scan target through the blackboard and index it.

    Reading through `bb.read_bb` rather than opening files directly is the point:
    every byte this pipeline looked at lands in `RUN-LOG.md` with a size and a
    hash, so the scan's inputs are auditable rather than asserted.
    """
    idx = CodeIndex()
    for rel, kind in (targets or SCAN_TARGETS):
        text = bb.read_bb(rel, agent)
        if kind == "js":
            scan_js_like(idx, rel, text)
        elif kind == "json":
            scan_json_rules(idx, rel, text)
        else:
            scan_python(idx, rel, text)
    return idx
