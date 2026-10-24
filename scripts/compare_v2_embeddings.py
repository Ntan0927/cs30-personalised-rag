import argparse
from pathlib import Path

from huggingface_hub import HfApi

from cs30.indexing.embedding_models import EMBEDDING_MODELS
from cs30.v2.contracts import Chunk
from cs30.v2.corpus.manifest import load_corpus_manifest
from cs30.v2.indexing import build_faiss_index_builder

DEFAULT_CORPUS_DIR = Path(
    "artifacts/v2/m4-four-book"
)

SMOKE_OUTPUT_ROOT = Path(
    "artifacts/dev/v2-m5-four-book-candidates"
)


def resolve_model_revision(model_name: str) -> str:
    """Resolve a Hugging Face model to an immutable commit SHA."""

    info = HfApi().model_info(model_name)

    if not info.sha:
        raise RuntimeError(
            f"Could not resolve model revision for {model_name}"
        )

    return info.sha


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
    corpus_dir: Path,
) -> None:
    config = EMBEDDING_MODELS[model_id]

    output_dir = SMOKE_OUTPUT_ROOT / model_id
    manifest = load_corpus_manifest(
        corpus_dir / "manifest.json"
    )

    revision = resolve_model_revision(config.model_name)

    builder = build_faiss_index_builder(
        model_name=config.model_name,
        revision=revision,
        batch_size=config.batch_size,
    )

    print(f"Model ID: {model_id}")
    print(f"Model: {config.model_name}")
    print(f"Chunks: {len(chunks)}")
    print(f"Output: {output_dir}")
    print(f"Batch size: {config.batch_size}")
    print(f"Model revision: {revision}")
    print(f"Corpus version: {manifest.corpus_version}")
    print(f"Corpus hash: {manifest.corpus_hash}")
    print(f"Manifest hash: {manifest.manifest_hash}")
    print(f"Chunk config hash: {manifest.chunk_config_hash}")

    artifact = builder.build(
        chunks,
        manifest,
        output_dir=output_dir,
    )
    artifact_path = output_dir / "artifact.json"
    artifact_path.write_text(
        artifact.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print(f"Artifact ID: {artifact.artifact_id}")
    print(f"Chunk count: {artifact.chunk_count}")
    print(f"Embedding dimension: {artifact.embedding_dimension}")
    print("v2 index build passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        choices=EMBEDDING_MODELS.keys(),
    )

    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=DEFAULT_CORPUS_DIR,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Validate only the first N v2 chunks. "
            "When set, no FAISS artifact is built."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    records_path = args.corpus_dir / "records.jsonl"

    chunks = load_chunks(
        records_path,
        limit=args.limit,
    )

    if not chunks:
        raise RuntimeError(
            f"No chunks loaded from {records_path}"
        )

    if args.limit is not None:
        print(f"Validated {len(chunks)} v2 chunks.")
        print("Schema/load smoke passed.")
        print(
            "FAISS build skipped because a subset must not "
            "be bound to the full corpus manifest."
        )
        return

    build_model(
        args.model,
        chunks,
        args.corpus_dir,
    )


if __name__ == "__main__":
    main()