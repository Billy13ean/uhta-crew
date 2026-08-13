"""Stage sequencing, the manifest, and the halt.

Five stages, one per assignment requirement, in dependency order. Anything that
fails stops the run and writes `FAILED.md` naming the stage — never a traceback
to the terminal, same as the other two pipelines.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from content.retriever import (Chunk, Exclusion, Retriever, chunk_markdown)

from . import AgentError
from . import codescan, features as feat, gap, generate, priority
from .policy import BUILDER_POLICY, policy_summary

GDD_DOC = "gdd/uhta-gdd-v0.9.9-condensed.md"
GDD_DETAIL_DOC = "gdd/uhta-gdd-v0.9.7-full.md"
CANON_DOC = "CANON.md"
BUILD_TARGET = "build/uhta-slice.html"

STAGES = [
    (1, "analyst", "read the GDD -> feature inventory"),
    (2, "codescan", "scan the codebase -> symbol / key-path index"),
    (3, "gap", "detect gaps -> PRESENT / PARTIAL / ABSENT with evidence"),
    (4, "priority", "prioritise -> ranked table, every term shown"),
    (5, "programmer", "generate code -> anchored patch + new self-test assertions"),
]


def apply_builder_policy(chunks: list[Chunk]) -> tuple[list[Chunk], list[Exclusion]]:
    """Scope the corpus for a build decision. See `policy.BUILDER_POLICY`."""
    kept, dropped = [], []
    for c in chunks:
        if c.doc in BUILDER_POLICY["exclude_docs"]:
            dropped.append(Exclusion(c.key, c.heading,
                                     BUILDER_POLICY["exclude_docs"][c.doc], c.words))
        elif c.top_level == "front-matter":
            dropped.append(Exclusion(c.key, c.heading,
                                     BUILDER_POLICY["exclude_front_matter"], c.words))
        elif c.top_level in BUILDER_POLICY["exclude_top_level"]:
            dropped.append(Exclusion(c.key, c.heading,
                                     BUILDER_POLICY["exclude_top_level"][c.top_level],
                                     c.words))
        else:
            kept.append(c)
    return kept, dropped


@dataclass
class BuilderRun:
    bb: object
    llm: object
    prompts_dir: Path
    mode: str = "live"
    node_bin: str = "node"
    top_n: int = 12
    force_feature: str | None = None

    gdd_text: str = ""
    chunks: list = field(default_factory=list)
    corpus_exclusions: list = field(default_factory=list)
    retriever: object | None = None

    features: list = field(default_factory=list)
    criteria: list = field(default_factory=list)
    parse_meta: dict = field(default_factory=dict)
    index: object | None = None
    verdicts: list = field(default_factory=list)
    adjudicated: list = field(default_factory=list)
    scores: list = field(default_factory=list)
    chosen: object | None = None

    patch: object | None = None
    patched_source: str = ""
    new_assertions: list = field(default_factory=list)
    repair_log: list = field(default_factory=list)
    selftest_result: tuple = (0, 0)
    retrieval: object | None = None

    stage_status: dict = field(default_factory=dict)
    started: float = field(default_factory=time.time)

    # ---------------- stages ----------------

    def stage1_features(self) -> None:
        self.bb.stage(1, "analyst", STAGES[0][2])
        self.gdd_text = self.bb.read_bb(GDD_DOC, "analyst")
        canon = self.bb.read_bb(CANON_DOC, "analyst")

        raw = chunk_markdown(self.gdd_text, Path(GDD_DOC).name)
        raw += chunk_markdown(canon, CANON_DOC)
        try:
            raw += chunk_markdown(self.bb.read_bb(GDD_DETAIL_DOC, "analyst"),
                                  Path(GDD_DETAIL_DOC).name)
        except Exception:
            self.bb.note("analyst", "v0.9.7-full not seeded — retrieval runs on v0.9.9 alone")
        self.chunks, self.corpus_exclusions = apply_builder_policy(raw)
        self.retriever = Retriever(self.chunks)
        self.bb.note("analyst", f"corpus {len(self.chunks)} chunks in, "
                                f"{len(self.corpus_exclusions)} excluded with reasons")

        self.features, self.criteria, self.parse_meta = feat.extract_deterministic(self.gdd_text)
        self.bb.note("analyst", f"deterministic parse: {self.parse_meta['verbs_parsed']} verbs, "
                                f"{self.parse_meta['tier_items_parsed']} tier items, "
                                f"{self.parse_meta['criteria_parsed']} criteria")

        sections = "\n\n".join(c.text for c in self.chunks
                               if c.doc == Path(GDD_DOC).name)[:36000]
        self.features = feat.run_analyst(self.llm, self.prompts_dir, self.features, sections)
        self.bb.note("analyst", f"{len(self.features)} features, all with signatures")
        self.stage_status[1] = "OK"

    def stage2_scan(self) -> None:
        self.bb.stage(2, "codescan", STAGES[1][2])
        self.index = codescan.build_index(self.bb, "codescan")
        s = self.index.stats()
        self.bb.note("codescan", f"{s['symbols']} symbols, {s['literals']} literals, "
                                 f"{s['key_paths']} rules key paths")
        self.bb.note("codescan", f"SCAN_POLICY excluded {s['excluded_regions']} region(s), "
                                 f"{s['excluded_chars']:,} characters")
        self.stage_status[2] = "OK"

    def stage3_gap(self) -> None:
        self.bb.stage(3, "gap", STAGES[2][2])
        self.verdicts = gap.detect_layer1(self.features, self.index)
        unsure = [v for v in self.verdicts if gap.needs_adjudication(v)]
        self.bb.note("gap", f"layer 1 decided {len(self.verdicts) - len(unsure)} of "
                            f"{len(self.verdicts)}; {len(unsure)} go to layer 2")
        for v in unsure:
            gap.adjudicate(self.llm, self.prompts_dir, v, self.index)
            self.adjudicated.append(v)
        gap.cross_check(self.verdicts)
        d = gap.disagreements(self.verdicts)
        self.bb.note("gap", f"cross-check vs GDD §3 status column: {len(d)} disagreement(s)")
        self.stage_status[3] = "OK"

    def stage4_priority(self) -> None:
        self.bb.stage(4, "priority", STAGES[3][2])
        self.scores = priority.rank(self.verdicts)
        if self.force_feature:
            hit = next((s for s in self.scores if s.feature.id == self.force_feature), None)
            if hit is None:
                raise AgentError("priority", f"--feature {self.force_feature!r} matches no "
                                             f"feature in the inventory")
            self.chosen = hit
            self.bb.note("priority", f"OVERRIDDEN by --feature: {hit.feature.id}")
        else:
            self.chosen = priority.select(self.scores)
        if self.chosen is None:
            raise AgentError("priority", "no selectable gap — every feature in the "
                                         "inventory scanned as PRESENT.")
        self.bb.note("priority", f"selected {self.chosen.feature.id} "
                                 f"(score {self.chosen.total:.2f}, "
                                 f"margin {priority.margin(self.scores)})")
        self.stage_status[4] = "OK"

    def stage5_generate(self) -> None:
        self.bb.stage(5, "programmer", STAGES[4][2])
        f = self.chosen.feature
        source = self.bb.read_bb(BUILD_TARGET, "programmer")
        self.retrieval = self.retriever.select_multi(
            [f"{f.name} {f.description}", f"player experience {f.name}"], per_query=1)
        (self.patch, self.patched_source, self.new_assertions, self.repair_log,
         self.selftest_result) = (
            generate.run_programmer(self.llm, self.prompts_dir, f, self.chosen.verdict,
                                    self.retrieval, source, self.index, self.node_bin))
        self.bb.write("uhta-slice.patched.html", self.patched_source, "programmer")
        self.bb.write("patch.diff",
                      generate.unified_diff(source, self.patched_source, BUILD_TARGET),
                      "programmer")
        before = len(generate.assertions_in(source))
        self.bb.note("programmer", f"self-test {before}/{before} -> "
                                   f"{before + len(self.new_assertions)}/"
                                   f"{before + len(self.new_assertions)}: "
                                   + ", ".join(self.new_assertions))
        np_, nf_ = self.selftest_result
        self.bb.note("programmer", f"headless run of the patched build: {np_} PASS / {nf_} FAIL"
                     if np_ >= 0 else "headless run SKIPPED — no node binary")
        if self.repair_log:
            self.bb.note("programmer", f"repair round-trip used ({len(self.repair_log)} rejection)")
        self.stage_status[5] = "OK"

    # ---------------- driver ----------------

    def run(self) -> None:
        for n, name, _ in STAGES:
            try:
                getattr(self, f"stage{n}_" + ("features" if n == 1 else
                                              "scan" if n == 2 else
                                              "gap" if n == 3 else
                                              "priority" if n == 4 else "generate"))()
            except Exception as exc:
                self.stage_status[n] = "FAILED"
                self.bb.write_failed(name, f"{n} — {STAGES[n-1][2]}", str(exc))
                raise

    def manifest(self) -> dict:
        return {
            "run_id": self.bb.run_id,
            "pipeline": "builder (Assignment 5 — goal-oriented coding agent)",
            "mode": self.mode,
            "prompt_versions": {
                "analyst": feat.PROMPT_VERSION,
                "gap-adjudicator": gap.PROMPT_VERSION,
                "programmer": generate.PROMPT_VERSION,
            },
            "policies": policy_summary(),
            "inputs": {"gdd": GDD_DOC, "build": BUILD_TARGET,
                       "scan_targets": [t[0] for t in codescan.SCAN_TARGETS]},
            "corpus": {"chunks": len(self.chunks), "excluded": len(self.corpus_exclusions)},
            "scan": self.index.stats() if self.index else {},
            "features": len(self.features),
            "verdicts": {v: sum(1 for x in self.verdicts if x.verdict == v)
                         for v in ("PRESENT", "PARTIAL", "ABSENT")},
            "adjudicated": len(self.adjudicated),
            "disagreements": [v.feature.id for v in gap.disagreements(self.verdicts)],
            "selected": self.chosen.feature.id if self.chosen else None,
            "selection_margin": priority.margin(self.scores) if self.scores else None,
            "new_assertions": self.new_assertions,
            "patched_selftest": {"pass": self.selftest_result[0], "fail": self.selftest_result[1]},
            "repair_round_trips": len(self.repair_log),
            "stage_status": self.stage_status,
            "duration_s": round(time.time() - self.started, 1),
            "artifacts": self.bb.artifact_hashes(),
            "blackboard_ledger": self.bb.ledger_json(),
        }

    def write_manifest(self) -> None:
        self.bb.write("manifest.json", json.dumps(self.manifest(), indent=2), "pipeline")
