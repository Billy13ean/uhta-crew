# GENERATED — narrated teaching opening

## What the agent built *[injected from this run]*

Add narrated teaching opening that names each verb once during genesis and ends permanently at first sleep.

GDD §sub-3 ruling 5 specifies a text narrator that names each verb and its consequence during the genesis cycle only, ending permanently at the first sleep. This is teaching-text instrumentation, not authorship. Implementation adds a pure resolver `teachingTextFor(sleep_no, verb)` that returns the teaching string during genesis (era 0) only, and returns null thereafter. The resolver is deterministic and testable without Phaser. The self-test verifies that teaching text appears for all verbs during genesis (sleep 0-5), disappears at first sleep (sleep 6), and never returns.

| | |
|---|---|
| feature | `narrated-teaching-opening` — narrated teaching opening (§3, NICE) |
| gap verdict | ABSENT (layer 1) |
| priority score | +11.50, margin 7.0 |
| inserted after | `function eraOf(s){return s>=ERA_SLEEPS[1]?2:s>=ERA_SLEEPS[0]?1:0;}` |
| lines added | 3 |
| new assertions | G9 teaching text: genesis-only, ends at first sleep |
| repair round-trips | 0 of 1 permitted |

## Existing behaviour this patch changes

- none

## Deterministic checks, all passed before anything was written

1. the anchor appears exactly once in the target
2. every pre-existing self-test assertion survives verbatim
3. at least one new assertion was added — a feature that cannot be asserted has not been finished
4. the patched script parses (`node --check`)

### Repair log

- none — the first patch passed every check

## Applying it

The in-place build was **not** modified. This run wrote `uhta-slice.patched.html` and `patch.diff` into its own directory; the Director applies them. The rules crew stops at a blank `## Ruling` and the content pipeline stops at an unfilled `## Director selection` — this pipeline stops here, for the same reason.

```bash
cp out/a5-live/uhta-slice.patched.html blackboard/build/uhta-slice.html
# then open it and read the self-test panel, bottom left
```

## Director verification

- [ ] the patched build loads and the self-test panel reads all PASS
- [ ] the feature does what §3 describes
- [ ] the new assertions fail if the feature is removed
