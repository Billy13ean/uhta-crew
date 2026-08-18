"""uhta GER pipeline — Assignment 6. Generator -> Evaluator -> Refiner -> Circuit Breaker.

Fourth pipeline in this repo, alongside `crew/` (A3, the game's numbers),
`content/` (A4, the game's words in bulk for a human curator) and `builder/`
(A5, the goal-oriented coding agent). This one closes a loop the other three
deliberately left open:

    A4's Writer produced narration candidates in BULK and stopped at an
    unfilled `## Director selection` block. A5's Programmer built the
    TEACHING_TEXT mechanism in the slice and stubbed the seven lines itself.
    The known gap (Rouke-uhta-A5-SUBMISSION-RUNBOOK.md, "Known gaps"): the
    lines in the shipped build are the mechanism's, not the Writer's.

The GER loop targets exactly that content type — the seven first-use verb
narration lines the build's `TEACHING_TEXT` const displays once each during
the genesis cycle (GDD §2.5: "a narrator names each verb the first time you
use it"; "the words end permanently at your first Sleep").

    Generator   one retrieval-grounded line per verb (temp 0.9)
    Evaluator   two layers. A deterministic register gate (ger/checks.py) that
                enforces the GDD §2.5 register rule — short, declarative,
                second person, names the verb, no UI-instruction language, no
                numbers — then an LLM judge (temp 0) that enforces what a
                regex cannot: no mythology, no invented canon, and consequence
                fidelity to the verb's own §2.2 row, quoting the chunk.
    Refiner     rewrites a failing line to address the evaluator's specific
                findings (temp 0.2). It never invents a defect and never
                judges — diagnosis is the Evaluator's, repair is the Refiner's.
                (This is the structural difference from A4, whose Critic did
                both in one call.)
    Breaker     two tiers. Per verb: after MAX_REFINE_ROUNDS failed repairs the
                verb is ESCALATED to the Director with its full round history —
                the loop stops spending on an item it cannot converge. Global:
                if escalations reach ESCALATION_LIMIT the run itself halts —
                systemic non-convergence means the Generator/Evaluator pair is
                misaligned, and that is a human's problem, not a retry's.

Halt discipline is inherited unchanged from A3/A4/A5: a structurally unusable
agent response (unparseable, an unquoted FAIL, a no-op refinement) raises
AgentError and halts the run by name. The circuit breaker is for CONTENT that
will not converge; halts are for CONTRACTS that were broken. The two are not
the same thing and this package keeps them apart.
"""
PIPELINE_VERSION = "ger v1 (Assignment 6)"
