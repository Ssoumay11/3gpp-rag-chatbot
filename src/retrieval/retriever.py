# Vector retrieval logic
from __future__ import annotations

from .embedder import BGEEmbedder
from .models import RetrievalResult
from .qdrant_store import QdrantStore
from .retrieval_config import RetrievalConfig
from .query_utils import (
    detect_specification,
    normalize_query,
)


class ThreeGPPRetriever:
    """
    Retrieval layer for the 3GPP corpus.
    """

    def __init__(
        self,
        embedder: BGEEmbedder,
        store: QdrantStore,
        config: RetrievalConfig | None = None,
    ) -> None:

        self.embedder = embedder

        self.store = store

        self.config = (
            config
            if config is not None
            else RetrievalConfig()
        )

    def retrieve(
        self,
        query: str,
        specification: str | None = None,
    ) -> list[RetrievalResult]:

        query = normalize_query(query)

        if not query:
            return []

        # Automatically detect:
        # "According to TS 23.501..."
        detected_spec = (
            detect_specification(query)
        )

        active_specification = (
            specification
            or detected_spec
        )

        # For the BGE model, query embedding is generated
        # directly from the normalized question.
        query_vector = self.embedder.encode(
            [query]
        )[0]

        points = self.store.search(
            query_vector=query_vector,
            limit=self.config.candidate_k,
            score_threshold=None,
            specification=active_specification,
        )

        results: list[RetrievalResult] = []

        for rank, point in enumerate(
            points,
            start=1,
        ):

            payload = point.payload or {}

            results.append(
                RetrievalResult(
                    rank=rank,
                    score=float(
                        point.score
                    ),
                    chunk_id=str(
                        payload.get(
                            "chunk_id",
                            point.id,
                        )
                    ),
                    specification=payload.get(
                        "specification"
                    ),
                    version=payload.get(
                        "version"
                    ),
                    section_number=payload.get(
                        "section_number"
                    ),
                    section_title=payload.get(
                        "section_title"
                    ),
                    page_start=payload.get(
                        "page_start"
                    ),
                    page_end=payload.get(
                        "page_end"
                    ),
                    content_type=payload.get(
                        "content_type"
                    ),
                    source_file=payload.get(
                        "source_file"
                    ),
                    text=payload.get(
                        "text",
                        "",
                    ),
                    payload=payload,
                )
            )

        return results

    def retrieve_top_k(
        self,
        query: str,
        specification: str | None = None,
    ) -> list[RetrievalResult]:

        results = self.retrieve(
            query=query,
            specification=specification,
        )

        return [
            result
            for result in results[
                : self.config.top_k
            ]
        ]