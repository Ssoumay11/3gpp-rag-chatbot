from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ChunkStore:
    """
    Persist generated chunks locally.
    """

    def __init__(
        self,
        directory: str = "data/chunks",
    ) -> None:

        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        document_id: str,
        chunks: list[dict[str, Any]],
    ) -> Path:

        path = (
            self.directory
            / f"{document_id}.jsonl"
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for chunk in chunks:

                file.write(
                    json.dumps(
                        chunk,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        return path

    def load(
        self,
        document_id: str,
    ) -> list[dict[str, Any]]:

        path = (
            self.directory
            / f"{document_id}.jsonl"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Chunk file not found: {path}"
            )

        chunks: list[
            dict[str, Any]
        ] = []

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if line:
                    chunks.append(
                        json.loads(line)
                    )

        return chunks