from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingModelConfig:
    """Configuration for a supported embedding model."""

    model_name: str
    batch_size: int
    query_instruction: str = ""
    passage_prefix: str = ""


EMBEDDING_MODELS = {
    "bge-m3": EmbeddingModelConfig(
        model_name="BAAI/bge-m3",
        batch_size=4,
    ),
    "gte-modernbert": EmbeddingModelConfig(
        model_name="Alibaba-NLP/gte-modernbert-base",
        batch_size=4,
    ),
    "e5-mistral": EmbeddingModelConfig(
        model_name="intfloat/e5-mistral-7b-instruct",
        batch_size=1,
    ),
}