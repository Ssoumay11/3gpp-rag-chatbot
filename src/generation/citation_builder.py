from __future__ import annotations

from src.retrieval.models import RetrievalResult

from .schema import Citation
from .trusted_citation import TrustedCitation


def build_trusted_citations(
    citations: list[Citation],
    evidence: list[RetrievalResult],
) -> list[TrustedCitation]:

    evidence_by_id = {
        item.chunk_id: item
        for item in evidence
    }

    trusted: list[TrustedCitation] = []

    for citation in citations:

        result = evidence_by_id.get(
            citation.chunk_id
        )

        if result is None:
            continue

        trusted.append(
            TrustedCitation(
                chunk_id=result.chunk_id,
                specification=result.specification,
                version=result.version,
                section=result.section_number,
                section_title=result.section_title,
                page_start=result.page_start,
                page_end=result.page_end,
            )
        )

    return trusted