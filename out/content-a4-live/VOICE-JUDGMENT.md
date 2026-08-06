# VOICE-JUDGMENT — does this sound like uhta?

> Self-assessment plus the one retrieval change that was measured rather than asserted.
>
> Run `content-a4-live` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-06 21:48:02

## The test a line has to pass

uhta's register is fixed in GDD §2.5: *"short declarative lines, no mythology"*, and the narration is **instrumentation, not lore**. So the question is not whether a line is pretty. It is:

> Would this line read identically in any other god-game about hope and fear?

If yes, it has failed, however well written it is. That is the `GENERIC` flag class in `prompts/critic.md`, and it is the one the Critic is told to be hardest about.

---

## The retrieval tweak, measured — beat `n4` (First Roar — whatever you intend)

GDD §4.5 records the change and the reason for it:

> The first hand-run retrieved **only** §2.5, the experience section, and every candidate came back generic: lines that would sit unchanged in any god-game about hope and fear. The fix was not a better prompt but a wider cut — **a narration beat now retrieves two chunks, the experience section *and* the verb's own row from the §2.2 table**.

That was design-stage. This run executes both arms on the same beat, with the same Writer temperature and candidate count, and hands **both candidate sets to the same Critic at temperature 0, judged against the same chunks** — so the only variable is what the Writer could see.

| arm | retrieval | chunks the Writer saw | candidates | cleared the Critic |
|---|---|---|---|---|
| **A — naive** | single experience-side query, top-1 | `§2.5` | 8 | **4/8** |
| **B — GDD §4.5 rule** | two queries (mechanic + experience), unioned | `§2.2`, `§2.5` | 8 | **5/8** |

**Read.** Arm B cleared a higher share of its candidates (5/8 vs 4/8). The mechanical chunk is what the extra passes are made of — the Critic's `GENERIC` class is the one arm A loses candidates to.

### Arm A — naive single-query top-1

- FAIL `GENERIC` — You roar — and everyone who witnesses it is frightened, whatever you intend.
    - *Omits the mechanical consequence (earth shattering) that distinguishes roar from generic fear-causing.*
- PASS — Roar. The earth shatters ahead, and all who hear are frightened — no matter what you feel.
- FAIL `GENERIC` — This is the roar. It frightens everyone who witnesses it, whatever color you hold.
    - *Omits the earth-shattering consequence entirely, reducing roar to generic fear-causing.*
- FAIL `WRONG-REGISTER` — Roar, and the ground breaks — but know that all who see it will fear you, even if you carry hope.
    - *The 'but know that' construction moralizes instead of instrumenting; it's advisory mythology, not declarative consequence.*
- PASS — You roar and the earth shatters. Everyone who witnesses it becomes frightened — your intention does not matter.
- PASS — The roar: it splits the earth, and frightens all who witness — regardless of the flame you carry.
- PASS — Roar. The land cracks open ahead, and every witness is made afraid — your feeling cannot change this.
- FAIL `WRONG-REGISTER` — This is roar — earth shatters where you face, and all who see are frightened, whatever you intend them to feel.
    - *The 'whatever you intend them to feel' construction is explanatory/psychological rather than declarative instrumentation.*

### Arm B — the two-chunk rule

- PASS — You roar — and everyone who witnesses it is frightened, whatever you intend.
- PASS — Roar. The earth shatters ahead of you. Everyone who sees it happen is afraid.
- FAIL `WRONG-REGISTER` — The roar frightens all who witness it, whatever you intend.
    - *Missing the verb-naming structure required by the tutorial format; reads as lore statement rather than action-consequence instruction.*
- PASS — You roar and the ground breaks open. Those who watch are frightened — even by hope.
- FAIL `EXCEEDS-SCOPE` — Roar — the line breaks, and everyone near enough to see is pushed toward fear.
    - *The phrase 'pushed toward fear' contradicts the chunks' consistent language of an 'unconditional Fear push' — this isn't gradual movement but immediate application.*
- PASS — When you roar, the earth splits. Anyone who witnesses the break is frightened, regardless of your flame.
- PASS — You roar. It clears a path — and frightens everyone close enough to see, no matter what color you carry.
- FAIL `GENERIC` — Roar: fast travel, and unconditional fear for those who watch it happen.
    - *Colon-label format strips away the 'whatever you intend' clause that makes this uhta-specific; could describe any AOE fear ability in any game.*

---

## Where this still falls short

- **One beat, one run.** The A/B is a single beat at n=8 candidates per arm. It is evidence about a retrieval policy, not a statistically meaningful measurement.
- **The Critic is the same model family as the Writer.** An adversarial evaluator that shares the generator's priors will miss the failures both share. The rules crew has the same limitation and names it too.
- **No player has read any of this.** GDD §2.8 is 0 of 6 tested. These lines are the thing that unblocks criteria 1 and 3; whether they *work* is a question only the stranger test answers.
- **Selection is not automated and should not be.** Every line here is a candidate. The `## Director selection` block in each content file is deliberately empty.
