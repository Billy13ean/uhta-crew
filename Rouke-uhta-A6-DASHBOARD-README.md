# The Director's Dashboard — approvals without a terminal

> Nicholas Rouke · Assignment 6 companion piece · tag: `assignment-6-dashboard`
> The human gate from the mini-game GER pipeline
> (`Rouke-uhta-A6-MINIGAME-README.md`), rendered as an interactive page —
> plus the crew console that launches every pipeline from a browser. This
> exists because the assignment's blocker is *"manually reviewing every one
> is slower than writing the content yourself"* — so the review itself
> should cost as little as possible.

---

## The 60-second tour (no setup, no API key)

1. Clone or download this repo, then open
   **`out/mg-live/MINIGAME-DASHBOARD.html`** in any browser (double-click —
   it is fully self-contained: no server, no network, no storage. GitHub's
   file viewer shows HTML as source, so open it from disk).
2. You are looking at the committed **live run's** six encounter mini-game
   candidates — one card each, split into **THE RULES** (premise, loop,
   controls, stakes, win/fail) and **THE VISUALS** (the diegetic signal
   map, written to hand to the render layer). Each card carries the LLM
   Judge's PASS verdict *with the GDD chunk it cites*, and "Steady the
   Flame" wears a **BUILT** badge — that design was carried through the
   build phase and is playable
   (`out/mg-directors-cut/uhta-slice.minigame.patched.html#mg`).
3. Check any boxes → **Generate Director's ruling** → the page produces a
   signed selection block plus the exact
   `python3 run_minigame.py --build --select <id> --from-run mg-live`
   command per approved item, downloadable as `DIRECTOR-SELECTION.md`.

That is the point of the artifact: **the gate stays structural.** The
dashboard cannot build anything — it writes the *command*, and a human
runs it. Escalated candidates render locked, exactly as the build phase
would refuse them (`--select` on an escalated id exits 1).

## Where it comes from

Every propose run emits its own dashboard automatically
(`minigame/assemble.py` → `minigame/dashboard.py`, deterministic — no LLM
touches it), and the entry point opens it in the default browser the
moment candidates exist. It can also be regenerated for any completed run:

```
python3 -m minigame.dashboard out/<run-id> [--built <id>=<note>]
```

## The companion: the crew console

```
python3 run_console.py        # http://127.0.0.1:8765, opens automatically
```

One local page (Python stdlib only — the one-dependency budget stays spent
on `anthropic`) that launches ANY of the five pipelines — A3 rules crew,
A4 content, A5 coding agent, A6 narration GER, A6 mini-game GER — in
selftest, mock, or live mode; shows running jobs with live log tails and
exit codes; links to a propose run's dashboard the moment it completes;
browses every run directory's artifacts; and saves a pasted ruling into a
run folder as committed evidence. It works because of the crew's
blackboard discipline: every pipeline communicates through files, so the
console never talks to an agent — it starts entry points and reads the
same artifacts the terminal user would. The human gates did not move; they
grew buttons.

## Honest limits

- The dashboard is a **viewer and a ruling-writer**, not an executor — by
  design. If you want one-click builds, the console's launch card does it,
  still as an explicit human action.
- The console binds `127.0.0.1` only and is a development cockpit, not a
  deployment.
- A fresh mock propose run emits a dashboard of **fixture** candidates
  (banner-stamped); the committed `out/mg-live/` dashboard is the one tied
  to real evidence.
