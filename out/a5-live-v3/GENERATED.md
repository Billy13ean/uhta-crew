# GENERATED — narrated teaching opening

## What the agent built *[injected from this run]*

Add narrated teaching opening that names each verb once during genesis (sleep 0) and ends permanently at first Sleep.

GDD v0.9.2 ruling 5 specifies 'a text narrator names each verb and its consequence during the genesis cycle only; the words end permanently at the first sleep.' This requires per-verb state (a set of spoken verbs), a gate on sleep_no===0 (literal 'first sleep'), and hooks at every verb dispatch point. The teaching text is instrumentation layer reading sim state, so it anchors beside other pure resolvers like eraOf(). Hooks fire in tryAct (flame/roar/raze/wait/beacon), moveStep (walk), and doSleep (sleep), and the guide() renderer checks for pending narration each frame.

| | |
|---|---|
| feature | `narrated-teaching-opening` — narrated teaching opening (§3, NICE) |
| gap verdict | ABSENT (layer 1) |
| priority score | +11.50, margin 7.0 |
| inserted after | `function roadStageFor(bornSleep,currentSleep){return bornSleep===currentSleep?'c` |
| lines added | 3 |
| new assertions | G12 teaching: once per verb on sleep 0 only, G13 teaching: all 7 verbs covered |
| repair round-trips | 0 of 1 permitted |

## Existing behaviour this patch changes

- replaced `    SIM.act('walk',np,null,WALK_C);` — Walk is dispatched in moveStep; narration fires once on sleep 0 when the verb succeeds
- replaced `    else SIM.act(kind,SIM.player_pos.slice(),SIM.player_pole,cost);` — All stamina verbs (flame/roar/raze/wait/beacon) dispatch here; narration fires once per verb on sleep 0
- replaced `    transitioning=true; this.nightAlpha=0;` — Sleep narration fires once at the start of the first sleep transition, before the world moves
- replaced `    if(!t.moved)       msg=`The world wakes as grey wanderers. Your <b>${p}</b> zealot gat` — Pending teaching text takes priority over all other guide messages; it clears after one frame so normal guidance resumes

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
cp out/a5-live-v3/uhta-slice.patched.html blackboard/build/uhta-slice.html
# then open it and read the self-test panel, bottom left
```

## Director verification

- [ ] the patched build loads and the self-test panel reads all PASS
- [ ] the feature does what §3 describes
- [ ] the new assertions fail if the feature is removed
