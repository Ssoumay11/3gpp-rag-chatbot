from src.retrieval.qdrant_config import QdrantConfig
from src.retrieval.qdrant_store import QdrantStore


def main() -> None:

    config = QdrantConfig()

    store = QdrantStore(
        config
    )

    if store.collection_exists():

        store.client.delete_collection(
            collection_name=(
                config.collection_name
            )
        )

        print(
            f"Deleted collection: "
            f"{config.collection_name}"
        )

    store.create_collection()

    print(
        "Collection recreated."
    )


if __name__ == "__main__":
    main()