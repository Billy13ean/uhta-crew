"""uhta mini-game pipeline — Assignment 6, pipeline #2.

Recommends encounter mini-games, runs them through a GER loop, STOPS at a
human gate, and only then hands the Director-selected design to a Programmer
agent that patches the slice. Fifth pipeline in this repo, and the first with
a human gate in the MIDDLE rather than only at the end:

    propose:  corpus -> [ per encounter slot x pole:
                Generator -> Evaluator -> (Refiner -> Evaluator)* ]
              -> MINIGAME-CANDIDATES.md  ... and the run ENDS. Nothing is
              built. The Director reads the surviving candidates and rules.

    build:    the Director's ruling IS the command line:
                  run_minigame.py --build --select <id> --from-run <run>
              The Programmer agent receives the selected design document plus
              deterministically-extracted anchors from the real slice, and
              emits a patch under the A5 contract: anchored inserts, new
              self-test assertions, every pre-existing assertion survives
              verbatim, the in-place build is never touched.

Why encounters. The GDD's PROPOSED tier designs exactly this content — three
encounter types x two poles, "the one place you touch a person" — and gates
building them on the stranger test (§3's stop rule). This pipeline respects
that gate structurally: propose-mode spends tokens on DESIGN, which the stop
rule does not restrict, and build-mode cannot run without a human typing the
selection. The stop rule's ruling on whether a built encounter is APPLIED to
the canonical slice remains the Director's, exactly as it was for A5's patch.

The GER loop reuses the Assignment-6 machinery where it is generic — the
circuit breaker (ger.breaker) and the halt discipline — and replaces what is
content-specific: the deterministic gate checks a design DOCUMENT (schema,
allowed inputs, outcome vocabulary, wordless language), and the LLM judge
enforces the GDD's encounter rules with its own flag classes:

    NOT-DIEGETIC    the design needs an interface, text, or a HUD — breaks
                    "no interface, no text, only your body and theirs"
    POLE-SYMMETRY   the Hope and Fear reading of the design play the same
                    game — breaks "the two poles never play the same game"
    CONTRADICTS-CHUNK / EXCEEDS-SCOPE / GENERIC  as in the other pipelines

Dependency direction: minigame/ imports crew/, content/ and ger/; nothing
imports minigame/.
"""
PIPELINE_VERSION = "minigame v1 (Assignment 6, pipeline #2)"
