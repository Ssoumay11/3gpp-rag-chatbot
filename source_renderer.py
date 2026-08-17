from __future__ import annotations

from typing import Any


def _get(source: Any, field: str, default=None):
    """
    Support both:
    - RetrievalResult objects
    - serialized dictionaries
    """
    if isinstance(source, dict):
        return source.get(field, default)

    return getattr(source, field, default)


def format_source(source: Any) -> str:

    specification = (
        _get(
            source,
            "specification",
        )
        or "Unknown specification"
    )

    version = (
        _get(
            source,
            "version",
        )
        or "Unknown version"
    )

    section = (
        _get(
            source,
            "section_number",
        )
        or "Unknown"
    )

    title = (
        _get(
            source,
            "section_title",
        )
        or ""
    )

    page_start = _get(
        source,
        "page_start",
    )

    page_end = _get(
        source,
        "page_end",
    )

    if (
        page_start is not None
        and page_end is not None
        and page_start != page_end
    ):
        pages = (
            f"Pages {page_start}–{page_end}"
        )

    elif page_start is not None:
        pages = f"Page {page_start}"

    else:
        pages = "Page unavailable"

    if title:
        section_text = (
            f"Section {section}: {title}"
        )
    else:
        section_text = (
            f"Section {section}"
        )

    return (
        f"**{specification} {version}**  \n"
        f"{section_text}  \n"
        f"{pages}"
    )


def format_citation(citation: Any) -> str:

    specification = _get(
        citation,
        "specification",
        "Unknown specification",
    )

    version = _get(
        citation,
        "version",
        "Unknown version",
    )

    section = _get(
        citation,
        "section",
        "Unknown",
    )

    page_start = _get(
        citation,
        "page_start",
    )

    page_end = _get(
        citation,
        "page_end",
    )

    if (
        page_start is not None
        and page_end is not None
        and page_start != page_end
    ):
        page_text = (
            f", Pages {page_start}–{page_end}"
        )

    elif page_start is not None:
        page_text = (
            f", Page {page_start}"
        )

    else:
        page_text = ""

    return (
        f"{specification} {version}, "
        f"Section {section}"
        f"{page_text}"
    )