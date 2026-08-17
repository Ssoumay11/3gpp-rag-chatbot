from __future__ import annotations

from statistics import mean

from .models import RetrievalResult


def summarize_results(
    results: list[RetrievalResult],
) -> dict:

    if not results:

        return {
            "count": 0,
            "best_score": None,
            "worst_score": None,
            "average_score": None,
            "score_gap": None,
        }

    scores = [
        result.score
        for result in results
    ]

    best_score = max(scores)

    worst_score = min(scores)

    average_score = mean(scores)

    score_gap = (
        best_score - scores[1]
        if len(scores) > 1
        else None
    )

    return {
        "count": len(results),
        "best_score": best_score,
        "worst_score": worst_score,
        "average_score": average_score,
        "score_gap": score_gap,
    }


def evidence_sufficient(
    results: list[RetrievalResult],
    minimum_results: int = 1,
    minimum_best_score: float = 0.35,
) -> bool:
    """
    Preliminary retrieval gate.

    This is intentionally conservative but should NOT
    be treated as the final hallucination gate.
    """

    if len(results) < minimum_results:
        return False

    best_score = results[0].score

    return best_score >= minimum_best_score