from __future__ import annotations


ZERO_UNSUPPORTED_CLAIMS_POLICY = """
FINAL SAFETY POLICY:

An answer may be returned only when:

1. Retrieval evidence passed the evidence gate.
2. The draft answer has valid citations.
3. Every factual claim was extracted.
4. Every factual claim was individually verified.
5. Every factual claim has explicit evidence.
6. No citation references an unavailable chunk.
7. No unsupported claim remains.

If any condition fails, return the standard refusal.

Never weaken these conditions to produce an answer.
"""