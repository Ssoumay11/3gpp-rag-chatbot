from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str = "BAAI/bge-small-en-v1.5"

    # BGE-small-v1.5 = 384 dimensions.
    dimension: int = 384

    # BGE model supports up to 512 tokens.
    max_length: int = 512

    # Adjust this based on available RAM/CPU.
    batch_size: int = 16

    # Normalize vectors so cosine similarity behaves consistently.
    normalize_embeddings: bool = True

    # CPU is the safest default for your current setup.
    device: str = "cpu"