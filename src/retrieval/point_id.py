from __future__ import annotations

import hashlib


def stable_point_id(chunk_id: str) -> int:
    """
    Convert chunk ID into a deterministic positive integer
    suitable for Qdrant point IDs.
    """

    digest = hashlib.sha256(
        chunk_id.encode("utf-8")
    ).hexdigest()

    # Use first 16 hex characters.
    value = int(
        digest[:16],
        16,
    )

    # Keep inside signed 63-bit integer range.
    return value & ((1 << 63) - 1)