# LlamaParse parser module
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from llama_cloud_services import LlamaParse

from scripts.test_llamaparse import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env", override=True)



class LlamaParseParser:
    """
    Primary parser.

    Uses LlamaParse to convert complex technical PDFs
    into Markdown while retaining page-level structure.
    """

    def __init__(self) -> None:
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")

        if not api_key:
            raise RuntimeError(
                "LLAMA_CLOUD_API_KEY is not configured in .env"
            )

        self.parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
            language="en",
            num_workers=2,
            verbose=True,
        )

    def parse(self, pdf_path: str | Path) -> list[dict[str, Any]]:
        """
        Parse a PDF and return page-level Markdown records.
        """

        pdf_path = str(pdf_path)

        print(f"[LlamaParse] Parsing: {pdf_path}")

        result = self.parser.parse(pdf_path)

        # Current Llama Cloud parsing results provide Markdown
        # documents through get_markdown_documents().
        documents = result.get_markdown_documents(
            split_by_page=True
        )

        if not documents:
            raise RuntimeError(
                "LlamaParse returned no Markdown documents."
            )

        records: list[dict[str, Any]] = []

        for index, document in enumerate(documents, start=1):
            text = getattr(document, "text", "") or ""

            metadata = getattr(document, "metadata", {}) or {}

            if not text.strip():
                continue

            records.append(
                {
                    "page_number": metadata.get(
                        "page_number",
                        index,
                    ),
                    "text": text,
                    "parser": "llamaparse",
                    "parser_metadata": metadata,
                }
            )

        if not records:
            raise RuntimeError(
                "LlamaParse returned documents but no usable text."
            )

        return records