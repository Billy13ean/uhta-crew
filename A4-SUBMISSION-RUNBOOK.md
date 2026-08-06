# Assignment 4 — run the content pipeline, then ship it

Runbook for the **uhta content pipeline** (`run_content.py`). Everything below
runs on your own machine, from the repo root (`uhta-crew/`, the directory
containing `run_content.py`).

Same shape as `A3-SUBMISSION-RUNBOOK.md`, and the same choices baked in: **gh
CLI**, **the existing `Billy13ean/uhta-crew` repo**, **commit a real live run as
evidence**. The one difference that matters: A3's long pole was the simulator;
here it is the API, and the run is cheap enough that you should plan to do it
twice.

Phases 0–2 are the graded path. Phase 3 is the one that decides whether you
score the Consistency Checking criterion, so do not skip it.

---

## Phase 0 — preflight (2 min)

```bash
cd /path/to/uhta-crew
git status --short          # should be clean before you start
python3 --version           # 3.10+ (the crew README says 3.11; 3.10 works)
gh auth status
```

The content pipeline needs no Docker and no `pip install` for the two no-key
modes — they are standard library only. Live mode needs `anthropic`, which is
already in `requirements.txt` from A3.

---

## Phase 1 — the two no-key modes (3 min, no API key)

```bash
python3 run_content.py --selftest
echo "exit: $?"            # expect 0
```

Expect 27 PASS lines across five groups and `SELFTEST PASSED`. This is the
assignment's *"code that does not run receives 0"* bar cleared without spending
a token. It asserts, with real numbers:

- the corpus policy actually removed §3, §4, §7 and `CANON-process.md`
- **§4.5 — your own hand-written worked narration example — is not indexed**
- a Roar query ranks the §2.2 verb table first (bm25 30.12 vs 16.45)
- two off-topic control queries retrieve **nothing** (best 0.00 vs threshold 8.0)
- all 16 beats retrieve two chunks; the A/B arms genuinely differ
- every Critic halt guard fires

```bash
python3 run_content.py --mock-llm --run-id content-mock-demo
echo "exit: $?"            # expect 0
```

Nine artifacts land in `out/content-mock-demo/`. **This is not content** — every
file carries a MOCK banner and `manifest.json` records `"llm_backend": "mock"`.
Commit it anyway: it is the cheapest possible proof for a grader with no key
that the orchestration executes end to end.

### Capture the role-clarity evidence while you are here (1 min, no key)

```bash
python3 run_content.py --mock-llm --drop-agent critic --run-id content-drop-critic
echo "exit: $?"          # expect 1 — the halt IS the passing result
cat out/content-drop-critic/FAILED.md
```

`FAILED.md` should name `critic-n1` as the missing producer and `assemble` as the
blocked consumer. Keep this run directory: it is cheap, deterministic, and the
only *demonstration* — rather than assertion — that the Writer→Critic handoff is
an artifact on the blackboard and not a variable in memory. That is the specific
breakage GDD §3.1 cites as the reason the Orchestrator cannot be removed.

---

## Phase 2 — the live run (the graded artifact)

Your key is already in `.env` from A3, but `run_content.py` reads the
environment directly rather than the file:

```bash
export ANTHROPIC_API_KEY=$(grep -m1 '^ANTHROPIC_API_KEY=' .env | cut -d= -f2-)
echo "${ANTHROPIC_API_KEY:0:7}…"      # sanity: should print sk-ant-…
```

Then:

```bash
python3 run_content.py --candidates 8 2>&1 | tee out/a4-live-console.log
```

Budget **5–10 minutes** and roughly a dollar: 16 beats × 2 calls, plus 4 calls
for the A/B stage — 36 calls at Sonnet prices. `--candidates 8` rather than the
default 6 is deliberate; see Phase 3.

Capture the run id and confirm it was really live:

```bash
RUN=$(ls -t out/ | grep '^content-' | grep -v mock | head -1)
echo "$RUN"
grep -o '"llm_backend": *"[^"]*"' out/$RUN/manifest.json     # must say "live"
grep -o '"status": *"[^"]*"' out/$RUN/manifest.json          # COMPLETE_PENDING_DIRECTOR
ls out/$RUN
```

You want all nine: `narration-lines.md`, `era-flavor.md`,
`endscreen-candidates.md`, `RAG-TRACE.md`, `CRITIC-LOG.md`, `VOICE-JUDGMENT.md`,
`README-A4.md`, `manifest.json`, `RUN-LOG.md`.

**If it halted**, `out/$RUN/FAILED.md` names the agent and the stage. The most
likely cause is a Critic that returned a `FAIL` with no `correction` — which is
the guard working, not a bug. Re-run; the Critic prompt states the requirement
twice and it usually complies on a second pass.

---

## Phase 3 — read CRITIC-LOG.md before anything else (the 2.0 points)

```bash
sed -n '/## Summary/,/## Catches/p' out/$RUN/CRITIC-LOG.md
```

The Consistency Checking criterion requires a catch **shown**. The pipeline
guarantees that any FAIL arrives with a correction; it cannot guarantee a FAIL
happens. So:

| What you see | What to do |
|---|---|
| **caught and corrected ≥ 1** | Done. Move to Phase 4. |
| **caught and corrected = 0** | Re-run at `--candidates 12`. A wider spread at temp 0.9 gives the Critic more to reject. |
| still 0 after that | Read the A/B section of `VOICE-JUDGMENT.md` — arm A retrieves only the experience chunk and is *designed* to produce genericisable lines. That is your likeliest honest catch, and it is already in the artifact. |

Do not manufacture a catch by hand. A CRITIC-LOG with a typed-in rejection is
the one thing in this submission that would be worth failing over, and the whole
architecture is built to make it unnecessary.

While you are in there, skim `VOICE-JUDGMENT.md`'s A/B table. If arm B did not
beat arm A, **leave it** — the document already reports that outcome honestly and
says why one beat at n=8 is a thin sample. A measured result that went the wrong
way is worth more than a claim that went the right way.

---

## Phase 4 — secret hygiene (do NOT skip; the repo is public)

`Billy13ean/uhta-crew` is public. Three checks, same as A3 Phase 4:

```bash
git check-ignore -v .env                        # must print a .gitignore line
grep -rn "sk-ant-[A-Za-z0-9]" out/$RUN out/content-mock-demo || echo "clean — no key in artifacts"
grep -rn "sk-ant-[A-Za-z0-9]" . --exclude-dir=.git --exclude=.env || echo "clean — no key in tree"
```

The console log is the new risk surface this time — `tee` captured whatever the
run printed:

```bash
grep -n "sk-ant" out/a4-live-console.log || echo "clean — no key in the console log"
```

All four must come back clean. If a key ever does land in a commit, rotate it at
console.anthropic.com rather than rewriting history under deadline.

---

## Phase 5 — commit and tag

`out/` is gitignored by design, so a plain `git add` silently skips the run
directories. `-f` is required — this is the same trap as A3:

```bash
git add -A
git status                  # confirm .env is absent
git add -f out/$RUN out/content-mock-demo out/a4-live-console.log
git status --short | grep "^A.*out/" | head    # confirm they are actually staged
```

Point the README at the committed evidence:

```bash
cat >> README.md <<EOF

- \`out/$RUN/\` — a real live content run, \`--candidates 8\`, all four stages.
  \`manifest.json\` records \`"llm_backend": "live"\`. Start at \`README-A4.md\`.
- \`out/content-mock-demo/\` — \`--mock-llm\`, no key needed to reproduce.
EOF

git add README.md
git commit -m "Assignment 4: RAG content pipeline for uhta, with a committed live run

Retriever (deterministic BM25 over the GDD, corpus-scoped to game material
with every exclusion recorded), Writer and Critic, plus an A/B stage that
measures the GDD 4.5 two-chunk retrieval rule against the naive cut.

Three content types the game specifically needs: the teacher's narration for
the opening cycle (which blocks Definition of Playable criteria 1 and 3), era
and settlement flavor, endscreen candidates. Ends at an unfilled Director
selection block.

Includes out/$RUN (live) and out/content-mock-demo (fixtures) as evidence."

git tag -a assignment-4 -m "Assignment 4 submission"
git push origin main
git push origin assignment-4
```

---

## Phase 6 — submit

```bash
echo "$(gh repo view --json url --jq .url)/tree/assignment-4"
```

Send the **tagged** link. Suggested note:

> Assignment 4 — uhta dynamic content pipeline: `<tagged link>`
> Public repo, no invite needed. Start at `out/<run-id>/README-A4.md` — it is
> generated from the run, with the injected numbers marked.
> `RAG-TRACE.md` is the query → chunk → output evidence; `CRITIC-LOG.md` is
> every verdict with its correction; `VOICE-JUDGMENT.md` carries the A/B that
> measures the retrieval tweak.
> `python3 run_content.py --selftest` reproduces the retrieval assertions with
> no API key at all.

---

## Quick reference

| What | Command | Key needed |
|---|---|---|
| Retrieval assertions | `python3 run_content.py --selftest` | no |
| Full orchestration, fixtures | `python3 run_content.py --mock-llm` | no |
| **Submission run** | `python3 run_content.py --candidates 8` | **yes** |
| Wider spread (if no catch) | `python3 run_content.py --candidates 12` | yes |
| One beat only | `python3 run_content.py --beats n4` | yes |
| Role-clarity halt | `python3 run_content.py --mock-llm --drop-agent critic` | no |
| Rules crew (A3, unchanged) | `python3 run_crew.py --selftest` | no |

---

## After the assignment — the part that is actually the point

The eight narration beats are not only content type #1. They are **handoff item
#1**: GDD §2.8 criteria 1 and 3 are Blocked on the narrated opening, and §2.7
lists it as the only unbuilt item blocking the Definition of Playable. Avery has
volunteered to playtest.

So the run does not end at the tag. Fill the `## Director selection` block in
`narration-lines.md`, hand the eight chosen lines to the Programmer, and the
stranger test becomes askable for the first time — which is the gate the whole
design has been waiting on at 0 of 6 tested.
