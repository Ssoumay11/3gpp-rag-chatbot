from __future__ import annotations

from src.retrieval.models import RetrievalResult


def format_evidence(
    results: list[RetrievalResult],
    max_chunks: int = 5,
    max_chars_per_chunk: int = 6000,
) -> str:
    """
    Convert retrieval results into a strongly delimited
    evidence packet.
    """

    blocks: list[str] = []

    for index, result in enumerate(
        results[:max_chunks],
        start=1,
    ):

        text = result.text.strip()

        if len(text) > max_chars_per_chunk:
            text = (
                text[:max_chars_per_chunk]
                + "\n[Evidence truncated]"
            )

        section = (
            result.section_number
            or "unknown"
        )

        section_title = (
            result.section_title
            or ""
        )

        page = result.page_start

        if (
            result.page_end
            and result.page_end != result.page_start
        ):
            page_text = (
                f"{result.page_start}-"
                f"{result.page_end}"
            )
        else:
            page_text = (
                str(page)
                if page is not None
                else "unknown"
            )

        block = f"""
<EVIDENCE_ITEM id="{index}">
chunk_id: {result.chunk_id}
specification: {result.specification}
version: {result.version}
section: {section}
section_title: {section_title}
page: {page_text}
content_type: {result.content_type}

TEXT:
{text}
</EVIDENCE_ITEM>
""".strip()

        blocks.append(block)

    if not blocks:
        return (
            "<NO_EVIDENCE>\n"
            "No evidence was retrieved.\n"
            "</NO_EVIDENCE>"
        )

    return "\n\n".join(
        blocks
    )