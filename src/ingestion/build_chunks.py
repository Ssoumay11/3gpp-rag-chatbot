from __future__ import annotations

import json
from pathlib import Path

from .chunk_config import ChunkConfig
from .chunk_storage import ChunkStore
from .chunker import ThreeGPPChunker
from .embedding_text import build_embedding_text


PARSED_DIR = Path("data/parsed")


def load_jsonl(
    path: Path,
) -> list[dict]:

    records: list[dict] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def process_file(
    parsed_path: Path,
    chunk_store: ChunkStore,
    chunker: ThreeGPPChunker,
) -> None:

    document_id = parsed_path.stem

    print("\n" + "=" * 70)
    print(
        f"Chunking: {parsed_path.name}"
    )
    print("=" * 70)

    records = load_jsonl(
        parsed_path
    )

    print(
        f"Parsed records: {len(records)}"
    )

    chunks = chunker.chunk(
        records
    )

    # Add embedding representation.
    for chunk in chunks:

        chunk["embedding_text"] = (
            build_embedding_text(
                chunk
            )
        )

    output_path = chunk_store.save(
        document_id,
        chunks,
    )

    # Statistics.
    text_count = sum(
        1
        for chunk in chunks
        if chunk.get("content_type")
        == "text"
    )

    table_count = sum(
        1
        for chunk in chunks
        if chunk.get("content_type")
        == "table"
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    print(
        f"Text chunks: {text_count}"
    )

    print(
        f"Table chunks: {table_count}"
    )

    print(
        f"Saved: {output_path}"
    )


def main() -> None:

    PARSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    parsed_files = sorted(
        PARSED_DIR.glob("*.jsonl")
    )

    if not parsed_files:

        print(
            "No parsed JSONL files found."
        )

        print(
            "Run Phase 2 first:"
        )

        print(
            "python -m src.ingestion.ingest"
        )

        return

    config = ChunkConfig()

    chunker = ThreeGPPChunker(
        config=config
    )

    chunk_store = ChunkStore()

    for parsed_path in parsed_files:

        process_file(
            parsed_path,
            chunk_store,
            chunker,
        )

    print(
        "\nPhase 3 chunking complete."
    )


if __name__ == "__main__":
    main()