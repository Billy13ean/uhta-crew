"""Critic — adversarial evaluation of the Writer's candidates. Temperature 0.

The one structural guarantee this module exists to make:

    A FAIL verdict with no `correction` raises AgentError and halts the run.

That is why `CRITIC-LOG.md` cannot contain a rejection without a repair — not
because the prompt asks nicely, but because the pipeline is incapable of writing
one. GDD §3.1: the Critic's definition of done is *a catch shown, not claimed*;
a catch with no correction is a claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from crew.llm import LLMCall

from . import AgentError, parse_json_payload, render_chunks

PROMPT_VERSION = "critic v1 (content pipeline)"
TEMPERATURE = 0.0

VALID_CLASSES = {"CONTRADICTS-CHUNK", "EXCEEDS-SCOPE", "WRONG-REGISTER", "GENERIC"}


@dataclass
class Verdict:
    index: int
    line: str
    verdict: str                 # PASS | FAIL
    flag_class: str | None
    quoted_chunk: str
    reason: str
    correction: str | None

    @property
    def failed(self) -> bool:
        return self.verdict == "FAIL"


def _load_prompt(prompts_dir: Path) -> str:
    text = Path(prompts_dir / "critic.md").read_text(encoding="utf-8")
    _, _, template = text.partition("## SYSTEM")
    return template


def run_critic(llm, prompts_dir: Path, beat, selection, candidates: list[str],
               content_type: dict, agent_label: str | None = None) -> list[Verdict]:
    agent = agent_label or f"critic-{beat.id}"
    template = _load_prompt(prompts_dir)
    numbered = "\n".join(f"{i}. {c}" for i, c in enumerate(candidates, 1))
    user = (
        template
        .replace("{{BEAT_LABEL}}", beat.label)
        .replace("{{REGISTER}}", content_type["register"])
        .replace("{{RETRIEVED_CHUNKS}}", render_chunks(selection))
        .replace("{{CANDIDATES}}", numbered)
    )
    out = llm.complete(LLMCall(
        agent=agent,
        system=("You are the Critic for uhta's content pipeline: an adversarial "
                "evaluator that must cite the retrieved chunk a line breaks or "
                "honors, and must repair anything it rejects."),
        user=user, temperature=TEMPERATURE, max_tokens=4000,
    ))
    payload = parse_json_payload(agent, out)
    if not isinstance(payload, list):
        raise AgentError(agent, f"expected a JSON array of verdicts, got {type(payload).__name__}")
    if len(payload) != len(candidates):
        raise AgentError(
            agent,
            f"returned {len(payload)} verdicts for {len(candidates)} candidates. "
            f"Every candidate must be judged; a silently dropped candidate is an "
            f"unreviewed line that could reach the build.",
        )

    verdicts: list[Verdict] = []
    for i, (raw, line) in enumerate(zip(payload, candidates), 1):
        if not isinstance(raw, dict):
            raise AgentError(agent, f"verdict {i} is not an object: {raw!r}")
        v = str(raw.get("verdict", "")).strip().upper()
        if v not in ("PASS", "FAIL"):
            raise AgentError(agent, f"verdict {i} has verdict={raw.get('verdict')!r}; "
                                    f"expected exactly 'PASS' or 'FAIL'")
        cls = raw.get("class")
        cls = str(cls).strip().upper() if cls else None
        correction = raw.get("correction")
        correction = str(correction).strip() if correction else None
        quoted = str(raw.get("quoted_chunk") or "").strip()
        reason = str(raw.get("reason") or "").strip()

        if v == "FAIL":
            # THE structural guarantee. Not advisory.
            if not correction:
                raise AgentError(
                    agent,
                    f"candidate {i} was FAILed with no correction. The Critic's "
                    f"definition of done (GDD §3.1) is a catch SHOWN, not claimed — "
                    f"a rejection without a repair is a claim. Line was: {line!r}",
                )
            if cls not in VALID_CLASSES:
                raise AgentError(
                    agent,
                    f"candidate {i} FAILed with class={cls!r}, which is not one of "
                    f"{sorted(VALID_CLASSES)}. An uncategorised flag cannot be "
                    f"audited.",
                )
            if not quoted:
                raise AgentError(
                    agent,
                    f"candidate {i} FAILed without quoting a chunk. The Critic must "
                    f"cite the text the line breaks, not paraphrase it.",
                )
        verdicts.append(Verdict(i, line, v, cls, quoted, reason, correction))
    return verdicts
