from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from .qdrant_config import QdrantConfig


class QdrantStore:
    """
    Qdrant storage and retrieval layer.
    """

    def __init__(
        self,
        config: QdrantConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else QdrantConfig()
        )

        print(
            f"[Qdrant] Connecting to "
            f"{self.config.url}"
        )

        self.client = QdrantClient(
            url=self.config.url
        )

    def collection_exists(self) -> bool:
        return self.client.collection_exists(
            self.config.collection_name
        )

    def create_collection(self) -> None:

        if self.collection_exists():

            print(
                f"[Qdrant] Collection already exists: "
                f"{self.config.collection_name}"
            )

            return

        self.client.create_collection(
            collection_name=(
                self.config.collection_name
            ),
            vectors_config=VectorParams(
                size=self.config.vector_size,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"[Qdrant] Created collection: "
            f"{self.config.collection_name}"
        )

    def upsert(
        self,
        points: list[PointStruct],
    ) -> None:

        if not points:
            return

        self.client.upsert(
            collection_name=(
                self.config.collection_name
            ),
            points=points,
            wait=True,
        )

    def count(self) -> int:

        result = self.client.count(
            collection_name=(
                self.config.collection_name
            ),
            exact=True,
        )

        return result.count

    def info(self) -> Any:

        return self.client.get_collection(
            collection_name=(
                self.config.collection_name
            )
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
        specification: str | None = None,
    ) -> list[Any]:
        """
        Dense semantic retrieval.

        An optional exact specification filter can be applied,
        e.g. TS 23.501.
        """

        query_filter = None

        if specification:

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="specification",
                        match=MatchValue(
                            value=specification
                        ),
                    )
                ]
            )

        result = self.client.query_points(
            collection_name=(
                self.config.collection_name
            ),
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        return result.points