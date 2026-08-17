from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi


CHUNK_DIR = Path("data/chunks")
INDEX_DIR = Path("data/bm25")


def tokenize(text: str) -> list[str]:
    """
    3GPP-friendly lexical tokenization.

    Keeps technical identifiers such as:
        AMF
        N2
        N3
        23.501
        5GC
        PDU-Session
        NAS
    """

    text = text.lower()

    # Preserve alphanumeric technical terms and
    # dotted identifiers.
    tokens = re.findall(
        r"[a-z0-9]+(?:[._/-][a-z0-9]+)*",
        text,
    )

    return tokens


class BM25Index:
    """
    Local persistent BM25 index over all generated chunks.
    """

    def __init__(
        self,
        index_path: str | Path = (
            "data/bm25/index.pkl"
        ),
    ) -> None:

        self.index_path = Path(
            index_path
        )

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.bm25: BM25Okapi | None = None
        self.chunks: list[dict[str, Any]] = []

    def build(self) -> None:

        chunk_files = sorted(
            CHUNK_DIR.glob("*.jsonl")
        )

        if not chunk_files:
            raise RuntimeError(
                "No chunk files found. "
                "Run Phase 3 first."
            )

        all_chunks: list[
            dict[str, Any]
        ] = []

        for path in chunk_files:

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                for line in file:

                    line = line.strip()

                    if line:
                        all_chunks.append(
                            json.loads(line)
                        )

        if not all_chunks:
            raise RuntimeError(
                "Chunk directory is empty."
            )

        corpus = [
            tokenize(
                chunk.get(
                    "embedding_text",
                    chunk.get(
                        "text",
                        "",
                    ),
                )
            )
            for chunk in all_chunks
        ]

        self.bm25 = BM25Okapi(
            corpus
        )

        self.chunks = all_chunks

        self.save()

        print(
            f"[BM25] Indexed "
            f"{len(all_chunks)} chunks."
        )

    def save(self) -> None:

        if self.bm25 is None:
            raise RuntimeError(
                "BM25 index is not initialized."
            )

        payload = {
            "bm25": self.bm25,
            "chunks": self.chunks,
        }

        with self.index_path.open(
            "wb"
        ) as file:

            pickle.dump(
                payload,
                file,
            )

    def load(self) -> None:

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"BM25 index not found: "
                f"{self.index_path}"
            )

        with self.index_path.open(
            "rb"
        ) as file:

            payload = pickle.load(file)

        self.bm25 = payload["bm25"]
        self.chunks = payload["chunks"]

        print(
            f"[BM25] Loaded "
            f"{len(self.chunks)} chunks."
        )

    def load_or_build(self) -> None:

        if self.index_path.exists():

            try:
                self.load()
                return

            except Exception as exc:

                print(
                    "[BM25] Existing index could "
                    "not be loaded."
                )

                print(
                    f"Reason: {exc}"
                )

        self.build()

    def search(
        self,
        query: str,
        top_k: int = 20,
        specification: str | None = None,
    ) -> list[tuple[int, float]]:

        if self.bm25 is None:
            raise RuntimeError(
                "BM25 index is not loaded."
            )

        query_tokens = tokenize(
            query
        )

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results: list[
            tuple[int, float]
        ] = []

        for index in ranked_indices:

            if len(results) >= top_k:
                break

            score = float(
                scores[index]
            )

            if score <= 0:
                continue

            chunk = self.chunks[index]

            if (
                specification
                and chunk.get(
                    "specification"
                )
                != specification
            ):
                continue

            results.append(
                (
                    index,
                    score,
                )
            )

        return results

    def chunk_at(
        self,
        index: int,
    ) -> dict[str, Any]:

        return self.chunks[index]