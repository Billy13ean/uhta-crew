# MINIGAME-CANDIDATES — encounter mini-games, awaiting a ruling — mg-live-2

> Pipeline `minigame` (Assignment 6 #2) · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-18 23:28:13


One design per encounter slot survived the GER loop (Generator -> two-layer Evaluator -> Refiner, circuit breaker on the residue). **Nothing has been built.** GDD §3's stop rule gates encounter BUILDS on the stranger test; this run spent tokens on design, and the build stage below cannot run without your typed selection — the gate is structural.


## `first-contact-hope` — ACCEPTED
**Steady the Flame** — `first-contact-hope` (first-contact/hope)

- **Premise:** A ring of grey nomads approaches slowly from all sides, wavering as they walk. They will only commit if your flame burns steady—not too bright, not too dim—when the first of them arrives at arm's reach.
- **Loop:** You hold space to raise the flame, release to let it dim. The flame pulses with a natural rhythm—it wants to flare when held, fade when released. The nomads approach in an uneven ring, each at their own pace, hesitating when the flame surges too bright, drifting sideways when it dims too low. You must read their distance and modulate pressure: short taps to keep the glow inside the narrow band they will accept, doing less as they draw near. One overcorrection—a flare that makes them flinch or a fade that breaks their focus—and that nomad turns away. The encounter ends when the first nomad reaches you or when all have drifted out of range.
- **Diegetic signals:** Flame brightness is the size and intensity of the light-corona around your body. Nomad commitment shows in posture: they lean forward when the flame is steady, recoil and raise a hand to shield their eyes when it flares, turn their heads and slow when it dims. Distance is literal: you see how many steps each nomad has left. The acceptable band is never shown numerically—you learn it by watching them hesitate at the edges.
- **On success:** The first nomad to reach you kneels, and the flame settles into their chest. One to three others who were still approaching when contact happened also kneel in sequence. Each converts deep—already devout.
- **On failure:** All nomads have turned away or stopped outside reach, standing with shoulders turned, gazes elsewhere. They walk back into the grey. No conversion.
- **Why fun:** The skill is fine motor restraint and rhythm-reading against a drifting target. The tension comes from knowing that doing more usually feels safer, but here the correct move is to do less—to trust the hold rather than chase it.
- **Pattern:** Threshold fight — the steady hold
- **GDD grounding:** They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less.
- **Controls:** space
- **Effects:** convert_devout, no_effect
- **Judge:** PASS — The design implements the GDD's exact intent: a threshold-hold mechanic where space modulates flame brightness, nomads approach in a ring and react to flare/fade with recoil/drift, and success yields few devout converts. The diegetic signals (flame corona size, nomad posture and lean) require no HUD, and the patience/restraint texture is distinctly Hope's pole.
  - chunk honored: "They approach in a wavering ring and commit only if the flame is steady when they arrive. Too bright and they break; too dim and they drift. The correct move is usually to do less. Few converts, and they arrive already devout"

## `first-contact-fear` — ACCEPTED
**The Scatter** — `first-contact-fear` (first-contact/fear)

- **Premise:** You roar — the unaligned nomad band fractures into panicked runners fleeing in all directions. The simulation freezes them mid-stride, each body a readable vector pointing toward escape.
- **Loop:** You sprint (WASD) to intercept. Each runner is a body aimed at the edge of the encounter radius, moving at constant speed. You are faster. When you cross a runner's path ahead of them (your body blocks their line), they stop, turn to face you, and kneel — converted. Runners you cannot reach flee past the boundary and vanish. The encounter ends when all runners have either converted or escaped, or when 45 seconds expire.
- **Diegetic signals:** Runner posture: sprinting away, backs to you, arms pumping. Speed: visible stride rate, dust trails. Your advantage: you cover ground faster, your body leaves a bright wake. Conversion: the moment you cut them off they freeze mid-step, pivot to face you, drop to one knee, and glow faintly in your Fear-red. Escape: a runner crosses the dark boundary ring and dissolves into shadow. Remaining time: the boundary ring itself pulses faster as seconds drain.
- **On success:** You block five or more runners before they reach the edge — they kneel in a scattered constellation around you, shallow converts already fading to pale red. The rest escape into the dark.
- **On failure:** Most of the band scatters past you. Only one or two kneel. The boundary dissolves and the simulation resumes with distant silhouettes still running, carrying the story outward.
- **Why fun:** Pure spatial triage under time pressure: you read eight fleeing angles, plot the collapse sequence that saves the most, commit to a sprinting line, and live with who you abandoned. The skill is chase geometry; the tension is that every miss has a name.
- **Pattern:** Interception — the cutoff
- **GDD grounding:** You roar, the band breaks, and you have a handful of strides to cut off the runners. Everyone you head off turns; everyone who escapes carries the story outward. Many converts, every one of them shallow.
- **Controls:** wasd-move
- **Effects:** convert_shallow, story_spreads, stamina_loss
- **Judge:** PASS — The design implements Fear's speed/force/many texture faithfully: sprint-based interception triage, visible fleeing vectors, immediate shallow conversions on cutoff, and escapees spreading the story. All state is diegetic (posture, dust trails, kneeling bodies, boundary pulse) with no interface elements, and the chase geometry plays nothing like Hope's patient flame-steadying.
  - chunk honored: "You roar, the band breaks, and you have a handful of strides to cut off the runners. Everyone you head off turns; everyone who escapes carries the story outward. Many converts, every one of them shallow."

## `vigil-hope` — ACCEPTED
**The Weaving** — `vigil-hope` (vigil/hope)

- **Premise:** Night falls and your believers stand scattered in the dark, holding candles. You have only your last stamina and the thread of light you carry to bind them together before sleep takes you.
- **Loop:** Click and hold on a believer to anchor your thread, then move the mouse smoothly to trace a glowing line toward another believer; release on them to complete the link. Each completed link drains stamina (longer links cost more). The thread breaks if you move too fast (mouse speed exceeds a threshold) or make too sharp a turn (angle threshold). Broken threads vanish and waste the stamina. You can branch from any anchored believer to start a new chain segment. When stamina depletes or you press space to sleep, the encounter ends.
- **Diegetic signals:** Believers appear as stationary figures holding small candle flames in the darkness. Your current stamina is the brightness of the thread you're drawing—it dims visibly as you extend lines and glows brightest when full. The thread itself is a living ribbon of light trailing your mouse; it shimmers steady when you move smoothly, flickers when you approach the speed limit, and shatters into fading sparks when you break it. Completed chains pulse gently between their anchored believers. Distance between believers is visible space; longer chains are obviously harder to hold smooth.
- **On success:** A web of light connects many believers in long, graceful chains. When you sleep, the channels glow and belief visibly flows along them, reaching distant figures. The believers you connected stand taller.
- **On failure:** Only short, scattered links survive, or many chains lie broken. Most believers remain isolated in the dark. When you sleep, the weak web barely holds and distant believers drift toward grey.
- **Why fun:** The tension between ambition and control: longer chains reach further and convert more deeply, but demand smoother execution and drain more stamina. You must judge what you can hold—planning the ideal web, then executing it without rushing or jerking the line. Failure is legible the instant your hand moves too fast.
- **Pattern:** Path tracing — the drawn line
- **GDD grounding:** Your believers hang in the dark and you trace lines between them with your last stamina. Completed chains become channels belief travels while you are gone; longer chains reach further and are harder to hold.
- **Controls:** mouse-move, left-click, space
- **Effects:** convert_devout, stamina_loss, story_spreads, drift_apathy
- **Judge:** PASS — The design is fully diegetic (thread brightness as stamina, spatial distance, visible shimmer/flicker/shatter as constraint feedback), implements Hope's patience texture (planning then smooth execution, rewarding control over speed), and directly instantiates the GDD's intent where longer chains cost more stamina and break under rushed movement. The mouse-tracing mechanic with speed and angle thresholds creates the 'harder to hold' constraint for ambitious webs.
  - chunk honored: "Your believers hang in the dark and you trace lines between them with your last stamina. Completed chains become channels belief travels while you are gone; longer chains reach further and are harder to hold."

## `vigil-fear` — ACCEPTED
**The Watch** — `vigil-fear` (vigil/fear)

- **Premise:** Night falls as you prepare to sleep. Your believers appear as flickering flames scattered across the dark. Shadows creep inward from all sides, closing on each flame.
- **Loop:** Each believer is a flame threatened by encroaching darkness. You left-click and drag to sweep your body through the space, pushing back shadows in an arc around you. Darkness advances in pulses—slow at first, then faster. Each sweep costs stamina (visible as your body dimming slightly). You cannot be everywhere; shadows will claim flames you don't protect. You must choose which clusters to defend and which to abandon before your stamina runs out and sleep takes you.
- **Diegetic signals:** Believers are flame-points, brighter for devout, dimmer for shallow. Darkness is visible as creeping shadow-tendrils advancing toward each flame. Your body glows, dimming as stamina drains. When you sweep through space, shadows recoil in that arc. Flames snuffed by shadow go dark where they stood. Flames you successfully guard burn steadier and brighter when dawn comes.
- **On success:** Multiple protected flames burn bright at dawn—the believers you shielded stand devout, their fear of the dark confirmed and you their proven guardian.
- **On failure:** Scattered dark points mark where flames died. Few believers remain, and those who do are shallow—you were there, but not everywhere, and they saw what you abandoned.
- **Why fun:** Pure triage under mounting pressure—you watch your choices play out spatially as shadows claim what you didn't protect. The skill is reading the map fast: which clusters are dense enough to save efficiently, which single flames cost too much, and when to cut your losses before stamina runs out.
- **Pattern:** Triage — protect what you can
- **GDD grounding:** Your believers are points of light and the dark presses in. You shield what you can and you cannot shield everything. Fear's version is triage — choosing who to abandon before dawn.
- **Controls:** mouse-move, left-click
- **Effects:** convert_devout, convert_shallow, drift_apathy, stamina_loss
- **Judge:** PASS — The design implements spatial triage with diegetic signals (flame brightness for devotion depth, shadow advance, body dimming for stamina) and Fear-appropriate texture (speed, force, many-but-shallow converts, cold abandonment choices). The mouse-drag sweeping mechanic creates pressure-under-time without interface elements, and the outcome correctly maps protected flames to devout Fear converts while abandoned flames drift toward apathy—matching Fear's 'many converts, every one of them shallow' when the player spreads thin, and deeper conversion only for the clusters successfully defended.
  - chunk honored: "Your believers are points of light and the dark presses in. You shield what you can and you cannot shield everything. Fear's version is triage — choosing who to abandon before dawn"

## `holding-hope` — ACCEPTED
**The Procession** — `holding-hope` (holding/hope)

- **Premise:** You stand at the edge of a rooted settlement, its heart visible deep within along winding roads. Converts from outside the settlement appear and begin to follow behind you as you walk the roads inward.
- **Loop:** You walk toward the settlement's heart using WASD, staying on the roads you've built. Each convert that appears falls into line behind you, forming a visible chain. If you move too quickly (hold movement keys without pausing), the tail of the line stretches and breaks — those behind the break stop following and stand where the break occurred. If you turn too sharply (sudden 90° or sharper direction changes), the chain whips and the tail detaches. You must modulate your pace with brief pauses and take wide, gentle turns. The line visibly tightens when you slow, loosens when you accelerate. When you reach the settlement's heart (a distinct gathering of residents), whoever remains in your procession causes one resident to step forward and shift toward your color.
- **Diegetic signals:** The procession line itself shows your success: each convert is a body in your color walking behind you, spacing shows tension (tight = safe, stretched = about to break). The settlement heart is a cluster of standing figures in neutral or opposing colors at the road's end. Residents who convert step out from the cluster and change color. Detached converts stand frozen where the line broke, still visible but no longer following.
- **On success:** You arrive at the heart with multiple converts still in line; one or more residents step forward from the cluster and shift to your color, standing taller.
- **On failure:** You arrive alone or with only one convert remaining; no residents move, or you lose patience and move too quickly, scattering everyone before you reach the heart.
- **Why fun:** The skill is restraint and spatial planning — reading the road ahead and choosing when to pause, when to creep forward, which turns to widen. The tension comes from impatience: you want to rush to preserve stamina and reach more settlements, but rushing destroys the very thing you're building.
- **Pattern:** Procession — follow-the-leader escort
- **GDD grounding:** Roads are the only way in. Converts fall in behind you as you walk and the line breaks if you move too fast or turn too sharply; whoever is still with you at the heart converts a resident.
- **Controls:** wasd-move
- **Effects:** convert_devout, stamina_loss, no_effect
- **Judge:** PASS — The design implements the GDD's exact procession mechanic: converts form a following line that breaks on excessive speed or sharp turns, with survivors converting residents at the heart. The loop is entirely diegetic (line spacing, body positions, color shifts visible in world-space), demands patience and restraint (Hope's texture per CHUNK 1's 'patience, depth, few'), and the skill lies in the leader's discipline rather than interface management, matching CHUNK 3's escort pattern guidance.
  - chunk honored: "Roads are the only way in. Converts fall in behind you as you walk and the line breaks if you move too fast or turn too sharply; whoever is still with you at the heart converts a resident."

## `holding-fear` — ACCEPTED
**The Breaking** — `holding-fear` (holding/fear)

- **Premise:** You stand before a rooted settlement whose resistance forms a visible ring around its heart. The ring pulses unevenly — some arcs glow thick and bright, others thin and wavering.
- **Loop:** You circle the settlement's perimeter with mouse-move, searching for the thinnest section of the resistance ring. Left-click strikes that arc, cracking it — the struck section darkens and crumbles, but the two neighbouring arcs immediately thicken and brighten in response. Each strike costs stamina (shown as your body's dimming glow). You must read the shifting ring, plan which arc to strike next, and find the collapsing sequence that breaks the entire structure before your light goes out. When the last arc falls, the settlement's inhabitants scatter outward in all directions.
- **Diegetic signals:** The resistance ring hovers above the settlement as a circular wall of light with visible thickness variations — thick bright sections are strong, thin dim sections are weak. Your stamina is your body's luminosity and size; as it drains you visibly shrink and dim. Each successful strike: the arc shatters with a crack, fragments fall, neighbouring arcs pulse and swell thicker. The settlement's people are visible inside as huddled silhouettes; when the ring breaks they burst outward as individual running figures.
- **On success:** The final arc shatters, the ring collapses entirely, and the settlement's inhabitants scatter in panic across the terrain — many shallow converts fleeing outward, carrying your pressure with them.
- **On failure:** Your body dims to near-invisibility, too faint to strike again. The remaining ring arcs pulse brighter in triumph. The settlement stands unbroken; you retreat with nothing.
- **Why fun:** The tension is resource-puzzle spatial — reading a dynamic structure under time pressure, committing to strikes that immediately reshape the problem, and discovering whether your chosen sequence was the collapsing order or a dead end that hardened the wall beyond your remaining strength.
- **Pattern:** Weak-point sequencing — the collapsing order
- **GDD grounding:** Resistance shows as a ring. Strike where it is thinnest — but each strike hardens the arc beside it, so winning means finding the collapsing sequence before your stamina runs out.
- **Controls:** mouse-move, left-click
- **Effects:** convert_shallow, stamina_loss, no_effect
- **Judge:** PASS — The design faithfully implements the GDD's exact specification: a visible resistance ring with thickness variations, strikes that harden neighboring arcs, and a stamina-constrained sequencing puzzle. The diegetic signals (ring thickness/brightness for strength, body luminosity for stamina, shattering arcs, scattering figures) require no interface, and the speed/force/many texture (mouse-driven striking, panic scatter, shallow converts) contrasts cleanly with Hope's patient procession design.
  - chunk honored: "Resistance shows as a ring. Strike where it is thinnest — but each strike hardens the arc beside it, so winning means finding the collapsing sequence before your stamina runs out."

---

## Director selection — the human gate

*The pipeline stops here by construction. To build ONE selected design (a minimal playable slice under the A5 patch contract):*

```
python3 run_minigame.py --build --select <id> --from-run mg-live-2
```

Selectable ids: first-contact-fear, first-contact-hope, holding-fear, holding-hope, vigil-fear, vigil-hope

**Selected:** ____________  **Rejected because:** ____________

**Signed (Director):** _______________  **Date:** ____________

