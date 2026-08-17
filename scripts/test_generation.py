from __future__ import annotations

import sys

from src.pipeline import ThreeGPPRAG


def main() -> None:

    if len(sys.argv) < 2:

        print(
            'Usage:\n'
            'python scripts/test_generation.py '
            '"your question"'
        )

        return

    question = " ".join(
        sys.argv[1:]
    )

    rag = ThreeGPPRAG()

    result = rag.ask(
        question
    )

    print("\n" + "=" * 80)
    print("3GPP GROUNDED ANSWER")
    print("=" * 80)

    print(
        f"\nQuestion:\n{question}"
    )

    print(
        f"\nAnswerable: "
        f"{result.answer.answerable}"
    )

    print(
        f"\nAnswer:\n"
        f"{result.answer.answer}"
    )

    print(
        "\nCitations:"
    )

    citations = (
        getattr(result, "trusted_citations", None)
        or result.answer.citations
    )

    for citation in citations:

        # TrustedCitation dataclass contains full metadata; fallback to
        # minimal Citation which only has chunk_id.
        spec = getattr(citation, "specification", None)
        if spec is None:
            print(f"- chunk_id: {citation.chunk_id}")
            continue

        print(
            f"- {citation.specification} "
            f"{citation.version}, "
            f"Section {citation.section}, "
            f"Pages "
            f"{citation.page_start}-"
            f"{citation.page_end}"
        )

    print(
        "\nEvidence decision:"
    )

    print(
        result.evidence_decision.reason
    )

    print(
        f"Best score: "
        f"{result.evidence_decision.best_score:.4f}"
    )

    print(
        f"Strong evidence: "
        f"{result.evidence_decision.strong_evidence_count}"
    )

    print(
        f"\nCitation valid: "
        f"{result.citation_valid}"
    )

    if result.citation_errors:

        print(
            "\nCitation errors:"
        )

        for error in result.citation_errors:

            print(
                f"- {error}"
            )

    if (
        result.citation_errors
    ):

        print(
            "\nVerification/Citation errors:"
        )

        for error in result.citation_errors:

            print(
                f"- {error}"
            )



    print(
        "\nRetrieved evidence:"
    )

    for result in result.evidence:

        print(
            f"- {result.chunk_id} | "
            f"{result.specification} | "
            f"Section {result.section_number} | "
            f"Page {result.page_start}"
        )


if __name__ == "__main__":
    main()