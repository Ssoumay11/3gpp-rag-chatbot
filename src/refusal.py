from __future__ import annotations


REFUSAL_TEXT = (
    "I could not find sufficient supporting information "
    "in the provided 3GPP documents."
)


def is_refusal(
    answer: str,
) -> bool:

    return answer.strip() == REFUSAL_TEXT