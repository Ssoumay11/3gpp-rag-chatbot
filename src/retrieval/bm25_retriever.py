from __future__ import annotations

from .bm25_index import BM25Index
from .models import RetrievalResult
from .query_utils import (
    detect_specification,
    normalize_query,
)


class BM25Retriever:

    def __init__(
        self,
        index: BM25Index,
    ) -> None:

        self.index = index

    def retrieve(
        self,
        query: str,
        top_k: int = 20,
        specification: str | None = None,
    ) -> list[RetrievalResult]:

        query = normalize_query(
            query
        )

        detected_specification = (
            detect_specification(query)
        )

        active_specification = (
            specification
            or detected_specification
        )

        raw_results = self.index.search(
            query=query,
            top_k=top_k,
            specification=active_specification,
        )

        results: list[
            RetrievalResult
        ] = []

        for rank, (index, score) in enumerate(
            raw_results,
            start=1,
        ):

            chunk = self.index.chunk_at(
                index
            )

            results.append(
                RetrievalResult(
                    rank=rank,
                    score=float(score),
                    chunk_id=chunk.get(
                        "chunk_id",
                        str(index),
                    ),
                    specification=chunk.get(
                        "specification"
                    ),
                    version=chunk.get(
                        "version"
                    ),
                    section_number=chunk.get(
                        "section_number"
                    ),
                    section_title=chunk.get(
                        "section_title"
                    ),
                    page_start=chunk.get(
                        "page_start"
                    ),
                    page_end=chunk.get(
                        "page_end"
                    ),
                    content_type=chunk.get(
                        "content_type"
                    ),
                    source_file=chunk.get(
                        "source_file"
                    ),
                    text=chunk.get(
                        "text",
                        "",
                    ),
                    payload=chunk,
                )
            )

        return results