"""The deterministic validation gate between the Mechanic Designer and everything
downstream.

GDD §3.5: "Validation happens before anything is compiled or imported."

A rules variant is not allowed downstream until it passes three checks, in order,
none of which involve a language model:

  (a) PARSE     — it is JSON.
  (b) SCHEMA    — it carries every required key path the ratified baseline
                  carries. The required set is DERIVED FROM THE BASELINE FILE at
                  runtime by walking it (see `required_paths`), never hand-typed:
                  a hand-typed schema goes stale the moment the baseline moves,
                  and this crew's whole claim is that the baseline is the schema.
  (c) LOAD+RUN  — the vendored reference harness imports it as `RULES` and
                  completes a short smoke run without raising. The harness reads
                  ~90 tunables at import time and more per tick, so "it loads and
                  ticks" is a much stronger statement than "it has the keys".

On failure the caller gets a `ValidationResult` carrying the exact error text,
which is fed back to the Designer for exactly ONE repair round-trip. A second
failure aborts the run: an agent that cannot produce a schema-valid artifact
after being shown its own error is not going to produce one on attempt three, and
looping burns the Director's money to no purpose.

Two documented exclusions from the required-key set, both structural rather than
convenient:
  * everything under `meta.` — provenance prose (gate notes, version notes). The
    harness reads none of it; requiring the Designer to reproduce ~4 KB of
    historical narrative verbatim would be a transcription test, not a schema
    test.
  * any path with a segment starting `_` — the baseline's own convention for
    inline annotation (`_declared_asymmetry`, `_burnout_note`).
Both exclusions are applied programmatically, so they too track the baseline.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SIM_TIMEOUT_S = 120


def required_paths(obj, prefix: str = "") -> set[str]:
    """Every dotted key path in a nested dict, minus documented exclusions.

    Lists are treated as leaves: the baseline's `ascension.tiers` is a list of
    four tier dicts, and requiring `ascension.tiers.0.stamina_cap` would forbid a
    variant from proposing three tiers or five. The list key itself is required;
    its shape is the harness's problem (check c).
    """
    out: set[str] = set()
    if not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        path = f"{prefix}{k}"
        out.add(path)
        if path == "meta":
            continue  # required as a key; its contents are prose, not schema
        if isinstance(v, dict):
            out |= required_paths(v, path + ".")
    return out


def present_paths(obj, prefix: str = "") -> set[str]:
    out: set[str] = set()
    if not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        path = f"{prefix}{k}"
        out.add(path)
        if isinstance(v, dict):
            out |= present_paths(v, path + ".")
    return out


@dataclass
class ValidationResult:
    ok: bool
    variant: str
    path: str
    checks: dict[str, str] = field(default_factory=dict)   # check -> PASS/FAIL:reason
    error: str = ""
    smoke: dict = field(default_factory=dict)

    def summary(self) -> str:
        marks = " ".join(
            f"{k}={'PASS' if v == 'PASS' else 'FAIL'}" for k, v in self.checks.items()
        )
        return f"variant {self.variant}: {'VALID' if self.ok else 'INVALID'} [{marks}]"


class Validator:
    def __init__(self, baseline_path: Path, sim_dir: Path):
        self.baseline_path = Path(baseline_path)
        self.sim_dir = Path(sim_dir)
        self.baseline = json.loads(self.baseline_path.read_text(encoding="utf-8"))
        self.required = required_paths(self.baseline)

    # ---- check (a) + (b) ----

    def check_schema(self, text: str, variant: str, path: str) -> ValidationResult:
        res = ValidationResult(ok=False, variant=variant, path=path)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            res.checks["parse"] = "FAIL"
            res.error = f"(a) PARSE failed: {exc}"
            return res
        res.checks["parse"] = "PASS"

        if not isinstance(data, dict):
            res.checks["schema"] = "FAIL"
            res.error = "(b) SCHEMA failed: top level must be a JSON object."
            return res

        have = present_paths(data)
        missing = sorted(self.required - have)
        if missing:
            res.checks["schema"] = "FAIL"
            shown = missing[:40]
            more = "" if len(missing) == len(shown) else f"\n  ... and {len(missing)-len(shown)} more"
            res.error = (
                f"(b) SCHEMA failed: {len(missing)} key path(s) present in the "
                f"ratified baseline ({self.baseline_path.name}) are missing from "
                f"variant {variant}:\n  "
                + "\n  ".join(shown) + more
                + "\n\nEvery baseline key path must appear. Emit the FULL rules file, "
                  "not a diff or a patch."
            )
            return res
        res.checks["schema"] = "PASS"
        res.ok = True
        return res

    # ---- check (c) ----

    def check_harness(self, rules_path: Path, res: ValidationResult) -> ValidationResult:
        """Import the reference harness against this rules file and tick it."""
        code = (
            "import json, sys\n"
            "import harness as H\n"
            "import bots as B\n"
            "r = H.run(B.bot_do_nothing, 0, max_sleeps=3)\n"
            "r.pop('front_events', None)\n"
            "print('SMOKE_JSON=' + json.dumps({k: (list(v) if isinstance(v, tuple) else v)"
            " for k, v in r.items()}))\n"
        )
        env = dict(os.environ)
        env["RULES"] = str(Path(rules_path).resolve())
        env["PYTHONPATH"] = str(self.sim_dir.resolve()) + os.pathsep + env.get("PYTHONPATH", "")
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(self.sim_dir), env=env, capture_output=True,
                text=True, timeout=SIM_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            res.ok = False
            res.checks["harness"] = "FAIL"
            res.error = f"(c) HARNESS failed: smoke run exceeded {SIM_TIMEOUT_S}s."
            return res
        if proc.returncode != 0:
            res.ok = False
            res.checks["harness"] = "FAIL"
            res.error = (
                "(c) HARNESS failed: the reference simulator could not load or tick "
                f"this ruleset (exit {proc.returncode}).\n\n"
                f"--- stderr ---\n{proc.stderr.strip()[-3000:]}"
            )
            return res
        for line in proc.stdout.splitlines():
            if line.startswith("SMOKE_JSON="):
                res.smoke = json.loads(line[len("SMOKE_JSON="):])
        res.checks["harness"] = "PASS"
        res.ok = True
        return res

    def validate_text(self, text: str, variant: str, dest: Path) -> ValidationResult:
        res = self.check_schema(text, variant, str(dest))
        if not res.ok:
            return res
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(json.loads(text), indent=1) + "\n", encoding="utf-8")
        return self.check_harness(dest, res)

    def validate_file(self, path: Path, variant: str) -> ValidationResult:
        path = Path(path)
        res = self.check_schema(path.read_text(encoding="utf-8"), variant, str(path))
        if not res.ok:
            return res
        return self.check_harness(path, res)
