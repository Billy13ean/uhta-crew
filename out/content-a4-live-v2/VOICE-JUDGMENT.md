# VOICE-JUDGMENT — does this sound like uhta?

> Self-assessment plus the one retrieval change that was measured rather than asserted.
>
> Run `content-a4-live-v2` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-07 01:47:04

## The test a line has to pass

uhta's register is fixed in GDD §2.5: *"short declarative lines, no mythology"*, and the narration is **instrumentation, not lore**. So the question is not whether a line is pretty. It is:

> Would this line read identically in any other god-game about hope and fear?

If yes, it has failed, however well written it is. That is the `GENERIC` flag class in `prompts/critic.md`, and it is the one the Critic is told to be hardest about.

---

## The retrieval tweak, measured — beat `n4` (First Roar — whatever you intend)

GDD §4.5 records the change and the reason for it:

> The first hand-run retrieved **only** §2.5, the experience section, and every candidate came back generic: lines that would sit unchanged in any god-game about hope and fear. The fix was not a better prompt but a wider cut — **a narration beat now retrieves two chunks, the experience section *and* the verb's own row from the §2.2 table**.

That was design-stage. This run executes both arms on the same beat with the same Writer temperature and candidate count. **The judge is held constant:** both candidate sets go to the same Critic at temperature 0, against the same chunk set — so the only variable is what the *Writer* could see.

The two columns below are read from the run's dispatch ledger, not typed. If they ever diverge, this table says so and the comparison is void.

| arm | Writer's retrieval | chunks the **Writer** saw | chunks the **Critic** judged against | candidates | cleared |
|---|---|---|---|---|---|
| **A — naive** | single experience-side query, top-1 | `§2.5` | `§2.2`, `§2.5` | 8 | **5/8** |
| **B — GDD §4.5 rule** | two queries (mechanic + experience), unioned | `§2.2`, `§2.5` | `§2.2`, `§2.5` | 8 | **6/8** |

**Judging context identical across arms: YES — the comparison is valid.** Arm A's Writer saw one chunk and arm B's saw two, but both Critics judged against the same two. A candidate that fails in one arm and passes in the other did so because of what the Writer was given, not because the judge changed.

**Read.** Arm B cleared a higher share of its candidates (6/8 vs 5/8). The mechanical chunk is what the extra passes are made of — the Critic's `GENERIC` class is the one arm A loses candidates to.

### Arm A — naive single-query top-1

- PASS — You roar, and everyone who witnesses it is frightened — whatever you intend.
- PASS — Roar. All who witness it are frightened, regardless of what you feel.
- FAIL `EXCEEDS-SCOPE` — The roar frightens everyone who hears it. Your intention does not matter.
    - *Chunks specify 'witness' not 'hears' — roar is witnessed along a line, not heard as sound.*
- FAIL `CONTRADICTS-CHUNK` — You roar. Everyone in its path becomes afraid — even if you burn with hope.
    - *Roar affects witnesses 'of the line' not 'in its path' — NPCs near the line are affected, not NPCs struck by it.*
- PASS — Roar, and all who witness are made fearful. The flame's color changes nothing.
- FAIL `WRONG-REGISTER` — The roar is fear itself. Everyone who hears it cowers, whatever color you carry.
    - *'The roar is fear itself' is mythological metaphor where instrumentation is required; 'cowers' is flavor not mechanical consequence.*
- PASS — You roar. The earth shatters ahead, and everyone who sees it is frightened — no matter your flame.
- PASS — Roar: it frightens all witnesses. What you intend makes no difference.

### Arm B — the two-chunk rule

- PASS — You roar. Everyone who witnesses it is frightened, whatever you intend.
- PASS — Roar. The earth shatters ahead — and everyone who sees you do it becomes afraid.
- PASS — You roar and the ground breaks open. All who witness it feel fear, no matter what your flame holds.
- PASS — Roar: it clears the path fast, but everyone who watches is pushed toward fear — even when you carry hope.
- FAIL `GENERIC` — You can roar to shatter the earth. Everyone within sight of the breaking will be frightened, regardless of what you feel.
    - *Uses 'within sight' instead of the witness-radius concept, and 'will be frightened' softens the unconditional mechanical push to generic emotional language.*
- PASS — Roar shatters a line of ground ahead of you. Anyone who witnesses the act is made afraid — your flame's color doesn't matter.
- FAIL `GENERIC` — You roar and the land splits. Every witness is frightened by what they see, whatever emotion you carry.
    - *'Frightened by what they see' implies reaction to spectacle rather than the mechanical push; 'whatever emotion you carry' is weaker than the flame-color independence.*
- PASS — Roar breaks the earth in a line. All who see it happen are afraid — the flame you hold changes nothing.

---

## Where this still falls short

- **One beat, one run.** The A/B is a single beat at n=8 candidates per arm. It is evidence about a retrieval policy, not a statistically meaningful measurement.
- **The Critic is the same model family as the Writer.** An adversarial evaluator that shares the generator's priors will miss the failures both share. The rules crew has the same limitation and names it too.
- **No player has read any of this.** GDD §2.8 is 0 of 6 tested. These lines are the thing that unblocks criteria 1 and 3; whether they *work* is a question only the stranger test answers.
- **Selection is not automated and should not be.** Every line here is a candidate. The `## Director selection` block in each content file is deliberately empty.
