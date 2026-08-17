from src.retrieval.qdrant_config import QdrantConfig
from src.retrieval.qdrant_store import QdrantStore


def main() -> None:

    config = QdrantConfig()

    store = QdrantStore(
        config
    )

    print("=" * 60)
    print("Qdrant Index Verification")
    print("=" * 60)

    print(
        f"Collection: {config.collection_name}"
    )

    print(
        f"Exists: {store.collection_exists()}"
    )

    print(
        f"Vector count: {store.count()}"
    )

    info = store.info()

    print("\nCollection info:")
    print(info)


if __name__ == "__main__":
    main()