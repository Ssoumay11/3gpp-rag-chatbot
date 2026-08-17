# Chunking logic
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .chunk_config import ChunkConfig
from .text_utils import (
    is_table,
    normalize_text,
    split_paragraphs,
)


class ThreeGPPChunker:
    """
    Section-aware chunker for 3GPP standards.

    Important properties:

    1. Does not mix unrelated sections.
    2. Keeps tables atomic.
    3. Preserves document/page metadata.
    4. Adds controlled overlap.
    5. Produces stable chunk IDs.
    """

    def __init__(
        self,
        config: ChunkConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else ChunkConfig()
        )

    def chunk(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not records:
            return []

        chunks: list[dict[str, Any]] = []

        current_section = None
        section_records: list[dict[str, Any]] = []

        for record in records:

            section_key = (
                record.get("section_number", ""),
                record.get("section_title", ""),
            )

            # Heading itself marks a new section context.
            if record.get("content_type") == "heading":

                # Flush previous section.
                chunks.extend(
                    self._chunk_section(
                        section_records,
                    )
                )

                section_records = []

                current_section = section_key

                continue

            record_section = (
                record.get("section_number", ""),
                record.get("section_title", ""),
            )

            # If the section changed without an explicit heading,
            # flush the previous section.
            if (
                current_section is not None
                and record_section != current_section
            ):

                chunks.extend(
                    self._chunk_section(
                        section_records,
                    )
                )

                section_records = []

                current_section = record_section

            if current_section is None:
                current_section = record_section

            section_records.append(record)

        # Flush final section.
        chunks.extend(
            self._chunk_section(
                section_records,
            )
        )

        # Stable global IDs.
        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            document_id = chunk.get(
                "document_id",
                "unknown",
            )

            chunk["chunk_id"] = (
                f"{document_id}_{index:06d}"
            )

            chunk["chunk_index"] = index

        return chunks

    def _chunk_section(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not records:
            return []

        result: list[dict[str, Any]] = []

        # Tables are handled separately.
        current_blocks: list[dict[str, Any]] = []

        for record in records:

            text = normalize_text(
                record.get("text", "")
            )

            if not text:
                continue

            table = (
                record.get("content_type") == "table"
                or is_table(text)
            )

            if table and self.config.keep_tables_atomic:

                # Flush prose before the table.
                if current_blocks:
                    result.extend(
                        self._chunk_prose(
                            current_blocks
                        )
                    )

                    current_blocks = []

                result.append(
                    self._create_table_chunk(
                        record
                    )
                )

            else:
                current_blocks.append(
                    {
                        **record,
                        "text": text,
                    }
                )

        # Flush remaining prose.
        if current_blocks:
            result.extend(
                self._chunk_prose(
                    current_blocks
                )
            )

        return result

    def _chunk_prose(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not records:
            return []

        paragraphs: list[dict[str, Any]] = []

        for record in records:

            text = normalize_text(
                record.get("text", "")
            )

            if not text:
                continue

            paragraphs.append(
                {
                    **record,
                    "text": text,
                }
            )

        chunks: list[dict[str, Any]] = []

        current_records: list[dict[str, Any]] = []
        current_size = 0

        for record in paragraphs:

            text = record["text"]
            text_size = len(text)

            # A huge individual paragraph must be split.
            if text_size > self.config.max_chars:

                # Flush existing material.
                if current_records:
                    chunks.append(
                        self._create_text_chunk(
                            current_records
                        )
                    )

                    current_records = []
                    current_size = 0

                long_parts = self._split_large_text(
                    text
                )

                for part in long_parts:

                    piece = {
                        **record,
                        "text": part,
                    }

                    chunks.append(
                        self._create_text_chunk(
                            [piece]
                        )
                    )

                continue

            # Normal accumulation.
            if (
                current_records
                and current_size + text_size
                > self.config.target_chars
            ):

                chunks.append(
                    self._create_text_chunk(
                        current_records
                    )
                )

                # Retain overlap from the last record.
                overlap_records = (
                    self._make_overlap(
                        current_records
                    )
                )

                current_records = overlap_records

                current_size = sum(
                    len(
                        item["text"]
                    )
                    for item in current_records
                )

            current_records.append(record)

            current_size += text_size

        if current_records:

            chunks.append(
                self._create_text_chunk(
                    current_records
                )
            )

        return self._merge_small_chunks(
            chunks
        )

    def _split_large_text(
        self,
        text: str,
    ) -> list[str]:

        words = text.split()

        if not words:
            return []

        parts: list[str] = []
        current: list[str] = []
        current_size = 0

        for word in words:

            addition = (
                len(word)
                + (1 if current else 0)
            )

            if (
                current
                and current_size + addition
                > self.config.target_chars
            ):

                parts.append(
                    " ".join(current)
                )

                # Simple word-level overlap.
                overlap_words = (
                    current[-40:]
                    if len(current) > 40
                    else current
                )

                current = overlap_words.copy()

                current_size = len(
                    " ".join(current)
                )

            current.append(word)
            current_size += addition

        if current:
            parts.append(
                " ".join(current)
            )

        return parts

    def _make_overlap(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not records:
            return []

        overlap: list[dict[str, Any]] = []
        size = 0

        for record in reversed(records):

            text = record["text"]

            if (
                size + len(text)
                > self.config.overlap_chars
            ):
                break

            overlap.insert(
                0,
                record,
            )

            size += len(text)

        return overlap

    def _merge_small_chunks(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if len(chunks) <= 1:
            return chunks

        merged: list[dict[str, Any]] = []

        for chunk in chunks:

            if (
                merged
                and len(chunk["text"])
                < self.config.min_chars
            ):

                previous = merged[-1]

                # Do not merge across sections.
                if (
                    previous.get("section_number")
                    == chunk.get("section_number")
                ):

                    previous["text"] = (
                        previous["text"]
                        + "\n\n"
                        + chunk["text"]
                    )

                    previous["page_end"] = max(
                        previous.get(
                            "page_end",
                            previous.get(
                                "page_start",
                                0,
                            ),
                        ),
                        chunk.get(
                            "page_end",
                            chunk.get(
                                "page_start",
                                0,
                            ),
                        ),
                    )

                    continue

            merged.append(chunk)

        return merged

    def _create_text_chunk(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:

        first = records[0]
        last = records[-1]

        text = "\n\n".join(
            record["text"]
            for record in records
        )

        return {
            "text": text,
            "content_type": "text",
            "document_id": first.get(
                "document_id"
            ),
            "specification": first.get(
                "specification"
            ),
            "version": first.get(
                "version"
            ),
            "section_number": first.get(
                "section_number",
                "",
            ),
            "section_title": first.get(
                "section_title",
                "",
            ),
            "page_start": first.get(
                "page_number"
            ),
            "page_end": last.get(
                "page_number"
            ),
            "parser": first.get(
                "parser"
            ),
            "source_file": first.get(
                "source_file"
            ),
        }

    def _create_table_chunk(
        self,
        record: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "text": normalize_text(
                record["text"]
            ),
            "content_type": "table",
            "document_id": record.get(
                "document_id"
            ),
            "specification": record.get(
                "specification"
            ),
            "version": record.get(
                "version"
            ),
            "section_number": record.get(
                "section_number",
                "",
            ),
            "section_title": record.get(
                "section_title",
                "",
            ),
            "page_start": record.get(
                "page_number"
            ),
            "page_end": record.get(
                "page_number"
            ),
            "parser": record.get(
                "parser"
            ),
            "source_file": record.get(
                "source_file"
            ),
        }