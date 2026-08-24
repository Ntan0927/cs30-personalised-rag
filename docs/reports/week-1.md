# Client weekly report — Week 1

**Week:** 1 · **Version:** `v0.1-thin-slice` · **Date:** 2026-08-24

> **Scope caveat, stated up front.** Week 1 delivers an engineering path
> validation. It contains no formal evaluation, and nothing in it may be used
> to claim that any retrieval method, embedding, or model performs better than
> another.

## 1. Delivered this week

- **Frozen cross-module contracts** (`OpenStaxDocument`, `Chunk`,
  `SciQQuestion`, `RetrievalResult`, `StudentProfile`, `GeneratedAnswer`,
  `PipelineRun`) with strict validation: unknown fields are rejected, and the
  character-span invariant tying a chunk back to the textbook is enforced by
  the contract layer rather than by convention.
- **Runnable end-to-end pipeline** with a single command-line entry point,
  covering profile → retrieval → generation → citation integrity check.
- **Module seams and skeletons** for all seven downstream roles. Computational
  modules have Protocols and fixture stand-ins; member 8 consumes `PipelineRun`
  directly. Offline building and online answering have separate dependency
  groups, and `IndexArtifact` fixes the member 5 → member 6 hand-off.
- **Grounding and refusal enforced in code.** An answer citing a chunk that
  retrieval did not return is rejected. A question the evidence does not cover
  produces an explicit refusal rather than an unsupported answer.
- **Configuration, logging, and typed errors**; development and staging
  environments; CI running lint, tests on Python 3.11–3.13, and two behavioural
  gates on every push.

## 2. Not delivered, and why

- **Real parsing, chunking, embeddings, index, retrieval, and generation.** The
  supervisor corpus has not arrived and GPU/model access is unconfirmed (risks
  R1, R2). Rather than wait, the team built against fixtures behind frozen
  interfaces; each real module now replaces its fixture without touching the
  pipeline.
- **All formal evaluation** (Evidence Alignment, gold spans, Hit@K / Recall@K /
  MRR, answer accuracy, Dev/Test split, multi-model comparison). Out of scope by
  design — see ADR-0001.

## 3. Demonstration

Two questions through the same pipeline:

1. An in-scope question returns Top-K evidence with textbook sources, an
   explanation whose wording changes across beginner / intermediate / advanced,
   and citations verified against the retrieval input.
2. An out-of-scope question returns no evidence and an explicit refusal.

**This proves** the path runs, the interfaces hold, citations cannot be
fabricated, and the system can decline to answer. **It does not prove** anything
about retrieval or answer quality: retrieval here is a lexical stand-in and no
model is called.

## 4. Risks

| id | Risk | Status | Change |
|---|---|---|---|
| R1 | Supervisor corpus unknown | open | Blocking parser and embedding choices; sample requested |
| R2 | GPU / model access unconfirmed | open | Blocks week 2 real modules and all model comparison |
| R4 | Fixture output mistaken for real performance | mitigated | Mode flag, banner, and CI gate added |
| R8 | Direct pushes to `main` | open | Branch protection to be enabled |

Full register: [risks.md](../risks.md).

## 5. Decisions needed from the supervisor

1. The dataset: form, language, size, existing structure, and whether question
   and answer pairs ship with it.
2. GPU availability, which determines local inference versus API for the
   required Llama / Qwen / Gemma / GPT comparison.

## 6. Next week

Evidence Alignment and the 30–50 pair evaluation set come first; no retrieval
tuning starts before a baseline exists. Full list: [backlog-week2.md](../backlog-week2.md).
