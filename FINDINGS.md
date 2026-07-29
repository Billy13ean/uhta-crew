# FINDINGS — defects this crew surfaced in the uhta game repo

Things the crew found by running against the real blackboard, for the Director's
work queue. Each entry names what it is, how it surfaced, what the crew does
about it now, and what the fix in the **game repo** would be.

The crew never edits `blackboard/sim/` — those files are vendored byte-identical
from the game repo, and the Playtester owns them (GDD §3.1). A crew that quietly
rewrote the reference suite to make its own arms pass would be manufacturing the
evidence it then reports. So every workaround lives in crew-side code, is
labelled as a workaround, and is logged every time it runs.

\---

## 1\. `run\_tyrant` is genesis-incompatible — hard-coded tribe index

**What it is.** `sim/bots.py::run\_tyrant` calls `make\_flamer(2, -1)`, targeting
tribe index 2. That index is correct for the **legacy** start
(`zealot\_poles=(-1,-1,1)`, three pre-clustered tribes) where index 2 is the hope
tribe — the one opposing the fear player. The ratified baseline
`rules-v3.9.1-C.json` enables `world.genesis` with `founding\_poles: \[-1, 1]`, so
the world begins with **two** tribes and grows by schism. `w.tribes\[2]` raises
`IndexError` on the first wake.

**How it was found.** A `--mock-llm` crew run whose fixture attack list named
`run\_tyrant` as a pole-balance probe. Every seed raised; the arm produced nothing.
It has presumably been silently unusable since the Run-20 genesis gate — the
canonical tyrant regression from `metrics-v2`/`v3.x` cannot have been re-run
against any genesis-enabled ruleset.

**Blast radius.** `run\_tyrant` is one of the Playtester's baseline roster arms
(`prompts/v2/playtester.md`, hard rule 4). Any metrics file claiming a tyrant
result on a genesis ruleset is either stale or was not actually run.

**What the crew does about it.** `crew/policy\_shims.py` provides a genesis-safe
`run\_tyrant` and `crew/probe\_runner.py` routes the policy name there instead of
to `bots.py`. The shim reproduces the policy's *intent* rather than its literal
index: resolve the target **once, at t0**, as the first tribe whose pole opposes
the player's — which is what index 2 meant in the world the policy was written
for. Resolving once (not per-wake) matters, because schism grows the tribe list
mid-run and re-picking would be a different policy under the same name. Pole,
15-sleep cap and the acting bot (`bots.make\_flamer`) are unchanged.

Every shimmed arm is stamped: a `SHIM:` line in `RUN-LOG.md` per arm, and a
declared **"Policy shims in force"** table in `metrics-vN.md` above the raw-facts
appendix. A shimmed number is never presented as a measurement of the upstream
policy as written.

**Measured after the shim** — `rules-v3.9.1-C`, seeds 0–7, cap 15, fear pole:

|metric|value|
|-|-|
|seed errors|**0** (was 8/8 `IndexError`)|
|wins|1/8 (seed 7, at sleep 14)|
|`max\_wf` per seed|0.372, 0.398, 0.529, 0.552, 0.823, 0.667, 0.496, 0.938 (median 0.540)|
|`fronts\_spawned` per seed|0, 0, 0, 0, 2, 1, 0, 2|

A live arm with a real spread, not a crash converted into noise. One honest
caveat: at 8 seeds the **medians** are identical across `rules-v3.9.1-C` and the
v3.9.2 fixture variants — only per-seed front counts move (seed 7: 2→1 under
variant A; seed 4: 2→1 under variant C). Read it as a fear-pole *regression
control* that should stay flat, where a move is the signal — not as a
discriminator between small data changes.

**The fix in the game repo.** One line in `sim/bots.py`:

```python
def run\_tyrant(seed):
    w = World(seed); w.player\_pole = -1
    target = next((t.idx for t in w.tribes if t.pole == 1), w.tribes\[-1].idx)
    bot = make\_flamer(target, -1)
    ...
```

Once that lands, delete the entry from `crew/policy\_shims.py::SHIMS` — the shim
is designed to be removable, and the registry is the list of things the game repo
still owes.

\---

## 2\. Composite bots do not carry the grief-front counters

**What it is.** `harness.run()` returns a stat dict including `fronts\_spawned`,
`front\_exposure`, `final\_lf` and `pop`. The composite policies in `bots.py` —
`run\_campaign\_v3`, `run\_siege`, `run\_selfburn` — do not go through
`harness.run()`; each builds its own return dict from a subset of world state, and
none of them includes the grief-front counters. So the campaign bot, which the
project treats as the canonical winning line, **cannot answer any question about
the antagonist.**

**How it was found.** A crew run whose attack list asked for
`median\_front\_exposure` on a `run\_campaign\_v3` arm. The probe executed fine and
the metric came back empty; the board rendered `—`. Nothing crashed, which is
exactly why it is worth writing down — this one fails silently.

**Blast radius.** Any front-feel question routed to the campaign or siege arms
returns nothing. In practice it means grief-front tuning has to be measured on
`bot\_throughput` or `make\_flamer`, which are naive policies, while the
sophisticated policy stays blind to the mechanic the project is currently tuning.

**What the crew does about it.** Nothing — and deliberately. This is a real
limitation of the reference suite, not a bug to wrap: a shim here would have to
invent a return contract for three policies, which is a design decision the
Playtester and the Director own. Instead `prompts/red-teamer.md` carries a
policy→metric table, so the Red-Teamer picks a policy that emits the metric its
invariant names rather than spending an arm to learn it. The Playtester is
required to say "not measured this run" instead of filling the gap.

**The fix in the game repo.** Have the composite bots return a superset — either
by folding the same end-of-run block `harness.run()` uses into each one, or by
factoring that block into a `harness.summarize(world)` helper the composites call.
Mechanical, no behaviour change, and it would make the campaign arm usable for
antagonist work.

\---

*Both entries were produced by running the crew, not by reading the code. That is
the argument for the pipeline: the validation gate and the real-execution
Playtester are what turn "the suite looks fine" into "arm P6 raised on 8 of 8
seeds, here is the exception."*



\---

# Findings 3–9 — surfaced by the first end-to-end live run (2026-07-28)

Findings 1 and 2 above came from *executing* the vendored bot suite. These came
from executing the crew itself against a real API for the first time. Seven
defects, four of them latent since the 3.9.1 schema landed. Every one of them was
invisible to `--selftest` and `--mock-llm`, because both replace the transport or
the model — which is itself the finding underneath the other seven.

Each entry gives the observed failure verbatim, the cause, and what changed.

\---

## 3\. A long generation was sent as a non-streaming request

**Observed**

```
mechanic-designer: Anthropic API call failed after 1 attempt(s)
(non-transient, not retried). Last error: ValueError: Streaming is required for
operations that may take longer than 10 minutes.
```

**Cause.** `crew/llm.py` called `client.messages.create(...)` and waited for a
complete response. The SDK refuses a non-streaming request whose worst-case
duration — derived from `max\\\_tokens` — exceeds ten minutes. The Mechanic Designer
emits up to three complete rulesets; the ratified baseline is 16 KB, so the
ceiling has to be high, and a high ceiling is exactly what trips the guard.

**Fix.** `complete()` now uses `client.messages.stream(...)` and
`get\\\_final\\\_message()`. The returned object is the same `Message`, so usage
accounting, `stop\\\_reason` and content extraction are unchanged.

**Note.** The pre-existing 20,000-token call sat just under the boundary. It had
never failed, and it had never been comfortable either.

\---

## 4\. Every agent's system prompt was its own changelog

**Cause.** `crew/agents/mechanic\\\_designer.py` split the prompt file with:

```python
system, \\\_, template = prompt.partition("## SYSTEM")
```

`str.partition` returns *(before, separator, after)*. The prompt files open with
a version header and a rev-diff blockquote, then `## SYSTEM`, then the role
instructions. So `system` received the **header**, not the instructions — and was
then truncated to 400 characters, cutting mid-sentence. The actual role
contract ("you own exactly one thing", the six hard rules, the variant count)
was concatenated into the *user* message instead.

The model was told its identity was:

> You are the Mechanic Designer for uhta. # Prompt: Mechanic Designer — v3 (crew
> port) > Role: the tunable ruleset for \\\*uhta\\\*. GDD §3.1. > Model: Opus-class
> where budget allows…

**Fix.** Partition twice — at `## SYSTEM`, then at `## CONTEXT PACKET` — so the
system slot gets the role contract and the user slot gets the template. The
`\\\[:400]` truncation is removed.

**Open.** Confirmed and fixed in `mechanic\\\_designer.py`. The other agents build
their prompts by placeholder substitution rather than this partition, so they are
probably unaffected, but **this has not been audited** and should be before the
next ruleset generation.

\---

## 5\. The API refused the Mechanic Designer's call, deterministically

**Observed**

```
LLMError: mechanic-designer: model returned no text content.
stop\\\_reason='refusal' blocks=\\\[] out\\\_tokens=1
```

Six consecutive attempts, across two models' worth of attempted testing.

**Diagnosis.** `crew/probe\\\_refusal.py` (committed) isolates the trigger by
ablation. Its output on the failing packet:

```
\\\[control: trivial            ] stop\\\_reason=end\\\_turn  blocks=\\\['text'] chars=3
\\\[real system, trivial user   ] stop\\\_reason=end\\\_turn  blocks=\\\['text'] chars=5
\\\[bland system, full packet   ] stop\\\_reason=end\\\_turn  blocks=\\\['text'] chars=5
\\\[real system + packet\\\[:2000] ] stop\\\_reason=refusal   blocks=\\\[]       chars=0
\\\[real system + packet\\\[:4000] ] stop\\\_reason=refusal   blocks=\\\[]       chars=0
\\\[real system + packet\\\[:8000] ] stop\\\_reason=end\\\_turn  blocks=\\\['text'] chars=5
\\\[real system + packet\\\[:16000]] stop\\\_reason=refusal   blocks=\\\[]       chars=0
```

Two things fall out. The packet alone is fine — 15.5 KB under a bland system
prompt returns `end\\\_turn`. And the ladder is **non-monotonic**: 8000 passes while
2000 fails, so no single passage is the trigger. It is the combination of the
role framing and the material, near a threshold.

**Cause.** uhta's domain vocabulary — contagion, conversion, wear, burnout,
self-burn, grief, siege, stragglers — is unremarkable in a game-design document
and reads differently stripped of its medium. No prompt in this repo stated that
uhta is a video game. A safety classifier evaluating "you own the contagion
ruleset's tunable cluster" over 15 KB of conversion-and-wear parameters, with no
statement of fictional context anywhere, declined.

**Fix.** A `GAME\\\_FRAMING` preamble now prefixes the Mechanic Designer's system
prompt: uhta is a fictional single-player browser game, every term names a
simulated entity or a numeric state variable, the task is balance tuning of a
JSON config, nothing here applies to real people. All of that is true and none of
it was previously written down. Stage 2 has passed on every run since.

**Worth naming as a design lesson.** A crew whose prompts never state their own
medium inherits that ambiguity at every stage. The other four roles carry the
same vocabulary and have not been given the same framing.

\---

## 6\. A refusal was treated as terminal rather than retryable

**Cause.** `LiveLLM.\\\_transient()` classified connection, timeout, rate-limit and
5xx errors as retryable. A refusal raised a plain `LLMError` and broke out of the
retry loop on the first attempt, halting the run.

**Fix.** New `RefusalError(LLMError)`, raised when `stop\\\_reason == 'refusal'` and
classified as transient. `MAX\\\_ATTEMPTS` raised to 6. A refusal costs one output
token, so the retries are nearly free, and each one is written to `RUN-LOG.md` by
the existing logger — visible in the artifact rather than hidden.

This did not fix finding 5 on its own (that refusal was deterministic), but the
classification was wrong independent of it.

\---

## 7\. The Designer was asked for a file it had never been shown

**Observed**

```
(b) SCHEMA failed: 191 key path(s) present in the ratified baseline
(rules-v3.9.1-C.json) are missing from variant A
```

After the one permitted repair round-trip: 153 missing. Converging, but not
toward completeness — toward whatever the model could reconstruct.

**Cause.** `prompts/mechanic-designer.md` v3 states that "the v2 inline schema
block is replaced by the baseline JSON itself, carried in the packet," and
`crew/validate.py` derives its 203 required key paths from that same baseline. But
the Keeper's packet is an *assembled summary*: observed at 13,065–16,161 B across
runs, against a baseline of 16,362 B. The packet is smaller than the file it is
supposed to contain, and its size varies run to run. The Designer was being asked
to reproduce hundreds of exact values it had never received.

**Fix.** Invert the contract. The model proposes a **delta**; code applies it.
`crew/agents/mechanic\\\_designer.py` now loads the ratified baseline through the
blackboard (so the read lands in `RUN-LOG.md`), deep-merges the model's JSON over
it, and hands the merged file to the validation gate.

This is stronger than what the prompt asked for. Under the old contract, a
"passing" variant was one where the model retyped 203 values from memory, and any
single value drifting would be an unproposed tuning change that nothing would
catch. Under the merge, every parameter the model did not explicitly name is the
ratified value byte-for-byte, and the changed paths are logged with old and new
values:

```
variant A: merged onto baseline — 10 path(s) changed:
  world.uhtcearu\\\_events.grief\\\_front.cooldown\\\_sleeps\\\_after\\\_expiry: 2 -> 3 …
```

**Open.** The merge contains the symptom. The cause — a packet that does not
carry the baseline intact — is unfixed. Either the Keeper must emit the baseline
verbatim, or the packet should carry a reference and the Designer should read the
baseline directly.

\---

## 8\. The merge accepted parameters the game does not have

**Observed.** With an unconstrained deep merge, all three variants reached
`parse=PASS schema=PASS` and then failed check (c):

```
(c) HARNESS failed: the reference simulator could not load or tick this ruleset
```

**Cause.** The model did not only change values; it invented paths —
`scale.initial`, `bands.grey\\\_min`, `contagion.sphere\\\_pressure\\\_per\\\_tick`,
`meta.rules\\\_version`. Plausible names for settings uhta does not have. The first
merge implementation added them all, and the simulator could not load the result.

**Fix.** The merge is now constrained by the baseline, which is the same
principle `crew/validate.py` already states: *the baseline is the schema*. A
variant may change a value at a path the baseline defines. It may not introduce a
path, and it may not change a value's type. `meta.\\\*` is exempt — the harness never
reads it and it carries provenance. Everything dropped is logged with its reason:

```
variant A: 38 proposed path(s) DROPPED (not in the ratified baseline):
  scale.initial; scale.decay\\\_per\\\_tick; bands.grey\\\_min; … 
```

**That drop count is a measurement worth keeping.** The live model dropped 38
paths per variant; the fixture designer in `tests/fixtures/` drops zero and
changes 5–6 real `grief\\\_front` dials. Same merge code. The gap is a direct read
on how far the live Designer drifts from its brief, recorded automatically every
run.

\---

## 9\. `--seeds N` does not control the seed count

**Observed.** `docker compose run --rm crew --seeds 20` produced a run header
reading `Seeds: \\\[0, 1, … 19]` and an `execution-log.json` in which every one of
the 16 arms ran `n=8`.

**Cause.** The Red-Teamer's `attacks.json` specifies a seed count per probe, and
the Playtester honours the probe. Nothing reconciles the probe's value with the
CLI flag, and nothing warns when they disagree.

**Status: unfixed.** The header is misleading as it stands. The minimum fix is
for the Orchestrator to detect the disagreement and either override the probes or
record the conflict in `manifest.json`; the Playtester's Conformance section
should then state the seed count actually used rather than the one requested.

\---

## Cross-cutting

Four of these seven (4, 5, 7, 8) predate tonight and had survived thirteen
ruleset generations. None was reachable by `--selftest` or `--mock-llm`, because
both modes replace the exact component that failed: the transport, the model, or
the model's judgement. The verification layers this repo is proudest of are
real — the validation gate caught findings 7 and 8 before an unloadable ruleset
reached the Red-Teamer, and the halt-by-name discipline made every one of these
diagnosable from a `FAILED.md` rather than a traceback. But no amount of
deterministic testing was going to find them.

The general form: **a pipeline that has never been run end to end against its
real dependencies has not been tested, however green its test suite is.**



