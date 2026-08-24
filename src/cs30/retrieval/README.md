# Member 6 - dense retrieval and backend API

Implement `cs30.ports.Retriever`:

    `load_index(artifact: IndexArtifact) -> None`
    `retrieve(query: str, top_k: int) -> RetrievalResult`

Drop the real implementation next to `fixture.py`, then swap it into
`build_real_deps()` in `src/cs30/pipeline.py`. Nothing else changes.

## Week 1 acceptance

- A question reliably returns Top-K chunks.
- Results carry textbook source and chunk id.
- Member 7 can build a prompt straight from the result.
- Bad index or input returns a clear error instead of exiting.

## Notes

Finding nothing is NOT an error: return `RetrievalResult` with an empty
`hits` list and let the generator abstain. Reserve exceptions
(`IndexUnavailableError`, `EmptyQueryError`) for genuine failures.
