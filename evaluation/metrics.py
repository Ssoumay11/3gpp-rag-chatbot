from __future__ import annotations

from statistics import mean
from typing import Any


def calculate_metrics(
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    valid = [
        result
        for result in results
        if "error" not in result
    ]

    if not valid:

        return {
            "total": len(results),
            "valid": 0,
        }

    answerability_correct = sum(
        1
        for result in valid
        if result.get(
            "answerability_correct",
            False,
        )
    )

    refusal_correct = sum(
        1
        for result in valid
        if result.get(
            "refusal_correct",
            False,
        )
    )

    citation_valid = sum(
        1
        for result in valid
        if result.get(
            "citation_valid",
            False,
        )
    )

    latencies = [
        result["latency_seconds"]
        for result in valid
    ]

    return {
        "total_questions": len(results),
        "valid_questions": len(valid),

        "answerability_accuracy": (
            answerability_correct
            / len(valid)
        ),

        "refusal_accuracy": (
            refusal_correct
            / len(valid)
        ),

        "citation_valid_rate": (
            citation_valid
            / len(valid)
        ),

        "average_latency_seconds": mean(
            latencies
        ),

        "max_latency_seconds": max(
            latencies
        ),

        "min_latency_seconds": min(
            latencies
        ),
    }