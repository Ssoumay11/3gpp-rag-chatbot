from __future__ import annotations

from src.retrieval.models import RetrievalResult

from .claim_extractor import (
    ClaimExtractor,
)
from .config import VerificationConfig
from .hard_validator import (
    hard_validate,
)
from .result import VerificationResult
from .verifier import ClaimVerifier


class HallucinationGuard:

    def __init__(
        self,
        config: VerificationConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else VerificationConfig()
        )

        self.claim_extractor = (
            ClaimExtractor(
                self.config
            )
        )

        self.verifier = ClaimVerifier(
            self.config
        )

    def verify(
        self,
        answer: str,
        evidence: list[RetrievalResult],
    ) -> VerificationResult:

        # ----------------------------------------------
        # 1. Extract claims
        # ----------------------------------------------

        claims = (
            self.claim_extractor.extract(
                answer
            )
        )

        if not claims:

            return VerificationResult(
                passed=False,
                claims=[],
                verification=None,
                evidence=evidence,
                errors=[
                    "No factual claims extracted."
                ],
            )

        # ----------------------------------------------
        # 2. Verify claims
        # ----------------------------------------------

        verification = (
            self.verifier.verify(
                claims=claims,
                evidence=evidence,
            )
        )

        # ----------------------------------------------
        # 3. Hard validation
        # ----------------------------------------------

        structurally_valid, errors = (
            hard_validate(
                verification,
                evidence,
            )
        )

        if not structurally_valid:

            return VerificationResult(
                passed=False,
                claims=claims,
                verification=verification,
                evidence=evidence,
                errors=errors,
            )

        # ----------------------------------------------
        # 4. Final gate
        # ----------------------------------------------

        passed = (
            verification.all_claims_supported
        )

        if not passed:

            unsupported = [
                claim.claim
                for claim
                in verification.claims
                if not claim.supported
            ]

            errors.extend(
                [
                    "Unsupported factual claim: "
                    + claim
                    for claim in unsupported
                ]
            )

        return VerificationResult(
            passed=passed,
            claims=claims,
            verification=verification,
            evidence=evidence,
            errors=errors,
        )