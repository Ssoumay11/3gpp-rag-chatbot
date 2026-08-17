from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.retrieval.models import RetrievalResult
from .schema import VerificationResponse


@dataclass
class VerificationResult:
    passed: bool
    claims: list[str]
    verification: VerificationResponse | None
    evidence: list[RetrievalResult]
    errors: list[str]
