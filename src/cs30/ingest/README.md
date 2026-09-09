# Member 2 - textbook catalogue and parsing boundary

The ingestion boundary implements `cs30.ports.DocumentParser`:

```python
parse(source: Path) -> TextbookDocument
```

`TextbookDocument` is the provider-neutral public name for the frozen v1.0
contract. `OpenStaxDocument` remains available as a compatibility name, so the
alias does not change the payload schema or the character-span convention.

`src/cs30/ingest/textbooks.py` is the source catalogue. It records the stable
textbook ID, display title, provider, source reference, subject, licence, and
identity markers needed by a later source adapter. The catalogue contains the
OpenStax College Physics 2e profile and the five physics-related CK-12 books
listed in SciQ Appendix A. It does not download or redistribute source files.

Textbook selection is configuration of a parser adapter. It is not an extra
argument to `DocumentParser.parse()`, which keeps the existing `BuildDeps` and
`run_build_pipeline()` seam stable. A later M2 build adapter can be configured
with a `textbook_id` and resolve its `TextbookSpec` through `get_textbook()`.

The exact local source file remains part of reproducibility. A real parser/build
PR must record its SHA-256, parser version, selected chapters, source URL,
and per-title QA results before the source is admitted to a frozen corpus.

## Interface acceptance

- Existing `OpenStaxDocument` fixtures continue to validate unchanged.
- Every catalogue entry has a stable ID, title, provider, source URL, subject,
  version label, licence, and non-empty identity markers.
- `TextbookDocument` and `TextbookChapter` remain runtime-compatible aliases.
- `cs30-list-textbooks` prints the catalogue as deterministic JSON.
- No source PDF, full corpus, model, or index is committed to the repository.

The provider-specific PDF parser and the offline `cs30-build` command belong to
a follow-up implementation PR. This PR establishes the names and metadata that
those adapters consume.
