"""In-memory stand-in for the FAISS index."""

from cs30.contracts import Chunk, IndexArtifact
from cs30.errors import IndexUnavailableError
from cs30.fixture_store import store_fixture_index


class FixtureIndexBuilder:
    """Hold chunks in memory so the retrieval seam can be exercised."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._loaded = False
        self._artifact: IndexArtifact | None = None

    def build(self, chunks: list[Chunk]) -> IndexArtifact:
        if not chunks:
            raise ValueError("cannot build an index from zero chunks")
        self._chunks = list(chunks)
        self._loaded = True
        self._artifact = store_fixture_index(chunks)
        return self._artifact

    def load(self) -> IndexArtifact:
        if not self._chunks or self._artifact is None:
            raise IndexUnavailableError("fixture index has not been built yet")
        self._loaded = True
        return self._artifact

    @property
    def chunks(self) -> list[Chunk]:
        if not self._loaded:
            raise IndexUnavailableError("index must be built or loaded before use")
        return self._chunks
