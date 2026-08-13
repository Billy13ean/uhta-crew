# FEATURES — the inventory read out of the GDD

Source: `blackboard/gdd/uhta-gdd-v0.9.9-condensed.md`. The verb table, the build-order tiers and the acceptance criteria were parsed deterministically; the `observable_signature` on each feature — what the code would look like if the feature existed — is the Analyst's, and is the only part of this stage a model produced.

**58 features.** *[injected from this run]*

| id | name | § | tier | kind | signature size | from |
|---|---|---|---|---|---|---|
| `the-12-12-scale` | The −12..+12 scale | §3 | CORE | mechanic | 12 | table |
| `the-unification-win-loss-check` | the unification win/loss check | §3 | CORE | system | 13 | table |
| `verb-flame` | Flame | §2/3 | CORE | verb | 14 | table |
| `verb-roar` | Roar | §2/3 | CORE | verb | 12 | table |
| `verb-sleep` | Sleep | §2/3 | CORE | verb | 9 | table |
| `verb-wait` | Wait | §2/3 | CORE | verb | 12 | table |
| `verb-walk` | Walk | §2/3 | CORE | verb | 12 | table |
| `final-art-and-audio` | final art and audio | §3 | CUT | content | 8 | table |
| `hopetrade-as-designed` | hopetrade as designed | §3 | CUT | system | 7 | table |
| `road-tier-chains` | road-tier chains | §3 | CUT | system | 8 | table |
| `traversal-cinematic` | traversal cinematic | §3 | CUT | ui | 7 | table |
| `interactive-structures` | interactive structures | §3 | NICE | content | 10 | table |
| `narrated-teaching-opening` | narrated teaching opening | §3 | NICE | ui | 9 | table |
| `procedural-maps` | procedural maps | §3 | NICE | system | 11 | table |
| `visible-trader-agents` | visible trader agents | §3 | NICE | content | 10 | table |
| `wordless-endscreen` | wordless endscreen | §3 | NICE | ui | 9 | table |
| `ascension` | ascension | §3 | PASS 1 | system | 10 | table |
| `beacons` | beacons | §3 | PASS 1 | verb | 14 | table |
| `burnout-the-save` | Burnout + the save | §3 | PASS 1 | mechanic | 11 | table |
| `genesis` | genesis | §3 | PASS 1 | system | 10 | table |
| `peer-contagion` | peer contagion | §3 | PASS 1 | mechanic | 7 | table |
| `settling` | settling | §3 | PASS 1 | system | 10 | table |
| `the-grief-front` | the Grief Front | §3 | PASS 1 | system | 12 | table |
| `worship-stamina` | worship→stamina | §3 | PASS 1 | system | 9 | table |
| `faction-fights` | faction fights | §3 | PASS 2 | system | 8 | table |
| `road-allegiance` | Road allegiance | §3 | PASS 2 | mechanic | 8 | table |
| `verb-beacon` | Beacon | §2/3 | PASS 2 | verb | 15 | table |
| `verb-raze` | Raze | §2/3 | PASS 2 | verb | 15 | table |
| `encounter-mini-games` | Encounter mini-games | §3 | PROPOSED | mechanic | 9 | table |
| `the-only-moment-the-player-touches-individuals` | the only moment the player touches individuals | §3 | PROPOSED | mechanic | 6 | table |
| `burnout` | Burnout | §2 | UNTIERED | mechanic | 10 | analyst |
| `emotion-scale` | Emotion Scale | §2 | UNTIERED | mechanic | 12 | analyst |
| `emotional-contagion` | Emotional Contagion | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-first-contact-fear` | First Contact (Fear) | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-first-contact-hope` | First Contact (Hope) | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-holding-fear` | Holding (Fear) | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-holding-hope` | Holding (Hope) | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-vigil-fear` | Vigil (Fear) | §2 | UNTIERED | mechanic | 9 | analyst |
| `encounter-vigil-hope` | Vigil (Hope) | §2 | UNTIERED | mechanic | 9 | analyst |
| `era-progression` | Era Progression | §1 | UNTIERED | system | 15 | analyst |
| `fog-of-war` | Fog of War | §4 | UNTIERED | system | 8 | analyst |
| `grief-decay` | Grief Decay | §2 | UNTIERED | mechanic | 9 | analyst |
| `grief-front` | Grief Front | §2 | UNTIERED | system | 12 | analyst |
| `loss-condition` | Loss Condition | §2 | UNTIERED | system | 9 | analyst |
| `narrated-opening` | Narrated Opening | §1 | UNTIERED | ui | 9 | analyst |
| `one-step-limit` | One Step Limit | §2 | UNTIERED | mechanic | 8 | analyst |
| `player-body-transformation` | Player Body Transformation | §2 | UNTIERED | content | 10 | analyst |
| `reference-simulator` | Reference Simulator | §4 | UNTIERED | system | 8 | analyst |
| `ruleset-json` | Ruleset JSON | §0 | UNTIERED | system | 8 | analyst |
| `schism` | Schism | §2 | UNTIERED | system | 10 | analyst |
| `self-test` | Self-Test | §4 | UNTIERED | system | 10 | analyst |
| `stamina-budget` | Stamina Budget | §2 | UNTIERED | mechanic | 8 | analyst |
| `tile-grid` | Tile Grid | §4 | UNTIERED | system | 9 | analyst |
| `visual-emotion-encoding` | Visual Emotion Encoding | §2 | UNTIERED | ui | 8 | analyst |
| `win-condition` | Win Condition | §2 | UNTIERED | system | 11 | analyst |
| `worship` | Worship | §2 | UNTIERED | system | 8 | analyst |
| `zealot-bands` | Zealot Bands | §2 | UNTIERED | content | 16 | analyst |
| `zealot-fate` | Zealot Fate | §2 | UNTIERED | system | 8 | analyst |

## Acceptance criteria (§4)

- **1.** Reaches their first Sleep without being told what any key does — *Blocked — needs the narrated opening*
- **2.** Can state unprompted what changed while they slept — *Untested — predicted pass*
- **3.** Can name the two things they can make people feel, and which they are doing — *Blocked — same dependency*
- **4.** Reaches a terminal within ~30 min / 10–30 sleeps — *Untested — the sleep envelope is bot-measured; the wall clock never has been*
- **5.** Can point at the fog bank and say what it is doing to them — *Untested — at risk*
- **6.** After losing, can say what they would do differently — *Untested — the one that matters*

## Corpus scope — 8 chunk(s) excluded, each with a reason

`BUILDER_POLICY` is not `CORPUS_POLICY`. The content pipeline wanted game material only, because it was writing prose a player reads. This pipeline also needs §3 and §4 — the build order and the acceptance test — because those are the criteria the build decision is made against. Same corpus, two policies, because the consumer differs.

| chunk | heading | reason |
|---|---|---|
| `uhta-gdd-v0.9.9-condensed.md#front-matter` | front matter | Version preamble. Describes what changed between GDD revisions, not what is true in the world or what remains to be built. |
| `uhta-gdd-v0.9.9-condensed.md#5` | 5. AI Architecture | §5 is the AI-architecture / agent roster — how the game is built, not what is in it and not how the build order is decided. A feature extracted from the roster would be an agent, not a game feature. |
| `uhta-gdd-v0.9.9-condensed.md#6` | 6. Technical Strategy | §6 is technical strategy, verification layers and token budget. It describes the pipeline's own economics; nothing in it is a feature the slice could be missing. |
| `uhta-gdd-v0.9.9-condensed.md#7` | 7. Revision & Growth | §7 is revision provenance — a record of which Assignment-1 note landed where. Document history, not game material. |
| `CANON.md#front-matter` | front matter | Version preamble. Describes what changed between GDD revisions, not what is true in the world or what remains to be built. |
| `uhta-gdd-v0.9.7-full.md#front-matter` | front matter | Version preamble. Describes what changed between GDD revisions, not what is true in the world or what remains to be built. |
| `uhta-gdd-v0.9.7-full.md#5` | 5. Identified Logic Gaps & the Red-Team Arc | §5 is the AI-architecture / agent roster — how the game is built, not what is in it and not how the build order is decided. A feature extracted from the roster would be an agent, not a game feature. |
| `uhta-gdd-v0.9.7-full.md#6` | 6. Open Questions (tuning — deferred to playtest, distinct from gaps) | §6 is technical strategy, verification layers and token budget. It describes the pipeline's own economics; nothing in it is a feature the slice could be missing. |
