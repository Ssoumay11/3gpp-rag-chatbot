from __future__ import annotations

import re


def repair_encoding(text: str) -> str:
    """
    Repair common UTF-8 -> Windows-1252 mojibake.

    Example:
        Â©    -> ©
        â„¢   -> ™
        Â®    -> ®
    """

    if not text:
        return ""

    try:
        repaired = text.encode(
            "latin1"
        ).decode(
            "utf-8"
        )

        # Only use the repaired version when it actually
        # reduces common mojibake markers.
        bad_markers = (
            "Â",
            "â",
            "ð",
            "Ã",
        )

        original_bad = sum(
            text.count(marker)
            for marker in bad_markers
        )

        repaired_bad = sum(
            repaired.count(marker)
            for marker in bad_markers
        )

        if repaired_bad < original_bad:
            return repaired

    except (
        UnicodeEncodeError,
        UnicodeDecodeError,
    ):
        pass

    return text


def normalize_text(text: str) -> str:
    """
    Normalize extracted PDF/Markdown text while preserving
    meaningful Markdown structure.
    """

    if not text:
        return ""

    text = repair_encoding(text)

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    lines = [
        line.rstrip()
        for line in text.splitlines()
    ]

    normalized_lines: list[str] = []

    empty_count = 0

    for line in lines:

        if not line.strip():

            empty_count += 1

            if empty_count <= 2:
                normalized_lines.append("")

        else:

            empty_count = 0

            normalized_lines.append(line)

    text = "\n".join(
        normalized_lines
    )

    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text,
    )

    return text.strip()


def is_table(text: str) -> bool:

    if not text:
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return False

    has_separator = any(
        re.match(
            r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$",
            line,
        )
        for line in lines
    )

    if has_separator:
        return True

    pipe_rows = sum(
        1
        for line in lines
        if line.count("|") >= 2
    )

    return pipe_rows >= 2


def split_paragraphs(
    text: str,
) -> list[str]:

    blocks = re.split(
        r"\n\s*\n+",
        text,
    )

    return [
        block.strip()
        for block in blocks
        if block.strip()
    ]