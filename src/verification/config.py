from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class VerificationConfig:

    model: str = os.getenv(
        "VERIFIER_MODEL",
        "openai/gpt-oss-20b",
    )

    temperature: float = 0.0

    max_tokens: int = 1200

    max_claims: int = 10

    max_evidence_chunks: int = 5

    max_evidence_chars: int = 4000

    minimum_supporting_evidence: int = 1