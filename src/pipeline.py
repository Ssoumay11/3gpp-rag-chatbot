# Main RAG pipeline
from __future__ import annotations

from src.generation.config import (
    GenerationConfig,
)
from src.generation.grounded_generator import (
    GroundedGenerator,
)
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


class ThreeGPPRAG:

    def __init__(self) -> None:

        print(
            "[Pipeline] Loading embedder..."
        )

        embedder = BGEEmbedder()

        print(
            "[Pipeline] Loading Qdrant..."
        )

        qdrant = QdrantStore()

        print(
            "[Pipeline] Loading BM25..."
        )

        bm25 = BM25Index()

        bm25.load_or_build()

        print(
            "[Pipeline] Loading reranker..."
        )

        reranker = BGEReranker()

        print(
            "[Pipeline] Building hybrid retriever..."
        )

        retriever = (
            Hybrid3GPPRetriever(
                embedder=embedder,
                qdrant_store=qdrant,
                bm25_index=bm25,
                reranker=reranker,
                config=(
                    HybridRetrievalConfig()
                ),
            )
        )

        print(
            "[Pipeline] Loading Groq..."
        )

        self.generator = GroundedGenerator(
            retriever=retriever,
            config=GenerationConfig(),
        )

    def ask(
        self,
        question: str,
    ):

        return self.generator.answer(
            question
        )