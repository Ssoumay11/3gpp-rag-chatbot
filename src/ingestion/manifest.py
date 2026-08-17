from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ManifestStore:
    """
    Stores ingestion state for each PDF.
    """

    def __init__(self, directory: str = "data/manifests"):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _manifest_path(
        self,
        document_id: str,
    ) -> Path:
        return self.directory / f"{document_id}.json"

    def load(
        self,
        document_id: str,
    ) -> dict[str, Any] | None:

        path = self._manifest_path(document_id)

        if not path.exists():
            return None

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save(
        self,
        document_id: str,
        data: dict[str, Any],
    ) -> None:

        path = self._manifest_path(document_id)

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )