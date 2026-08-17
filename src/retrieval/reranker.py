# Re-ranking logic
from __future__ import annotations

from sentence_transformers import CrossEncoder

from .models import RetrievalResult


class BGEReranker:
    """
    Cross-encoder reranker.

    The model scores query-document pairs directly.
    """

    def __init__(
        self,
        model_name: str = (
            "BAAI/bge-reranker-base"
        ),
        device: str = "cpu",
    ) -> None:

        print(
            f"[Reranker] Loading "
            f"{model_name}"
        )

        self.model = CrossEncoder(
            model_name,
            device=device,
            max_length=512,
        )

        print(
            "[Reranker] Model loaded."
        )

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        if not results:
            return []

        pairs = [
            (
                query,
                result.text,
            )
            for result in results
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        reranked = []

        for result, score in zip(
            results,
            scores,
        ):

            result.payload[
                "reranker_score"
            ] = float(score)

            reranked.append(
                (
                    result,
                    float(score),
                )
            )

        reranked.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        output: list[
            RetrievalResult
        ] = []

        for rank, (
            result,
            score,
        ) in enumerate(
            reranked,
            start=1,
        ):

            result.rank = rank
            result.payload[
                "reranker_rank"
            ] = rank

            output.append(
                result
            )

        return output