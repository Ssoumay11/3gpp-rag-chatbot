from __future__ import annotations

from src.retrieval.models import RetrievalResult


def format_verification_evidence(
    results: list[RetrievalResult],
    max_chunks: int = 5,
    max_chars_per_chunk: int = 5000,
) -> str:

    blocks: list[str] = []

    for result in results[:max_chunks]:

        text = result.text.strip()

        if len(text) > max_chars_per_chunk:
            text = (
                text[:max_chars_per_chunk]
                + "\n[TRUNCATED]"
            )

        block = f"""
<EVIDENCE>
chunk_id: {result.chunk_id}
specification: {result.specification}
version: {result.version}
section: {result.section_number}
section_title: {result.section_title}
page_start: {result.page_start}
page_end: {result.page_end}

TEXT:
{text}
</EVIDENCE>
""".strip()

        blocks.append(block)

    return "\n\n".join(blocks)