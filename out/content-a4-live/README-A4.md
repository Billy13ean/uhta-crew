# Assignment 4 — dynamic content pipeline for uhta

> What content was generated, does it sound like the game, and what did the Critic catch.
>
> Run `content-a4-live` · backend `live` · model `claude-sonnet-4-5` · generated 2026-08-06 21:48:02

## What this is

`run_content.py` generates the **text** of uhta — a wordless browser god-game about emotional contagion — against the game's own GDD read as a RAG corpus. It is a second, independent pipeline in the Assignment-3 repo: it reuses `crew/blackboard.py`, `crew/llm.py` and `crew.agents.AgentError` verbatim, and **nothing in `crew/` imports `content/`**, so adding it could not change what a rules run does.

```
corpus (deterministic)   chunk 4 blackboard files at ### boundaries, scope by
                         CORPUS_POLICY, record every exclusion -> BM25 index
retrieval (deterministic) per beat: two queries (mechanic + experience),
                         union their cuts, record every exclusion
generation               Writer (temp 0.9, N candidates) -> Critic (temp 0.0,
                         verdict + quoted chunk + correction)
ab                       the same beat twice: naive top-1 vs the GDD §4.5
                         two-chunk rule, both sets judged by the same Critic
assembly (deterministic) content files + RAG-TRACE / CRITIC-LOG /
                         VOICE-JUDGMENT / this file, all generated
```

---

## 1. The knowledge base is the game's own GDD

*[injected from this run]*

- Corpus files: `CANON.md`, `CANON-process.md`, `uhta-gdd-v0.9.7-full.md`, `uhta-gdd-v0.9.7-abridged.md`
- **24 chunks / 12,315 words indexed**
- **28 chunks / 13,311 words excluded**, each with a recorded reason (see `RAG-TRACE.md`)

There is no placeholder lore anywhere in this pipeline. The corpus is `uhta-gdd-v0.9.7`, its abridged submission variant, and `CANON.md`, the locked-decision digest.

**The corpus is *scoped*, which is the part worth arguing about.** The GDD is two documents in one binding — the design of uhta, and the design of the pipeline that builds uhta. Only the first is a knowledge base for writing the game's text, so `CORPUS_POLICY` keeps §1, §2, §5, §6 and Appendix A and drops §3, §4, §7, the version changelogs and `CANON-process.md`. The sharp case is **§4.5**, which contains the Director's own hand-written worked narration example. Indexed, it ranks near the top on a Roar query — and a Writer handed it is not generating a line, it is handing the Director's back. Excluding it is the difference between a pipeline that writes and one that retrieves an answer.

---

## 2. Three content types the game specifically needs

### Teacher narration — the opening cycle — 8 beats → `narration-lines.md`

**The gap.** uhta is wordless after the first dawn, and the one narrated cycle has never been written. GDD §2.8 criteria 1 and 3 are **Blocked** on exactly this: a stranger cannot reach their first Sleep without being told what the keys do, and cannot name the two things they can make people feel. §2.7 lists the narrated opening as NICE #1 and as the only unbuilt item that currently blocks the Definition of Playable. This is not thin content — it is absent content on the critical path.

### Era and settlement flavor — the three eras — 5 beats → `era-flavor.md`

**The gap.** GDD §2.3 locks the division of labor — 'landscape tint communicates feeling; era art communicates time' — and §2.6 ships era progression (Nomad/Tribal → Village → Victorian at sleeps 6 and 14) as built. The art exists; the words that tell an art pass what a settlement in each era *is* do not. §4.5 names 'era-transition and settlement flavor across three eras' as one of the three content gaps. Without it the eras are dress changes with no stated meaning.

### Endscreen candidates — 3 beats → `endscreen-candidates.md`

**The gap.** GDD §6 carries the endscreen as an **open question the Director has not ruled on**: can the outcome be delivered wordlessly, with a text card demoted to a post-image epilogue, and does the teacher's voice return once at the very end? §2.7 lists the wordless endscreen as NICE #2. The run currently ends on a readout. These are candidates for a ruling, and are marked UNRULED throughout.

None of these is a demonstration topic. The narration lines in particular are the single item on the project's critical path: GDD §2.7 lists the narrated opening as the only unbuilt thing blocking the Definition of Playable, and §2.8 criteria 1 and 3 are **Blocked** on it by name.

---

## 3. Retrieval — query, chunk and output side by side

`RAG-TRACE.md` is the artifact for this and it is generated per run: for every beat it prints both queries, every chunk selected with its BM25 score, an excerpt of the chunk text, every chunk cut with the reason it was cut, and the candidates that came out.

Retrieval is **BM25 in pure Python** (`content/retriever.py`, k1=1.5, b=0.75, non-negative IDF) rather than a package, because the assignment permits one third-party dependency and it is already spent on `anthropic`. The scorer being written out is not a purity argument — it is what lets `--selftest` assert specific ranking behaviour with numbers, without a key and without a model.

---

## 4. What the Critic caught

*[injected from this run]*

- **128 candidates judged**, 66 passed, **62 caught and corrected**
- Flag classes fired: `CONTRADICTS-CHUNK`, `EXCEEDS-SCOPE`, `GENERIC`, `WRONG-REGISTER`

**The first catch, in full:**

> **Rejected** — The flame in your hand is white and undetermined.
>
> **Chunk it breaks** — The white flame is genuinely undetermined
>
> **Why** — Uses 'undetermined' as abstract descriptor rather than stating the mechanical consequence that makes it undetermined in uhta's system.
>
> **Correction** — The white flame becomes whatever you do with it.

The consistency loop is **structural, not exhortative**. `content/agents/critic.py` raises `AgentError` and halts the run on a `FAIL` with an empty `correction`, on a flag class outside the four allowed, and on a FAIL that quotes no chunk. `CRITIC-LOG.md` therefore cannot contain a rejection without a repair — the pipeline is incapable of producing one.

---

## 5. Does it sound like uhta?

`VOICE-JUDGMENT.md`, generated from this run, is the self-assessment — including the A/B stage that measures the one retrieval change on record instead of asserting it, and a closing section on where the whole thing still falls short.

---

## 6. Running it

```bash
python3 run_content.py --selftest      # no key: retrieval assertions
python3 run_content.py --mock-llm      # no key: full pipeline on fixtures (NOT content)
python3 run_content.py --candidates 8  # LIVE — needs ANTHROPIC_API_KEY
```

`--mock-llm` replays canned fixtures and produces no real content; every artifact it writes is stamped as such and `manifest.json` records `"llm_backend": "mock"`. The retrieval half is real in every mode.

**It ends at a human.** The rules crew stops at a blank `## Ruling`; this pipeline stops at an unfilled `## Director selection`, and the endscreen file is marked UNRULED throughout because GDD §6 records that question as open.
