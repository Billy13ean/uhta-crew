# Content-pipeline fixtures (`--mock-llm`)

Canned text for the no-API-key mode. **Nothing here is real design work.**

- `writer-pool.json` — a pool of placeholder candidate lines. The mock Writer
  returns N of them, rotated by a stable hash of the agent label so different
  beats get different (still canned) sets.
- `critic-text.json` — the canned verdict text. The verdict *pattern* (which
  candidate positions fail, with which class) lives in `content/fixtures.py`
  and is documented there, because the Critic must return exactly one verdict
  per candidate and the candidate count is a CLI flag.

Every artifact a mock run writes carries a banner saying all of this, and
`manifest.json` records `"llm_backend": "mock"`.

The **retrieval** half of a mock run is real: chunking, the corpus policy and
BM25 ranking execute identically in every mode. Only the two LLM roles are
replaced.
