"""Runtime citation-integrity checks."""

from cs30.contracts import GeneratedAnswer, RetrievalResult
from cs30.errors import CitationIntegrityError


def validate_citations(answer: GeneratedAnswer, retrieval: RetrievalResult) -> None:
    """Raise when an answer cites a chunk not supplied by retrieval."""

    allowed = {hit.chunk_id for hit in retrieval.hits}
    invalid = sorted(set(answer.citations) - allowed)
    if invalid:
        raise CitationIntegrityError(
            f"answer contains unknown citation IDs: {', '.join(invalid)}"
        )
