from __future__ import annotations

import json
from pathlib import Path

from evaluation.metrics import (
    calculate_metrics,
)


RESULT_PATH = Path(
    "evaluation/reports/"
    "end_to_end_results.json"
)

REPORT_PATH = Path(
    "evaluation/reports/"
    "evaluation_report.json"
)


def main() -> None:

    results = json.loads(
        RESULT_PATH.read_text(
            encoding="utf-8"
        )
    )

    metrics = calculate_metrics(
        results
    )

    report = {
        "metrics": metrics,
        "questions": results,
    }

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("=" * 70)
    print("3GPP RAG Evaluation")
    print("=" * 70)

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )

    print(
        f"\nSaved: {REPORT_PATH}"
    )


if __name__ == "__main__":
    main()