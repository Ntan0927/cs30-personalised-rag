# Week 1 core interface contract

Contract version: `1.0`

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

## Ownership

| Contract | Producer | Primary consumers |
|---|---|---|
| `OpenStaxDocument` | Member 2 | Member 4, Leader |
| `Chunk` | Member 4 | Members 5 and 6 |
| `SciQQuestion` | Member 3 | Members 6 and 7 |
| `RetrievalResult` | Member 6 | Member 7, Leader |
| `StudentProfile` | Member 7 / UI | Prompt builder |
| `GeneratedAnswer` | Member 7 | UI, citation checker |

## Integration gate

Every Pull Request crossing a module boundary must include:

1. A payload that validates against the relevant contract.
2. A small fixture or test covering the new behaviour.
3. Explicit errors for missing inputs rather than process termination.
4. A successful run of the mock end-to-end pipeline.

