from __future__ import annotations

from src.retrieval.qdrant_store import (
    QdrantStore,
)


def check_qdrant() -> tuple[bool, str]:

    try:

        store = QdrantStore()

        if not store.collection_exists():

            return (
                False,
                "Qdrant collection does not exist.",
            )

        count = store.count()

        return (
            True,
            f"Qdrant OK — {count} vectors indexed.",
        )

    except Exception as exc:

        return (
            False,
            f"Qdrant unavailable: {exc}",
        )