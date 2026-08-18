# RUN-LOG — mg-live

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
- `mg-designer-first-contact-hope` **WRITE** `out/mg-live/rounds/first-contact-hope-r0-draft.json` (2529 B, sha256:407614fd51100c5f)
- `mg-judge-first-contact-hope` **READ** `out/mg-live/rounds/first-contact-hope-r0-draft.json` (2529 B, sha256:407614fd51100c5f)
- `mg-judge-first-contact-hope` **WRITE** `out/mg-live/rounds/first-contact-hope-r0-findings.json` (87 B, sha256:0a2363899409e6c4)
- `mg-first-contact-hope` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-first-contact-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 21.28), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 9.68), `minigame-patterns.md §sec-6` (bm25 28.91)
- `mg-designer-first-contact-fear` **WRITE** `out/mg-live/rounds/first-contact-fear-r0-draft.json` (2544 B, sha256:bb4fe1cb4cb02495)
- `mg-judge-first-contact-fear` **READ** `out/mg-live/rounds/first-contact-fear-r0-draft.json` (2544 B, sha256:bb4fe1cb4cb02495)
- `mg-judge-first-contact-fear` **WRITE** `out/mg-live/rounds/first-contact-fear-r0-findings.json` (87 B, sha256:8d55f72788a8597b)
- `mg-first-contact-fear` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-vigil-hope` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 15.09), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 11.98), `minigame-patterns.md §sec-4` (bm25 40.94)
- `mg-designer-vigil-hope` **WRITE** `out/mg-live/rounds/vigil-hope-r0-draft.json` (2560 B, sha256:e7300ad7551838a6)
- `mg-judge-vigil-hope` **READ** `out/mg-live/rounds/vigil-hope-r0-draft.json` (2560 B, sha256:e7300ad7551838a6)
- `mg-judge-vigil-hope` **WRITE** `out/mg-live/rounds/vigil-hope-r0-findings.json` (79 B, sha256:49b2257d7ec5e511)
- `mg-vigil-hope` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-vigil-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 15.09), `minigame-patterns.md §sec-7` (bm25 22.61)
- `mg-designer-vigil-fear` **WRITE** `out/mg-live/rounds/vigil-fear-r0-draft.json` (2316 B, sha256:da6519db30f5b215)
- `mg-judge-vigil-fear` **READ** `out/mg-live/rounds/vigil-fear-r0-draft.json` (2316 B, sha256:da6519db30f5b215)
- `mg-judge-vigil-fear` **WRITE** `out/mg-live/rounds/vigil-fear-r0-findings.json` (703 B, sha256:70271b8e534f8a57)
- `mg-refiner-vigil-fear` **WRITE** `out/mg-live/rounds/vigil-fear-r1-draft.json` (2764 B, sha256:26746ced2f738c2a)
- `mg-judge-vigil-fear` **READ** `out/mg-live/rounds/vigil-fear-r1-draft.json` (2764 B, sha256:26746ced2f738c2a)
- `mg-judge-vigil-fear` **WRITE** `out/mg-live/rounds/vigil-fear-r1-findings.json` (79 B, sha256:3bcca4f808d22ca4)
- `mg-vigil-fear` **ACCEPTED** at round 1 (1 refinement(s))
- `retriever-holding-hope` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 12.04), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 11.67), `minigame-patterns.md §sec-5` (bm25 46.53)
- `mg-designer-holding-hope` **WRITE** `out/mg-live/rounds/holding-hope-r0-draft.json` (2805 B, sha256:2ccdd563b80fed96)
- `mg-judge-holding-hope` **READ** `out/mg-live/rounds/holding-hope-r0-draft.json` (2805 B, sha256:2ccdd563b80fed96)
- `mg-judge-holding-hope` **WRITE** `out/mg-live/rounds/holding-hope-r0-findings.json` (81 B, sha256:35feb1164883bcad)
- `mg-holding-hope` **ACCEPTED** at round 0 (0 refinement(s))
- `retriever-holding-fear` selected `uhta-gdd-v0.9.9-condensed.md §2` (bm25 12.04), `uhta-gdd-v0.9.7-full.md §2.2` (bm25 9.56), `minigame-patterns.md §sec-8` (bm25 38.10)
- `mg-designer-holding-fear` **WRITE** `out/mg-live/rounds/holding-fear-r0-draft.json` (2449 B, sha256:4bbe7d3cba906fd6)
- `mg-judge-holding-fear` **READ** `out/mg-live/rounds/holding-fear-r0-draft.json` (2449 B, sha256:4bbe7d3cba906fd6)
- `mg-judge-holding-fear` **WRITE** `out/mg-live/rounds/holding-fear-r0-findings.json` (81 B, sha256:e6b28309c90c3351)
- `mg-holding-fear` **ACCEPTED** at round 0 (0 refinement(s))

## Stage 3 — assembly

Candidates document + evidence. Deterministic; no LLM. The run ENDS here, at the Director gate.
- `assemble` **WRITE** `out/mg-live/MINIGAME-CANDIDATES.md` (20302 B, sha256:c673ffb14ce53d93)
- `assemble` **WRITE** `out/mg-live/CANDIDATES.json` (16314 B, sha256:41ce7517c2a95885)
- `assemble` **WRITE** `out/mg-live/MG-GER-LOG.md` (5376 B, sha256:48ab1b70db223648)

**Propose run complete.** Nothing was built. The Director rules in MINIGAME-CANDIDATES.md, then:
`python3 run_minigame.py --build --select <id> --from-run mg-live`
