"""FAISS index builder for educational RAG chunks."""

from pathlib import Path
import json
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from cs30.contracts import Chunk, IndexArtifact
from cs30.errors import IndexUnavailableError


class FaissIndexBuilder:
    """Build, save, and load a FAISS dense vector index."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_dir: str = "data/index",
    ) -> None:
        self.model_name = model_name
        self.index_dir = Path(index_dir)

        # Load the embedding model.
        self.model = SentenceTransformer(model_name)

        # These are populated after build() or load().
        self._index = None
        self._chunks: list[Chunk] = []
        self._chunk_map: list[dict[str, object]] = []

    def _embed_chunks(self, chunks: list[Chunk]) -> np.ndarray:
        """Convert chunk.embedding_input values into embedding vectors."""

        # IMPORTANT:
        # Use embedding_input rather than chunk.text directly.
        # embedding_input uses embed_text when available and falls back
        # to the original chunk text otherwise.
        texts = [chunk.embedding_input for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return np.asarray(embeddings)

    def _build_faiss_index(
        self,
        embeddings: np.ndarray,
    ):
        """Build an IndexFlatIP index using L2-normalised embeddings."""

        # FAISS expects float32 vectors.
        embeddings = embeddings.astype("float32")

        # After L2 normalisation, inner product corresponds to
        # cosine similarity ranking.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        return index

    def _get_embedding_source(
        self,
        chunks: list[Chunk],
    ) -> str:
        """Describe whether text or enriched embed_text was embedded."""

        uses_embed_text = [
            chunk.embed_text is not None
            for chunk in chunks
        ]

        if all(uses_embed_text):
            return "embed_text"

        if not any(uses_embed_text):
            return "text"

        return "mixed"

    def build(
        self,
        chunks: list[Chunk],
    ) -> IndexArtifact:
        """Build and persist a FAISS index from chunks."""

        if not chunks:
            raise ValueError(
                "cannot build an index from zero chunks"
            )

        start_time = time.perf_counter()

        # ---------------------------------------------------------
        # 1. Convert chunk text into embedding vectors
        # ---------------------------------------------------------
        embeddings = self._embed_chunks(chunks)

        # ---------------------------------------------------------
        # 2. Build FAISS IndexFlatIP
        # ---------------------------------------------------------
        index = self._build_faiss_index(embeddings)

        self._chunks = list(chunks)
        self._index = index

        # ---------------------------------------------------------
        # 3. Prepare output directory
        # ---------------------------------------------------------
        self.index_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = self.index_dir / "index.faiss"
        chunk_map_path = self.index_dir / "chunks.json"
        artifact_path = self.index_dir / "artifact.json"

        # ---------------------------------------------------------
        # 4. Save FAISS index
        # ---------------------------------------------------------
        faiss.write_index(
            index,
            str(index_path),
        )

        # ---------------------------------------------------------
        # 5. Save vector position -> chunk_id mapping
        # ---------------------------------------------------------
        chunk_map = [
            {
                "position": position,
                "chunk_id": chunk.chunk_id,
            }
            for position, chunk in enumerate(chunks)
        ]

        self._chunk_map = chunk_map

        with chunk_map_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                chunk_map,
                file,
                indent=2,
            )

        # ---------------------------------------------------------
        # 6. Record build information
        # ---------------------------------------------------------
        build_time = time.perf_counter() - start_time

        device = str(self.model.device)

        embedding_source = self._get_embedding_source(
            chunks
        )

        artifact = IndexArtifact(
            artifact_id="faiss-index-v1",
            index_type="faiss-flat-ip",
            location=str(self.index_dir),
            chunk_count=len(chunks),
            metadata={
                "embedding_model": self.model_name,
                "dimension": str(embeddings.shape[1]),
                "device": device,
                "build_time_seconds": f"{build_time:.4f}",
                "index_file": str(index_path),
                "chunk_map": str(chunk_map_path),
                "embedding_source": embedding_source,
                "normalisation": "L2",
                "similarity": "inner_product",
            },
        )

        # ---------------------------------------------------------
        # 7. Save IndexArtifact manifest
        # ---------------------------------------------------------
        with artifact_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                artifact.model_dump_json(indent=2)
            )

        return artifact

    def load(self) -> IndexArtifact:
        """Load a previously saved FAISS index and metadata."""

        index_path = self.index_dir / "index.faiss"
        chunk_map_path = self.index_dir / "chunks.json"
        artifact_path = self.index_dir / "artifact.json"

        # ---------------------------------------------------------
        # Check that all required files exist
        # ---------------------------------------------------------
        if not index_path.exists():
            raise IndexUnavailableError(
                f"FAISS index not found: {index_path}"
            )

        if not chunk_map_path.exists():
            raise IndexUnavailableError(
                f"chunk map not found: {chunk_map_path}"
            )

        if not artifact_path.exists():
            raise IndexUnavailableError(
                f"index artifact not found: {artifact_path}"
            )

        try:
            # -----------------------------------------------------
            # 1. Restore FAISS index
            # -----------------------------------------------------
            self._index = faiss.read_index(
                str(index_path)
            )

            # -----------------------------------------------------
            # 2. Restore chunk_id mapping
            # -----------------------------------------------------
            with chunk_map_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                self._chunk_map = json.load(file)

            # -----------------------------------------------------
            # 3. Restore IndexArtifact
            # -----------------------------------------------------
            with artifact_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                artifact_data = json.load(file)

            artifact = IndexArtifact.model_validate(
                artifact_data
            )

        except Exception as exc:
            raise IndexUnavailableError(
                f"failed to load FAISS index: {exc}"
            ) from exc

        return artifact

    @property
    def index(self):
        """Return the loaded FAISS index."""

        if self._index is None:
            raise IndexUnavailableError(
                "index must be built or loaded before use"
            )

        return self._index

    @property
    def chunk_map(self) -> list[dict[str, object]]:
        """Return the FAISS position-to-chunk_id mapping."""

        if not self._chunk_map:
            raise IndexUnavailableError(
                "chunk map must be built or loaded before use"
            )

        return self._chunk_map
