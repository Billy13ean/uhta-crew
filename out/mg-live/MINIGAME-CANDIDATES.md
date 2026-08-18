# MINIGAME-CANDIDATES — encounter mini-games, awaiting a ruling — mg-live

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 01:31:34


One design per encounter slot survived the GER loop (Generator -> two-layer Evaluator -> Refiner, circuit breaker on the residue). **Nothing has been built.** GDD §3's stop rule gates encounter BUILDS on the stranger test; this run spent tokens on design, and the build stage below cannot run without your typed selection — the gate is structural.


## `first-contact-hope` — ACCEPTED
**Steady the Flame** — `first-contact-hope` (first-contact/hope)

- **Premise:** A ring of grey nomads approach slowly from all sides, wavering between curiosity and fear. The flame above you flickers with each input—your task is to hold it steady as they close the distance.
- **Loop:** The flame brightness responds to left-click (brightens) and naturally decays toward dim. The nomads approach in a slow, uneven ring, pausing when the flame wavers outside a narrow 'steady' band. Hold the flame in the correct range—visible but not blazing—by tapping left-click sparingly to counteract decay. Over-click and the flame flares too bright, cracking the air with light; the nomads recoil and some break away. Under-maintain and it dims toward grey; wavering nomads drift back into the fog. The steady band itself drifts slightly, demanding constant reading rather than a fixed rhythm.
- **Diegetic signals:** Flame brightness is the flame itself, glowing above your body—gold-white core when steady, searing white when too bright, ember-dim when failing. Nomad commitment shows in their posture: upright and steady when the flame is right, leaning back and hesitating when it flares, turning away and fading when it dims. Distance closes visibly—they walk toward you, and their ring tightens as the encounter progresses. No meters, no UI—only the flame's glow and their bodies.
- **On success:** The ring closes completely. The nomads kneel in unison, their grey forms saturating to warm gold as they convert. Few in number, but their posture is deep—heads bowed, fully committed.
- **On failure:** The flame either shatters in a white flash (too bright) or gutters to ash (too dim). Nomads scatter or fade back into the fog. The encounter ends with no conversions, or worse—some grey out entirely, ringed in the faint gold they almost carried.
- **Why fun:** Tests restraint and reading a drifting target—the skill is knowing when to act and when to let the flame settle. The tension comes from fighting the instinct to over-correct; one extra click can undo the entire hold.
- **Pattern:** Threshold fight — the steady hold
- **GDD grounding:** They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less.
- **Controls:** left-click
- **Effects:** convert_devout, burnout, drift_apathy, no_effect
- **Judge:** PASS — The design implements the GDD's exact intent: a threshold-hold game where restraint is the skill, flame brightness is diegetically visible, nomads' commitment reads in their posture and distance, and the outcome delivers few devout converts. The loop matches the retrieved pattern's 'sustained modulation rather than bursts' and 'one overcorrection undoes the hold,' and all failure states (burnout from flare, drift from dimness) align with chunk mechanics.
  - chunk honored: "They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less. Few converts, and they arrive already devout"

## `first-contact-fear` — ACCEPTED
**The Scatter** — `first-contact-fear` (first-contact/fear)

- **Premise:** You meet an unaligned nomad band. You roar and they break in all directions—grey figures sprinting away on diverging paths across the terrain.
- **Loop:** The player has superior speed for a handful of seconds. Runners flee on readable vectors—each body leaning into its escape angle, leaving faint trails showing direction. The player sprints (wasd-move) to position their body across escape lines, physically blocking fleeing nomads. When the player's body intersects a runner's path, that runner stops, turns to face the player, and shifts from grey to pale red (shallow convert). Runners the player cannot reach continue sprinting until they exit visibility range, their trails brightening as they carry the story outward. The window closes when all runners have either been cut off or escaped—typically 8-12 seconds.
- **Diegetic signals:** Runner count and speed: visible as the number of grey bodies and their sprint animation speed. Escape vectors: shown by body lean, arm position, and the faint dust trail each runner leaves. Cutoff success: the runner stops, turns 180°, and their grey desaturates to pale Fear-red. Escape success: the runner's trail brightens to white as they exit the visible radius. Time remaining: the player's own body glows brighter red as stamina drains, dimming as the window closes. Conversion depth: shallow converts remain pale red, never deepening to the saturated crimson of devout followers.
- **On success:** Four to six pale-red converts standing in a loose cluster where you blocked them, breathing hard. Two to four bright trails fading at the edge of vision—stories spreading.
- **On failure:** One or two pale converts, seven or eight bright escape trails. The story spreads wide and thin.
- **Why fun:** Instant spatial triage under time pressure—you read the scatter geometry, commit to an intercept angle knowing you're abandoning others, and live with watching half the band carry fear outward. The skill is reading vectors and choosing which losses you can afford.
- **Pattern:** Interception — the cutoff
- **GDD grounding:** You roar, the band breaks, and you have a handful of strides to cut off the runners. Everyone you head off turns; everyone who escapes carries the story outward. Many converts, every one of them shallow.
- **Controls:** wasd-move
- **Effects:** convert_shallow, story_spreads, stamina_loss
- **Judge:** PASS — The design implements Fear's first-contact texture exactly as specified: speed-based interception geometry yielding many shallow converts, with escaped runners spreading the story. All state is diegetic (body lean, dust trails, color shifts, player glow), controls use only movement, and the triage-under-pressure loop is mechanically distinct from Hope's patient flame-steadying.
  - chunk honored: "You roar, the band breaks, and you have a handful of strides to cut off the runners. Everyone you head off turns; everyone who escapes carries the story outward. Many converts, every one of them shallow"

## `vigil-hope` — ACCEPTED
**The Weaving** — `vigil-hope` (vigil/hope)

- **Premise:** Night falls as you prepare to Sleep. Your believers stand scattered across the dark landscape, each a small warm light. You have stamina for one last act before dawn.
- **Loop:** Click and hold on a believer to begin a thread of light flowing from your body. While holding, move the mouse to draw the thread toward another believer—but the thread dims and frays if you move too fast or turn too sharply. Release on a second believer to complete the chain; it flashes bright and holds. Completed chains glow steadily between believers. Each chain costs stamina; longer chains (more distance, more turns) cost more and demand steadier hands. You choose: many short safe chains, or fewer ambitious ones that might break if you rush.
- **Diegetic signals:** Each believer is a warm point of light, brightness showing their devotion depth. Your thread flows visibly from your position as pale light following the mouse. Thread brightness shows stability—bright when slow and smooth, flickering when you move too fast, breaking entirely if you jerk or overshoot. Completed chains are steady lines of light between believers. Your body dims as stamina drains with each chain attempt. The dark presses in around uncompleted believers.
- **On success:** A web of light connects your scattered believers. The chains pulse gently. As Sleep takes you, belief will flow along these threads while you are gone—longer chains reaching distant believers, the whole network holding your presence in the world through the dark generation.
- **On failure:** Few chains hold, or only short ones. Most believers stand isolated as night comes. Many will drift toward grey without the channels to carry belief while you sleep. Broken thread-ends fade around the disconnected.
- **Why fun:** Patience and smooth execution under scarcity. You want ambitious chains that reach far, but greed and haste break the thread. The skill is choosing which connections matter most, then tracing them with a steady hand before stamina runs out.
- **Pattern:** Path tracing — the drawn line
- **GDD grounding:** Your believers hang in the dark and you trace lines between them with your last stamina. Completed chains become channels belief travels while you are gone; longer chains reach further and are harder to hold.
- **Controls:** mouse-move, left-click
- **Effects:** convert_devout, story_spreads, stamina_loss, drift_apathy
- **Judge:** PASS — The design faithfully implements the GDD's vigil-hope intent as a path-tracing game where thread stability depends on smooth, patient execution—longer chains cost more stamina and demand steadier control. All state is diegetic (believer lights, thread brightness/fraying, body dimming) with no interface elements, and the patience/depth/few texture matches Hope's pole identity from CHUNK 1's encounter table.
  - chunk honored: "Your believers hang in the dark and you trace lines between them with your last stamina. Completed chains become channels belief travels while you are gone; longer chains reach further and are harder to hold."

## `vigil-fear` — ACCEPTED
**The Watch** — `vigil-fear` (vigil/fear)

- **Premise:** Night falls as you prepare to sleep. Your believers scatter across the dark landscape as points of dim light, flickering. Shadows creep inward from the edges—visible as encroaching darkness that will extinguish any light it reaches.
- **Loop:** You are a bright flame that can move (WASD). Your light casts a protective radius around you—a visible dome. Believers inside your dome when darkness reaches them survive; those outside are extinguished. The darkness advances in waves from all edges. You have 45 seconds before dawn. Your flame shrinks visibly each time you move—each step costs size, and your protective radius shrinks with you. You begin large enough to cover perhaps a third of the field if you stand still, but movement is expensive. The choice: stay central and save a dense cluster, or spend yourself moving between groups, arriving smaller each time, able to shelter fewer. More believers than you can possibly cover; you must choose who to reach and who to abandon.
- **Diegetic signals:** Your flame's size IS your remaining capacity—it shrinks visibly with each step, and your protective dome shrinks with it. Believer lights flicker more urgently as darkness nears them. The dome edge glows in your color with clear visible boundary. The dark is literal encroaching blackness, advancing in visible pulses. Distance between believer-lights shows clustering—near groups versus distant stragglers. Extinguished believers vanish to black exactly where they stood. Dawn arrives as sudden light from the horizon.
- **On success:** Many lights still burn at dawn—the ones inside your final radius. Your body brightens as you absorb their faith. The darkness retreats.
- **On failure:** Few or no lights remain. The darkness holds the field. Your body is barely visible, starved.
- **Why fun:** Pure spatial resource allocation under time pressure. Your shrinking body IS the resource meter—legible through the encounter's own geometry. The skill is recognizing whether to hold position over a dense cluster or spend yourself reaching distant groups. The tension is watching lights you chose NOT to reach flicker out in the distance while you stand over the ones you saved—cold triage made visceral through your own diminishing presence.
- **Pattern:** Triage — protect what you can
- **GDD grounding:** Your believers are points of light and the dark presses in. You shield what you can and you cannot shield everything. Fear's version is triage — choosing who to abandon before dawn.
- **Controls:** wasd-move
- **Effects:** convert_shallow, stamina_gain, drift_apathy, burnout
- **Judge:** PASS — The shrinking flame body as movement cost creates genuine spatial triage—you literally cannot cover everyone and your protective radius diminishes with each repositioning choice. The design is purely diegetic (flame size, dome radius, encroaching darkness, flickering lights), plays to Fear's speed/force/many texture through time pressure and shallow converts, and mechanically diverges from Hope's patient weaving by forcing rapid allocation decisions rather than careful connection-building.
  - chunk honored: "Fear's version is triage — choosing who to abandon before dawn"

## `holding-hope` — ACCEPTED
**The Procession** — `holding-hope` (holding/hope)

- **Premise:** You stand at the edge of a rooted settlement whose roads glow faintly with resistance. A handful of wanderers appear at the settlement's border, watching you. To convert a resident at the heart, you must lead these converts inward without breaking the line.
- **Loop:** You walk slowly along the settlement's roads toward the central hearth. Each wanderer who sees you begins to follow, forming a line behind you. The line stretches and thins as you move—walk too fast and the tail detaches, turn too sharply and the chain snaps at the bend. Residents appear as still figures along the route; they only acknowledge the procession when you pass close with your line intact. The road itself narrows and curves as it approaches the center, demanding tighter control. You must balance forward progress against the elasticity of your following.
- **Diegetic signals:** Followers glow softly in your color and trail visible light-threads connecting each to the next; when you move too abruptly the thread stretches taut and snaps, and the severed convert stops moving, their glow dimming to grey. Residents stand upright and still, their posture closed; as an intact procession passes within arm's reach they shift—leaning slightly toward the line, their color beginning to warm. The settlement's heart is visible as a brighter concentration of structures and a central fire. Distance between you and your last follower shows as the literal space and the brightness of the connecting thread.
- **On success:** You reach the heart with followers still connected. The line collapses inward as each convert touches a resident; those residents shift fully into your color, postures opening. The converts who made the journey kneel, deeply devout.
- **On failure:** You arrive alone or with only one or two followers. The few who remain convert shallowly—standing but uncertain, their color pale. Any you dropped stand frozen where the line broke, grey and unreachable until the next encounter.
- **Why fun:** The skill is restraint and spatial planning—reading the road ahead and governing your own speed, resisting the urge to rush. The tension lives in the growing tail: each new follower is a gift and a liability, lengthening the fragile chain you must protect.
- **Pattern:** Procession — follow-the-leader escort
- **GDD grounding:** Roads are the only way in. Converts fall in behind you as you walk and the line breaks if you move too fast or turn too sharply; whoever is still with you at the heart converts a resident
- **Controls:** wasd-move, mouse-move
- **Effects:** convert_devout, convert_shallow, drift_apathy, stamina_loss
- **Judge:** PASS — The design implements the GDD's exact procession mechanic: followers form a line that breaks on excessive speed or sharp turns, roads constrain entry, and intact arrival converts residents. The diegetic signals (light-threads, follower glow, resident posture shifts) require no HUD, the patience-and-restraint texture matches Hope's pole, and the outcome correctly yields few devout converts rather than many shallow ones.
  - chunk honored: "Roads are the only way in. Converts fall in behind you as you walk and the line breaks if you move too fast or turn too sharply; whoever is still with you at the heart converts a resident"

## `holding-fear` — ACCEPTED
**The Breaking** — `holding-fear` (holding/fear)

- **Premise:** You stand before a rooted settlement's outer edge. Its resistance forms a visible ring of light around the heart — brighter where conviction runs deep, dimmer where doubt has crept in.
- **Loop:** You left-click a segment of the ring to strike it with a roar-pulse. The struck segment darkens (resistance drops) but the arcs immediately adjacent flare brighter (hardening). You must find the sequence — which segment to break first, second, third — that collapses the entire ring before your stamina (shown as the intensity of your own glow) runs out. Each strike costs stamina; each wrong choice hardens the structure against you. The ring must fully darken to breach the settlement.
- **Diegetic signals:** The settlement's resistance is a ring of light encircling its center — segment brightness IS conviction strength. Your stamina is your body's glow intensity, dimming with each strike. Struck segments visibly darken and crack; adjacent segments flare brighter and pulse. When the ring collapses, the light shatters and scatters outward. Settlers themselves appear as silhouettes within — more upright where the ring is bright, slumping where it dims.
- **On success:** The ring shatters completely. The settlement's silhouettes scatter in all directions like startled birds — many turn and face you (conversion), their postures bent low in fear.
- **On failure:** Your glow dims to nothing before the ring breaks. You stagger back. The ring pulses once, bright and intact, and the settlement's silhouettes stand taller, unbroken.
- **Why fun:** The tension is spatial planning under pressure — reading the structure, committing to a sequence, and watching your stamina drain as each choice either opens the path or hardens the wall. The skill is pattern recognition and adaptive sequencing when early strikes reveal unexpected thickness.
- **Pattern:** Weak-point sequencing — the collapsing order
- **GDD grounding:** Resistance shows as a ring. Strike where it is thinnest — but each strike hardens the arc beside it, so winning means finding the collapsing sequence before your stamina runs out.
- **Controls:** mouse-move, left-click
- **Effects:** convert_shallow, convert_shallow, convert_shallow, stamina_loss, resistance_drop, story_spreads
- **Judge:** PASS — The design faithfully implements the GDD's exact prescription: segment brightness encodes resistance strength diegetically, striking hardens neighbors, and the puzzle is finding the collapsing sequence within stamina constraints. The Fear texture is present — speed, force, many shallow converts scattering like startled birds — and all state (ring brightness, body glow intensity, settler postures) lives in visible bodies and light with no interface required.
  - chunk honored: "Resistance shows as a ring. Strike where it is thinnest — but each strike hardens the arc beside it, so winning means finding the collapsing sequence before your stamina runs out."

---

## Director selection — the human gate

*The pipeline stops here by construction. To build ONE selected design (a minimal playable slice under the A5 patch contract):*

```
python3 run_minigame.py --build --select <id> --from-run mg-live
```

Selectable ids: first-contact-fear, first-contact-hope, holding-fear, holding-hope, vigil-fear, vigil-hope

**Selected:** ____________  **Rejected because:** ____________

**Signed (Director):** _______________  **Date:** ____________

