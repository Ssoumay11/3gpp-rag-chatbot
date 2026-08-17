from __future__ import annotations

import re


SPECIFICATION_ALIASES = {
    "23.501": "TS 23.501",
    "23501": "TS 23.501",
    "23.502": "TS 23.502",
    "23502": "TS 23.502",
    "23.503": "TS 23.503",
    "23503": "TS 23.503",
    "33.501": "TS 33.501",
    "33501": "TS 33.501",
}


def normalize_query(query: str) -> str:
    """
    Normalize whitespace without removing
    technical identifiers.
    """

    query = query.strip()

    query = re.sub(
        r"\s+",
        " ",
        query,
    )

    return query


def detect_specification(
    query: str,
) -> str | None:
    """
    Detect explicit references such as:

        TS 23.501
        23.501
        23501
    """

    normalized = query.lower()

    # Explicit TS forms.
    explicit = re.search(
        r"\bts\s*[- ]?(\d{2}\.\d{3})\b",
        normalized,
    )

    if explicit:
        number = explicit.group(1)

        return SPECIFICATION_ALIASES.get(
            number
        )

    # Direct numeric form.
    for alias, specification in SPECIFICATION_ALIASES.items():
        if alias in normalized:
            return specification

    return None