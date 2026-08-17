from __future__ import annotations

from .bm25_index import BM25Index
from .bm25_retriever import BM25Retriever
from .boosting import boost_results
from .embedder import BGEEmbedder
from .evidence_gate import (
    EvidenceDecision,
    evaluate_evidence,
)
from .hybrid_config import (
    HybridRetrievalConfig,
)
from .models import RetrievalResult
from .qdrant_store import QdrantStore
from .query_utils import detect_specification
from .retriever import ThreeGPPRetriever
from .rrf import (
    RankedItem,
    reciprocal_rank_fusion,
)


class Hybrid3GPPRetriever:
    """
    Dense + BM25 + RRF + cross-encoder reranking.
    """

    def __init__(
        self,
        embedder: BGEEmbedder,
        qdrant_store: QdrantStore,
        bm25_index: BM25Index,
        reranker,
        config: HybridRetrievalConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else HybridRetrievalConfig()
        )

        self.bm25_index = bm25_index

        self.bm25_retriever = (
            BM25Retriever(
                bm25_index
            )
        )

        self.dense_retriever = (
            ThreeGPPRetriever(
                embedder=embedder,
                store=qdrant_store,
            )
        )

        self.reranker = reranker

    def retrieve(
        self,
        query: str,
        specification: str | None = None,
    ) -> tuple[
        list[RetrievalResult],
        EvidenceDecision,
    ]:

        active_specification = (
            specification
            or detect_specification(query)
        )

        # --------------------------------------------------
        # 1. Dense retrieval
        # --------------------------------------------------

        dense_results = (
            self.dense_retriever.retrieve(
                query=query,
                specification=(
                    active_specification
                ),
            )
        )

        dense_ranked = [
            RankedItem(
                item=result,
                score=result.score,
                rank=result.rank,
            )
            for result in dense_results[
                : self.config.dense_k
            ]
        ]

        # --------------------------------------------------
        # 2. BM25 retrieval
        # --------------------------------------------------

        lexical_results = (
            self.bm25_retriever.retrieve(
                query=query,
                top_k=self.config.lexical_k,
                specification=(
                    active_specification
                ),
            )
        )

        lexical_ranked = [
            RankedItem(
                item=result,
                score=result.score,
                rank=result.rank,
            )
            for result in lexical_results
        ]

        # --------------------------------------------------
        # 3. Reciprocal Rank Fusion
        # --------------------------------------------------

        fused = reciprocal_rank_fusion(
            ranked_lists=[
                dense_ranked,
                lexical_ranked,
            ],
            weights=[
                self.config.dense_weight,
                self.config.lexical_weight,
            ],
            k=self.config.rrf_k,
        )

        candidates = [
            item.item
            for item in fused[
                : self.config.fusion_k
            ]
        ]

        if not candidates:

            decision = evaluate_evidence(
                [],
                reranker_threshold=(
                    self.config.reranker_threshold
                ),
                minimum_evidence_chunks=(
                    self.config.minimum_evidence_chunks
                ),
                minimum_strong_evidence_chunks=(
                    self.config.minimum_strong_evidence_chunks
                ),
                requested_specification=(
                    active_specification
                ),
            )

            return [], decision

        # --------------------------------------------------
        # 4. Cross-encoder reranking
        # --------------------------------------------------

        reranked = self.reranker.rerank(
            query=query,
            results=candidates[
                : self.config.reranker_k
            ],
        )

        # --------------------------------------------------
        # 5. Small technical-term boost
        # --------------------------------------------------

        reranked = boost_results(
            query=query,
            results=reranked,
        )

        final_results = reranked[
            : self.config.final_k
        ]

        # --------------------------------------------------
        # 6. Evidence gate
        # --------------------------------------------------

        decision = evaluate_evidence(
            final_results,
            reranker_threshold=(
                self.config.reranker_threshold
            ),
            minimum_evidence_chunks=(
                self.config.minimum_evidence_chunks
            ),
            minimum_strong_evidence_chunks=(
                self.config.minimum_strong_evidence_chunks
            ),
            requested_specification=(
                active_specification
            ),
        )

        return final_results, decision