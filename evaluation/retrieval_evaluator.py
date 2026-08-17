from __future__ import annotations

import json
from pathlib import Path

from src.retrieval.bm25_index import BM25Index
from src.retrieval.embedder import BGEEmbedder
from src.retrieval.hybrid_config import (
    HybridRetrievalConfig,
)
from src.retrieval.hybrid_retriever import (
    Hybrid3GPPRetriever,
)
from src.retrieval.qdrant_store import QdrantStore
from src.retrieval.reranker import BGEReranker

from evaluation.schema import (
    EvaluationQuestion,
)


DATASET_PATH = Path(
    "evaluation/datasets/questions.json"
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


def recall_at_k(
    retrieved_ids: list[str],
    gold_ids: list[str],
    k: int,
) -> float:

    if not gold_ids:
        return 0.0

    retrieved = set(
        retrieved_ids[:k]
    )

    gold = set(
        gold_ids
    )

    return (
        1.0
        if retrieved.intersection(gold)
        else 0.0
    )


def main() -> None:

    questions = load_dataset()

    embedder = BGEEmbedder()

    qdrant = QdrantStore()

    bm25 = BM25Index()

    bm25.load_or_build()

    reranker = BGEReranker()

    retriever = Hybrid3GPPRetriever(
        embedder=embedder,
        qdrant_store=qdrant,
        bm25_index=bm25,
        reranker=reranker,
        config=HybridRetrievalConfig(
            final_k=5
        ),
    )

    results = []

    for question in questions:

        retrieved, decision = (
            retriever.retrieve(
                query=question.question,
                specification=(
                    question.specification
                ),
            )
        )

        retrieved_ids = [
            item.chunk_id
            for item in retrieved
        ]

        results.append(
            {
                "id": question.id,
                "question": question.question,
                "type": question.type,
                "expected_answerable": (
                    question.expected_answerable
                ),
                "evidence_allowed": (
                    decision.allowed
                ),
                "best_score": (
                    decision.best_score
                ),
                "strong_evidence_count": (
                    decision.strong_evidence_count
                ),
                "retrieved_chunk_ids": (
                    retrieved_ids
                ),
                "recall_at_5": recall_at_k(
                    retrieved_ids,
                    question.gold_chunk_ids,
                    5,
                ),
            }
        )

    output_path = Path(
        "evaluation/reports/retrieval_results.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()