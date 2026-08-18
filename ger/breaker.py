"""The Circuit Breaker — the GER loop's fourth component, two tiers.

Tier 1, per verb: after MAX_REFINE_ROUNDS failed repairs, the verb is
ESCALATED. The loop stops spending on it, the full round history (every line,
every finding) is written to ESCALATED.md, and the run continues to the next
verb. Escalation is a first-class outcome, not a failure: the assignment's
blocker is that manually reviewing every output is slower than writing the
content yourself, and the fix is a loop that self-corrects the cheap failures
and hands a human ONLY the residue, with the evidence attached.

Tier 2, global: if escalations reach ESCALATION_LIMIT, the breaker trips the
whole run. A loop escalating most of its items is not converging item by
item — the Generator/Evaluator pair is misaligned, and every further API call
is spent proving it. Tripping raises BreakerTripped, which the pipeline turns
into FAILED.md naming the breaker as the halting agent.

What the breaker is NOT for: structural contract violations (unparseable
responses, unquoted FAILs, no-op refinements) raise AgentError and halt the
run immediately, exactly as in A3/A4/A5. The breaker meters CONTENT that will
not converge; halts punish CONTRACTS that were broken. Conflating the two
would let a malformed agent burn the whole round budget looking like a hard
line.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MAX_REFINE_ROUNDS = 2      # refinement attempts per verb, after the initial draft
ESCALATION_LIMIT = 3       # escalated verbs (of 7) that trip the whole run


class BreakerTripped(RuntimeError):
    def __init__(self, escalated: list[str], limit: int):
        self.escalated = escalated
        super().__init__(
            f"CIRCUIT BREAKER TRIPPED: {len(escalated)} of the verbs escalated "
            f"({', '.join(escalated)}), reaching the limit of {limit}. A loop "
            f"escalating this many items is not failing item by item — the "
            f"Generator/Evaluator pair is misaligned, and further calls would "
            f"only prove it at API prices. See ESCALATED.md for every round of "
            f"evidence; the fix is a prompt or spec change, then a fresh run."
        )


@dataclass
class RoundRecord:
    round_no: int            # 0 = the Generator's draft, 1.. = refinements
    line: str
    findings: list           # list[Finding]; empty = accepted this round
    judgment: object = None  # the LLM Judgment, when the line reached layer 2

    @property
    def passed(self) -> bool:
        return not self.findings


@dataclass
class VerbOutcome:
    verb: str
    status: str              # ACCEPTED | ESCALATED
    rounds: list[RoundRecord] = field(default_factory=list)

    @property
    def final_line(self) -> str | None:
        return self.rounds[-1].line if self.status == "ACCEPTED" else None

    @property
    def refinements_used(self) -> int:
        return max(0, len(self.rounds) - 1)


class CircuitBreaker:
    def __init__(self, max_rounds: int = MAX_REFINE_ROUNDS,
                 escalation_limit: int = ESCALATION_LIMIT):
        self.max_rounds = max_rounds
        self.escalation_limit = escalation_limit
        self.escalated: list[VerbOutcome] = []

    def allow_refinement(self, rounds_used: int) -> bool:
        """May the loop spend another refinement on this verb?"""
        return rounds_used < self.max_rounds

    def escalate(self, outcome: VerbOutcome) -> None:
        """Record a verb the loop could not converge. Raises BreakerTripped
        the moment the global limit is reached — not at end of run, because
        every call after the trip condition is money spent on a known
        conclusion."""
        outcome.status = "ESCALATED"
        self.escalated.append(outcome)
        if len(self.escalated) >= self.escalation_limit:
            raise BreakerTripped([o.verb for o in self.escalated],
                                 self.escalation_limit)

    def summary(self) -> dict:
        return {
            "max_refine_rounds_per_verb": self.max_rounds,
            "escalation_limit": self.escalation_limit,
            "escalated_verbs": [o.verb for o in self.escalated],
            "tripped": len(self.escalated) >= self.escalation_limit,
        }
