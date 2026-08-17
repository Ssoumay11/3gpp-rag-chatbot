from __future__ import annotations

import hashlib
import re
from pathlib import Path


SPECIFICATION_PATTERN = re.compile(
    r"(?:3GPP\s+)?TS\s+(\d{2}\.\d{3})",
    re.IGNORECASE,
)

VERSION_PATTERN = re.compile(
    r"V(\d+\.\d+\.\d+)",
    re.IGNORECASE,
)


def calculate_sha256(file_path: str | Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    This allows us to detect whether a PDF has changed.
    """
    path = Path(file_path)

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def extract_specification(filename: str) -> str:
    """
    Extract specification number from filenames such as:
    TS_23.501_V17.6.0.pdf
    """
    match = SPECIFICATION_PATTERN.search(filename.replace("_", " "))

    if match:
        return f"TS {match.group(1)}"

    return Path(filename).stem


def extract_version(filename: str) -> str | None:
    """
    Extract version such as V17.6.0.
    """
    match = VERSION_PATTERN.search(filename)

    if match:
        return f"V{match.group(1)}"

    return None


def detect_heading(line: str) -> tuple[str, str] | None:
    """
    Detect common 3GPP section headings.

    Supports:
        ## 4.2 Network Functions
        4.2 Network Functions
        4.2.1 AMF
    """

    clean = line.strip()

    if not clean:
        return None

    # Markdown heading
    markdown_match = re.match(
        r"^(#{1,6})\s+(.+?)\s*$",
        clean,
    )

    if markdown_match:
        title = markdown_match.group(2).strip()

        number_match = re.match(
            r"^(\d+(?:\.\d+)*)\b[.:\-]?\s*(.*)$",
            title,
        )

        if number_match:
            return number_match.group(1), number_match.group(2).strip()

        return "", title

    # Plain 3GPP heading
    plain_match = re.match(
        r"^(\d+(?:\.\d+)+)\s+[A-Z].*$",
        clean,
    )

    if plain_match:
        section_number = plain_match.group(1)
        section_title = clean[len(section_number):].strip(" .:-")

        return section_number, section_title

    return None