# Acceptance Criteria
# 3GPP RAG Acceptance Criteria

## Retrieval

- Recall@5 should be measured on manually validated gold evidence.
- Specification filtering must never return evidence from an excluded specification.

## Refusal

- Out-of-domain questions must be refused.
- Related-but-unsupported questions must be refused.
- Adversarial external-knowledge questions must be refused.

## Citations

- Every answerable response must contain citations.
- Every citation must reference a retrieved chunk.
- Document, version, section, and page metadata must match the retrieved chunk.

## Claim Verification

- Every factual claim must be individually verified.
- Any unsupported factual claim invalidates the complete response.
- An invalid response must not be shown to the user.

## Final Safety Property

The application must never return a final answer containing
a claim that failed the evidence-verification layer.