from dataclasses import dataclass

from qdrant_client.models import Distance


@dataclass(frozen=True)
class QdrantConfig:
    url: str = "http://localhost:6333"

    collection_name: str = "3gpp_documents"

    vector_size: int = 384

    distance: Distance = Distance.COSINE

    upsert_batch_size: int = 64