# Member 6 - dense retrieval and backend API

Implement `cs30.ports.Retriever`:

    `load_index(artifact: IndexArtifact) -> None`
    `retrieve(query: str, top_k: int) -> RetrievalResult`

`CombinedEvidenceRetriever` is the portable local implementation currently
wired into `build_real_deps()`. It searches all evidence supplied by the
original fixture, packaged Member 3 SciQ data, and locally available SciQ rows.
It uses weighted concept-term coverage with a minimum match threshold and can
later be replaced by Member 6's dense retriever without changing this interface.

## Week 1 acceptance

- A question reliably returns Top-K chunks.
- Results carry textbook source and chunk id.
- Member 7 can build a prompt straight from the result.
- Bad index or input returns a clear error instead of exiting.

## Notes

Finding nothing is NOT an error: return `RetrievalResult` with an empty
`hits` list and let the generator abstain. Reserve exceptions
(`IndexUnavailableError`, `EmptyQueryError`) for genuine failures.

The combined retriever is an engineering integration path, not a retrieval
quality result. Multi-term questions must match at least two meaningful terms,
which prevents single-word accidents such as `painted` matching a chemistry
passage about protective paint.
