from dataclasses import dataclass


@dataclass(frozen=True)
class HybridRetrievalConfig:
    # Dense candidates from Qdrant.
    dense_k: int = 20

    # Lexical candidates from BM25.
    lexical_k: int = 20

    # Number of fused candidates passed to reranker.
    fusion_k: int = 20

    # Final number of evidence chunks.
    final_k: int = 5

    # RRF constant.
    rrf_k: int = 60

    # Relative importance during fusion.
    dense_weight: float = 0.55
    lexical_weight: float = 0.45

    # Reranker.
    reranker_model: str = "BAAI/bge-reranker-base"

    # Number of candidates passed to reranker.
    reranker_k: int = 15

    # Reranker score is model-dependent.
    # This is a preliminary gate and must be calibrated.
    reranker_threshold: float = 0.20

    # Evidence gate.
    minimum_evidence_chunks: int = 1
    minimum_strong_evidence_chunks: int = 1

    # Require supporting evidence from the same specification
    # when a question explicitly names one.
    enforce_specification_consistency: bool = True