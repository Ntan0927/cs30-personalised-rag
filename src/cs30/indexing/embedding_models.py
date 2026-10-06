from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingModelConfig:
    """Configuration for a supported embedding model."""

    model_name: str
    batch_size: int
    query_instruction: str = ""
    passage_prefix: str = ""
    trust_remote_code: bool = False


EMBEDDING_MODELS = {
    "bge-m3": EmbeddingModelConfig(
        model_name="BAAI/bge-m3",
        batch_size=4,
    ),
    "gte-modernbert": EmbeddingModelConfig(
        model_name="Alibaba-NLP/gte-modernbert-base",
        batch_size=4,
    ),
    "qwen3-embedding": EmbeddingModelConfig(
        model_name="Qwen/Qwen3-Embedding-0.6B",
        batch_size=2,
    ),
}