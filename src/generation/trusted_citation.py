from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrustedCitation:

    chunk_id: str

    specification: str | None

    version: str | None

    section: str | None

    section_title: str | None

    page_start: int | None

    page_end: int | None