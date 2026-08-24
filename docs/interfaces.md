# Week 1 core interface contract

Contract version: `1.0` (revised 2026-08-24 before module development began —
see [ADR-0001](adr/0001-week1-thin-slice.md))

All cross-module payloads must be validated by the Pydantic models in
`src/cs30/contracts`. Unknown fields are rejected to expose interface drift.

## Character-span convention

`char_start` is inclusive and `char_end` is exclusive, matching Python slicing:

```python
assert document.text[chunk.char_start:chunk.char_end] == chunk.text
```

Spans refer to the normalised document text produced by the frozen parser
version. Changing normalisation requires a new `parser_version` and document
hash, followed by chunk and index regeneration.

`Chunk` enforces `len(text) == char_end - char_start` at construction, so a
mismatched span fails immediately instead of surfacing during a demo.

## String handling: two kinds of field

The contract layer **never rewrites text that a span points at**.

| Kind | Fields | Behaviour |
|---|---|---|
| `SpanText` | `OpenStaxDocument.text`, `Chunk.text`, `RetrievalHit.text` | Kept verbatim. Never stripped — stripping would move the text without moving the offsets |
| `Identifier` | all `*_id`, `source`, `version`, `document_hash`, `parser_version`, citation entries | Surrounding whitespace removed, so `"ch01 "` and `"ch01"` cannot become two chapters |
| `NonEmptyText` | `question`, `support`, `explanation`, `title` | Stripped; no span semantics |

This distinction is about whether a pair of offsets points at the string. It is
not about content type: figures and formulas are a separate question, tracked as
R3 in the team planning materials maintained outside GitHub.

## No evidence, and refusal

Both are first-class outcomes, not errors:

- `RetrievalResult.hits` may be empty. Retrieval ran and found nothing relevant.
  Reserve exceptions (`IndexUnavailableError`, `EmptyQueryError`) for genuine
  failures.
- `GeneratedAnswer` may set `abstained=True`, which requires no `final_choice`
  and no citations. Conversely a non-abstained answer **must** cite at least one
  chunk, so an ungrounded claim cannot be constructed.

`cs30.citation.validate_citations` then rejects any citation that retrieval did
not return.

## Metadata fields

`Chunk.metadata` and `PipelineRun.metadata` are `dict[str, str]`: **string
values only**. Use `{"section": "1"}`, not `{"section": 1}`.

## Ownership

| Contract | Producer | Primary consumers |
|---|---|---|
| `OpenStaxDocument` | Member 2 | Member 4, Leader |
| `Chunk` | Member 4 | Members 5 and 6 |
| `IndexArtifact` | Member 5 | Member 6 |
| `SciQQuestion` | Member 3 | Members 6 and 7 |
| `RetrievalResult` | Member 6 | Member 7, Leader |
| `StudentProfile` | Member 7 / UI | Prompt builder |
| `GeneratedAnswer` | Member 7 | UI, citation checker |
| `PipelineRun` | Leader | Member 8, ablation table |

Member numbers follow the week 1 division of labour held in the team Drive.

## Module seams

Computational modules implement Protocols from `src/cs30/ports.py`. Members 2,
4, and 5 are orchestrated by `BuildDeps` / `run_build_pipeline()`; members 6 and
7 are orchestrated by `PipelineDeps` / `run_pipeline()`. Member 3 supplies
validated questions through `QuestionProvider`. Member 8 consumes `PipelineRun`
directly. See each module package's `README.md` for its acceptance criteria.

`IndexArtifact` is the explicit hand-off between index building and retrieval.
It records the index type, stable location, chunk count, and implementation
metadata. A retriever must accept it through `load_index()` before querying the
corresponding real index. The fixture implementation uses a process-local
`memory://` location; real adapters must use a persistent location that another
process can reopen.

`validate_citations()` raises `CitationIntegrityError` when generated citations
are not present in the retrieval result. Because it derives from `CS30Error`,
the command-line boundary reports the problem cleanly instead of leaking a
traceback.

## Integration gate

Every Pull Request crossing a module boundary must include:

1. A payload that validates against the relevant contract.
2. A small fixture or test covering the new behaviour.
3. Explicit errors for missing inputs rather than process termination.
4. A successful run of the end-to-end pipeline.

## Changing a contract

1. Raise it with the Leader; `CODEOWNERS` routes `src/cs30/contracts/` changes.
2. If any module already produces stored data in the old shape, bump
   `schema_version` and state the migration. Before that point, revise in place
   and record the revision in the ADR.
3. Update the packaged fixtures and this document in the same Pull Request.
