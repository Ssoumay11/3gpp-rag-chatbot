from __future__ import annotations


def serialize_source(
    source,
) -> dict:

    return {
        "chunk_id": source.chunk_id,
        "specification": source.specification,
        "version": source.version,
        "section_number": source.section_number,
        "section_title": source.section_title,
        "page_start": source.page_start,
        "page_end": source.page_end,
        "content_type": source.content_type,
        "source_file": source.source_file,
        "text": source.text,
    }


def serialize_citation(
    citation,
) -> dict:

    return {
        "chunk_id": citation.chunk_id,
        "specification": citation.specification,
        "version": citation.version,
        "section": citation.section,
        "page_start": citation.page_start,
        "page_end": citation.page_end,
    }