# Member 4 - chunking and metadata

Implement `cs30.ports.Chunker`:

    `chunk(document: OpenStaxDocument) -> list[Chunk]`

Drop the real implementation next to `fixture.py`. The Leader supplies it as the
`chunker` field of `BuildDeps`; `run_build_pipeline()` itself does not change.

## Week 1 acceptance

- Every chunk has a unique id and a chapter source.
- Chunk text can be located back in the normalised document.
- No empty chunks and no cross-chapter mixing.
- Output feeds member 6 directly.

## Notes

The contract enforces `len(text) == char_end - char_start`, so a wrong span
fails at construction instead of at demo time. `Chunk.metadata` accepts
string values only: use `{"section": "1"}`, not `{"section": 1}`.
