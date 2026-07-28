# FAILED — run-20260728-232857-mock

| field | value |
|---|---|
| agent | **red-teamer** |
| stage | **playtester** |
| time | 2026-07-28 23:28:59 |

## Error

```
PIPELINE HALT: playtester requires the artifact 'out/run-20260728-232857-mock/attacks.json', which is produced by the red-teamer. It is not on the blackboard.
  -> The red-teamer did not run, or its stage failed, or its output was deleted.
  -> This crew has no fallback for a missing upstream artifact: continuing would produce a downstream artifact that LOOKS real and is not. Fix the red-teamer and re-run.
```

## What this means

The pipeline halted rather than continuing with a missing or invalid
upstream artifact. Downstream agents in this crew have no fallback by
design: a Playtester with no attack list, or a Keeper with no metrics,
would emit a document that reads like evidence and is not.

See `RUN-LOG.md` in this directory for the full read/write trail up to
the halt, and `manifest.json` for the stage statuses.
