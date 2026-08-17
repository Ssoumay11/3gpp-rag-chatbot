from __future__ import annotations

from dataclasses import dataclass

from src.retrieval.evidence_gate import (
    EvidenceDecision,
)
from src.retrieval.models import RetrievalResult

from src.verification.result import (
    VerificationResult,
)

from .schema import GroundedAnswer
from .trusted_citation import TrustedCitation


@dataclass
class GenerationResult:

    answer: GroundedAnswer

    evidence: list[RetrievalResult]

    trusted_citations: list[TrustedCitation]

    evidence_decision: EvidenceDecision

    citation_valid: bool

    citation_errors: list[str]

    verification: VerificationResult | None = None