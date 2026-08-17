from src.retrieval.bm25_index import BM25Index


def main() -> None:

    index = BM25Index()

    index.build()

    print(
        "BM25 index created successfully."
    )


if __name__ == "__main__":
    main()