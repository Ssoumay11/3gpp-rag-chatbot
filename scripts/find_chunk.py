from src.retrieval.qdrant_config import QdrantConfig
from src.retrieval.qdrant_store import QdrantStore


TARGET = "TS_33_501_V17_6_0_000122"


def main() -> None:

    config = QdrantConfig()
    store = QdrantStore(config)

    offset = None

    while True:

        points, offset = store.client.scroll(
            collection_name=(
                config.collection_name
            ),
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:

            payload = point.payload or {}

            if (
                payload.get("chunk_id")
                == TARGET
            ):

                print(
                    f"Chunk: {TARGET}"
                )

                print(
                    f"Specification: "
                    f"{payload.get('specification')}"
                )

                print(
                    f"Section number: "
                    f"{payload.get('section_number')}"
                )

                print(
                    f"Section title: "
                    f"{payload.get('section_title')}"
                )

                print(
                    f"Page: "
                    f"{payload.get('page_start')}"
                )

                print(
                    "\nText:"
                )

                print(
                    payload.get(
                        "text",
                        "",
                    )
                )

                return

        if offset is None:
            break

    print(
        f"Chunk not found: {TARGET}"
    )


if __name__ == "__main__":
    main()