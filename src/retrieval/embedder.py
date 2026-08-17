from __future__ import annotations

from typing import Sequence

from sentence_transformers import SentenceTransformer

from .embedding_config import EmbeddingConfig


class BGEEmbedder:
    """
    Local embedding engine using BAAI/bge-small-en-v1.5.
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else EmbeddingConfig()
        )

        print(
            f"[Embedding] Loading "
            f"{self.config.model_name}"
        )

        self.model = SentenceTransformer(
            self.config.model_name,
            device=self.config.device,
        )

        # Ensure the tokenizer does not exceed the model's
        # supported maximum sequence length.
        self.model.max_seq_length = (
            self.config.max_length
        )

        print(
            "[Embedding] Model loaded."
        )

    def encode(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        embeddings = self.model.encode(
            list(texts),
            batch_size=self.config.batch_size,
            normalize_embeddings=(
                self.config.normalize_embeddings
            ),
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        return embeddings.tolist()

    def dimension(self) -> int:
        return self.model.get_embedding_dimension()