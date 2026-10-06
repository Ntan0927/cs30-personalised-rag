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
        query_instruction="",
    ),
    "gte-modernbert": EmbeddingModelConfig(
        model_name="Alibaba-NLP/gte-modernbert-base",
        batch_size=4,
        query_instruction="",
    ),
    "qwen3-embedding": EmbeddingModelConfig(
        model_name="Qwen/Qwen3-Embedding-0.6B",
        batch_size=2,
        query_instruction=(
            "Instruct: Given a web search query, retrieve relevant passages "
            "that answer the query\nQuery:{query}"
        ),
    ),
}