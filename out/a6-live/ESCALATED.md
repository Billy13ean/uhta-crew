# ESCALATED — what the loop hands the Director — a6-live

> Pipeline `ger` (Assignment 6) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 00:38:20


The circuit breaker stops spending on a verb after 2 failed refinements and hands it here WITH its evidence — the point of the loop is that a human reviews the residue, not every output. Global trip threshold: 3 escalations.


## `flame`

| round | line | findings |
|---|---|---|
| 0 | You raise the flame, and it applies what you feel. | [llm] CONTRADICTS-CHUNK: The line omits that the flame applies alignment specifically to NPCs, making it sound like a general emotional broadcast rather than the targeted NPC-affecting verb the mechanics demand. — chunk: "Raise / wave the flame \| ~2.5 \| Clears fog locally; applies the flame's current alignment to NPCs in radius" |
| 1 | You raise the flame, and it applies what you feel to those who see it. | [llm] CONTRADICTS-CHUNK: The line says the flame applies 'what you feel' but omits the load-bearing fact that it applies the flame's *current* alignment (which can be Hope or Fear), making it sound like a simple expression of emotion rather than the mechanical consequence that it pushes NPCs toward whatever color the flame currently holds. — chunk: "applies the flame's current alignment to NPCs in radius" |
| 2 | You raise the flame, and it applies the flame's current alignment to those who see it. | [llm] CONTRADICTS-CHUNK: The line says the flame applies alignment 'to those who see it' (witness-based), but the chunk specifies it applies 'to NPCs in radius' — a spatial mechanic, not a line-of-sight one, and the beat brief explicitly demands the load-bearing fact that it applies the flame's *current* alignment (so not a heal, but whatever you currently are), which this line buries under the wrong trigger condition. — chunk: "applies the flame's current alignment to NPCs in radius (~3 tiles, grows with Ascension)" |

**Director options:** write the `flame` line by hand; keep the build's current stub; or adjust the spec/prompt and re-run `--verbs flame`.

