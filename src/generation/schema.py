from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str


class GroundedAnswer(BaseModel):
    answerable: bool
    answer: str
    citations: list[Citation] = Field(
        default_factory=list
    )