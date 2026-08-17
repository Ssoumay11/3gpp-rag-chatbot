from __future__ import annotations

import sys

from src.retrieval.diagnostics import (
    summarize_results,
)
from src.retrieval.embedder import BGEEmbedder
from src.retrieval.qdrant_store import QdrantStore
from src.retrieval.retrieval_config import (
    RetrievalConfig,
)
from src.retrieval.retriever import (
    ThreeGPPRetriever,
)


def print_result(
    result,
) -> None:

    print("\n" + "-" * 70)

    print(
        f"Rank: {result.rank}"
    )

    print(
        f"Score: {result.score:.4f}"
    )

    print(
        f"Chunk: {result.chunk_id}"
    )

    print(
        f"Specification: "
        f"{result.specification}"
    )

    print(
        f"Version: {result.version}"
    )

    print(
        f"Section: "
        f"{result.section_number} "
        f"{result.section_title}"
    )

    print(
        f"Pages: "
        f"{result.page_start} - "
        f"{result.page_end}"
    )

    print(
        f"Content type: "
        f"{result.content_type}"
    )

    preview = result.text.replace(
        "\n",
        " ",
    )

    if len(preview) > 700:
        preview = (
            preview[:700]
            + "..."
        )

    print(
        f"Evidence:\n{preview}"
    )


def main() -> None:

    if len(sys.argv) < 2:

        print(
            'Usage:\n'
            'python scripts/test_retrieval.py '
            '"your question"'
        )

        return

    query = " ".join(
        sys.argv[1:]
    )

    embedder = BGEEmbedder()

    store = QdrantStore()

    retriever = ThreeGPPRetriever(
        embedder=embedder,
        store=store,
        config=RetrievalConfig(
            candidate_k=15,
            top_k=5,
        ),
    )

    results = retriever.retrieve_top_k(
        query
    )

    print("=" * 70)
    print("3GPP RETRIEVAL TEST")
    print("=" * 70)

    print(
        f"\nQuestion:\n{query}"
    )

    if not results:

        print(
            "\nNo results returned."
        )

        return

    diagnostics = summarize_results(
        results
    )

    print(
        "\nRetrieval diagnostics:"
    )

    print(
        f"Results: "
        f"{diagnostics['count']}"
    )

    print(
        f"Best score: "
        f"{diagnostics['best_score']:.4f}"
    )

    print(
        f"Worst score: "
        f"{diagnostics['worst_score']:.4f}"
    )

    print(
        f"Average score: "
        f"{diagnostics['average_score']:.4f}"
    )

    for result in results:
        print_result(result)


if __name__ == "__main__":
    main()