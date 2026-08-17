from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VerificationMetrics:

    total_claims: int

    supported_claims: int

    unsupported_claims: int

    verification_passed: bool

    @property
    def support_rate(self) -> float:

        if self.total_claims == 0:
            return 0.0

        return (
            self.supported_claims
            / self.total_claims
        )


def calculate_metrics(
    verification,
) -> VerificationMetrics:

    total = len(
        verification.claims
    )

    supported = sum(
        1
        for claim
        in verification.claims
        if claim.supported
    )

    unsupported = (
        total - supported
    )

    return VerificationMetrics(
        total_claims=total,
        supported_claims=supported,
        unsupported_claims=unsupported,
        verification_passed=(
            verification.all_claims_supported
        ),
    )