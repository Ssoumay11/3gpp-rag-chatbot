from __future__ import annotations

from pydantic import BaseModel, Field


class ClaimVerification(BaseModel):
    claim: str

    supported: bool

    evidence_chunk_ids: list[str] = Field(
        default_factory=list
    )

    explanation: str


class VerificationResponse(BaseModel):
    all_claims_supported: bool

    claims: list[ClaimVerification]