from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ParsedDocumentStore:
    """
    Stores canonical parsed content locally.

    JSONL is used because it handles large documents without
    requiring the entire corpus to be loaded into memory.
    """

    def __init__(
        self,
        directory: str = "data/parsed",
    ):
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def path_for(
        self,
        document_id: str,
    ) -> Path:
        return self.directory / (
            f"{document_id}.jsonl"
        )

    def save(
        self,
        document_id: str,
        records: list[dict[str, Any]],
    ) -> Path:

        output_path = self.path_for(document_id)

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for record in records:
                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        return output_path