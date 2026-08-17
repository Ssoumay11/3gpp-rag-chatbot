from __future__ import annotations

import json

from pydantic import ValidationError

from .schema import GroundedAnswer


REFUSAL_TEXT = (
    "I could not find sufficient supporting "
    "information in the provided 3GPP documents."
)


def parse_response(
    raw_response: str,
) -> GroundedAnswer:

    try:
        data = json.loads(
            raw_response
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"Groq returned invalid JSON: {exc}"
        ) from exc

    try:

        answer = GroundedAnswer.model_validate(
            data
        )

    except ValidationError as exc:

        raise RuntimeError(
            f"Invalid grounded response schema: {exc}"
        ) from exc

    # Enforce our application-level refusal text.
    if not answer.answerable:

        answer.answer = REFUSAL_TEXT

        # No citations for a refusal.
        answer.citations = []

    return answer