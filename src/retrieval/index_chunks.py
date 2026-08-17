from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qdrant_client.models import PointStruct

from .embedder import BGEEmbedder
from .embedding_config import EmbeddingConfig
from .payload import build_payload
from .point_id import stable_point_id
from .qdrant_config import QdrantConfig
from .qdrant_store import QdrantStore


CHUNK_DIR = Path("data/chunks")


def load_chunks(
    path: Path,
) -> list[dict[str, Any]]:

    chunks: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                chunks.append(
                    json.loads(line)
                )

    return chunks


def build_points(
    chunks: list[dict[str, Any]],
    vectors: list[list[float]],
) -> list[PointStruct]:

    points: list[PointStruct] = []

    for chunk, vector in zip(
        chunks,
        vectors,
    ):

        chunk_id = chunk["chunk_id"]

        points.append(
            PointStruct(
                id=stable_point_id(
                    chunk_id
                ),
                vector=vector,
                payload=build_payload(
                    chunk
                ),
            )
        )

    return points


def process_file(
    chunk_path: Path,
    embedder: BGEEmbedder,
    store: QdrantStore,
) -> None:

    print("\n" + "=" * 70)
    print(
        f"Indexing: {chunk_path.name}"
    )
    print("=" * 70)

    chunks = load_chunks(
        chunk_path
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    batch_size = (
        embedder.config.batch_size
    )

    upsert_batch_size = (
        store.config.upsert_batch_size
    )

    total = len(chunks)

    for start in range(
        0,
        total,
        batch_size,
    ):

        end = min(
            start + batch_size,
            total,
        )

        batch = chunks[
            start:end
        ]

        texts = [
            chunk["embedding_text"]
            for chunk in batch
        ]

        vectors = embedder.encode(
            texts
        )

        # Split vector batch into Qdrant-sized
        # upsert batches.
        for q_start in range(
            0,
            len(batch),
            upsert_batch_size,
        ):

            q_end = min(
                q_start
                + upsert_batch_size,
                len(batch),
            )

            points = build_points(
                batch[q_start:q_end],
                vectors[q_start:q_end],
            )

            store.upsert(
                points
            )

        print(
            f"[Indexed] {end}/{total}"
        )

    print(
        f"[Done] {chunk_path.name}"
    )


def main() -> None:

    CHUNK_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunk_files = sorted(
        CHUNK_DIR.glob("*.jsonl")
    )

    if not chunk_files:

        print(
            "No chunk files found."
        )

        print(
            "Run Phase 3 first:"
        )

        print(
            "python -m src.ingestion.build_chunks"
        )

        return

    embedding_config = (
        EmbeddingConfig()
    )

    qdrant_config = (
        QdrantConfig()
    )

    embedder = BGEEmbedder(
        embedding_config
    )

    actual_dimension = (
        embedder.dimension()
    )

    if (
        actual_dimension
        != qdrant_config.vector_size
    ):

        raise RuntimeError(
            "Embedding dimension mismatch: "
            f"model={actual_dimension}, "
            f"Qdrant={qdrant_config.vector_size}"
        )

    store = QdrantStore(
        qdrant_config
    )

    store.create_collection()

    for chunk_file in chunk_files:

        process_file(
            chunk_file,
            embedder,
            store,
        )

    print("\n" + "=" * 70)
    print("Qdrant indexing complete")
    print("=" * 70)

    print(
        f"Collection: "
        f"{qdrant_config.collection_name}"
    )

    print(
        f"Vectors stored: "
        f"{store.count()}"
    )


if __name__ == "__main__":
    main()