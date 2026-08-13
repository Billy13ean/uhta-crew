# GAP REPORT — the GDD against the codebase

**1 present · 10 partial · 52 absent** across 63 features. 13 went to layer-2 adjudication. *[injected from this run]*

## The cross-check — 19 disagreement(s) with the GDD's own status column

The detector never sees §3's Built/Unbuilt column. `Feature.for_detection()` withholds it, and `--selftest` asserts the withholding. The two readings are therefore independent, and this section is where they differ — which is the only evidence available that this pipeline reads a codebase rather than a status column. An agent that had merely read that column could not disagree with it.

### `verb-walk` — **PARTIAL** (layer 2, score 0.27, signature 4/12)

Walk — §2/3. The code implements walking movement (player_pos update) and road creation (layRoad), but there is no evidence that roads are created 'in player's alignment color' - the road_allegiance system exists but is not connected to the walk action in the visible code.

Evidence, quoted from the source:

```js
this.layRoad(SIM.player_pos,np);            // your trail becomes a road (nomads follow roads)
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-flame` — **PARTIAL** (layer 2, score 0.20, signature 3/14)

Flame — §2/3. The code implements flame pushing NPCs toward player alignment within a radius, but does not implement the 'saves opposite-burned' mechanic described in the GDD—instead it clears burn status and restores frozen value for opposite-aligned burned NPCs, which is a different behavior than 'saving' them.

Evidence, quoted from the source:

```js
if(x.burn){if(x.I*pole<0){x.burn=false;x.v=trunc(x.burn_frozen*SAVE_F);if(x.v===0)x.ever_nonzero=true;}}
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-roar` — **PARTIAL** (layer 2, score 0.20, signature 3/12)

Roar — §2/3. The code implements fear push on witnesses (roar_fear_push:2.8, roar_witness_radius_R_tiles:6) and saves hope-burned NPCs, but there is no evidence of 'carve road line' functionality in the roar implementation.

Evidence, quoted from the source:

```js
if(x.burn&&x.I>0){x.burn=false;x.v=trunc(x.burn_frozen*SAVE_F);if(x.v===0)x.ever_nonzero=true;}
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-beacon` — **ABSENT** (layer 1, score 0.12, signature 2/15)

Beacon — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-raze` — **PARTIAL** (layer 2, score 0.20, signature 3/15)

Raze — §2/3. The code implements raze with fear effects within a radius and cost scaling with devout count, but the GDD says 'fear spike' while the code applies 'fear_push_per_witness' which suggests a push mechanic rather than a spike, and the cost calculation counts devouts but the actual fear application mechanism differs from what 'spike' implies.

Evidence, quoted from the source:

```js
for(const x of this.npcs){if(x.zealot||x.burn)continue;if(cheb(x.pos,pos)<=RAZE.witness_radius_tiles)add(x,-RAZE.fear_push_per_witness*this.eff_mult(x,-
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-wait` — **ABSENT** (layer 1, score 0.12, signature 2/12)

Wait — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-sleep` — **ABSENT** (layer 1, score 0.15, signature 3/10)

Sleep — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-12-12-scale` — **ABSENT** (layer 2, score 0.28, signature 2/10)

The −12..+12 scale — §3. No implementation of the -12 to +12 emotional alignment scale from Fear to Hope is found in the source. The signature elements that would indicate this feature (alignment, emotionalAlignment, belief scale, or the specific range -12 to +12) are all absent.

Searched for and did not find: `alignment`, `emotionalAlignment`, `emotional_alignment`, `beliefScale`, `belief_scale`, `-12`, `12`, `Fear`

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-unification-win-loss-check` — **ABSENT** (layer 1, score 0.12, signature 2/12)

the unification win/loss check — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `burnout-the-save` — **PARTIAL** (layer 2, score 0.16, signature 2/10)

Burnout + the save — §3. Configuration parameters for burnout thresholds and save mechanics exist, but the actual implementation logic that detects excessive pressure, freezes people grey, and saves them with opposite feeling is not present in the shown source.

Evidence, quoted from the source:

```js
Y      = RULES['burnout']['overdose_threshold_Y_per_tick']  # 4
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `genesis` — **ABSENT** (layer 1, score 0.15, signature 2/10)

genesis — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `settling` — **ABSENT** (layer 1, score 0.07, signature 1/10)

settling — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `beacons` — **ABSENT** (layer 1, score 0.12, signature 2/16)

beacons — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `worship-stamina` — **ABSENT** (layer 1, score 0.00, signature 0/9)

worship→stamina — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `ascension` — **ABSENT** (layer 1, score 0.15, signature 3/12)

ascension — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `peer-contagion` — **ABSENT** (layer 1, score 0.00, signature 0/9)

peer contagion — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-grief-front` — **PARTIAL** (layer 2, score 0.21, signature 3/13)

the Grief Front — §3. The grief_front configuration shows duration_sleeps:3 and spawns at the largest dominant tribe, but there is no evidence in the source of desaturating fog visual effects or cancellation of zealot pull mechanics.

Evidence, quoted from the source:

```js
grief_front:{trigger_dominance_min:0.55,max_concurrent_fronts:1,cooldown_sleeps_after_expiry:2,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `road-allegiance` — **PARTIAL** (layer 2, score 0.21, signature 2/8)

Road allegiance — §3. The code implements road allegiance with player ownership (implied by 'enemy_road') and strength mechanics, but does not show evidence that roads 'enable influence on rooted settlements' as the GDD describes.

Evidence, quoted from the source:

```js
road_allegiance:{enabled:true,initial_strength:3,erode_per_sleep:1.0,wear_per_crossing:1,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `faction-fights` — **ABSENT** (layer 1, score 0.00, signature 0/8)

faction fights — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

## Gaps found

### `verb-walk` — **PARTIAL** (layer 2, score 0.27, signature 4/12)

Walk — §2/3. The code implements walking movement (player_pos update) and road creation (layRoad), but there is no evidence that roads are created 'in player's alignment color' - the road_allegiance system exists but is not connected to the walk action in the visible code.

Evidence, quoted from the source:

```js
this.layRoad(SIM.player_pos,np);            // your trail becomes a road (nomads follow roads)
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-flame` — **PARTIAL** (layer 2, score 0.20, signature 3/14)

Flame — §2/3. The code implements flame pushing NPCs toward player alignment within a radius, but does not implement the 'saves opposite-burned' mechanic described in the GDD—instead it clears burn status and restores frozen value for opposite-aligned burned NPCs, which is a different behavior than 'saving' them.

Evidence, quoted from the source:

```js
if(x.burn){if(x.I*pole<0){x.burn=false;x.v=trunc(x.burn_frozen*SAVE_F);if(x.v===0)x.ever_nonzero=true;}}
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-roar` — **PARTIAL** (layer 2, score 0.20, signature 3/12)

Roar — §2/3. The code implements fear push on witnesses (roar_fear_push:2.8, roar_witness_radius_R_tiles:6) and saves hope-burned NPCs, but there is no evidence of 'carve road line' functionality in the roar implementation.

Evidence, quoted from the source:

```js
if(x.burn&&x.I>0){x.burn=false;x.v=trunc(x.burn_frozen*SAVE_F);if(x.v===0)x.ever_nonzero=true;}
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-beacon` — **ABSENT** (layer 1, score 0.12, signature 2/15)

Beacon — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-raze` — **PARTIAL** (layer 2, score 0.20, signature 3/15)

Raze — §2/3. The code implements raze with fear effects within a radius and cost scaling with devout count, but the GDD says 'fear spike' while the code applies 'fear_push_per_witness' which suggests a push mechanic rather than a spike, and the cost calculation counts devouts but the actual fear application mechanism differs from what 'spike' implies.

Evidence, quoted from the source:

```js
for(const x of this.npcs){if(x.zealot||x.burn)continue;if(cheb(x.pos,pos)<=RAZE.witness_radius_tiles)add(x,-RAZE.fear_push_per_witness*this.eff_mult(x,-
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-wait` — **ABSENT** (layer 1, score 0.12, signature 2/12)

Wait — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-sleep` — **ABSENT** (layer 1, score 0.15, signature 3/10)

Sleep — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-12-12-scale` — **ABSENT** (layer 2, score 0.28, signature 2/10)

The −12..+12 scale — §3. No implementation of the -12 to +12 emotional alignment scale from Fear to Hope is found in the source. The signature elements that would indicate this feature (alignment, emotionalAlignment, belief scale, or the specific range -12 to +12) are all absent.

Searched for and did not find: `alignment`, `emotionalAlignment`, `emotional_alignment`, `beliefScale`, `belief_scale`, `-12`, `12`, `Fear`

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-unification-win-loss-check` — **ABSENT** (layer 1, score 0.12, signature 2/12)

the unification win/loss check — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `burnout-the-save` — **PARTIAL** (layer 2, score 0.16, signature 2/10)

Burnout + the save — §3. Configuration parameters for burnout thresholds and save mechanics exist, but the actual implementation logic that detects excessive pressure, freezes people grey, and saves them with opposite feeling is not present in the shown source.

Evidence, quoted from the source:

```js
Y      = RULES['burnout']['overdose_threshold_Y_per_tick']  # 4
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `genesis` — **ABSENT** (layer 1, score 0.15, signature 2/10)

genesis — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `settling` — **ABSENT** (layer 1, score 0.07, signature 1/10)

settling — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `beacons` — **ABSENT** (layer 1, score 0.12, signature 2/16)

beacons — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `worship-stamina` — **ABSENT** (layer 1, score 0.00, signature 0/9)

worship→stamina — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `ascension` — **ABSENT** (layer 1, score 0.15, signature 3/12)

ascension — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `peer-contagion` — **ABSENT** (layer 1, score 0.00, signature 0/9)

peer contagion — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-grief-front` — **PARTIAL** (layer 2, score 0.21, signature 3/13)

the Grief Front — §3. The grief_front configuration shows duration_sleeps:3 and spawns at the largest dominant tribe, but there is no evidence in the source of desaturating fog visual effects or cancellation of zealot pull mechanics.

Evidence, quoted from the source:

```js
grief_front:{trigger_dominance_min:0.55,max_concurrent_fronts:1,cooldown_sleeps_after_expiry:2,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `road-allegiance` — **PARTIAL** (layer 2, score 0.21, signature 2/8)

Road allegiance — §3. The code implements road allegiance with player ownership (implied by 'enemy_road') and strength mechanics, but does not show evidence that roads 'enable influence on rooted settlements' as the GDD describes.

Evidence, quoted from the source:

```js
road_allegiance:{enabled:true,initial_strength:3,erode_per_sleep:1.0,wear_per_crossing:1,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `faction-fights` — **ABSENT** (layer 1, score 0.00, signature 0/8)

faction fights — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `narrated-teaching-opening` — **ABSENT** (layer 1, score 0.00, signature 0/9)

narrated teaching opening — §3. deterministic signature probe

### `wordless-endscreen` — **ABSENT** (layer 1, score 0.00, signature 0/9)

wordless endscreen — §3. deterministic signature probe

### `visible-trader-agents` — **ABSENT** (layer 1, score 0.00, signature 0/9)

visible trader agents — §3. deterministic signature probe

### `interactive-structures` — **ABSENT** (layer 1, score 0.00, signature 0/9)

interactive structures — §3. deterministic signature probe

### `procedural-maps` — **ABSENT** (layer 1, score 0.00, signature 0/10)

procedural maps — §3. deterministic signature probe

### `encounter-mini-games` — **ABSENT** (layer 1, score 0.00, signature 0/11)

Encounter mini-games — §3. deterministic signature probe

### `the-only-moment-the-player-touches-individuals` — **ABSENT** (layer 1, score 0.00, signature 0/9)

the only moment the player touches individuals — §3. deterministic signature probe

### `hopetrade-as-designed` — **PARTIAL** (layer 2, score 0.37, signature 3/8)

hopetrade as designed — §3. The GDD states the feature is 'deferred until core loop proven fun', meaning it should NOT be implemented yet. However, the code shows HOPE_TRADE being loaded from world configuration and assigned to a variable, suggesting at least partial implementation infrastructure exists rather than being truly deferred.

Evidence, quoted from the source:

```js
HOPE_TRADE = WORLD.get('hope_trade', None)                  # schema 3.7.2 (hope colonies trade -> green roads)
```

### `road-tier-chains` — **ABSENT** (layer 1, score 0.00, signature 0/9)

road-tier chains — §3. deterministic signature probe

### `traversal-cinematic` — **ABSENT** (layer 1, score 0.00, signature 0/8)

traversal cinematic — §3. deterministic signature probe

### `final-art-and-audio` — **ABSENT** (layer 1, score 0.07, signature 1/10)

final art and audio — §3. deterministic signature probe

### `emotional-scale` — **ABSENT** (layer 2, score 0.19, signature 2/12)

Emotional Scale — §2. No source code provided to examine, and all expected identifiers for a twelve-step emotional scale (emotionalPosition, emotional_scale, emotionalScale, apathyCenter, scale values -12/0/12) are reported as not found.

Searched for and did not find: `emotionalPosition`, `emotional_scale`, `emotionalScale`, `scaleMin`, `scaleMax`, `apathyCenter`, `-12`, `12`

### `stamina-budget` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Stamina Budget — §2. deterministic signature probe

### `burnout` — **ABSENT** (layer 1, score 0.00, signature 0/10)

Burnout — §2. deterministic signature probe

### `schism` — **ABSENT** (layer 1, score 0.15, signature 2/11)

Schism — §2. deterministic signature probe

### `zealot-fate` — **ABSENT** (layer 1, score 0.00, signature 0/10)

Zealot Fate — §2. deterministic signature probe

### `worship` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Worship — §2. deterministic signature probe

### `grief-front` — **ABSENT** (layer 1, score 0.14, signature 2/12)

Grief Front — §2. deterministic signature probe

### `grief-decay` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Grief Decay — §2. deterministic signature probe

### `one-step-limit` — **ABSENT** (layer 1, score 0.00, signature 0/8)

One Step Limit — §2. deterministic signature probe

### `win-condition` — **ABSENT** (layer 1, score 0.06, signature 1/13)

Win Condition — §2. deterministic signature probe

### `loss-condition` — **ABSENT** (layer 1, score 0.06, signature 1/11)

Loss Condition — §2. deterministic signature probe

### `emotional-bands` — **PARTIAL** (layer 2, score 0.38, signature 7/14)

Emotional Bands — §2. The code implements four emotional bands (grey, tentative, devout, zealot) based on intensity thresholds, but 'grey' is only returned when intensity is exactly zero, not as a visible band at extremes as the GDD describes. The bands appear at: zero (grey), low intensity (tentative), medium (devout), and high (zealot), which doesn't match 'at extremes' for all four bands.

Evidence, quoted from the source:

```js
function band(I){const a=Math.abs(I);if(a===0)return'grey';if(a<=TENT_HI)return'tentative';if(a<=DEV_HI)return'devout';return'zealot';}
```

### `encounter-first-contact-hope` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Encounter: First Contact (Hope) — §2. deterministic signature probe

### `encounter-first-contact-fear` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Encounter: First Contact (Fear) — §2. deterministic signature probe

### `encounter-vigil-hope` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Encounter: Vigil (Hope) — §2. deterministic signature probe

### `encounter-vigil-fear` — **ABSENT** (layer 1, score 0.00, signature 0/10)

Encounter: Vigil (Fear) — §2. deterministic signature probe

### `encounter-holding-hope` — **ABSENT** (layer 1, score 0.07, signature 1/9)

Encounter: Holding (Hope) — §2. deterministic signature probe

### `encounter-holding-fear` — **ABSENT** (layer 1, score 0.07, signature 1/9)

Encounter: Holding (Fear) — §2. deterministic signature probe

### `eras` — **ABSENT** (layer 1, score 0.08, signature 2/14)

Eras — §1. deterministic signature probe

### `fog-of-war` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Fog of War — §4. deterministic signature probe

### `narrated-opening` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Narrated Opening — §3. deterministic signature probe

### `color-coding` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Color Coding — §2. deterministic signature probe

### `player-alignment` — **ABSENT** (layer 1, score 0.15, signature 4/11)

Player Alignment — §1. deterministic signature probe

### `generation-counter` — **ABSENT** (layer 1, score 0.15, signature 1/8)

Generation Counter — §2. deterministic signature probe

### `dominance-tracking` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Dominance Tracking — §2. deterministic signature probe

### `tribe-system` — **ABSENT** (layer 1, score 0.11, signature 1/7)

Tribe System — §2. deterministic signature probe

### `self-test` — **PARTIAL** (layer 2, score 0.31, signature 4/10)

Self Test — §4. The code implements a self-test function that runs on load and reports PASS/FAIL, but there is no evidence it compares against a 'reference simulator' tick-for-tick as specified in the GDD. The test creates World instances and performs checks, but no reference implementation or tick-by-tick validation is visible.

Evidence, quoted from the source:

```js
function selfTest(){
```

### `ruined-basins` — **ABSENT** (layer 1, score 0.00, signature 0/11)

Ruined Basins — §2. deterministic signature probe

### `visible-body` — **ABSENT** (layer 1, score 0.15, signature 2/10)

Visible Body — §2. deterministic signature probe

### `tick-system` — **ABSENT** (layer 1, score 0.15, signature 1/8)

Tick System — §2. deterministic signature probe

### `npc-stance` — **ABSENT** (layer 1, score 0.00, signature 0/6)

NPC Stance — §2. deterministic signature probe

### `follower-behavior` — **ABSENT** (layer 1, score 0.00, signature 0/7)

Follower Behavior — §2. deterministic signature probe

## Scan scope

Indexed **856 symbols**, 341 string literals and 226 ruleset key paths. `SCAN_POLICY` excluded **5 region(s), 1,253,989 characters** — overwhelmingly the vendored Phaser bundle. That exclusion is the code-side twin of the content pipeline's §4.5 exclusion: §4.5 was cut because indexing it let the Writer retrieve the answer instead of writing one, and Phaser is cut because indexing it makes every feature look already built.

| file | line | chars | rule | reason |
|---|---|---|---|---|
| `build/uhta-slice.html` | 8 | 1,181,901 | vendor_signature | line opens with the minified-bundle preamble '!function(t,e){'; this is a vendored library, and indexing it would make every feature appear already implemented |
| `build/uhta-slice.html` | 776 | 11,761 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 777 | 50,583 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 778 | 9,416 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 779 | 328 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
