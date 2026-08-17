from __future__ import annotations

import json
import time
from pathlib import Path

from src.pipeline import ThreeGPPRAG

from evaluation.schema import (
    EvaluationQuestion,
)


DATASET_PATH = Path(
    "evaluation/datasets/questions.json"
)


REFUSAL_TEXT = (
    "I could not find sufficient supporting "
    "information in the provided 3GPP documents."
)


def load_dataset() -> list[EvaluationQuestion]:

    data = json.loads(
        DATASET_PATH.read_text(
            encoding="utf-8"
        )
    )

    return [
        EvaluationQuestion.model_validate(
            item
        )
        for item in data
    ]


def main() -> None:

    questions = load_dataset()

    rag = ThreeGPPRAG()

    results = []

    for index, question in enumerate(
        questions,
        start=1,
    ):

        print(
            f"\n[{index}/{len(questions)}] "
            f"{question.id}"
        )

        start = time.perf_counter()

        try:

            result = rag.ask(
                question.question
            )

            total_claims = 0
            unsupported_claims = 0
            verification_passed = None
            if result.verification:
                verification_passed = (
                    result.verification.passed
                )
                if result.verification.verification:
                    total_claims = len(
                        result.verification.verification.claims
                    )
                    unsupported_claims = sum(
                        1
                        for claim
                        in result.verification.verification.claims
                        if not claim.supported
                    )
            elapsed = (
                time.perf_counter()
                - start
            )

            predicted_answerable = (
                result.answer.answerable
            )

            expected = (
                question.expected_answerable
            )

            answerability_correct = (
                predicted_answerable
                == expected
            )

            refusal_correct = (
                (
                    not expected
                    and result.answer.answer
                    == REFUSAL_TEXT
                )
                or expected
            )

            results.append(
                {
                    "id": question.id,
                    "question": question.question,
                    "type": question.type,
                    "expected_answerable": expected,
                    "predicted_answerable": (
                        predicted_answerable
                    ),
                    "answerability_correct": (
                        answerability_correct
                    ),
                    "refusal_correct": (
                        refusal_correct
                    ),
                    "answer": result.answer.answer,
                    "citation_valid": (
                        result.citation_valid
                    ),
                    "citation_errors": (
                        result.citation_errors
                    ),
                    "evidence_allowed": (
                        result.evidence_decision.allowed
                    ),
                    "best_evidence_score": (
                        result.evidence_decision.best_score
                    ),
                    "strong_evidence_count": (
                        result.evidence_decision
                        .strong_evidence_count
                    ),
                    "latency_seconds": elapsed,
                    "total_claims": total_claims,
                    "unsupported_claims": unsupported_claims,
                    "verification_passed": verification_passed,
                    "unsupported_claim_rate": (
                        unsupported_claims / total_claims
                        if total_claims > 0
                        else 0.0
                    ),
                }
            )

            print(
                f"Evidence allowed: "
                f"{result.evidence_decision.allowed}"
            )

            print(
                f"Evidence reason: "
                f"{result.evidence_decision.reason}"
            )

            print(
                f"Best evidence score: "
                f"{result.evidence_decision.best_score:.4f}"
            )

            print(
                f"Strong evidence count: "
                f"{result.evidence_decision.strong_evidence_count}"
            )

            print(
                f"Latency: "
                f"{elapsed:.2f}s"
            )

        except Exception as exc:

            elapsed = (
                time.perf_counter()
                - start
            )

            results.append(
                {
                    "id": question.id,
                    "question": question.question,
                    "type": question.type,
                    "error": str(exc),
                    "latency_seconds": elapsed,
                }
            )

            print(
                f"ERROR: {exc}"
            )

    output_path = Path(
        "evaluation/reports/"
        "end_to_end_results.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nSaved: {output_path}"
    )


if __name__ == "__main__":
    main()