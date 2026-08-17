from __future__ import annotations

import re

from .models import RetrievalResult


def extract_query_terms(
    query: str,
) -> set[str]:

    return {
        token.lower()
        for token in re.findall(
            r"[A-Za-z0-9._/-]+",
            query,
        )
        if len(token) > 1
    }


def boost_results(
    query: str,
    results: list[RetrievalResult],
) -> list[RetrievalResult]:

    query_terms = extract_query_terms(
        query
    )

    scored = []

    for result in results:

        text = result.text.lower()

        overlap = sum(
            1
            for term in query_terms
            if term in text
        )

        # Small lexical boost.
        boost = min(
            overlap * 0.02,
            0.10,
        )

        result.payload[
            "term_overlap"
        ] = overlap

        result.payload[
            "lexical_boost"
        ] = boost

        current_score = result.payload.get(
            "reranker_score",
            0.0,
        )

        result.payload[
            "final_score"
        ] = (
            float(current_score)
            + boost
        )

        scored.append(
            result
        )

    scored.sort(
        key=lambda result:
        result.payload.get(
            "final_score",
            0.0,
        ),
        reverse=True,
    )

    for rank, result in enumerate(
        scored,
        start=1,
    ):
        result.rank = rank

    return scored