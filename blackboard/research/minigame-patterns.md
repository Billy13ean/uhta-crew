# Mini-game design patterns — curated research corpus

> Seeded 2026-08-18 for the A6 mini-game pipeline. Curated from published
> design writing (sources cited per section); each pattern is summarised for
> ONE purpose — retrieval grounding for encounter mini-game candidates that
> must satisfy uhta's encounter rules: wordless and diegetic ("no interface,
> no text, only your body and theirs"), pole-asymmetric ("the two poles never
> play the same game"), and individual-scale. Patterns are described
> mechanically, not as lore; nothing here is uhta canon.

## Herding — pressure steering

The player never commands the crowd; they position their own body so the
crowd's avoidance/attraction pushes it where they want. Kyon's designers
found the mechanic lives or dies on responsiveness and on making the flock's
intent legible — they added a visible leader animal so players could read
where the herd was heading, and found that "sheep pileups" (congestion with
no read on why) were the main failure mode. The fun is indirect control: the
player feels in control "of not only their character, but also the flock."
Wordless feasibility: total — pressure, spacing and a visible leader carry
all state. Demands: positioning, patience, reading collective motion.
Failure texture: over-pressure scatters or jams the group.
(Source: Kyon devblog, "Core Mechanics: Herding Sheep and Having Fun Doing
It", kyon-game.com, 2017.)

## Threshold fight — the steady hold

A continuous quantity (line tension, lock torque, flame brightness) must be
held inside a moving band: push too hard and it snaps, ease off and it
slips. The fishing-minigame taxonomy calls this the "threshold fight" catch
style (Stardew's bar-follow, press-and-release tension), and distinguishes
it from button-mashing by what it asks of the player: sustained modulation
rather than bursts. Its emotional register is excitement layered on top of a
calm approach phase — the taxonomy's three axes are serenity (the wait),
surprise (the bite), excitement (the fight). Wordless feasibility: total —
the held quantity can be shown diegetically (glow, tremble, bend). Demands:
fine motor restraint, reading a drifting target. Failure texture: the snap —
one overcorrection undoes the hold. The correct move is often to do less.
(Source: Davide Aversa, "Taxonomy of Fishing Mini-games", davideaversa.it /
Game Developer.)

## Timing window — the bite

A discrete moment arrives (visibly or invisibly signalled) and the player
must respond inside a window. The fishing taxonomy's approach/bite/catch
structure shows the window works best as a punctuation mark between a calm
phase and an active phase — the wait makes the window land. Hidden-signal
variants trade fairness for surprise; visible-signal variants are learnable.
Wordless feasibility: total (animation is the signal). Demands: attention,
reaction. Failure texture: the moment passes and the opportunity walks away.
(Source: Aversa, fishing taxonomy, as above.)

## Path tracing — the drawn line

The player traces or walks a path under constraint — speed limits, turn
limits, don't-lift rules — and the path itself is the artifact (a rope, a
thread, a road, a chain). Fun comes from the tension between the ideal line
and what the constraint lets you draw; longer or more ambitious lines are
worth more and are harder to hold. Wordless feasibility: total — the line is
visible in the world. Demands: planning then smooth execution. Failure
texture: the line breaks where you rushed it.
(Related to procession/escort below; pattern generalised from line-drawing
and route games surveyed in the mini-game literature, GameDev.net mini-games
threads.)

## Procession — follow-the-leader escort

Recruits fall in behind the player and the growing line must be kept intact:
move too fast, turn too sharply, or clip a hazard and the tail detaches.
Escort/conga mechanics put the cost on the LEADER's discipline, not the
followers' AI — the player's restraint is the skill. The RPG mini-game
literature's warning applies directly: forced repetition of an escort sours
fast, so instances should be short and stakes visible. Wordless feasibility:
total — the line itself is the state display. Demands: tempo control,
route choice. Failure texture: whoever you dropped is still standing where
you lost them.
(Sources: Kyon herding follow-behaviour notes; Game Developer, "Designing
RPG Mini-Games (and Getting Them Right)".)

## Interception — the cutoff

Targets flee on readable vectors; the player has a few seconds of superior
speed to choose which escape lines to close. It is chase geometry as a
puzzle: you cannot catch everyone, and the design's honesty is in making
that visible — every runner you head off is caught, every one you ignored
gets away and the miss has consequences. Wordless feasibility: total.
Demands: instant triage of angles, commitment. Failure texture: choosing
badly and watching the fastest runner carry the story out of reach.
(Pattern surveyed from herding/pursuit mechanics: Flockers, flocking-AI
design literature — O'Reilly "AI for Game Developers" ch.4 flocking.)

## Triage — protect what you can

More things need protection than the player can protect; resources (light,
shields, attention) are allocated under pressure and the design guarantees
loss. The skill is choosing WHAT to lose. The RPG mini-game principles say
stakes must be real and legible or the choice is noise — triage only lands
when the player can see, afterwards, exactly what their allocation cost.
Wordless feasibility: total — coverage is shown spatially (a shield you are
holding over one point is visibly not over another). Demands: valuation
under time pressure. Failure texture: the thing you abandoned dies exactly
where you left it. This is the coldest pattern in the set and reads
naturally as a Fear-side mechanic.
(Source: Game Developer, "Designing RPG Mini-Games (and Getting Them
Right)" — stakes and consequence principles.)

## Weak-point sequencing — the collapsing order

A defensive structure (a ring, a wall, a formation) has segments of varying
strength; striking one segment hardens its neighbours. The puzzle is finding
the ORDER of strikes that collapses the whole before resources run out — a
sequencing puzzle wearing an action skin. Wordless feasibility: total —
segment strength reads as thickness/brightness. Demands: reading a
structure, planning a sequence, adapting when a strike reveals new
information. Failure texture: an opening squandered — the wall you softened
hardened again behind your wasted stamina.
(Pattern generalised from boss-armor sequencing and lock mechanics — NME on
"Museum of Mechanics: Lockpicking", which catalogues staged-resistance lock
designs.)

## Diegetic state display — no HUD, no words

The craft rule that makes all of the above compatible with a wordless game:
state lives in the world, not on the screen. Dead Space's health-on-the-
spine and Metro's wrist watch are the canonical examples; the working
principles are consistency (the display obeys the world's own visual
language), functionality (it is still unambiguous), integration (it exists
IN the scene), and immediate feedback. The stated ideal: "a well-designed
diegetic interface is invisible." The named pitfalls are the evaluator's
checklist in reverse: obscurity (player cannot read the state), and
intrusiveness (the display upstages the scene).
(Source: Wayline, "Beyond the HUD: The Power of Diegetic Interfaces in Game
Design".)

## Integration principles — when a mini-game helps the host game

From the RPG mini-game literature, the conditions under which a mini-game
strengthens rather than interrupts: (1) thematic coherence — the mini-game
must make sense inside the world's own logic, though it need not reuse the
host's mechanics; (2) stakes wired to the main loop — outcomes must pay in
the host game's real currencies, not a side wallet; (3) introduce once,
never force mastery of optional instances; (4) short instances, difficulty
ramping across repeats; (5) production quality — an unfinished mini-game
damages trust in the whole. The budget rule is blunt: if the project is
over budget, mini-games are cut first — which is an argument for designing
them small enough to finish.
(Source: Game Developer, "Designing RPG Mini-Games (and Getting Them
Right)".)
