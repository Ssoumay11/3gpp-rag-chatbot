from __future__ import annotations

from src.retrieval.models import RetrievalResult

from .schema import VerificationResponse


def hard_validate(
    verification: VerificationResponse,
    evidence: list[RetrievalResult],
) -> tuple[bool, list[str]]:

    valid_chunk_ids = {
        result.chunk_id
        for result in evidence
    }

    errors: list[str] = []

    for claim in verification.claims:

        if not claim.supported:
            continue

        if not claim.evidence_chunk_ids:

            errors.append(
                f"Supported claim has no evidence: "
                f"{claim.claim}"
            )

            continue

        for chunk_id in (
            claim.evidence_chunk_ids
        ):

            if chunk_id not in valid_chunk_ids:

                errors.append(
                    "Verifier referenced an evidence "
                    f"chunk that was not supplied: "
                    f"{chunk_id}"
                )

    if not verification.claims:

        errors.append(
            "No claims were verified."
        )

    expected = all(
        claim.supported
        for claim in verification.claims
    )

    if (
        verification.all_claims_supported
        != expected
    ):

        errors.append(
            "Verification summary does not "
            "match individual claim results."
        )

    return (
        len(errors) == 0,
        errors,
    )