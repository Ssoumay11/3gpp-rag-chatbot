from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal[
    "answerable",
    "out_of_domain",
    "unsupported",
    "adversarial",
]


class EvaluationQuestion(BaseModel):
    id: str

    question: str

    type: QuestionType

    expected_answerable: bool

    specification: str | None = None

    expected_sections: list[str] = Field(
        default_factory=list
    )

    gold_chunk_ids: list[str] = Field(
        default_factory=list
    )

    notes: str = ""