"""Preliminary comparison of embedding models for the FAISS index."""

from __future__ import annotations

import time

from cs30.chunking import BlockAwareChunker
from cs30.contracts import OpenStaxDocument
from cs30.fixtures import load_fixture
from cs30.indexing import FaissIndexBuilder

MODELS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet": "sentence-transformers/all-mpnet-base-v2",
    "e5": "intfloat/e5-base-v2",
    "bge": "BAAI/bge-base-en-v1.5",
}


def main() -> None:
    document = OpenStaxDocument.model_validate(
        load_fixture("openstax_document.json")
    )

    chunks = BlockAwareChunker().chunk(document)

    print(f"Document: {document.title}")
    print(f"Chunks: {len(chunks)}")
    print()

    for short_name, model_name in MODELS.items():
        print("=" * 70)
        print(f"Model: {model_name}")

        builder = FaissIndexBuilder(
            model_name=model_name,
            index_dir=f"data/index/experiments/{short_name}",
        )

        started = time.perf_counter()
        artifact = builder.build(chunks)
        elapsed = time.perf_counter() - started

        print(f"Embedding dimension: {artifact.metadata['dimension']}")
        print(f"Build time: {elapsed:.4f} seconds")
        print(f"Artifact ID: {artifact.artifact_id}")
        print(f"Index location: {artifact.location}")

        loaded_artifact = builder.load()

        print(f"Reload successful: {loaded_artifact.artifact_id == artifact.artifact_id}")
        print()


if __name__ == "__main__":
    main()