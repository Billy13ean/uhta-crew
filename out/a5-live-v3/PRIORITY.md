# PRIORITY — what to build first, and the arithmetic that decided it

No model produced this ranking. Every term is computed in `builder/priority.py` and printed below, so it can be recomputed by hand.

```
score =  5.0 · (§4 criteria this feature blocks)
       +       tier weight   (CORE 4 · PASS 1 3 · PASS 2 2 · NICE 1 · PROPOSED 0 · CUT −2)
       +  1.5 if no unmet dependency, −3.0 if gated on the stranger test
       −  0.5 · estimated size
       −  4.0 if below the CORE/PASS-1 line AND not unblocking a §4 criterion
```

| # | feature | tier | scan | gate | tier | dep | cost | stop | total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `narrated-teaching-opening` | NICE | ABSENT | +10.0 | +1.0 | +1.5 | -1.0 | +0.0 | **+11.50** |
| 2 | `verb-flame` | CORE | PARTIAL | +0.0 | +4.0 | +1.5 | -1.0 | +0.0 | **+4.50** |
| 3 | `verb-roar` | CORE | PARTIAL | +0.0 | +4.0 | +1.5 | -1.0 | +0.0 | **+4.50** |
| 4 | `verb-sleep` | CORE | ABSENT | +0.0 | +4.0 | +1.5 | -1.0 | +0.0 | **+4.50** |
| 5 | `verb-wait` | CORE | ABSENT | +0.0 | +4.0 | +1.5 | -1.0 | +0.0 | **+4.50** |
| 6 | `verb-walk` | CORE | PARTIAL | +0.0 | +4.0 | +1.5 | -1.0 | +0.0 | **+4.50** |
| 7 | `the-12-12-scale` | CORE | ABSENT | +0.0 | +4.0 | +1.5 | -1.5 | +0.0 | **+4.00** |
| 8 | `the-unification-win-loss-check` | CORE | ABSENT | +0.0 | +4.0 | +1.5 | -1.5 | +0.0 | **+4.00** |
| 9 | `beacons` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.0 | +0.0 | **+3.50** |
| 10 | `ascension` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 11 | `burnout-the-save` | PASS 1 | PARTIAL | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 12 | `genesis` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 13 | `peer-contagion` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 14 | `settling` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 15 | `the-grief-front` | PASS 1 | PARTIAL | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 16 | `worship-stamina` | PASS 1 | ABSENT | +0.0 | +3.0 | +1.5 | -1.5 | +0.0 | **+3.00** |
| 17 | `verb-beacon` | PASS 2 | ABSENT | +0.0 | +2.0 | +1.5 | -1.0 | -4.0 | **-1.50** |
| 18 | `verb-raze` | PASS 2 | PARTIAL | +0.0 | +2.0 | +1.5 | -1.0 | -4.0 | **-1.50** |
| 19 | `faction-fights` | PASS 2 | ABSENT | +0.0 | +2.0 | +1.5 | -1.5 | -4.0 | **-2.00** |
| 20 | `road-allegiance` | PASS 2 | PARTIAL | +0.0 | +2.0 | +1.5 | -1.5 | -4.0 | **-2.00** |
| 21 | `color-coding` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 22 | `emotional-bands` | UNTIERED | PARTIAL | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 23 | `eras` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 24 | `interactive-structures` | NICE | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 25 | `map-size` *(present — not a gap)* | UNTIERED | PRESENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 26 | `narrated-opening` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 27 | `npc-stance` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 28 | `ruined-basins` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 29 | `visible-body` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 30 | `visible-trader-agents` | NICE | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 31 | `wordless-endscreen` | NICE | ABSENT | +0.0 | +1.0 | +1.5 | -1.0 | -4.0 | **-2.50** |
| 32 | `burnout` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 33 | `dominance-tracking` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 34 | `emotional-scale` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 35 | `encounter-first-contact-fear` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 36 | `encounter-first-contact-hope` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 37 | `encounter-holding-fear` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 38 | `encounter-holding-hope` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 39 | `encounter-vigil-fear` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 40 | `encounter-vigil-hope` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 41 | `fog-of-war` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 42 | `follower-behavior` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 43 | `generation-counter` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 44 | `grief-decay` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 45 | `grief-front` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 46 | `loss-condition` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 47 | `one-step-limit` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 48 | `player-alignment` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 49 | `procedural-maps` | NICE | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 50 | `schism` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 51 | `self-test` | UNTIERED | PARTIAL | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 52 | `stamina-budget` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 53 | `tick-system` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 54 | `tribe-system` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 55 | `win-condition` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 56 | `worship` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 57 | `zealot-fate` | UNTIERED | ABSENT | +0.0 | +1.0 | +1.5 | -1.5 | -4.0 | **-3.00** |
| 58 | `final-art-and-audio` | CUT | ABSENT | +0.0 | -2.0 | +1.5 | -1.0 | -4.0 | **-5.50** |
| 59 | `traversal-cinematic` | CUT | ABSENT | +0.0 | -2.0 | +1.5 | -1.0 | -4.0 | **-5.50** |
| 60 | `hopetrade-as-designed` | CUT | PARTIAL | +0.0 | -2.0 | +1.5 | -1.5 | -4.0 | **-6.00** |
| 61 | `road-tier-chains` | CUT | ABSENT | +0.0 | -2.0 | +1.5 | -1.5 | -4.0 | **-6.00** |
| 62 | `encounter-mini-games` | PROPOSED | ABSENT | +0.0 | +0.0 | -3.0 | -1.5 | -4.0 | **-8.50** |
| 63 | `the-only-moment-the-player-touches-individuals` | PROPOSED | ABSENT | +0.0 | +0.0 | -3.0 | -1.5 | -4.0 | **-8.50** |

## Selected: `narrated-teaching-opening` — narrated teaching opening *[injected from this run]*

- **gate** `+10.00` — blocks §4 criteria 1, 3 × 5.0
- **tier** `+1.00` — NICE tier weight
- **dep** `+1.50` — no unmet dependency
- **cost** `-1.00` — estimated size 2 (ui) × -0.5
- **stop** `+0.00` — §3 stop rule WAIVED — the carve-out exempts work that unblocks a §4 criterion: this is the gate, not an addition to it

**Total +11.50**, winning by **7.0** over the next buildable item (`verb-flame`, +4.50).

### Why this is not the obvious answer

`narrated-teaching-opening` sits in the **NICE** tier — the lowest positive tier weight in the table. On build-order value alone it would lose to anything above it. It wins on the `gate` term: it blocks §4 criteria 1, 3, and §4 is the acceptance test the entire project is paused on.

The `stop` term is what makes that legal rather than merely appealing. GDD §3 forbids building anything below the CORE/PASS-1 line until a stranger has played the loop — *except work that unblocks a §4 criterion, which is the gate rather than a violation.* The agent evaluates that carve-out and waives the −4.0 penalty. Every other sub-line feature keeps it.

So the ranking reproduces the Director's own written stop rule, from the rule's text rather than from its conclusion.
