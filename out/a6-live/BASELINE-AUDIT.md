# BASELINE AUDIT — the Evaluator vs the shipped build — a6-live

> Pipeline `ger` (Assignment 6) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 00:38:19


The rule under enforcement (GDD §2.5): *"Short, declarative, second person. Names the verb and states its consequence. Instrumentation, not lore — GDD §2.5: 'short declarative lines, no mythology'. No interface language: this is a wordless game's one narrated cycle, not a tutorial overlay — the narrator names what the being DOES, never which key the player presses. No numbers (§2.3, banded display)."*

Before generating anything, the Evaluator was pointed at the text already in `blackboard/build/uhta-slice.html`: the seven stub `TEACHING_TEXT` lines A5's Programmer wrote as placeholders, and the `guide()` tutorial strings the A5 repo findings measured against the GDD. A pipeline that only ever judges its own output has never been tested against a real failure.


## guide() tutorial strings vs the register gate

| # | string (truncated) | findings |
|---|---|---|
| 1 | `The world wakes as grey wanderers. Your <b>${p}</b> zealot gathers the first of …` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 124 chars / 26 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 2 | `<b>Left-click</b> to wash a wave of your color over the wanderers and deepen you…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'Left-click' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 167 chars / 32 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 3 | `Your flame dims (the shrinking ring). Press <b>space</b> to <b>sleep</b> — a gen…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'Press' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 130 chars / 21 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 4 | `Your <b>WASD</b> trail becomes a road stamped your color — it erodes enemies who…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'WASD' — the register is the narrator naming what the being does, not which key is pressed<br>[deterministic] R3 SHORT: 172 chars / 31 words exceeds the gate (120 chars / 24 words) — §2.5: 'short declarative lines' |
| 5 | `a ruined basin waits — stand beside it and press <b>E</b> to light it in your co…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed |
| 6 | `Flame nearly spent — press <b>space</b> to rest; the world lives a generation on…` | [deterministic] R2 NO-UI-LANGUAGE: interface vocabulary 'press' — the register is the narrator naming what the being does, not which key is pressed |
| 7 | `The land turns <b>${p}</b>'s color — hold it.${oppZealot?` | [deterministic] R4 DECLARATIVE: contains ? — §2.5: 'short DECLARATIVE lines'; the narrator states, never asks or exclaims |

**7 of 7** shipped tutorial strings fail the register gate — `press`, `W A S D`, click vocabulary. This is the exact failure class the Pre-Build Declaration named, found in text that is in the game today.


## The build's current TEACHING_TEXT stubs, judged

### `walk`

> You walk. The grey wanderers see your trail and follow roads.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line omits the load-bearing consequence that roads carry your color—the player is told wanderers follow roads but not that those roads are colored and therefore spread the player's alignment, which is the mechanical heart of Walk.
  - chunk cited: "every tile walked becomes a compacted road NPCs traverse faster, and roads now **carry your color**"

### `flame`

> You kindle a flame. Nearby people feel its warmth and adopt your conviction.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line says the flame makes people 'adopt your conviction' (implying conversion to your alignment), but the chunk specifies it 'applies the flame's current alignment' — the load-bearing fact is that it applies *whatever you currently are* (hope, fear, or grey), not that it converts people to follow you.
  - chunk cited: "Raise / wave the flame | ~2.5 | Clears fog locally; applies the flame's current alignment to NPCs in radius"

### `roar`

> You roar. The sound carves a road through the land.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line omits the load-bearing unconditional consequence demanded by the beat brief — that everyone who witnesses the roar is frightened regardless of flame color — making it read identically in a Hope run and thus materially misleading about the verb's effect.
  - chunk cited: "NPCs within **witness radius R (~6 tiles)** of the line take an unconditional Fear push (~2.8) regardless of flame color"

### `wait`

> You wait and witness. Apathy grows where you stand idle.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line says apathy grows 'where you stand idle' (locational), but the chunk specifies it pushes 'nearby NPCs' (affects people in radius), and the beat brief demands the consequence that withholding teaches people watching 'that you do not matter' — the line omits the load-bearing relational consequence (you teach watchers you're irrelevant) and replaces it with a spatial effect.
  - chunk cited: "witnessed inaction pushes nearby NPCs toward Apathy (~0.5)"

### `beacon`

> You light a beacon. It calls the devoted even while you sleep.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line says the beacon 'calls the devoted' but the chunk specifies it radiates the flame's color (which applies emotion to NPCs), omitting the load-bearing consequence that the beacon works by radiating color/emotion, not by召唤ing already-devoted followers.
  - chunk cited: "Places a permanent aura that radiates the flame's current color every generation tick, including while you sleep."

### `raze`

> You raze a structure. Its people scatter back to wandering.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line omits the load-bearing consequence that Raze is Fear's hammer — it pushes a massive Fear spike onto witnesses — making it read gentle when the beat brief and chunk demand the player understand this is a terror weapon, not a neutral demolition tool.
  - chunk cited: "pushes a massive Fear spike onto witnesses (~2.5 each within ~5 tiles). Fear's hammer against entrenchment"

### `sleep`

> You sleep. The world moves without you; your people spread your belief.

- layer 2: **FAIL** `CONTRADICTS-CHUNK` — The line omits the load-bearing positional consequence—that the sleeping body itself radiates continuously at a location—and replaces it with 'your people spread your belief,' which misleadingly suggests NPCs are the mechanism when the chunks specify the sleeping body is the radiating source.
  - chunk cited: "the sleeping body radiates the flame's emotion over a radius (~3 tiles, grows with Ascension) for every tick of the generation. Where you sleep is the last decision of every cycle"

**7 of 7** stub lines flagged. Each flagged stub is a line currently shipping in the build that the loop replaces (or escalates) below.

