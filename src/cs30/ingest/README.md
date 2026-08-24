# Member 2 - OpenStax data engineering

Implement `cs30.ports.DocumentParser`:

    `parse(source: Path) -> OpenStaxDocument`

Drop the real implementation next to `fixture.py`. The Leader supplies it as the
`parser` field of `BuildDeps`; `run_build_pipeline()` itself does not change.

## Week 1 acceptance

- Same input reproduces byte-identical normalised text.
- Chapters, titles, and body text are not misaligned.
- Record `document_hash` and `parser_version` on every document.
- Any demo chunk can be traced back to the textbook.

## Notes

`OpenStaxDocument.text` is never stripped by the contract layer: it is the
coordinate system every char span refers to. Emit it exactly as the parser
produced it, and never re-normalise it later without bumping
`parser_version` and regenerating chunks and indexes.
