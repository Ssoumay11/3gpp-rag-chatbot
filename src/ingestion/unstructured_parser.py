# Unstructured parser module
from __future__ import annotations

from pathlib import Path
from typing import Any

from markdownify import markdownify


def html_to_markdown(html: str) -> str:
    """
    Convert an HTML table into Markdown.
    """
    if not html.strip():
        return ""

    return markdownify(
        html,
        heading_style="ATX",
    ).strip()


class UnstructuredPDFParser:
    """
    Fallback parser.

    IMPORTANT:
    Unstructured is imported lazily inside parse().
    This prevents ONNX / ml_dtypes DLL issues from
    breaking the primary LlamaParse pipeline.
    """

    def parse(
        self,
        pdf_path: str | Path,
    ) -> list[dict[str, Any]]:

        # Lazy import.
        # It will only execute if LlamaParse fails.
        try:
            from unstructured.documents.elements import Table
            from unstructured.partition.pdf import partition_pdf
        except Exception as exc:
            raise RuntimeError(
                "Unstructured fallback is unavailable. "
                "Its dependencies could not be imported.\n"
                f"Original error: {exc}"
            ) from exc

        pdf_path = str(pdf_path)

        print(f"[Unstructured] Parsing: {pdf_path}")

        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            infer_table_structure=True,
            include_page_breaks=True,
        )

        if not elements:
            raise RuntimeError(
                "Unstructured returned no elements."
            )

        records: list[dict[str, Any]] = []

        for element in elements:

            text = getattr(
                element,
                "text",
                "",
            ) or ""

            metadata = getattr(
                element,
                "metadata",
                None,
            )

            page_number = None

            if metadata is not None:
                page_number = getattr(
                    metadata,
                    "page_number",
                    None,
                )

            category = getattr(
                element,
                "category",
                element.__class__.__name__,
            )

            # Preserve tables.
            if isinstance(element, Table):

                html = ""

                if metadata is not None:
                    html = getattr(
                        metadata,
                        "text_as_html",
                        "",
                    ) or ""

                if html:
                    text = html_to_markdown(html)

                category = "Table"

            if not text.strip():
                continue

            parser_metadata = {}

            if metadata is not None:
                try:
                    parser_metadata = metadata.to_dict()
                except Exception:
                    parser_metadata = {}

            records.append(
                {
                    "page_number": page_number,
                    "text": text,
                    "element_type": category,
                    "parser": "unstructured",
                    "parser_metadata": parser_metadata,
                }
            )

        if not records:
            raise RuntimeError(
                "Unstructured returned no usable content."
            )

        return records