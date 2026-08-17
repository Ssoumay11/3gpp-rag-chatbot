from __future__ import annotations

from src.retrieval.bm25_index import (
    BM25Index,
)
from src.retrieval.embedder import (
    BGEEmbedder,
)
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

from src.verification.pipeline import (
    HallucinationGuard,
)


def main() -> None:

    question = (
        "What is the role of the AMF "
        "in the 5G system?"
    )

    print("[1] Loading models...")

    embedder = BGEEmbedder()

    reranker = BGEReranker()

    qdrant = QdrantStore()

    bm25 = BM25Index()

    bm25.load_or_build()

    retriever = Hybrid3GPPRetriever(
        embedder=embedder,
        qdrant_store=qdrant,
        bm25_index=bm25,
        reranker=reranker,
        config=HybridRetrievalConfig(),
    )

    print("[2] Retrieving evidence...")

    evidence, decision = (
        retriever.retrieve(
            question
        )
    )

    print(
        f"Evidence gate: "
        f"{decision.allowed}"
    )

    if not decision.allowed:

        print(
            "Insufficient evidence."
        )

        return

    draft = (
        "The AMF is responsible for "
        "registration management and "
        "provides the UPF user-plane data path."
   
    )

    print(
        "\nDraft:"
    )

    print(draft)

    print(
        "\n[3] Verifying claims..."
    )

    guard = HallucinationGuard()

    result = guard.verify(
        answer=draft,
        evidence=evidence,
    )

    print(
        f"\nVerification passed: "
        f"{result.passed}"
    )

    print(
        f"Claims: "
        f"{result.claims}"
    )

    if result.verification:

        for claim in (
            result.verification.claims
        ):

            print(
                "\nClaim:"
            )

            print(
                claim.claim
            )

            print(
                f"Supported: "
                f"{claim.supported}"
            )

            print(
                "Evidence chunks: "
                f"{claim.evidence_chunk_ids}"
            )

            print(
                f"Explanation: "
                f"{claim.explanation}"
            )

    if result.errors:

        print(
            "\nErrors:"
        )

        for error in result.errors:

            print(
                f"- {error}"
            )


if __name__ == "__main__":
    main()