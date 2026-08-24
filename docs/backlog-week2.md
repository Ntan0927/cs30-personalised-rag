# Week 2 backlog

Ordering follows the project rule in `CLAUDE.md`: **an evaluation set exists
before any optimisation is attempted.** Without a baseline, every later
"improvement" is unfalsifiable.

## Must land before any tuning

| # | Item | Owner | Depends on | Done when |
|---|---|---|---|---|
| B1 | Confirm the supervisor corpus: form, language, size, structure, whether Q&A pairs ship with it | Leader | — | R1 closed; embedding and parser choices unblocked |
| B2 | Confirm GPU / model access; decide local vs API per model | Leader | — | R2 closed; multi-model comparison is schedulable |
| B3 | Evidence Alignment: map SciQ `support` to OpenStax char spans | M3 + M2 | B1 | Answerable set produced; unalignable items listed, not silently dropped |
| B4 | Evaluation set, 30–50 pairs: gold answer, gold support span, difficulty tier | M3 | B3 | Covers several chapters and all three levels |
| B5 | Dev/Test split isolated by chapter or concept group, never random | Leader + M3 | B4 | Split is reproducible and documented |

## Real modules replacing fixtures

| # | Item | Owner | Done when |
|---|---|---|---|
| B6 | Real OpenStax parsing for 2–3 chapters | M2 | Byte-identical re-parse; 10+ passages hand-checked |
| B7 | Real 500-token chunking with metadata | M4 | Span invariant holds across the whole corpus |
| B8 | Real embeddings + FAISS `IndexFlatIP`, save/load | M5 | Index rebuilds identically; build/load returns a valid `IndexArtifact` |
| B9 | Real dense retriever behind the `Retriever` protocol | M6 | Loads member 5's `IndexArtifact`; `build_real_deps()` swaps it in; empty results still abstain |
| B10 | Real LLM adapter with JSON schema validation and retries | M7 | 10–20 questions end to end; one API failure does not abort the batch |
| B11 | Demo interface on `PipelineRun` | M8 | Level selector, question box, answer, sources, visible mode banner |

## Measurement infrastructure

| # | Item | Owner | Done when |
|---|---|---|---|
| B12 | Retrieval metrics: Hit@K, Recall@K, MRR against gold spans | M6 + Leader | Reproducible from a single command |
| B13 | Ablation harness: one run per knob setting, `PipelineRun.metadata` into one table row | Leader | A table row can be traced back to its exact configuration |
| B14 | Personalisation evaluation dimensions (explanation depth match, skipped steps, unexplained jargon) | Leader + M7 | Rubric agreed before more personalisation is built — see R9 |

## Engineering debt

| # | Item | Owner |
|---|---|---|
| B15 | Dependency lock file (R7) | M8 |
| B16 | Branch protection on `main`; stop direct pushes (R8) | Leader |
| B17 | Contract v1.1 decision on non-text content, only after B1 (R3) | Leader |
| B18 | Add `document_id` to `RetrievalHit` before a second document enters the corpus | Leader |

## Explicitly still out of scope

Restricted KG, level-aware reranking, calibrated abstention thresholds, and the
longitudinal student simulator. These stay parked until the retrieval and
evaluation baselines exist.
