from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkConfig:
    """
    Configuration for 3GPP-aware chunking.
    """

    # Approximate character target.
    # We use characters at this stage rather than tokens,
    # because the final embedding model will tokenize later.
    target_chars: int = 4200

    # Never create normal text chunks above this size
    # unless the block is a table.
    max_chars: int = 6000

    # Tiny fragments are merged with neighboring content.
    min_chars: int = 500

    # Amount of overlap between normal chunks.
    overlap_chars: int = 500

    # Tables are treated as independent retrieval units.
    keep_tables_atomic: bool = True

    # Include neighboring context when creating the
    # embedding text representation.
    include_context: bool = True