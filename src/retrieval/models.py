from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalResult:
    rank: int
    score: float
    chunk_id: str

    specification: str | None
    version: str | None

    section_number: str | None
    section_title: str | None

    page_start: int | None
    page_end: int | None

    content_type: str | None
    source_file: str | None

    text: str

    payload: dict[str, Any]