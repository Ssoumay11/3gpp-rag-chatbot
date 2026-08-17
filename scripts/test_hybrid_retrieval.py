from __future__ import annotations

import sys

from src.retrieval.bm25_index import BM25Index
from src.retrieval.embedder import BGEEmbedder
from src.retrieval.hybrid_config import (
    HybridRetrievalConfig,
)
from src.retrieval.hybrid_retriever import (
    Hybrid3GPPRetriever,
)
from src.retrieval.qdrant_store import (
    QdrantStore,
)
from src.retrieval.reranker import (
    BGEReranker,
)


def print_result(
    result,
) -> None:

    print("\n" + "-" * 75)

    print(
        f"Rank: {result.rank}"
    )

    print(
        f"Reranker score: "
        f"{result.payload.get('reranker_score')}"
    )

    print(
        f"Final score: "
        f"{result.payload.get('final_score')}"
    )

    print(
        f"Term overlap: "
        f"{result.payload.get('term_overlap')}"
    )

    print(
        f"Specification: "
        f"{result.specification}"
    )

    print(
        f"Section: "
        f"{result.section_number} "
        f"{result.section_title}"
    )

    print(
        f"Pages: "
        f"{result.page_start}-{result.page_end}"
    )

    print(
        f"Chunk: "
        f"{result.chunk_id}"
    )

    preview = (
        result.text
        .replace("\n", " ")
    )

    if len(preview) > 800:

        preview = (
            preview[:800]
            + "..."
        )

    print(
        f"\nEvidence:\n{preview}"
    )


def main() -> None:

    if len(sys.argv) < 2:

        print(
            'Usage:\n'
            'python scripts/test_hybrid_retrieval.py '
            '"your question"'
        )

        return

    query = " ".join(
        sys.argv[1:]
    )

    print(
        "[1/4] Loading embedding model..."
    )

    embedder = BGEEmbedder()

    print(
        "[2/4] Loading BM25..."
    )

    bm25 = BM25Index()

    bm25.load_or_build()

    print(
        "[3/4] Connecting to Qdrant..."
    )

    qdrant = QdrantStore()

    print(
        "[4/4] Loading reranker..."
    )

    reranker = BGEReranker()

    retriever = Hybrid3GPPRetriever(
        embedder=embedder,
        qdrant_store=qdrant,
        bm25_index=bm25,
        reranker=reranker,
        config=HybridRetrievalConfig(),
    )

    results, decision = (
        retriever.retrieve(
            query
        )
    )

    print("\n" + "=" * 75)
    print("3GPP HYBRID RETRIEVAL")
    print("=" * 75)

    print(
        f"\nQuestion:\n{query}"
    )

    print(
        f"\nEvidence allowed: "
        f"{decision.allowed}"
    )

    print(
        f"Decision reason: "
        f"{decision.reason}"
    )

    print(
        f"Best score: "
        f"{decision.best_score:.4f}"
    )

    if decision.second_score is not None:

        print(
            f"Second score: "
            f"{decision.second_score:.4f}"
        )

    print(
        f"Strong evidence chunks: "
        f"{decision.strong_evidence_count}"
    )

    print(
        "Supporting specifications: "
        f"{decision.supporting_specifications}"
    )

    for result in results:
        print_result(result)


if __name__ == "__main__":
    main()