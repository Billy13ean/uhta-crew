# sonder — runbook (Windows, C:\dev\uhta-crew\sonder)

Due 25 Aug 2026 11:59 PM ET. Standalone — nothing here imports the crew
pipelines and nothing imports it.

## 1. Land it
```bat
cd C:\dev\uhta-crew
:: the sonder\ folder is already there (committed from the Cowork drop)
cd sonder
pip install -r requirements.txt
copy .env.example .env        :: paste your ANTHROPIC_API_KEY (same key as the crew's .env)
python sonder.py --selftest   :: expect: SELFTEST PASSED — 203 assertions, no API calls
python sonder.py --mock       :: opens http://127.0.0.1:8765 — play a round to see the terminal, no cost
```

## 2. The live runs (the evidence)
```bat
python sonder.py --script scripts\loyal.txt --seed 7        :: ~33 calls; the deal (era + person) comes from the seed
python sonder.py --script scripts\betrayal.txt --seed 3     :: ~33 calls
python sonder.py                                             :: then play one yourself in the page — the dark deals
```
Each writes `sessions\<id>\` — `transcript.md` is the readable one,
`turn-NN.json` has the full ledger after every turn (rubric: "ledger state
visible in the output or logs"). Read the two scripted transcripts side by
side: same seed family, opposite people.

README §5 is written from the first three live sessions (ila-…45f5,
brand-…e1b3, tate-…df0e). If a later run surprises you more, swap it in and
cite the session id.

## 3. The bank
```bat
python sonder.py --compile            :: mock stories are excluded automatically
start bank\demo.html                  :: click "the red flame converts someone"
```

## 4. Commit
```bat
cd C:\dev\uhta-crew
git add sonder\
git commit -m "A8 sonder: narrative engine + Sonder story bank for uhta"
git tag assignment-8
git push origin main --tags
```
Submit: the repo link (folder `sonder/`), README.md, and one or two
`sessions\<id>\transcript.md` files attached or linked.

## If something goes wrong
- `FAILED: ANTHROPIC_API_KEY is not set` — `.env` is missing or the key line is commented.
- `the dungeon master stumbled: …refused` — a rare stochastic refusal (see crew FINDINGS.md); say the line again, differently.
- Port busy — `python sonder.py --port 8766`.
- The page shows red "style gate — shipped with findings" — that is the gate being honest, not a crash; it is logged in the turn JSON.
