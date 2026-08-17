from src.retrieval.embedder import BGEEmbedder


def main() -> None:
    embedder = BGEEmbedder()

    texts = [
        (
            "TS 23.501 V17.6.0 | "
            "Section 4.2 | Network Functions\n\n"
            "The AMF provides registration and connection "
            "management functionality."
        ),
        (
            "TS 33.501 V17.6.0 | "
            "Security architecture\n\n"
            "The 5G system provides security mechanisms."
        ),
    ]

    vectors = embedder.encode(texts)

    print("=" * 60)
    print("Embedding test")
    print("=" * 60)

    print(f"Number of vectors: {len(vectors)}")
    print(f"Vector dimension: {len(vectors[0])}")

    print(
        f"Expected dimension: "
        f"{embedder.dimension()}"
    )

    print("\nFirst 5 values:")
    print(vectors[0][:5])


if __name__ == "__main__":
    main()