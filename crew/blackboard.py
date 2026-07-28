"""Blackboard = the filesystem.

GDD §3.3: "Cross-agent communication happens through artifacts, not through one
giant context window. ... Sessions are cleared between runs; anything worth
keeping is written to a file first, so no run depends on another run's live
context."

This module is the only way crew code touches disk. Two regions:

  blackboard/          seeded, read-mostly. CANON, the GDD, the ratified rules
                       JSON, the vendored reference sim. Agents READ here.
  out/<run-id>/        per-run. Every artifact this run produces. Agents WRITE
                       here, and read each OTHER'S artifacts here.

No agent ever receives another agent's live context — only files. Every read and
every write is logged (append-only, to RUN-LOG.md and to an in-memory ledger the
manifest hashes), so the run log is the evidence that the pattern was followed
rather than merely claimed.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class MissingArtifactError(RuntimeError):
    """A required upstream artifact is not on the blackboard.

    Raised with the name of the AGENT that was supposed to produce it, because
    the whole point of the dependency chain is that a missing agent is
    identifiable from the failure, not merely implied by it.
    """

    def __init__(self, path: str, producer: str, consumer: str):
        self.path, self.producer, self.consumer = path, producer, consumer
        super().__init__(
            f"PIPELINE HALT: {consumer} requires the artifact '{path}', which is "
            f"produced by the {producer}. It is not on the blackboard.\n"
            f"  -> The {producer} did not run, or its stage failed, or its output "
            f"was deleted.\n"
            f"  -> This crew has no fallback for a missing upstream artifact: "
            f"continuing would produce a downstream artifact that LOOKS real and "
            f"is not. Fix the {producer} and re-run."
        )


@dataclass
class LedgerEntry:
    op: str          # "read" | "write" | "copy"
    region: str      # "blackboard" | "out"
    path: str        # repo-relative
    agent: str
    bytes: int
    sha256: str
    ts: float = field(default_factory=time.time)


class Blackboard:
    def __init__(self, run_id: str, root: Path | None = None, quiet: bool = False):
        self.root = Path(root) if root else REPO_ROOT
        self.run_id = run_id
        self.bb_dir = self.root / "blackboard"
        self.run_dir = self.root / "out" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.ledger: list[LedgerEntry] = []
        self.quiet = quiet
        self._log_path = self.run_dir / "RUN-LOG.md"
        if not self._log_path.exists():
            self._log_path.write_text(
                f"# RUN-LOG — {run_id}\n\n"
                "Every blackboard read and write, in order. The blackboard IS the\n"
                "shared memory (GDD §3.3): no agent receives another agent's live\n"
                "context, so this log is the complete record of inter-agent\n"
                "communication for this run.\n\n",
                encoding="utf-8",
            )

    # ---------------- logging ----------------

    def log(self, line: str) -> None:
        with self._log_path.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip() + "\n")
        if not self.quiet:
            print(line.rstrip(), flush=True)

    def stage(self, n: int, agent: str, what: str) -> None:
        self.log(f"\n## Stage {n} — {agent}\n\n{what}\n")

    def note(self, agent: str, msg: str) -> None:
        self.log(f"- `{agent}` {msg}")

    def _record(self, op: str, region: str, p: Path, agent: str, data: bytes) -> None:
        rel = os.path.relpath(p, self.root)
        e = LedgerEntry(op, region, rel, agent, len(data),
                        hashlib.sha256(data).hexdigest()[:16])
        self.ledger.append(e)
        self.log(f"- `{agent}` **{op.upper()}** `{rel}` ({e.bytes} B, sha256:{e.sha256})")

    # ---------------- seeded region (read-mostly) ----------------

    def read_bb(self, rel: str, agent: str) -> str:
        p = self.bb_dir / rel
        if not p.exists():
            raise MissingArtifactError(f"blackboard/{rel}", "blackboard seeding", agent)
        data = p.read_bytes()
        self._record("read", "blackboard", p, agent, data)
        return data.decode("utf-8")

    def bb_path(self, rel: str) -> Path:
        return self.bb_dir / rel

    # ---------------- per-run region ----------------

    def write(self, name: str, content: str, agent: str) -> Path:
        p = self.run_dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8")
        p.write_bytes(data)
        self._record("write", "out", p, agent, data)
        return p

    def read(self, name: str, agent: str, producer: str) -> str:
        """Read another agent's artifact. `producer` is the agent that owns it —
        it is named in the halt message if the artifact is absent."""
        p = self.run_dir / name
        if not p.exists():
            raise MissingArtifactError(f"out/{self.run_id}/{name}", producer, agent)
        data = p.read_bytes()
        self._record("read", "out", p, agent, data)
        return data.decode("utf-8")

    def require(self, name: str, agent: str, producer: str) -> Path:
        """Assert an upstream artifact exists; halt naming its producer if not."""
        p = self.run_dir / name
        if not p.exists() or p.stat().st_size == 0:
            raise MissingArtifactError(f"out/{self.run_id}/{name}", producer, agent)
        return p

    def exists(self, name: str) -> bool:
        p = self.run_dir / name
        return p.exists() and p.stat().st_size > 0

    def path(self, name: str) -> Path:
        return self.run_dir / name

    def copy_into_run(self, src: Path, name: str, agent: str) -> Path:
        dst = self.run_dir / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        self._record("copy", "out", dst, agent, dst.read_bytes())
        return dst

    # ---------------- manifest support ----------------

    def artifact_hashes(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for p in sorted(self.run_dir.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(self.run_dir))
                out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out

    def ledger_json(self) -> list[dict]:
        return [
            {"op": e.op, "region": e.region, "path": e.path, "agent": e.agent,
             "bytes": e.bytes, "sha256": e.sha256}
            for e in self.ledger
        ]

    def write_failed(self, agent: str, stage: str, error: str) -> Path:
        body = (
            f"# FAILED — {self.run_id}\n\n"
            f"| field | value |\n|---|---|\n"
            f"| agent | **{agent}** |\n"
            f"| stage | **{stage}** |\n"
            f"| time | {time.strftime('%Y-%m-%d %H:%M:%S')} |\n\n"
            f"## Error\n\n```\n{error}\n```\n\n"
            f"## What this means\n\n"
            f"The pipeline halted rather than continuing with a missing or invalid\n"
            f"upstream artifact. Downstream agents in this crew have no fallback by\n"
            f"design: a Playtester with no attack list, or a Keeper with no metrics,\n"
            f"would emit a document that reads like evidence and is not.\n\n"
            f"See `RUN-LOG.md` in this directory for the full read/write trail up to\n"
            f"the halt, and `manifest.json` for the stage statuses.\n"
        )
        p = self.run_dir / "FAILED.md"
        p.write_text(body, encoding="utf-8")
        self.log(f"\n**FAILED.md written** — agent=`{agent}` stage=`{stage}`\n")
        return p
