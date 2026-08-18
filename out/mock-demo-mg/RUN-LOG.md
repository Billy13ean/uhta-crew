# RUN-LOG — mock-demo-mg

Every blackboard read and write, in order. The blackboard IS the
shared memory (GDD §3.3): no agent receives another agent's live
context, so this log is the complete record of inter-agent
communication for this run.


## Stage 1 — corpus

Chunk three documents under the PER-DOC policy (v0.9.9 game sections + v0.9.7 §2 mechanics + the seeded mini-game patterns research doc), build the BM25 index. Deterministic; no LLM.
- `corpus` **READ** `blackboard/gdd/uhta-gdd-v0.9.9-condensed.md` (20826 B, sha256:8e5249696eddb1f3)
- `corpus` **READ** `blackboard/gdd/uhta-gdd-v0.9.7-full.md` (99631 B, sha256:a2a6921c280eb233)
- `corpus` **READ** `blackboard/research/minigame-patterns.md` (8401 B, sha256:c7a9e855090e6e4f)
- `corpus` indexed **22** chunks; excluded **23**, each with a reason (policy `minigame per-doc policy v1`)

## Stage 2 — GER loop (per encounter slot)

design -> evaluate -> (refine -> evaluate) x 2 -> accept or escalate. Every draft and every finding lands on the blackboard before the next stage reads it.
- `retriever-first-contact-hope` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 21.28), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 8.26), `minigame-patterns.md §sec-2` (bm25 44.63)
- `mg-designer-first-contact-hope` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-first-contact-hope` **WRITE** `out/mock-demo-mg/rounds/first-contact-hope-r0-draft.json` (1226 B, sha256:6e76b2ae6793ffab)
- `mg-judge-first-contact-hope` **READ** `out/mock-demo-mg/rounds/first-contact-hope-r0-draft.json` (1226 B, sha256:6e76b2ae6793ffab)
- `mg-judge-first-contact-hope` MOCK replay <- `tests/fixtures/minigame/` (verdict PASS)
- `mg-judge-first-contact-hope` **WRITE** `out/mock-demo-mg/rounds/first-contact-hope-r0-findings.json` (87 B, sha256:0a2363899409e6c4)
- `mg-first-contact-hope` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-first-contact-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 21.28), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 9.68), `minigame-patterns.md §sec-6` (bm25 28.91)
- `mg-designer-first-contact-fear` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-first-contact-fear` **WRITE** `out/mock-demo-mg/rounds/first-contact-fear-r0-draft.json` (1188 B, sha256:e004424c33754372)
- `mg-judge-first-contact-fear` **READ** `out/mock-demo-mg/rounds/first-contact-fear-r0-draft.json` (1188 B, sha256:e004424c33754372)
- `mg-judge-first-contact-fear` MOCK replay <- `tests/fixtures/minigame/` (verdict PASS)
- `mg-judge-first-contact-fear` **WRITE** `out/mock-demo-mg/rounds/first-contact-fear-r0-findings.json` (87 B, sha256:8d55f72788a8597b)
- `mg-first-contact-fear` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-vigil-hope` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 15.09), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 11.98), `minigame-patterns.md §sec-4` (bm25 40.94)
- `mg-designer-vigil-hope` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-vigil-hope` **WRITE** `out/mock-demo-mg/rounds/vigil-hope-r0-draft.json` (1188 B, sha256:d5d89bf934fa0453)
- `mg-judge-vigil-hope` **READ** `out/mock-demo-mg/rounds/vigil-hope-r0-draft.json` (1188 B, sha256:d5d89bf934fa0453)
- `mg-judge-vigil-hope` MOCK replay <- `tests/fixtures/minigame/` (verdict PASS)
- `mg-judge-vigil-hope` **WRITE** `out/mock-demo-mg/rounds/vigil-hope-r0-findings.json` (79 B, sha256:49b2257d7ec5e511)
- `mg-vigil-hope` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-vigil-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 15.09), `minigame-patterns.md §sec-7` (bm25 22.61)
- `mg-designer-vigil-fear` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-vigil-fear` **WRITE** `out/mock-demo-mg/rounds/vigil-fear-r0-draft.json` (1056 B, sha256:3f7c1a32913104c6)
- `mg-judge-vigil-fear` **READ** `out/mock-demo-mg/rounds/vigil-fear-r0-draft.json` (1056 B, sha256:3f7c1a32913104c6)
- `mg-judge-vigil-fear` layer-1 design gate: **1 finding(s)** (round 0) — design never reached the LLM judge
- `mg-judge-vigil-fear` **WRITE** `out/mock-demo-mg/rounds/vigil-fear-r0-findings.json` (222 B, sha256:9bdd792fcfb5d61d)
- `mg-refiner-vigil-fear` MOCK replay <- `tests/fixtures/minigame/` (refined design round 1)
- `mg-refiner-vigil-fear` **WRITE** `out/mock-demo-mg/rounds/vigil-fear-r1-draft.json` (1166 B, sha256:a91992b55fb106b1)
- `mg-judge-vigil-fear` **READ** `out/mock-demo-mg/rounds/vigil-fear-r1-draft.json` (1166 B, sha256:a91992b55fb106b1)
- `mg-judge-vigil-fear` MOCK replay <- `tests/fixtures/minigame/` (verdict PASS)
- `mg-judge-vigil-fear` **WRITE** `out/mock-demo-mg/rounds/vigil-fear-r1-findings.json` (79 B, sha256:3bcca4f808d22ca4)
- `mg-vigil-fear` **ACCEPTED** at round 1 (1 refinement(s))
- `retriever-holding-hope` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 12.04), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 11.67), `minigame-patterns.md §sec-5` (bm25 46.53)
- `mg-designer-holding-hope` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-holding-hope` **WRITE** `out/mock-demo-mg/rounds/holding-hope-r0-draft.json` (1011 B, sha256:8b3ea6419d15b678)
- `mg-judge-holding-hope` **READ** `out/mock-demo-mg/rounds/holding-hope-r0-draft.json` (1011 B, sha256:8b3ea6419d15b678)
- `mg-judge-holding-hope` MOCK replay <- `tests/fixtures/minigame/` (verdict FAIL)
- `mg-judge-holding-hope` **WRITE** `out/mock-demo-mg/rounds/holding-hope-r0-findings.json` (401 B, sha256:27efd3d4ea147c3b)
- `mg-refiner-holding-hope` MOCK replay <- `tests/fixtures/minigame/` (refined design round 1)
- `mg-refiner-holding-hope` **WRITE** `out/mock-demo-mg/rounds/holding-hope-r1-draft.json` (1196 B, sha256:c1823f08eab2da25)
- `mg-judge-holding-hope` **READ** `out/mock-demo-mg/rounds/holding-hope-r1-draft.json` (1196 B, sha256:c1823f08eab2da25)
- `mg-judge-holding-hope` MOCK replay <- `tests/fixtures/minigame/` (verdict PASS)
- `mg-judge-holding-hope` **WRITE** `out/mock-demo-mg/rounds/holding-hope-r1-findings.json` (81 B, sha256:00aa3c55e495cb48)
- `mg-holding-hope` **ACCEPTED** at round 1 (1 refinement(s))
- `retriever-holding-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 12.04), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 9.56), `minigame-patterns.md §sec-8` (bm25 38.10)
- `mg-designer-holding-fear` MOCK replay <- `tests/fixtures/minigame/` (design)
- `mg-designer-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r0-draft.json` (952 B, sha256:44d9559bba57197e)
- `mg-judge-holding-fear` **READ** `out/mock-demo-mg/rounds/holding-fear-r0-draft.json` (952 B, sha256:44d9559bba57197e)
- `mg-judge-holding-fear` layer-1 design gate: **1 finding(s)** (round 0) — design never reached the LLM judge
- `mg-judge-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r0-findings.json` (333 B, sha256:04d4b74af9ef7cbb)
- `mg-refiner-holding-fear` MOCK replay <- `tests/fixtures/minigame/` (refined design round 1)
- `mg-refiner-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r1-draft.json` (916 B, sha256:3ae77ae7de43f25c)
- `mg-judge-holding-fear` **READ** `out/mock-demo-mg/rounds/holding-fear-r1-draft.json` (916 B, sha256:3ae77ae7de43f25c)
- `mg-judge-holding-fear` layer-1 design gate: **1 finding(s)** (round 1) — design never reached the LLM judge
- `mg-judge-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r1-findings.json` (382 B, sha256:19db1efdd3d79d2b)
- `mg-refiner-holding-fear` MOCK replay <- `tests/fixtures/minigame/` (refined design round 2)
- `mg-refiner-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r2-draft.json` (898 B, sha256:269a9b10850ea2ef)
- `mg-judge-holding-fear` **READ** `out/mock-demo-mg/rounds/holding-fear-r2-draft.json` (898 B, sha256:269a9b10850ea2ef)
- `mg-judge-holding-fear` layer-1 design gate: **1 finding(s)** (round 2) — design never reached the LLM judge
- `mg-judge-holding-fear` **WRITE** `out/mock-demo-mg/rounds/holding-fear-r2-findings.json` (334 B, sha256:db33cda23b60b72c)
- `circuit-breaker` `holding-fear` **ESCALATED** — 2 refinement round(s) spent, still failing (C3 BUILDABLE-INPUT)

## Stage 3 — assembly

Candidates document + evidence. Deterministic; no LLM. The run ENDS here, at the Director gate.
- `assemble` **WRITE** `out/mock-demo-mg/MINIGAME-CANDIDATES.md` (8675 B, sha256:33a718e28ec14ae4)
- `assemble` **WRITE** `out/mock-demo-mg/CANDIDATES.json` (6512 B, sha256:a1738538cce3bed7)
- `assemble` **WRITE** `out/mock-demo-mg/MG-GER-LOG.md` (4085 B, sha256:ac85b6540910485a)
- `assemble` **WRITE** `out/mock-demo-mg/MG-ESCALATED.md` (1772 B, sha256:c99176e18e1299bf)

**Propose run complete.** Nothing was built. The Director rules in MINIGAME-CANDIDATES.md, then:
`python3 run_minigame.py --build --select <id> --from-run mock-demo-mg`
