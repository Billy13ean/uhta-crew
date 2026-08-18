# tests/fixtures/ger — what these files are NOT

These are the canned responses `--mock-llm` replays. They exist to prove the
GER orchestration — generate → evaluate → refine → accept/escalate, both
evaluator layers, and the circuit breaker — executes end to end without an
API key. **They are not content, and nothing here is evidence about uhta's
text.** Every mock-run artifact is banner-stamped to say so, and every canned
verdict carries a `[MOCK FIXTURE]` marker in its reason.

The script is deliberately rigged so one mock run walks every path:

| verb | scripted path |
|---|---|
| walk, wait, beacon, sleep | accepted at round 0 |
| roar | generator line says `Press R` → **deterministic** R2 catch → refined → accepted |
| flame | generator line invents "the old gods" → mock judge FAILs EXCEEDS-SCOPE → refined → accepted |
| raze | three lines fail three different deterministic checks (`?`, `!`, digit) → **ESCALATED** by the circuit breaker |

The baseline-audit verdict for the build's stub `roar` line (CONTRADICTS-CHUNK,
"omits the unconditional Fear push") is the catch a **live** run is expected to
make; here it is canned so the mock run demonstrates where such a catch would
surface. Do not quote it as a real finding — run live and quote that.
