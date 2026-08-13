# Rouke — *uhta* — Assignment 5: submission runbook

Counterpart to `A3-SUBMISSION-RUNBOOK.md` and `A4-SUBMISSION-RUNBOOK.md`.
**Due 13 Aug, 11:59 PM ET.**

Deliverables: (1) the runnable agent, (2) a README answering three questions.
Both exist. What remains is landing the files, one live run, and the commit.

---

## Phase 0 — land the drop

The agent was built and verified in a cloud container. `a5-drop.tar.gz` was
delivered in the chat.

```bat
cd C:\dev\uhta-crew
tar -xzf %USERPROFILE%\Downloads\a5-drop.tar.gz
```

It unpacks:

```
builder/{__init__,policy,features,codescan,gap,priority,generate,pipeline,assemble,fixtures}.py
prompts/{analyst,gap-adjudicator,programmer}.md
run_builder.py
README-A5.md
blackboard/gdd/uhta-gdd-v0.9.9-condensed.md
```

`blackboard/build/uhta-slice.html` is **already in place** — it was committed to
the working tree earlier this session, byte-identical to the copy you attached
(`sha256 0c68d981…`, 1,351,456 B, 11 assertions).

Nothing in the drop overwrites an existing file. Confirm:

```bat
git status --short
```

Everything should be `??` (untracked). If anything shows `M`, stop and read the
diff before continuing.

---

## Phase 1 — verify, before any API call

```bat
python run_builder.py --selftest
```

Expect **`SELFTEST PASSED — 46 assertions`**, exit 0. No key required, no calls.

Then confirm nothing regressed in the other two pipelines:

```bat
python run_crew.py --selftest
python run_content.py --selftest
```

Both must still print `SELFTEST PASSED` and exit 0. `crew/` and `content/` do not
import `builder/`, so a failure here means the drop touched something it should
not have.

Node is required for the parse check and the headless run:

```bat
node --version
```

If Node is missing, `check_parses` degrades to a brace-balance check and
`check_selftest_runs` reports `SKIPPED` rather than passing — the run still works
but loses its strongest guarantee. Install Node before the live run.

---

## Phase 2 — the orchestration, without spending anything

```bat
python run_builder.py --mock-llm --run-id mock-demo-a5
```

Expect exit 0 and eight artifacts in `out\mock-demo-a5\`. Every one is
banner-stamped as fixture output. Then verify the patched build actually runs —
this is the evidence for deliverable question 3:

```bat
node tools\verify_slice.js out\mock-demo-a5\uhta-slice.patched.html
```

Expect `13 PASS / 0 FAIL`. Against `blackboard\build\uhta-slice.html` you should
get `11 PASS / 0 FAIL`.

*(If `tools\verify_slice.js` isn't in the drop, the same check runs inside
`builder/generate.py::check_selftest_runs` on every live run — the standalone
script is a convenience, not the gate.)*

---

## Phase 3 — the live run

### 3a. Install the one dependency

`--selftest` and `--mock-llm` run on the standard library alone; live mode does
not. Use `python -m pip` rather than bare `pip`, so the install lands in the
interpreter that will actually run the script:

```powershell
python -m pip install -r requirements.txt
python -c "import anthropic; print(anthropic.__version__)"
```

### 3b. Get the key into the ENVIRONMENT, not just into `.env`

**Nothing in this repo reads `.env`.** `crew/llm.py` reads `os.environ`
directly; the file is consumed by `docker-compose.yml`, or exported by hand. The
A4 runbook does it with a bash one-liner, which is not what PowerShell wants.
PowerShell equivalent — loads every key in `.env` into the current session:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim('"').Trim("'"), 'Process')
  }
}
$env:ANTHROPIC_API_KEY.Substring(0,14)     # sanity check — expect sk-ant-api...
$env:CREW_MODEL
```

This sets them for **this PowerShell window only**. Open a new terminal and you
must run it again — which is correct behaviour for a key, not an annoyance.

### 3c. Run

```powershell
python run_builder.py --run-id a5-live
```

**Cost:** roughly 20–25 calls — 1 Analyst, ~15–18 gap adjudications, 1–2
Programmer. Comparable to the A4 live run: about $1 and five to ten minutes.

### What to check in the output

1. **`out\a5-live\PRIORITY.md`** — `narrated-teaching-opening` should rank first,
   with `gate +10.0` and `stop +0.0`. If something else wins, read the table
   before overriding: the ranking is deterministic, so a different winner means
   the gap detection came out differently, and that is a finding rather than a
   bug.
2. **`out\a5-live\GAP-REPORT.md`** — the cross-check section. The narrated
   opening should come back **PARTIAL**, quoting a real line from `guide()`.
   That verdict is the strongest thing in the submission; if it comes back
   ABSENT, the adjudicator missed `guide()` and the report is weaker but still
   honest.
3. **`out\a5-live\GENERATED.md`** — the patch summary, the new assertion names,
   and the repair-round-trip count.
4. **The headless line in `RUN-LOG.md`** — `headless run of the patched build:
   13 PASS / 0 FAIL`, or however many assertions the live patch adds.

### If it halts

`FAILED.md` names the agent and the stage. The halt is the design working — every
guard exists because the alternative is an artifact that reads like evidence and
is not. Re-run after fixing; runs are independent.

The most likely halt is the Programmer failing both patch attempts. Read the
repair log in `FAILED.md`: if it anchored below `function selfTest()`, that is the
temporal-dead-zone trap, and `prompts/programmer.md` already warns about it — the
warning may need to be louder.

---

## Phase 4 — apply the patch to the game

The pipeline does **not** modify the build. You do.

```bat
copy blackboard\build\uhta-slice.html blackboard\build\uhta-slice.pre-a5.html
copy out\a5-live\uhta-slice.patched.html blackboard\build\uhta-slice.html
```

Then open `blackboard\build\uhta-slice.html` in a browser and read the self-test
panel, bottom left. It must be all PASS. Play to the first Sleep and confirm the
narration stops.

Director checklist is at the bottom of `GENERATED.md`.

---

## Phase 5 — commit

**The gitignore trap, same as A3 and A4.** `.gitignore` carries `out/*` with only
`!out/.gitkeep` excepted, so the run directory will not be added by `git add .`
and the submission would ship with no evidence. Force-add it:

```bat
git add builder/ prompts/analyst.md prompts/gap-adjudicator.md prompts/programmer.md
git add run_builder.py README-A5.md A5-SUBMISSION-RUNBOOK.md
git add blackboard/gdd/uhta-gdd-v0.9.9-condensed.md
git add blackboard/build/uhta-slice.html
git add -f out/a5-live/
git status --short
```

`git status` must show `out/a5-live/PRIORITY.md`, `GAP-REPORT.md`, `FEATURES.md`,
`GENERATED.md`, `patch.diff`, `uhta-slice.patched.html`, `RUN-LOG.md` and
`manifest.json` as staged. If they are absent, the `-f` did not take.

`uhta-slice.patched.html` is ~1.35 MB because the build vendors Phaser inline.
That is fine for git; it is the same size as the file already tracked.

```bat
git commit -m "Assignment 5: goal-oriented coding agent, with a committed live run"
git tag assignment-5
git push origin main --tags
```

---

## Phase 6 — submit

Two items:

1. **The agent** — the repo, or the `assignment-5` tag:
   `https://github.com/Billy13ean/uhta-crew/tree/assignment-5`
2. **The README** — `README-A5.md`, which answers all three required questions:
   what was built (§1), why that feature (§2), and whether it ran in the game (§3).

If the grader wants a single document rather than a repo link, `README-A5.md`
stands alone — it quotes the ranking table, the three-way contradiction the gap
detector found in `guide()`, and the headless self-test output.

---

## Known gaps, stated rather than hidden

- **The narration lines in the patch are the mechanism's, not the Writer's.** A4's
  `out/content-a4-live-v2/narration-lines.md` holds the real generated lines.
  Wiring those in is one edit and is worth doing before the capstone; the README
  says plainly that A5 built the thing that shows the words and A4 wrote them.
- **The scan is regex, not a parser.** A feature implemented under a name nothing
  in its signature predicts reads as a false gap. §6 of the README says so.
- **This still does not test whether the game is fun.** That is §4's stranger
  test, and it remains 0 of 6.
