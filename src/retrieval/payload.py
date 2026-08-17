from __future__ import annotations

from typing import Any


def build_payload(
    chunk: dict[str, Any],
) -> dict[str, Any]:

    return {
        "chunk_id": chunk.get(
            "chunk_id"
        ),

        "document_id": chunk.get(
            "document_id"
        ),

        "specification": chunk.get(
            "specification"
        ),

        "version": chunk.get(
            "version"
        ),

        "section_number": chunk.get(
            "section_number",
            "",
        ),

        "section_title": chunk.get(
            "section_title",
            "",
        ),

        "page_start": chunk.get(
            "page_start"
        ),

        "page_end": chunk.get(
            "page_end"
        ),

        "content_type": chunk.get(
            "content_type",
            "text",
        ),

        "parser": chunk.get(
            "parser"
        ),

        "source_file": chunk.get(
            "source_file"
        ),

        # Keep the actual text in the payload.
        #
        # This allows us to reconstruct evidence directly
        # from Qdrant without needing to reopen the PDF.
        "text": chunk.get(
            "text",
            "",
        ),

        # The exact string used for embedding.
        "embedding_text": chunk.get(
            "embedding_text",
            "",
        ),
    }