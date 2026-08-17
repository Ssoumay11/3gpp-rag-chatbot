from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalConfig:
    # Number returned to the application.
    top_k: int = 5

    # Retrieve more candidates internally.
    # Later this gives us room for reranking.
    candidate_k: int = 15

    # Minimum similarity accepted by the retrieval layer.
    #
    # This is NOT our final hallucination threshold.
    # It is only a retrieval-quality signal.
    score_threshold: float = 0.35

    # Return payload/evidence.
    with_payload: bool = True

    # Do not return vectors to the application.
    with_vectors: bool = False