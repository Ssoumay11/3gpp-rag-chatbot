from __future__ import annotations

from pathlib import Path
import sys

# Ensure project root is on sys.path so `src` package is importable when
# running this script directly from the `scripts/` folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.embedder import BGEEmbedder
from src.retrieval.qdrant_store import QdrantStore
from src.retrieval.retrieval_config import RetrievalConfig
from src.retrieval.retriever import ThreeGPPRetriever


def main() -> None:

    query = (
        "What security mechanisms are used "
        "for authentication?"
    )

    specification = "TS 33.501"

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
        query=query,
        specification=specification,
    )

    print("=" * 70)

    print(
        f"Query: {query}"
    )

    print(
        f"Filter: {specification}"
    )

    print("=" * 70)

    for result in results:

        print(
            f"\nRank {result.rank}"
        )

        print(
            f"Score: {result.score:.4f}"
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
            f"{result.text[:500]}"
        )


if __name__ == "__main__":
    main()