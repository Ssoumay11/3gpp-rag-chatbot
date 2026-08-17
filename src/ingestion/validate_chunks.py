from __future__ import annotations

import json
import re
from pathlib import Path


CHUNK_DIR = Path(
    "data/chunks"
)


MOJIBAKE_MARKERS = (
    "Â",
    "â",
    "ð",
    "Ã",
)


BAD_HEADINGS = (
    "copyright notification",
    "foreword",
    "intellectual property rights",
)


def load_chunks(
    path: Path,
) -> list[dict]:

    chunks = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if line.strip():
                chunks.append(
                    json.loads(line)
                )

    return chunks


def check_chunk(
    chunk: dict,
) -> list[str]:

    problems = []

    text = chunk.get(
        "text",
        "",
    )

    title = chunk.get(
        "section_title",
        "",
    ).lower()

    # Encoding corruption
    if any(
        marker in text
        for marker in MOJIBAKE_MARKERS
    ):
        problems.append(
            "possible_mojibake"
        )

    # Front matter
    if any(
        heading in title
        for heading in BAD_HEADINGS
    ):
        problems.append(
            "nontechnical_section"
        )

    # Missing section metadata
    if not chunk.get(
        "section_number"
    ):
        problems.append(
            "missing_section_number"
        )

    # Excessive chunk length
    if len(text) > 7000:
        problems.append(
            "chunk_too_large"
        )

    return problems


def main() -> None:

    files = sorted(
        CHUNK_DIR.glob("*.jsonl")
    )

    total = 0
    bad = 0

    for path in files:

        chunks = load_chunks(path)

        print(
            f"\n{path.name}"
        )

        for chunk in chunks:

            total += 1

            problems = check_chunk(
                chunk
            )

            if problems:

                bad += 1

                print(
                    f"  {chunk.get('chunk_id')}: "
                    f"{problems}"
                )

    print("\n" + "=" * 60)

    print(
        f"Total chunks: {total}"
    )

    print(
        f"Problematic chunks: {bad}"
    )

    if total:
        print(
            f"Quality rate: "
            f"{((total - bad) / total) * 100:.2f}%"
        )


if __name__ == "__main__":
    main()