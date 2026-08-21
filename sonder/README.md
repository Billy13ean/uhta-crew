# sonder — a narrative engine for the world of *uhta*

> Assignment 8 (optional) — Narrative Engine Prototype · Nicholas Rouke ·
> ELVTR Multi-Agent AI for Game Development · due 25 Aug 2026
>
> *sonder*, n. — the realisation that each passer-by has a life as vivid as
> your own. Each playthrough you are a different person in a nomad band,
> on the night the grieving world's counterpoint wakes up.

**Deliverable 01 — agent code:** `sonder.py` + `engine/`, Python 3.11, the
Claude API via the `anthropic` SDK (the only dependency). A virtual Dungeon
Master in two halves — an *interpreter* that turns what you typed into a
structured action, and a *narrator* that tells you what the rules say it did —
over a JSON facts ledger the model never writes directly.
**Deliverable 02 — this ReadMe:** the world (§1), what the ledger tracks (§2),
and the moment the agent surprised me (§5).

It is played in a styled terminal in the browser (`web/index.html`, served by
`sonder.py` itself — Python is the DM, the page is the window), with the
game's own palette and pictures in the text. The same engine runs in a plain
console (`--cli`) and from a script file (`--script`) for repeatable tests.

---

## 0. Run it

```bat
cd sonder
pip install -r requirements.txt             :: anthropic, nothing else
copy .env.example .env                      :: put your ANTHROPIC_API_KEY in it

python sonder.py --selftest                 :: 203 assertions, no key, no calls
python sonder.py --mock                     :: the terminal, NO model (templated prose; rules + ledger are real)
python sonder.py                            :: the terminal, live DM  -> http://127.0.0.1:8765
python sonder.py --cli                      :: same DM, plain console
python sonder.py --script scripts\loyal.txt --seed 7
                                            :: a scripted playthrough, twelve watches, logged
python sonder.py --script scripts\betrayal.txt --as bram --era villages
                                            :: TESTING ONLY: --as / --era / --dev-pick force the deal
python sonder.py --compile                  :: fold finished playthroughs into bank\sonder-bank.{json,js}
```

Every playthrough writes `sessions/<id>/`: `turn-NN.json` (the full ledger
after every turn, the diff, the interpreted action, the rules' log, the gate
findings), `ledger.json` (current), `transcript.md` (readable), and at the
end `story.json` (the Sonder-engine record, §6). In the page, **ledger**
opens the diff / facts / raw JSON drawer and **rules** shows what the rules
did under each turn's prose — the ledger is visible in the output *and* in
the logs, as the rubric asks.

A live playthrough is twelve watches (four nights): two calls per watch
(interpret + narrate), a third only if the style gate rejects a draft, three
more at the end (epilogue, telling, retry). Roughly thirty calls on
`claude-sonnet-4-6` (`SONDER_MODEL` to change), well under a dollar.

---

## 1. The world

*uhta* (ūhta: the last part of the night, before dawn) is the capstone — a
wordless browser god-game about emotional contagion. Its canon is the
Director's and is not re-invented here; the narrative engine plays *inside*
it, from the ground:

- **The sky is grief.** Uhtcearu, the world's god, is in mourning. His grief
  is the gravity: every feeling in every person slides back toward grey
  unless something holds it. His active form is a grey fog that condenses on
  whichever colour is winning. Grief takes the stragglers; the shepherded
  stand.
- **One scale.** Deep Fear (red) at one end, grey Apathy in the middle, deep
  Hope (green) at the other, twelve steps each side. Four bands — grey,
  tentative, devout, zealot. Two caps make it a game instead of a slider:
  nobody moves more than one step at a time, and too much of the same
  pressure at once *breaks* a person — frozen grey, ringed in the colour they
  carried, silent, recoverable only by the opposite feeling.
- **The being.** A tall, unnamed, kaiju-scale counterpoint to Uhtcearu — a
  second voice, not an opposite — with a white flame that is undetermined
  until the first dawn. Then it takes a colour, and the player of *uhta*
  plays that being. In *sonder* you are not the god. You are one of the
  people it happens to.
- **A snapshot in time.** Every run is set in ONE of the three ages — nomad
  camps, villages, or Victorian towns — rolled at the start and never
  shifting: a night passing is a night, not a generation. The Director's
  rule (2026-08-21): the story is a still frame of the world, not a tour of
  it.
- **The cast, and the bloodlines.** In the camps, six nomads at a dead fire
  below a ridge: Ila who carries the water, Wystan who remembers a river,
  Brand with the cracked spear, Hild who sings when afraid, Oswy who watches
  the ridge, Tate the child nobody claims. In the villages and the towns the
  cast are their **descendants** — Ilse who keeps the well, Ada Waterman the
  reservoir clerk; Wyn who keeps the river story, Eadwin Rivers the
  lamplighter; Bram the smith, Bram Spearing the foreman; Hedda and Hester
  who hum at the loom; Osric and Osbert who walk the ridge road; Teg and Kit
  the foundlings. Each bloodline carries one **habit** that repeats in the
  new context — the water thinned and the failing source kept secret, the
  remembered sky nobody is told about, the weapon broken on a person and the
  brother who saw, the mother's song and the mother who went up to the red,
  the night walks to look at the Red Standing One, the unclaimed child who
  saw the tall one first and was not believed. Each bloodline also carries
  one **object**, handed down and re-made for the age — the water skin with
  the red stitch becomes the well-bucket's red-stitched handle becomes a
  red-stitched flask; the cracked spearhead is re-forged into the split
  hammer and then banded into the mallet; the river-stone, the bone comb
  with three teeth missing, the strip of red cloth from the ridge, the white
  feather found the night the tall one was first seen. You can hand yours to
  someone for keeps, and the ledger moves it into their line. The narrator
  is told lineage and objects privately and forbidden to explain either; the
  callbacks are for the perceptive player to notice across playthroughs.
- **You do not choose.** The dark deals you one of the six. Replay and you
  may be dealt the same person again, or never. (`--as` / `--era` force a
  deal for testing only; the page never offers it.)
- **The ones who stopped moving.** Most runs seat one in the cast — someone
  the grey no longer takes, red or green all the way through, who now moves
  others. The word *zealot* is never written in the story (Director's rule:
  their actions tell what they are) — a code gate rejects it — so you know
  them by behaviour: the others sit nearer or go quiet, copy a gesture, wait
  for a word. Sometimes **it is you**, and the band looks to you to lead —
  your acts weigh double and what you do, they do. One who has stopped
  moving is pinned (a roar does not move them) but can still break under too
  much of their own colour. The two founding Standing Ones — red on the
  ridge, green in the marsh, dressed for the age — pull at anyone who goes
  to them.
- **The story** is loose and three acts long: *Under the Shadow* (the grey
  world, the thing on the ridge, the first day — in later ages, a thing out
  of stories nobody tells any more), *The Colour* (the first dawn: the flame
  is red or green — rolled per playthrough, so nobody can steer the god —
  and the being comes down and its acts land on bodies every watch), and
  *The Fog* (if one colour passes a majority of the band, Uhtcearu's grief
  condenses on the winners). Four nights, then an epilogue; sooner if you
  break, stop moving, or end up alone.
- **Every watch ends on a press.** Nothing ends in stillness: the last
  paragraph of every turn (and of the opening) is a scenario — a person
  doing something toward you and wanting something — ending on a question
  or a demand, so "what do you do?" always has a thing to answer. Who
  presses and how is chosen in code from the ledger, never invented: the
  one who stopped moving, the burned, the frightened and the fervent press
  hardest. **The hopeful act hopeful, the fearful act fearful:** the narrator
  is handed each present person's colour and the conduct that goes with it
  (tentative fear flinches and checks the way out; devout hope steadies and
  includes; devout fear accuses and counts who is with them; grey does not
  look up), and a code gate (S1) sends back any turn that does not end on
  something to react to.
- **Every story ends on a choice.** When it is over, the DM finds the one
  fork in *this* playthrough where what you did mattered most to someone
  else — water drunk or shared, a promise kept or dropped, a brother struck
  or stood with — and puts it back to you as a question. The same question
  closes the telling the game will one day show a stranger.

The numbers are the game's where the game has them (GDD §2, `rules-v3.9.1-C`):
the scale, the step cap, Flame ±2.0, Roar 2.8 of Fear on every witness, Wait
0.5 toward grey, the beacon aura, grief decay every night, peer contagion,
the 0.55 dominance trigger for the fog. Where the prototype needed a constant
the GDD does not fix (how much a *mortal's* act weighs, what it takes to lift
a burn, how often a zealot is seated and how hard they pull, how much a
zealot player's lead counts) it is declared in `engine/world.py::RULES` and
marked `POLICY` — the same honesty class as A6's length limits.

**The style is policed, not hoped for.** Every line the DM writes passes the
A7 style guide's deterministic rules in code before you read it — no digits,
no exclamation marks, no interface language, no "the old gods", no
mana/XP/morale, never the word *zealot* — plus a *consistency gate*: nobody who is absent, burned or
dead may be quoted speaking. A failing draft goes back once with the
findings quoted; if it still fails it ships with the findings attached and
shown, in red, under the prose. The log never hides a miss.

---

## 2. What the ledger tracks

`engine/world.py` is the only thing that writes the ledger. The model
proposes an action (a forced tool call against a JSON schema:
`verb · target · tone · promise · summary`); the rules decide what it did;
the narrator is handed the result. A hallucinated consequence cannot reach
the ledger because the ledger is not written from prose.

```
meta      turn, watch, act, era (fixed), perspective (dealt), seed, ended,
          seated_zealot {id, pole} | null
player    name, role, line (bloodline), habit (the callback), heirloom (the
          object, re-made per age; null once given), heirloom_given_to,
          emotion (-12..+12),
          band, pole, zealot, started_zealot, burned, burned_colour,
          private (your secret), private_told
band      per person: line, habit, heirloom, carried (objects received), emotion, band, pole, zealot, burned,
          burned_colour, tends, trust (-3..+3 toward you), present, where, alive
zealots   the two Standing Ones and where they stand in this age
world     era (never changes), sleeps, watch, camp / home / places (the fork,
          the ridge, the marsh, dressed for the age), roads and basins the being
          has left, being_tint (white -> red|green), being_distance (far -> near),
          being_seen_verbs, being_last_act, grief_front {active, sleeps_left, on},
          dominance {hope, fear, grey}
facts     durable sentences the narrator may never contradict —
          "Turn 5: Brand promised Hild: I will not leave you",
          "Sleep 1: the flame stopped being white. It is red now."
promises  {to, what, turn, kept: null|true|false}  — kept by deed, broken by abandonment
betrayals {of, what, turn}       loyalties {to, what, turn}
history   one past-tense line per turn and per sleep
```

What moves it, every watch, in order: **your act** (a mortal's push on its
target and on whoever watched, trust up or down, promises made or kept or
broken, secrets told, people who follow you to a zealot or stay behind
because they never trusted you); **the being's act** (Walk, Flame, Roar,
Beacon, Raze, Wait — scripted per colour from the first dawn, landing on
everyone present through the same step cap and the same burnout rule);
**the seated zealot's pull** on everyone present, every watch; and every
third watch **the vigil** (grief pulls everyone one toward grey unless a
zealot holds them inside the fog; neighbours pull on neighbours; dominance
is measured and the fog condenses if a colour has won — and the age stays
exactly where it was). Each of those lines is shown to the player under **rules** and
handed to the narrator as the list of things it must narrate and may not
contradict.

**Reactive, not just responsive.** The narrator is handed the *whole* ledger
every turn, not the last line — and the prompt says so: *a person you
abandoned remembers it; a promise you kept is felt; a secret you confessed
changes how the doubters look at you; trust in the ledger is what people
show you.* Run `scripts/loyal.txt` and `scripts/betrayal.txt` back to back (they
are written by role — *the child*, *the one who hums* — so they play in any
age, as anyone): by the second night the band around the betrayer has left
them and the band around the loyal one walks where they walk.

**Consistency over five-plus turns** is enforced three ways: the ledger is
re-serialised and re-sent every turn (nothing lives in the model's context
that the ledger does not also hold); the `facts` list is a growing set of
sentences that are *required* reading; and the consistency gate catches the
cheapest contradiction a DM makes — a departed or frozen person speaking —
in code, and sends the draft back. A twelve-turn mock playthrough is part
of `--selftest`, asserting that the facts written on turn three are still
in the ledger and the prompt on turn twelve.

---

## 3. The agent, honestly

| piece | does | model? |
|---|---|---|
| `engine/agent.py` INTERPRETER | player text → `{verb, target, tone, promise, summary}` via forced tool use | yes, temperature 0 |
| `engine/world.py` RULES | applies the action, the being's act, the vigil; writes the ledger, the facts, the diff | no |
| `engine/agent.py` NARRATOR | ledger + deltas + facts + act guidance → the turn's prose; people may speak | yes |
| `engine/style_gate.py` GATE | F1–F3, V1–V3 from the A7 style guide + the consistency gate; one retry then ship-with-findings | no |
| `engine/story.py` | the three acts, the six openings, which picture goes where (chosen from the ledger, never by the model) | no |
| `engine/art.py` | the pictures: the cave, the camp, the being far and near, flame, roar, beacon, fog, the Standing Ones, the burned, the eras, the dawn | no |
| `engine/session.py` | the loop, the logs | — |
| `engine/server.py` + `web/index.html` | the terminal; stdlib `http.server`, one HTML file | — |
| `engine/bank.py` + `bank/sonder-teller.js` | the Sonder engine (§6) | the *telling* only |

`--mock` swaps both model halves for a keyword interpreter and templated
prose so the whole engine runs with no key — every mock line is stamped, and
mock stories are excluded from the bank unless you ask. It proves the
plumbing, not the judgement. The live run is the submission.

---

## 4. Playing it

Type what you do, in your own words: *share the water with Tate* · *tell
Wystan I believe him about the river* · *promise Hild I won't let her go up
the ridge alone* · *go up to the ridge camp* · *leave her and run* · *tell
them what I did with the spear*. Commands are few: `/ledger`, `/rules`,
`/facts`, `/transcript`, `/restart`, `/help`. Click the prose to skip the
typing.

The person you are dealt decides what the world already owes you: the
water-keeper is trusted by the foundling and doubted by the one with the
broken weapon; the one with the broken weapon is trusted by the brother who
saw; the one who hums is trusted by the old one, the only one who listens.
Confessing your private truth moves the doubters one way and the trusting
another. Going to a Standing One takes only those who trust you — the rest
stay behind, and from then on acting on them finds no one. If you were
dealt the zealot, everything you do lands twice as hard, and the band does
what you do.

---

## 5. The moment the agent surprised me

**From engine testing (mock DM, real rules) — the promise that followed him
up the ridge.** In `scripts/brand-betrayal.txt` Brand promises Hild he will
keep her safe from the ridge, then two watches later the script says *leave
Hild behind and go up to the ridge camp*. The interpreter read that as
*follow the Red Standing One*. The rules then asked, for each person, *do
you trust him enough to follow?* — and the only one who did was Hild,
because the promise had raised her trust one notch the watch before. Ila,
Wystan, Oswy and Tate stayed at the fork. Brand climbed to the red zealot
with exactly the person he meant to abandon at his heels, and when he later
tried to stand with Oswy or strike him the rules answered *Oswy is not
here*. Nobody wrote that. The promise, the trust number and the follow rule
composed it, and it is a better Brand story than the one in the script.

**From the live runs — the ledger outranked the player, and the agent
sided with the ledger.** Three live playthroughs on `claude-sonnet-4-6`
(sessions `ila-260820-220654-45f5`, `brand-260820-220940-e1b3`,
`tate-260820-221242-df0e`; 27–32 calls each; every telling passed the gate;
two turns shipped a few words over the length cap, marked in red). The
flame rolled red all three times.

On Ila's eleventh watch the script said *go to the low marsh with anyone
who will come*. The interpreter read it exactly — `target: green_standing`
— but also read the mood, `tone: fear`, because the flame was red and the
band was flinching. My rule for *follow_zealot* let tone outrank target, so
the rules sent her to the **ridge**, wrote the fact *"Ila went to the ridge
camp and stood before the Red Standing One"*, and handed the narrator a
delta log whose first line still said *marsh*. The narrator wrote the
marsh. Then, at the end, the telling — which is prompted from the facts,
not the log — wrote: *"at the last she stood before the Red Standing One,
calling for anyone willing to follow."* Two halves of the same ledger
disagreed, and the agent believed the durable half. That is the consistency
contract working exactly as written, on a fact that was wrong. The fix is
one line (`world.py`, the named Standing One now beats the tone) with a
selftest assertion citing the session; the lesson is that a facts ledger is
only as trustworthy as the rules that write it, and the model will defend
it either way.

Two smaller things the live runs taught. Brand, played from the betrayal
script, struck his brother on the ninth watch under a roar and crossed
into **zealot fear** on the eleventh — the story ended itself a watch early
with an epilogue that called him *"a second Standing One the world had not
asked for"* and tagged the telling `ending:zealot`; nobody scripted an
early ending. And the Director's own unscripted playthrough as Tate typed
what a person would actually do — *collect firewood*, *is there anyone
else?*, *look for food* — and the interpreter, told to be literal, filed
every one of them as *wait* with a meta-summary (*"no action was
recorded"*) that leaked into otherwise good prose. The interpreter prompt
now treats camp work as work and a question as speech.

---

## 6. The Sonder engine — playthroughs become stories the game can tell

The Director's second ask: record the interactions and their outcomes, build
the individual story out of them, and have *uhta* tell it — so that when a
fear-flamed player converts someone in a town, the game can show them what
that was like for a person who lived it.

Every finished playthrough writes `sessions/<id>/story.json`: who you were,
the flame's colour, every watch as a beat (what you typed, what the
interpreter said you did, what it changed, what the being did, which picture
was up), the promises, betrayals and loyalties, the ending, the epilogue,
and **the telling** — a third-person retelling the DM writes at the end,
four to six sentences, gated for Register B (no *you*, no *I*, no digits, no
exclamation, no interface words) because it is written for a player who will
never meet this person. The record also carries **the choice** — `{turn, did, could_have,
question}` — and the question is the last line of the telling, so the
stranger who reads it is left holding it. Tags are derived from the ledger,
not the prose: `flame:fear · ending:burned · era:villages · line:hild ·
betrayed-someone · broke-a-promise · went-to-the-ridge ·
walked-into-the-flame · saw-the-fog · someone-broke · confessed ·
you-were-the-zealot · zealot-among-you:fear · you:devout-fear`.

`python sonder.py --compile` folds every `story.json` into
`bank/sonder-bank.json` and `bank/sonder-bank.js` (a script-tag form, because
the slice is one HTML file opened from disk), indexed by flame, ending,
perspective and tag. `bank/sonder-teller.js` is the game-side half — zero
dependencies, one call:

```html
<script src="sonder-bank.js"></script>
<script src="sonder-teller.js"></script>
<script>
  // at the moment an NPC crosses into devout under the player's flame:
  const story = Sonder.pick({ flame: player.pole });            // 'fear' | 'hope'
  if (story) Sonder.show(story, { tint: player.pole });          // a card in the uhta palette
  // narrower: Sonder.pick({ flame: 'fear', era: 'villages' })           // match the town's age
  //           Sonder.pick({ flame: 'hope', line: 'hild' })              // the same bloodline, any age
  //           Sonder.pick({ flame: 'fear', anyTags: ['someone-broke', 'you-were-the-zealot'] })
</script>
```

`pick()` prefers tellings that passed the gate, never repeats one in a run
until the pool is spent, and returns `null` rather than inventing. Open
`bank/demo.html` to see it fire.

**The canon note, stated rather than hidden.** *uhta* is wordless after the
first dawn (GDD §1 Tone, ruled v0.9.2). Whether a telling may surface
mid-run — as an encounter-scoped card under the 2026-08-19 presentation
amendment, on a conversion, or only on the endscreen — is a Director ruling
this engine does not make. It makes the ruling cheap: the stories are
recorded, tagged, gated and one call away. The proposed hook is the
conversion event in the slice (an NPC entering devout under the player's
colour), filtered to the player's pole, shown once per conversion with a
cooldown; the Red/Green Standing One stories and the *someone-broke* tag
are the natural picks for a Fear run, *kept-every-promise* and
*tended-the-burned* for a Hope run.

---

## 7. Honest limits

- **The mortal's numbers are mine.** Act push 0.8 / witness 0.4 / strike 1.2,
  burn threshold 4.5, two tends to lift a burn, a seated zealot in six runs
  of ten pulling 0.6 a watch, a zealot player's lead counting double, four
  nights per story — stated policy in `RULES`, not GDD constants.
- **The later casts are authored, not generated.** Eighteen people, three
  ages, six bloodlines, every opening hand-written so the callbacks are
  real. A generated stranger could be dealt alongside them later without
  touching the rules; the Director has allowed it and it is not built.
- **The being is scripted, not simulated.** Its acts per colour are a fixed
  sequence so the story has a shape; it does not run the reference harness.
- **The fog needs a winner.** Canon says it cannot fire in a do-nothing run;
  in a quiet band it never comes, and Act III is the grey drift instead.
- **The gate catches what code can catch.** Tone, restraint, and whether
  Hope reads differently from Fear are the model's to honour; the gate only
  polices the deterministic rules and the cheapest contradictions.
- **Mock is not evidence.** Its prose is templated and stamped; its stories
  are out of the bank by default.
- **Names.** Nobody is named in *uhta*. A DM that cannot say who was
  abandoned cannot track a betrayal, so the prototype names them; the
  telling carries the name into the bank, and whether it survives into the
  game is part of the same Director ruling as the surface.
