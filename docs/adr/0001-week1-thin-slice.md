# ADR-0001: Week 1 thin-slice architecture

- Status: Accepted for Week 1
- Target version: `v0.1-thin-slice`
- Scope: Engineering path validation only

## Context

The team needs a runnable client demonstration while GPU, model access, and the
final supervisor-provided dataset remain unresolved. Waiting for those decisions
would block interface, parsing, chunking, integration, and UI work.

## Decision

1. Use one small OpenStax Physics chapter as a temporary technical fixture.
2. Freeze version 1.0 cross-module contracts before full module development.
3. Use 500-token chunking, one future embedding model, and FAISS `IndexFlatIP`.
4. Provide mock retrieval and generation adapters until real services are ready.
5. Support beginner, intermediate, and advanced profile levels from the start.
6. Require generated citations to be a subset of retrieved chunk IDs.
7. Keep the main branch runnable throughout the week.

## Explicitly out of scope

- Formal Evidence Alignment and gold-span annotation
- Hit@K, Recall@K, MRR, or answer-accuracy conclusions
- Formal Dev/Test splits
- BM25/RRF comparisons
- Abstention calibration, restricted KG, and multi-model comparison

## Revision, 2026-08-24 (before module development began)

Version 1.0 was revised in place rather than superseded, because no module yet
produced data in the old shape. Three defects made the original shape unusable:

1. **Contract-level whitespace stripping broke the character-span invariant.**
   The base model normalised every string, so a chunk whose text began or ended
   with whitespace was silently shortened while its offsets were not, and
   validation still passed. Text bound to a span is now kept verbatim; only
   identifiers and span-free free text are normalised, and `Chunk` asserts
   `len(text) == char_end - char_start`.

2. **The contract could not express "no evidence" or "cannot answer".**
   `RetrievalResult.hits` and `GeneratedAnswer.citations` both required at least
   one entry, so retrieval could not report an empty result and the generator
   could not refuse. Refusal is a stated goal of the project, so both lists may
   now be empty, and `GeneratedAnswer.abstained` distinguishes a refusal from an
   ungrounded answer. A non-abstained answer must still cite evidence.

3. **The index builder had no explicit hand-off to retrieval.** `build()` and
   `load()` returned nothing, so members 5 and 6 could not agree on which index,
   chunk map, or configuration was being used. Both now return an
   `IndexArtifact`, and `Retriever.load_index()` accepts that manifest.

`PipelineRun` was added at the same time to carry run metadata, so a later
ablation-table row can be traced back to the configuration that produced it.

Freezing exists to stop churn during development, not to preserve a defect
discovered before development started.

## Consequences

The team can develop in parallel against fixtures and replace adapters without
changing public payloads. The Week 1 demo cannot be used to claim that a model,
embedding, or retrieval method performs better.

