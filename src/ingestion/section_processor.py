from __future__ import annotations

import re
from typing import Any

from .metadata import detect_heading


# Common PDF footer/header patterns that must NEVER become
# section headings.
FOOTER_PATTERNS = [
    re.compile(
        r"^3GPP\s+TS\s+\d{2}\.\d{3}",
        re.IGNORECASE,
    ),
    re.compile(
        r"^3gpp\s+ts\s+\d{2}\.\d{3}\s+v\d+\.\d+\.\d+",
        re.IGNORECASE,
    ),
    re.compile(
        r"^release\s+\d+",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\d{1,4}$",
        re.IGNORECASE,
    ),
]


def is_footer_or_header(
    line: str,
) -> bool:
    clean = line.strip()

    if not clean:
        return False

    return any(
        pattern.search(clean)
        for pattern in FOOTER_PATTERNS
    )


def enrich_with_sections(
    page_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Walk through page-level Markdown and maintain
    current 3GPP section context.

    Header/footer artifacts are explicitly excluded.
    """

    enriched: list[dict[str, Any]] = []

    current_section_number = ""
    current_section_title = ""

    for record in page_records:

        page_number = record.get(
            "page_number"
        )

        text = record.get(
            "text",
            "",
        )

        lines = text.splitlines()

        current_block: list[str] = []

        for line in lines:

            clean_line = line.strip()

            if not clean_line:
                current_block.append("")
                continue

            # --------------------------------------------------
            # Ignore PDF headers/footers.
            # --------------------------------------------------

            if is_footer_or_header(
                clean_line
            ):
                continue

            heading = detect_heading(
                clean_line
            )

            if heading:

                # Reject malformed headings.
                section_number = (
                    heading[0]
                )

                section_title = (
                    heading[1]
                )

                if not section_number:
                    current_block.append(
                        clean_line
                    )
                    continue

                # Section number must begin with a numeric
                # hierarchy such as 5.6 or 6.1.1.1.
                if not re.match(
                    r"^\d+(?:\.\d+)+$",
                    section_number,
                ):
                    current_block.append(
                        clean_line
                    )
                    continue

                # Flush text before heading.
                if current_block:

                    block_text = (
                        "\n".join(
                            current_block
                        ).strip()
                    )

                    if block_text:

                        enriched.append(
                            {
                                **record,
                                "text": block_text,
                                "section_number": (
                                    current_section_number
                                ),
                                "section_title": (
                                    current_section_title
                                ),
                                "content_type": "text",
                            }
                        )

                    current_block = []

                current_section_number = (
                    section_number
                )

                current_section_title = (
                    section_title
                )

                enriched.append(
                    {
                        **record,
                        "text": clean_line,
                        "section_number": (
                            current_section_number
                        ),
                        "section_title": (
                            current_section_title
                        ),
                        "content_type": "heading",
                    }
                )

                continue

            current_block.append(
                clean_line
            )

        # Flush page remainder.
        if current_block:

            block_text = (
                "\n".join(
                    current_block
                ).strip()
            )

            if block_text:

                content_type = (
                    "table"
                    if (
                        "| ---" in block_text
                        or re.search(
                            r"\n\|.*\|",
                            block_text,
                        )
                    )
                    else "text"
                )

                enriched.append(
                    {
                        **record,
                        "text": block_text,
                        "section_number": (
                            current_section_number
                        ),
                        "section_title": (
                            current_section_title
                        ),
                        "content_type": content_type,
                    }
                )

    return enriched