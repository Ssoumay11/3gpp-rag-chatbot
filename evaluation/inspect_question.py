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
from src.retrieval.qdrant_store import QdrantStore
from src.retrieval.reranker import BGEReranker


def main() -> None:

    if len(sys.argv) < 2:

        print(
            'Usage:\n'
            'python evaluation/inspect_question.py '
            '"question"'
        )

        return

    question = " ".join(
        sys.argv[1:]
    )

    embedder = BGEEmbedder()

    qdrant = QdrantStore()

    bm25 = BM25Index()

    bm25.load_or_build()

    reranker = BGEReranker()

    retriever = Hybrid3GPPRetriever(
        embedder=embedder,
        qdrant_store=qdrant,
        bm25_index=bm25,
        reranker=reranker,
        config=HybridRetrievalConfig(
            final_k=10
        ),
    )

    results, decision = (
        retriever.retrieve(
            question
        )
    )

    print(
        f"\nEvidence allowed: "
        f"{decision.allowed}"
    )

    for result in results:

        print("\n" + "=" * 80)

        print(
            f"Chunk ID: {result.chunk_id}"
        )

        print(
            f"Specification: "
            f"{result.specification}"
        )

        print(
            f"Section: "
            f"{result.section_number}"
        )

        print(
            f"Section title: "
            f"{result.section_title}"
        )

        print(
            f"Pages: "
            f"{result.page_start}-"
            f"{result.page_end}"
        )

        print(
            f"Score: "
            f"{result.payload.get('final_score')}"
        )

        print(
            "\nTEXT:\n"
            f"{result.text}"
        )


if __name__ == "__main__":
    main()