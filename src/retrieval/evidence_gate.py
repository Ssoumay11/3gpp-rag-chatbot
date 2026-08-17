# Evidence validation gate
from __future__ import annotations

from dataclasses import dataclass

from .models import RetrievalResult


@dataclass
class EvidenceDecision:
    allowed: bool
    reason: str

    best_score: float
    second_score: float | None

    strong_evidence_count: int
    supporting_specifications: set[str]


def evaluate_evidence(
    results: list[RetrievalResult],
    *,
    reranker_threshold: float = 0.20,
    minimum_evidence_chunks: int = 1,
    minimum_strong_evidence_chunks: int = 2,
    requested_specification: str | None = None,
) -> EvidenceDecision:

    if not results:

        return EvidenceDecision(
            allowed=False,
            reason="No evidence retrieved.",
            best_score=0.0,
            second_score=None,
            strong_evidence_count=0,
            supporting_specifications=set(),
        )

    scores = [
        float(
            result.payload.get(
                "final_score",
                result.payload.get(
                    "reranker_score",
                    0.0,
                ),
            )
        )
        for result in results
    ]

    best_score = scores[0]

    second_score = (
        scores[1]
        if len(scores) > 1
        else None
    )

    strong_results = [
        result
        for result in results
        if float(
            result.payload.get(
                "final_score",
                result.payload.get(
                    "reranker_score",
                    0.0,
                ),
            )
        ) >= reranker_threshold
    ]

    supporting_specifications = {
        result.specification
        for result in strong_results
        if result.specification
    }

    if len(results) < minimum_evidence_chunks:

        return EvidenceDecision(
            allowed=False,
            reason="Insufficient retrieved evidence.",
            best_score=best_score,
            second_score=second_score,
            strong_evidence_count=len(
                strong_results
            ),
            supporting_specifications=(
                supporting_specifications
            ),
        )

    if (
        len(strong_results)
        < minimum_strong_evidence_chunks
    ):

        return EvidenceDecision(
            allowed=False,
            reason=(
                "Retrieved evidence is below "
                "the required support threshold."
            ),
            best_score=best_score,
            second_score=second_score,
            strong_evidence_count=len(
                strong_results
            ),
            supporting_specifications=(
                supporting_specifications
            ),
        )

    if (
        requested_specification
        and requested_specification
        not in supporting_specifications
    ):

        return EvidenceDecision(
            allowed=False,
            reason=(
                "Evidence does not sufficiently "
                "support the requested 3GPP specification."
            ),
            best_score=best_score,
            second_score=second_score,
            strong_evidence_count=len(
                strong_results
            ),
            supporting_specifications=(
                supporting_specifications
            ),
        )

    return EvidenceDecision(
        allowed=True,
        reason="Evidence threshold satisfied.",
        best_score=best_score,
        second_score=second_score,
        strong_evidence_count=len(
            strong_results
        ),
        supporting_specifications=(
            supporting_specifications
        ),
    )