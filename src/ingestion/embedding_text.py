from __future__ import annotations

from typing import Any


def build_embedding_text(
    chunk: dict[str, Any],
) -> str:
    """
    Create the text that will eventually be embedded.

    Metadata is explicitly included because a standalone
    chunk should remain understandable to the retriever.
    """

    specification = chunk.get(
        "specification",
        "",
    )

    version = chunk.get(
        "version",
        "",
    )

    section_number = chunk.get(
        "section_number",
        "",
    )

    section_title = chunk.get(
        "section_title",
        "",
    )

    content_type = chunk.get(
        "content_type",
        "text",
    )

    body = chunk.get(
        "text",
        "",
    )

    header_parts = [
        specification,
        version,
    ]

    if section_number:
        header_parts.append(
            f"Section {section_number}"
        )

    if section_title:
        header_parts.append(
            section_title
        )

    header = " | ".join(
        part
        for part in header_parts
        if part
    )

    return (
        f"{header}\n"
        f"Content type: {content_type}\n\n"
        f"{body}"
    )