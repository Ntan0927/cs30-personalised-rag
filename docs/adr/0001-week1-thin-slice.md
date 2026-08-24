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

## Consequences

The team can develop in parallel against fixtures and replace adapters without
changing public payloads. The Week 1 demo cannot be used to claim that a model,
embedding, or retrieval method performs better.

