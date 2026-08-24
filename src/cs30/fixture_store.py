"""Process-local hand-off used only by the Week 1 fixture index."""

import uuid

from cs30.contracts import Chunk, IndexArtifact
from cs30.errors import IndexUnavailableError

_INDEXES: dict[str, list[Chunk]] = {}


def store_fixture_index(chunks: list[Chunk]) -> IndexArtifact:
    """Store fixture chunks and return the manifest used to retrieve them."""

    artifact_id = f"fixture-index-{uuid.uuid4().hex}"
    _INDEXES[artifact_id] = list(chunks)
    return IndexArtifact(
        artifact_id=artifact_id,
        index_type="fixture-lexical",
        location=f"memory://fixture-index/{artifact_id}",
        chunk_count=len(chunks),
        metadata={"embedding_model": "none", "persistence": "process-local"},
    )


def load_fixture_index(artifact: IndexArtifact) -> list[Chunk]:
    """Resolve a fixture manifest to the chunks stored in this process."""

    expected_location = f"memory://fixture-index/{artifact.artifact_id}"
    if artifact.location != expected_location:
        raise IndexUnavailableError(
            f"fixture retriever cannot load index artifact: {artifact.location}"
        )
    try:
        chunks = _INDEXES[artifact.artifact_id]
    except KeyError as exc:
        raise IndexUnavailableError(
            f"fixture index is unavailable in this process: {artifact.artifact_id}"
        ) from exc
    if len(chunks) != artifact.chunk_count:
        raise IndexUnavailableError("fixture index manifest does not match stored chunks")
    return list(chunks)
