from __future__ import annotations

import json
from pathlib import Path


REPORT_PATH = Path(
    "evaluation/reports/"
    "evaluation_report.json"
)


def main() -> None:

    report = json.loads(
        REPORT_PATH.read_text(
            encoding="utf-8"
        )
    )

    metrics = report["metrics"]

    checks = {
        "answerability_accuracy": (
            metrics.get(
                "answerability_accuracy",
                0.0,
            )
            >= 0.95
        ),

        "refusal_accuracy": (
            metrics.get(
                "refusal_accuracy",
                0.0,
            )
            >= 0.98
        ),

        "citation_valid_rate": (
            metrics.get(
                "citation_valid_rate",
                0.0,
            )
            >= 1.0
        ),

        "unsupported_claim_rate": (
            metrics.get(
                "unsupported_claim_rate",
                1.0,
            )
            == 0.0
        ),
    }

    print(
        "=" * 70
    )

    print(
        "3GPP RAG ACCEPTANCE TEST"
    )

    print(
        "=" * 70
    )

    for name, passed in checks.items():

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"{name}: {status}"
        )

    overall = all(
        checks.values()
    )

    print(
        "\nOverall: "
        + (
            "PASS"
            if overall
            else "FAIL"
        )
    )

    if not overall:
        raise SystemExit(1)


if __name__ == "__main__":
    main()