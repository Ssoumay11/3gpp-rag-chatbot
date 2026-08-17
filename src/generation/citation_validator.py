from __future__ import annotations

from src.retrieval.models import RetrievalResult

from .schema import GroundedAnswer


def validate_citations(
    answer: GroundedAnswer,
    evidence: list[RetrievalResult],
) -> tuple[bool, list[str]]:

    errors: list[str] = []

    valid_chunk_ids = {
        result.chunk_id
        for result in evidence
    }

    if not answer.answerable:
        return True, []

    if not answer.citations:

        errors.append(
            "Answerable response contains no citations."
        )

        return False, errors

    for citation in answer.citations:

        if citation.chunk_id not in valid_chunk_ids:

            errors.append(
                "Citation references a chunk "
                f"not supplied in evidence: "
                f"{citation.chunk_id}"
            )

    return (
        len(errors) == 0,
        errors,
    )