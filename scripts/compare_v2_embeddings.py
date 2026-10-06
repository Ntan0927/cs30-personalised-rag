import argparse
from pathlib import Path

from cs30.contracts import Chunk
from cs30.indexing.embedding_models import EMBEDDING_MODELS
from cs30.indexing.faiss_index import FaissIndexBuilder

DEFAULT_CORPUS = Path(
    "artifacts/w5/m4-v3/retrieval_corpus/records.jsonl"
)

SMOKE_OUTPUT_ROOT = Path(
    "artifacts/dev/v2-m5-smoke"
)


def load_chunks(
    records_path: Path,
    limit: int | None = None,
) -> list[Chunk]:
    chunks: list[Chunk] = []

    with records_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            chunks.append(
                Chunk.model_validate_json(line)
            )

            if limit is not None and len(chunks) >= limit:
                break

    return chunks


def build_model(
    model_id: str,
    chunks: list[Chunk],
) -> None:
    config = EMBEDDING_MODELS[model_id]

    output_dir = SMOKE_OUTPUT_ROOT / model_id

    builder = FaissIndexBuilder(
        model_name=config.model_name,
        index_dir=str(output_dir),
        batch_size=config.batch_size,
        query_instruction=config.query_instruction,
        passage_prefix=config.passage_prefix,
    
    )

    print(f"Model ID: {model_id}")
    print(f"Model: {config.model_name}")
    print(f"Chunks: {len(chunks)}")
    print(f"Output: {output_dir}")
    print(f"Batch size: {config.batch_size}")

    artifact = builder.build(chunks)

    print(f"Artifact ID: {artifact.artifact_id}")
    print(f"Chunk count: {artifact.chunk_count}")
    print("Smoke build passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        choices=EMBEDDING_MODELS.keys(),
    )

    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Number of chunks used for the smoke test.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    chunks = load_chunks(
        args.corpus,
        limit=args.limit,
    )

    if not chunks:
        raise RuntimeError(
            f"No chunks loaded from {args.corpus}"
        )

    build_model(
        args.model,
        chunks,
    )


if __name__ == "__main__":
    main()