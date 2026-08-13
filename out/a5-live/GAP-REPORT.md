# GAP REPORT — the GDD against the codebase

**1 present · 12 partial · 45 absent** across 58 features. 16 went to layer-2 adjudication. *[injected from this run]*

## The cross-check — 19 disagreement(s) with the GDD's own status column

The detector never sees §3's Built/Unbuilt column. `Feature.for_detection()` withholds it, and `--selftest` asserts the withholding. The two readings are therefore independent, and this section is where they differ — which is the only evidence available that this pipeline reads a codebase rather than a status column. An agent that had merely read that column could not disagree with it.

### `verb-walk` — **ABSENT** (layer 1, score 0.12, signature 2/12)

Walk — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-flame` — **PARTIAL** (layer 2, score 0.20, signature 3/14)

Flame — §2/3. The code implements flame pushing NPCs toward player alignment within a radius, but does not show the 'save opposite-burned' mechanic described in the GDD (reversing burn state and restoring frozen value for opposite-aligned burned NPCs).

Evidence, quoted from the source:

```js
if(kind==='flame'){const fr=this.flame_r;  // schema 3.8 ascension-scaled flame radius
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

Raze — §2/3. The code implements raze with fear effects and cost scaling with devout count, but the GDD specifies a 'fear spike' while the code applies 'fear_push_per_witness' which suggests a push mechanic rather than a spike, and the cost calculation uses 'RAZE_' (appears truncated) rather than clearly showing the devout multiplier structure described in the GDD.

Evidence, quoted from the source:

```js
razeCost(){let d=0;for(const x of SIM.npcs)if(!x.zealot&&!x.burn&&cheb(x.pos,SIM.player_pos)<=RAZE.witness_radius_tiles&&band(x.I)==='devout')d++;return RAZE_
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-wait` — **PARTIAL** (layer 2, score 0.27, signature 4/12)

Wait — §2/3. The code pushes NPCs when the player waits, but it pushes toward the NPC's current direction (copysign(WAIT_PUSH, x.v)) rather than unconditionally toward Apathy as the GDD specifies.

Evidence, quoted from the source:

```js
if(cheb(x.pos,pos)<=WAIT_R&&x.I!==0)add(x,-copysign(WAIT_PUSH,x.v),false);
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-sleep` — **ABSENT** (layer 1, score 0.15, signature 2/9)

Sleep — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-12-12-scale` — **ABSENT** (layer 2, score 0.19, signature 2/12)

The −12..+12 scale — §3. No source code was shown in the matches section, and signature elements for emotional alignment, the -12 to +12 range, Fear, Hope, or alignment scale were not found in the indexed source.

Searched for and did not find: `alignment`, `emotionalState`, `emotional_state`, `beliefScale`, `belief_scale`, `-12`, `12`, `Fear`

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-unification-win-loss-check` — **ABSENT** (layer 1, score 0.12, signature 2/13)

the unification win/loss check — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `burnout-the-save` — **PARTIAL** (layer 2, score 0.16, signature 2/11)

Burnout + the save — §3. Configuration parameters and a burnout frame type exist, but the actual logic that freezes a person grey upon excessive same-pressure or saves them with opposite feeling is not visible in the provided source.

Evidence, quoted from the source:

```js
Y      = RULES['burnout']['overdose_threshold_Y_per_tick']  # 4
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `genesis` — **PARTIAL** (layer 2, score 0.20, signature 2/10)

genesis — §3. The genesis configuration exists with grey_nomads (55) and founding_poles ([-1,1]), but the GDD specifies 'one founding zealot per pole' while the code shows 'zealot_seeds_each:3', meaning three zealots per pole rather than one.

Evidence, quoted from the source:

```js
genesis:{enabled:true,grey_nomads:55,zealot_seeds_each:3,min_settle_members:5,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `settling` — **ABSENT** (layer 1, score 0.07, signature 1/10)

settling — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `beacons` — **PARTIAL** (layer 2, score 0.21, signature 3/14)

beacons — §3. Beacons exist and are rendered with alignment-based visuals (hope/fear), but there is no evidence in the source that they reveal map in ruined basins or radiate a permanent aura as described in the GDD.

Evidence, quoted from the source:

```js
for(const [bp,bpole] of SIM.beacons){const col=bpole>0?COL.hope:COL.fear;const bx=bp[0]*CELL+CELL/2,by=bp[1]*CELL+CELL/2;
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `worship-stamina` — **ABSENT** (layer 1, score 0.00, signature 0/9)

worship→stamina — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `ascension` — **ABSENT** (layer 1, score 0.07, signature 1/10)

ascension — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `peer-contagion` — **ABSENT** (layer 1, score 0.00, signature 0/7)

peer contagion — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-grief-front` — **PARTIAL** (layer 2, score 0.30, signature 4/12)

the Grief Front — §3. The grief front is implemented as a fog bank on the winner's largest tribe with a 3-sleep duration, but there is no evidence in the source that it cancels zealot pull during those three sleeps—the code shows zealot behavior is tested but not that the front actively suppresses zealot mechanics.

Evidence, quoted from the source:

```js
grief_front:{trigger_dominance_min:0.55,max_concurrent_fronts:1,cooldown_sleeps_after_expiry:2,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `road-allegiance` — **PARTIAL** (layer 2, score 0.21, signature 2/8)

Road allegiance — §3. The code implements road allegiance with strength and enemy-road detection, but does not show evidence that roads 'enable influence on rooted settlements' as the GDD specifies.

Evidence, quoted from the source:

```js
road_allegiance:{enabled:true,initial_strength:3,erode_per_sleep:1.0,wear_per_crossing:1,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `faction-fights` — **ABSENT** (layer 1, score 0.00, signature 0/8)

faction fights — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

## Gaps found

### `verb-walk` — **ABSENT** (layer 1, score 0.12, signature 2/12)

Walk — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `verb-flame` — **PARTIAL** (layer 2, score 0.20, signature 3/14)

Flame — §2/3. The code implements flame pushing NPCs toward player alignment within a radius, but does not show the 'save opposite-burned' mechanic described in the GDD (reversing burn state and restoring frozen value for opposite-aligned burned NPCs).

Evidence, quoted from the source:

```js
if(kind==='flame'){const fr=this.flame_r;  // schema 3.8 ascension-scaled flame radius
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

Raze — §2/3. The code implements raze with fear effects and cost scaling with devout count, but the GDD specifies a 'fear spike' while the code applies 'fear_push_per_witness' which suggests a push mechanic rather than a spike, and the cost calculation uses 'RAZE_' (appears truncated) rather than clearly showing the devout multiplier structure described in the GDD.

Evidence, quoted from the source:

```js
razeCost(){let d=0;for(const x of SIM.npcs)if(!x.zealot&&!x.burn&&cheb(x.pos,SIM.player_pos)<=RAZE.witness_radius_tiles&&band(x.I)==='devout')d++;return RAZE_
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-wait` — **PARTIAL** (layer 2, score 0.27, signature 4/12)

Wait — §2/3. The code pushes NPCs when the player waits, but it pushes toward the NPC's current direction (copysign(WAIT_PUSH, x.v)) rather than unconditionally toward Apathy as the GDD specifies.

Evidence, quoted from the source:

```js
if(cheb(x.pos,pos)<=WAIT_R&&x.I!==0)add(x,-copysign(WAIT_PUSH,x.v),false);
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `verb-sleep` — **ABSENT** (layer 1, score 0.15, signature 2/9)

Sleep — §2/3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-12-12-scale` — **ABSENT** (layer 2, score 0.19, signature 2/12)

The −12..+12 scale — §3. No source code was shown in the matches section, and signature elements for emotional alignment, the -12 to +12 range, Fear, Hope, or alignment scale were not found in the indexed source.

Searched for and did not find: `alignment`, `emotionalState`, `emotional_state`, `beliefScale`, `belief_scale`, `-12`, `12`, `Fear`

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-unification-win-loss-check` — **ABSENT** (layer 1, score 0.12, signature 2/13)

the unification win/loss check — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `burnout-the-save` — **PARTIAL** (layer 2, score 0.16, signature 2/11)

Burnout + the save — §3. Configuration parameters and a burnout frame type exist, but the actual logic that freezes a person grey upon excessive same-pressure or saves them with opposite feeling is not visible in the provided source.

Evidence, quoted from the source:

```js
Y      = RULES['burnout']['overdose_threshold_Y_per_tick']  # 4
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `genesis` — **PARTIAL** (layer 2, score 0.20, signature 2/10)

genesis — §3. The genesis configuration exists with grey_nomads (55) and founding_poles ([-1,1]), but the GDD specifies 'one founding zealot per pole' while the code shows 'zealot_seeds_each:3', meaning three zealots per pole rather than one.

Evidence, quoted from the source:

```js
genesis:{enabled:true,grey_nomads:55,zealot_seeds_each:3,min_settle_members:5,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `settling` — **ABSENT** (layer 1, score 0.07, signature 1/10)

settling — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `beacons` — **PARTIAL** (layer 2, score 0.21, signature 3/14)

beacons — §3. Beacons exist and are rendered with alignment-based visuals (hope/fear), but there is no evidence in the source that they reveal map in ruined basins or radiate a permanent aura as described in the GDD.

Evidence, quoted from the source:

```js
for(const [bp,bpole] of SIM.beacons){const col=bpole>0?COL.hope:COL.fear;const bx=bp[0]*CELL+CELL/2,by=bp[1]*CELL+CELL/2;
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `worship-stamina` — **ABSENT** (layer 1, score 0.00, signature 0/9)

worship→stamina — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `ascension` — **ABSENT** (layer 1, score 0.07, signature 1/10)

ascension — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `peer-contagion` — **ABSENT** (layer 1, score 0.00, signature 0/7)

peer contagion — §3. deterministic signature probe

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found ABSENT.

### `the-grief-front` — **PARTIAL** (layer 2, score 0.30, signature 4/12)

the Grief Front — §3. The grief front is implemented as a fog bank on the winner's largest tribe with a 3-sleep duration, but there is no evidence in the source that it cancels zealot pull during those three sleeps—the code shows zealot behavior is tested but not that the front actively suppresses zealot mechanics.

Evidence, quoted from the source:

```js
grief_front:{trigger_dominance_min:0.55,max_concurrent_fronts:1,cooldown_sleeps_after_expiry:2,
```

> **Disagrees with the GDD.** §3 reports this feature as *Built*, which implies PRESENT. The scan found PARTIAL.

### `road-allegiance` — **PARTIAL** (layer 2, score 0.21, signature 2/8)

Road allegiance — §3. The code implements road allegiance with strength and enemy-road detection, but does not show evidence that roads 'enable influence on rooted settlements' as the GDD specifies.

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

### `wordless-endscreen` — **ABSENT** (layer 1, score 0.07, signature 1/9)

wordless endscreen — §3. deterministic signature probe

### `visible-trader-agents` — **ABSENT** (layer 1, score 0.00, signature 0/10)

visible trader agents — §3. deterministic signature probe

### `interactive-structures` — **ABSENT** (layer 1, score 0.00, signature 0/10)

interactive structures — §3. deterministic signature probe

### `procedural-maps` — **ABSENT** (layer 1, score 0.00, signature 0/11)

procedural maps — §3. deterministic signature probe

### `encounter-mini-games` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Encounter mini-games — §3. deterministic signature probe

### `the-only-moment-the-player-touches-individuals` — **ABSENT** (layer 1, score 0.00, signature 0/6)

the only moment the player touches individuals — §3. deterministic signature probe

### `hopetrade-as-designed` — **ABSENT** (layer 2, score 0.26, signature 2/7)

hopetrade as designed — §3. The source shows only a JSON file header with no trading mechanic implementation visible. The signature elements expected for a trading action (tradeAction, actions.hope_trade, verbs.trade) were not found.

Searched for and did not find: `tradeAction`, `trade_action`, `hopeTradeEnabled`, `actions.hope_trade`, `verbs.trade`, `Hope pole`, `trading mechanic`

### `road-tier-chains` — **ABSENT** (layer 1, score 0.00, signature 0/8)

road-tier chains — §3. deterministic signature probe

### `traversal-cinematic` — **ABSENT** (layer 1, score 0.00, signature 0/7)

traversal cinematic — §3. deterministic signature probe

### `final-art-and-audio` — **ABSENT** (layer 1, score 0.00, signature 0/8)

final art and audio — §3. deterministic signature probe

### `emotion-scale` — **ABSENT** (layer 2, score 0.19, signature 2/12)

Emotion Scale — §2. No emotion scale implementation found. While generic scale.min and scale.max exist somewhere, there are no emotion-specific identifiers, no twelve-step range values, and no references to Fear, Apathy, or Hope.

Searched for and did not find: `emotionValue`, `emotion_scale`, `emotionScale`, `FEAR_MIN`, `HOPE_MAX`, `APATHY_CENTER`, `Fear`, `Hope`

### `emotional-contagion` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Emotional Contagion — §2. deterministic signature probe

### `one-step-limit` — **ABSENT** (layer 1, score 0.00, signature 0/8)

One Step Limit — §2. deterministic signature probe

### `burnout` — **ABSENT** (layer 1, score 0.07, signature 1/10)

Burnout — §2. deterministic signature probe

### `stamina-budget` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Stamina Budget — §2. deterministic signature probe

### `schism` — **ABSENT** (layer 1, score 0.15, signature 1/10)

Schism — §2. deterministic signature probe

### `zealot-fate` — **PARTIAL** (layer 2, score 0.21, signature 2/8)

Zealot Fate — §2. The code shows zealot_fate configuration with trigger conditions and convert_eval parameters, but does not show the dual behavior described in the GDD: Hope converting rejected fear-zealots AND Fear expelling rejected hope-zealots. Only conversion evaluation is visible, with no evidence of the expulsion mechanism.

Evidence, quoted from the source:

```js
convert_eval:{at_check2_if_avg_abs_gte:{fear_zealot:8.0,hope_zealot:null},
```

### `worship` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Worship — §2. deterministic signature probe

### `grief-front` — **PARTIAL** (layer 2, score 0.29, signature 4/12)

Grief Front — §2. The code implements a grief_front with duration_sleeps:3 and trigger_dominance_min:0.55 on the largest_dominant_pole_tribe_position, but there is no evidence of 'desaturating fog' visual effect or explicit 'cancel zealot pull' mechanism in the shown source.

Evidence, quoted from the source:

```js
grief_front:{trigger_dominance_min:0.55,max_concurrent_fronts:1,cooldown_sleeps_after_expiry:2,
```

### `grief-decay` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Grief Decay — §2. deterministic signature probe

### `win-condition` — **ABSENT** (layer 1, score 0.12, signature 1/11)

Win Condition — §2. deterministic signature probe

### `loss-condition` — **ABSENT** (layer 1, score 0.12, signature 1/9)

Loss Condition — §2. deterministic signature probe

### `zealot-bands` — **PARTIAL** (layer 2, score 0.31, signature 7/16)

Zealot Bands — §2. The code implements four emotion bands (grey, tentative, devout, zealot) but does not place them 'at each extreme' as the GDD describes. The band() function shows grey is at zero (center), tentative and devout are intermediate ranges, and only zealot is at the extremes.

Evidence, quoted from the source:

```js
function band(I){const a=Math.abs(I);if(a===0)return'grey';if(a<=TENT_HI)return'tentative';if(a<=DEV_HI)return'devout';return'zealot';}
```

### `encounter-first-contact-hope` — **ABSENT** (layer 1, score 0.00, signature 0/9)

First Contact (Hope) — §2. deterministic signature probe

### `encounter-first-contact-fear` — **ABSENT** (layer 1, score 0.00, signature 0/9)

First Contact (Fear) — §2. deterministic signature probe

### `encounter-vigil-hope` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Vigil (Hope) — §2. deterministic signature probe

### `encounter-vigil-fear` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Vigil (Fear) — §2. deterministic signature probe

### `encounter-holding-hope` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Holding (Hope) — §2. deterministic signature probe

### `encounter-holding-fear` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Holding (Fear) — §2. deterministic signature probe

### `era-progression` — **ABSENT** (layer 1, score 0.08, signature 2/15)

Era Progression — §1. deterministic signature probe

### `fog-of-war` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Fog of War — §4. deterministic signature probe

### `narrated-opening` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Narrated Opening — §1. deterministic signature probe

### `visual-emotion-encoding` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Visual Emotion Encoding — §2. deterministic signature probe

### `player-body-transformation` — **ABSENT** (layer 1, score 0.15, signature 2/10)

Player Body Transformation — §2. deterministic signature probe

### `tile-grid` — **ABSENT** (layer 1, score 0.00, signature 0/9)

Tile Grid — §4. deterministic signature probe

### `reference-simulator` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Reference Simulator — §4. deterministic signature probe

### `ruleset-json` — **ABSENT** (layer 1, score 0.00, signature 0/8)

Ruleset JSON — §0. deterministic signature probe

## Scan scope

Indexed **856 symbols**, 341 string literals and 226 ruleset key paths. `SCAN_POLICY` excluded **5 region(s), 1,253,989 characters** — overwhelmingly the vendored Phaser bundle. That exclusion is the code-side twin of the content pipeline's §4.5 exclusion: §4.5 was cut because indexing it let the Writer retrieve the answer instead of writing one, and Phaser is cut because indexing it makes every feature look already built.

| file | line | chars | rule | reason |
|---|---|---|---|---|
| `build/uhta-slice.html` | 8 | 1,181,901 | vendor_signature | line opens with the minified-bundle preamble '!function(t,e){'; this is a vendored library, and indexing it would make every feature appear already implemented |
| `build/uhta-slice.html` | 776 | 11,761 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 777 | 50,583 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 778 | 9,416 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
| `build/uhta-slice.html` | 779 | 328 | data_uri | line embeds a base64 `data:image/...` payload — an art asset, not authored code; its characters are not identifiers |
