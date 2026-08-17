from __future__ import annotations

import re


EXCLUDED_HEADINGS = {
    "copyright notification",
    "foreword",
    "intellectual property rights",
    "change history",
    "history",
    "references",
}


def clean_heading(text: str) -> str:
    text = text.strip()

    # Remove Markdown heading markers.
    text = re.sub(
        r"^#+\s*",
        "",
        text,
    )

    # Remove Markdown emphasis.
    text = text.replace(
        "**",
        "",
    )

    text = text.replace(
        "__",
        "",
    )

    return text.strip().lower()


def is_nontechnical_heading(
    section_number: str,
    section_title: str,
) -> bool:

    title = clean_heading(
        section_title
    )

    # Numbered sections are normally technical.
    if section_number:
        return False

    return title in EXCLUDED_HEADINGS


def should_keep_record(
    record: dict,
) -> bool:

    section_number = record.get(
        "section_number",
        "",
    )

    section_title = record.get(
        "section_title",
        "",
    )

    if is_nontechnical_heading(
        section_number,
        section_title,
    ):
        return False

    text = record.get(
        "text",
        "",
    )

    # Remove obvious copyright boilerplate.
    copyright_markers = (
        "No part may be reproduced",
        "All rights reserved",
        "Trade Mark of ETSI",
        "registered and owned by",
    )

    copyright_hits = sum(
        marker.lower() in text.lower()
        for marker in copyright_markers
    )

    if copyright_hits >= 2:
        return False

    return True