# CS-30 Personalised RAG

Semester-long capstone repository for a personalised AI learning assistant
using Retrieval-Augmented Generation and Large Language Models. It contains
the system implementation, experiments, documentation, and final delivery
assets for the complete CS-30 project.

The current milestone is `v0.1-thin-slice`: a small OpenStax Physics path used
to validate the engineering workflow. It does not report formal retrieval or
model-effectiveness results.

## Repository scope

This is the single source repository for the whole project, including:

1. Week 1 thin-slice integration and staging demo.
2. Dataset preparation, Evidence Alignment, and evaluation infrastructure.
3. Dense and hybrid retrieval experiments.
4. Student profiles, personalised retrieval, and personalised prompting.
5. Reliability controls, citation checks, and calibrated abstention.
6. Optional restricted knowledge-graph extensions.
7. Multi-model experiments, analysis, LaTeX report, and final demonstration.

## Week 1 scope

```text
OpenStax chapter
-> normalised document
-> 500-token chunks
-> embedding and FAISS dense retrieval
-> student profile
-> personalised prompt
-> fixed JSON answer
-> citation integrity check
-> demo interface
```

Until GPU and model access are confirmed, the repository provides validated
contracts, fixtures, and a mock end-to-end pipeline so all modules can be built
in parallel.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m cs30.pipeline --question "What is acceleration?" --level beginner
python -m pytest
```

The mock command must return a JSON object containing the question, selected
student level, Top-K evidence, generated answer, and verified citations.

## Repository layout

```text
src/cs30/contracts/     Frozen cross-module schemas
src/cs30/pipeline.py    Unified mock/real pipeline entry point
configs/                Development and staging configuration
tests/fixtures/         Small, non-sensitive integration fixtures
tests/                  Contract and smoke tests
docs/adr/               Architecture decision records
data/raw/               Local source data; ignored by Git
indexes/                Local FAISS indexes; ignored by Git
```

## Collaboration rules

1. Do not commit directly to `main`; use a short-lived branch and Pull Request.
2. Every module must accept and return the schemas in `src/cs30/contracts`.
3. Submit a small working sample before scaling to the full Week 1 target.
4. Do not commit API keys, private student data, full model files, or indexes.
5. A change is mergeable only when tests pass and the mock pipeline still runs.

## Current interfaces

The first contract version includes:

- `OpenStaxDocument`
- `Chunk`
- `SciQQuestion`
- `RetrievalResult`
- `StudentProfile`
- `GeneratedAnswer`

See [docs/interfaces.md](docs/interfaces.md) for ownership and field semantics.
