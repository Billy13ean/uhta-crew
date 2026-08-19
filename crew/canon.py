"""The canon bench — the rules registry, and the Director's rulings over it.

The registry (`canon/rules.json`) is the single written-down source of the
law the two GER Evaluators enforce: the encounter rules, the narration
register, the deterministic-check parameters. The pipelines READ it here;
they never edit it. The Director rules on it through the Bible page
(crew/bible.py -> canon/CANON-BIBLE.html), which writes a ruling file
(`canon/CANON-RULING.json`) this module validates and applies.

A rule has exactly three possible statuses:

    UPHELD    the default. Absence of a ruling IS an upheld ruling.
    AMENDED   the Director's edited text/params are enforced instead; the
              baseline stays in the registry as history.
    REPEALED  the rule is not enforced — and the skip is LOGGED every run
              (CANON-IN-FORCE.md + manifest), never silent.

There is deliberately no WAIVED/IGNORED status. The Director ruled it off
the bench (2026-08-19): a silently skippable check makes every green run
log unfalsifiable — "did it pass C5, or was C5 off?". A repeal is loud; an
ignore is invisible. Loud won.

Contract violations (unknown rule id, invalid status, amending a field the
rule does not have, repealing a rule marked repealable=false) raise
CanonError and halt the run — same posture as AgentError: a broken
contract is never smoothed over.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = REPO_ROOT / "canon" / "rules.json"
RULING_PATH = REPO_ROOT / "canon" / "CANON-RULING.json"

VALID_STATUSES = ("UPHELD", "AMENDED", "REPEALED")
_BANNED_STATUSES = ("WAIVED", "IGNORED", "SKIPPED", "DISABLED")


class CanonError(RuntimeError):
    """A ruling that breaks the canon contract. Halts, never smoothed over."""


class Canon:
    """The registry with a ruling applied. Construct via Canon.load() in
    pipelines; construct directly with dicts in tests."""

    def __init__(self, registry: dict, ruling: dict | None = None,
                 ruling_sha: str = ""):
        self.registry = registry
        self.rules: dict[str, dict] = {r["id"]: r
                                       for r in registry.get("rules", [])}
        self.proposals: list[dict] = registry.get("proposals", [])
        self.ruling = ruling or {}
        self.ruling_sha = ruling_sha
        self._validate()

    # ---------------- loading ----------------

    @classmethod
    def load(cls, root: Path | None = None) -> "Canon":
        rules_path = (root / "canon" / "rules.json") if root else RULES_PATH
        ruling_path = (root / "canon" / "CANON-RULING.json") if root \
            else RULING_PATH
        if not rules_path.exists():
            if ruling_path.exists():
                raise CanonError(
                    f"{ruling_path.name} exists but {rules_path.name} does "
                    f"not — a ruling over a missing registry is not "
                    f"interpretable. Restore canon/rules.json.")
            # Registry not shipped (e.g. a partial docker COPY): baseline
            # law is in the specs themselves, so run with an empty canon —
            # every lookup falls back to the caller's baseline default.
            return cls({"rules": [], "proposals": []})
        registry = json.loads(rules_path.read_text(encoding="utf-8"))
        ruling, sha = None, ""
        if ruling_path.exists():
            raw = ruling_path.read_bytes()
            sha = hashlib.sha256(raw).hexdigest()[:16]
            ruling = json.loads(raw.decode("utf-8"))
        return cls(registry, ruling, sha)

    # ---------------- validation (the contract) ----------------

    def _validate(self) -> None:
        for rid, entry in (self.ruling.get("rules") or {}).items():
            if rid not in self.rules:
                raise CanonError(
                    f"ruling names unknown rule id {rid!r} — known: "
                    f"{sorted(self.rules)}")
            status = str(entry.get("status", "")).upper()
            if status in _BANNED_STATUSES:
                raise CanonError(
                    f"rule {rid!r}: status {status!r} does not exist. The "
                    f"Director ruled ignore off the bench (2026-08-19): a "
                    f"rule is UPHELD, AMENDED, or REPEALED — never "
                    f"silently skipped.")
            if status not in VALID_STATUSES:
                raise CanonError(
                    f"rule {rid!r}: status {status!r} not in "
                    f"{VALID_STATUSES}")
            rule = self.rules[rid]
            if status == "REPEALED" and not rule.get("repealable", True):
                why = rule.get("why_not_repealable", "")
                raise CanonError(
                    f"rule {rid!r} is not repealable. {why} "
                    f"(AMEND is available.)")
            if status == "AMENDED":
                has_text = bool(str(entry.get("text", "")).strip())
                params = entry.get("params") or {}
                if rule.get("kind") == "prose":
                    if not has_text:
                        raise CanonError(
                            f"rule {rid!r}: AMENDED prose rule needs "
                            f"non-empty 'text'")
                else:
                    if not params and not has_text:
                        raise CanonError(
                            f"rule {rid!r}: AMENDED needs 'params' "
                            f"(or 'text' for prose)")
                    base = rule.get("params") or {}
                    unknown = [k for k in params if k not in base]
                    if unknown:
                        raise CanonError(
                            f"rule {rid!r}: amended params {unknown} do not "
                            f"exist on the rule (has {sorted(base)})")
                    for k, v in params.items():
                        if type(v) is not type(base[k]):
                            raise CanonError(
                                f"rule {rid!r}: param {k!r} must be "
                                f"{type(base[k]).__name__}, got "
                                f"{type(v).__name__}")

    # ---------------- lookups ----------------

    def status(self, rid: str) -> str:
        entry = (self.ruling.get("rules") or {}).get(rid)
        if not entry:
            return "UPHELD"
        return str(entry["status"]).upper()

    def enforced(self, rid: str) -> bool:
        return self.status(rid) != "REPEALED"

    def text(self, rid: str, default: str = "") -> str:
        rule = self.rules.get(rid)
        entry = (self.ruling.get("rules") or {}).get(rid) or {}
        if self.status(rid) == "AMENDED" and str(entry.get("text", "")).strip():
            return str(entry["text"]).strip()
        if rule and str(rule.get("text", "")).strip():
            return str(rule["text"])
        return default

    def params(self, rid: str, default: dict | None = None) -> dict:
        rule = self.rules.get(rid)
        base = dict((rule or {}).get("params") or (default or {}))
        if self.status(rid) == "AMENDED":
            entry = (self.ruling.get("rules") or {}).get(rid) or {}
            base.update(entry.get("params") or {})
        return base

    def param(self, rid: str, key: str, default: Any = None) -> Any:
        return self.params(rid).get(key, default)

    # ---------------- evidence ----------------

    def summary(self) -> dict:
        """For the run manifest: what law was in force, verifiably."""
        non_upheld = {rid: self.status(rid) for rid in self.rules
                      if self.status(rid) != "UPHELD"}
        return {
            "registry": "canon/rules.json" if self.rules else "(absent — baseline)",
            "rules": len(self.rules),
            "ruling_file": "canon/CANON-RULING.json" if self.ruling else None,
            "ruling_sha256_16": self.ruling_sha or None,
            "ruled_by": self.ruling.get("ruled_by"),
            "ruled_at": self.ruling.get("ruled_at"),
            "non_upheld": non_upheld,
        }

    def render_in_force(self) -> str:
        """CANON-IN-FORCE.md — written at the top of every run so the run
        dir itself says what law it was judged under."""
        lines = ["# Canon in force for this run", ""]
        if not self.rules:
            lines += ["Registry absent — baseline rules (the spec constants) "
                      "in force, no rulings possible.", ""]
            return "\n".join(lines)
        if self.ruling:
            lines += [f"Ruling: `canon/CANON-RULING.json` "
                      f"(sha256:{self.ruling_sha}) — ruled by "
                      f"{self.ruling.get('ruled_by', '(unsigned)')} at "
                      f"{self.ruling.get('ruled_at', '(undated)')}", ""]
        else:
            lines += ["No ruling on file — every rule UPHELD as written.", ""]
        for rid, rule in self.rules.items():
            st = self.status(rid)
            mark = {"UPHELD": "UPHELD", "AMENDED": "**AMENDED**",
                    "REPEALED": "**REPEALED — not enforced this run**"}[st]
            lines.append(f"- `{rid}` ({rule.get('title', '')}): {mark}")
            if st == "AMENDED":
                entry = (self.ruling.get("rules") or {}).get(rid) or {}
                if str(entry.get("text", "")).strip():
                    lines.append(f"  - amended text: \"{self.text(rid)}\"")
                if entry.get("params"):
                    lines.append(f"  - amended params: "
                                 f"{json.dumps(entry['params'])}")
                if entry.get("reason"):
                    lines.append(f"  - reason: {entry['reason']}")
            if st == "REPEALED":
                entry = (self.ruling.get("rules") or {}).get(rid) or {}
                lines.append(
                    f"  - the check still exists and is SKIPPED, logged "
                    f"here — not silently absent."
                    + (f" Reason: {entry.get('reason')}"
                       if entry.get("reason") else ""))
        lines.append("")
        return "\n".join(lines)


def validate_ruling(registry: dict, ruling: dict) -> list[str]:
    """Validate a candidate ruling against a registry WITHOUT applying it.
    Returns a list of error strings (empty = valid). Used by the console's
    save endpoint so a bad ruling is rejected before it touches disk."""
    try:
        Canon(registry, ruling)
        return []
    except CanonError as e:
        return [str(e)]


def render_ruling_md(registry: dict, ruling: dict) -> str:
    """The human-readable twin of CANON-RULING.json."""
    rules = {r["id"]: r for r in registry.get("rules", [])}
    props = {p["id"]: p for p in registry.get("proposals", [])}
    out = ["# Director's canon ruling", "",
           f"Ruled by: {ruling.get('ruled_by', '(unsigned)')}",
           f"Ruled at: {ruling.get('ruled_at', '(undated)')}", ""]
    if ruling.get("note"):
        out += [f"> {ruling['note']}", ""]
    for rid, entry in (ruling.get("rules") or {}).items():
        title = rules.get(rid, {}).get("title", "")
        out.append(f"## {rid} — {title}: **{entry.get('status')}**")
        if str(entry.get("text", "")).strip():
            out += ["", f"Amended text: \"{entry['text']}\""]
        if entry.get("params"):
            out += ["", f"Amended params: `{json.dumps(entry['params'])}`"]
        if entry.get("reason"):
            out += ["", f"Reason: {entry['reason']}"]
        out.append("")
    for pid, entry in (ruling.get("proposals") or {}).items():
        title = props.get(pid, {}).get("title", pid)
        out.append(f"## Proposal — {title}: chose "
                   f"**{entry.get('choice', '(none)')}**")
        if entry.get("notes"):
            out += ["", entry["notes"]]
        out.append("")
    hist = ruling.get("history") or []
    if hist:
        out.append(f"_{len(hist)} prior ruling(s) preserved in the history "
                   f"array of CANON-RULING.json._")
        out.append("")
    return "\n".join(out)


_CANON: Canon | None = None


def get_canon() -> Canon:
    """Process-cached canon for pipeline runs. Each CLI/console-spawned run
    is a fresh process, so a saved ruling is picked up on the next run."""
    global _CANON
    if _CANON is None:
        _CANON = Canon.load()
    return _CANON
