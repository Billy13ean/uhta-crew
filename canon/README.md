# canon/ — the rules registry and the Director's rulings

This folder is the single written-down source of the law the two GER
Evaluators enforce, and the bench the Director rules on it from.

```
rules.json          the registry: every rule (encounter law, narration
                    register, deterministic-check parameters) with its
                    baseline text/params, where it is enforced, and
                    whether it is repealable. Pipelines READ it (via
                    crew/canon.py); nothing ever edits it at run time.
CANON-BIBLE.html    the Bible page — the registry as cards with an
                    uphold / amend / repeal bench. Regenerate with
                    `python3 -m crew.bible`, or serve it live from the
                    crew console at /bible.
CANON-RULING.json   the Director's current ruling (absent = everything
CANON-RULING.md     UPHELD). Written by the Bible page — via the console's
                    save endpoint, or downloaded and dropped here. A new
                    ruling preserves the old one in its `history` array.
```

Three statuses, deliberately no fourth: **UPHELD** (default — absence of
a ruling is an upheld ruling), **AMENDED** (the Director's edited text or
parameters are enforced instead; baseline kept as history), **REPEALED**
(not enforced — and every run logs the skip in its `CANON-IN-FORCE.md`).
There is no ignored/waived status, by the Director's ruling of
2026-08-19: a silently skippable check makes every green run log
unfalsifiable. A repeal is loud; an ignore is invisible.

How it flows: the Bible writes the ruling → `crew/canon.py` validates it
(unknown rule ids, banned statuses, repeals of non-repealable rules all
halt with `CanonError`) → both pipelines load it at run start, enforce
the effective law (prompts get amended text; deterministic checks get
amended params or are skipped if repealed) → each run writes
`CANON-IN-FORCE.md` and a `canon` block in its manifest naming exactly
what law it was judged under, with the ruling file's sha256.

**Commit `CANON-RULING.json` and `.md` whenever you rule** — the ruling
is evidence, the same class of artifact as `DIRECTOR-SELECTION.md`.
