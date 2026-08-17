# Ingestion pipeline entrypoint
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from .unstructured_parser import UnstructuredPDFParser
from .llamaparse_parser import LlamaParseParser
from .manifest import ManifestStore
from .metadata import (
    calculate_sha256,
    extract_specification,
    extract_version,
)
from .section_processor import enrich_with_sections
from .storage import ParsedDocumentStore
from .unstructured_parser import UnstructuredPDFParser


RAW_DIR = Path("data/raw")


def build_document_id(
    pdf_path: Path,
) -> str:
    """
    Build a stable ID from specification + version.
    """

    spec = extract_specification(
        pdf_path.name
    )

    version = extract_version(
        pdf_path.name
    ) or "unknown"

    return (
        f"{spec.replace(' ', '_')}_{version}"
        .replace(".", "_")
    )


def parse_with_fallback(
    pdf_path: Path,
) -> tuple[list[dict[str, Any]], str]:

    # --------------------------------------------------
    # Primary parser: LlamaParse
    # --------------------------------------------------

    try:
        parser = LlamaParseParser()

        records = parser.parse(pdf_path)

        if records:
            return records, "llamaparse"

    except Exception as exc:
        print(
            "\n[LlamaParse] FAILED"
        )
        print(
            f"Reason: {exc}"
        )
        print(
            "[Pipeline] Switching to Unstructured..."
        )

    # --------------------------------------------------
    # Fallback parser: Unstructured
    # --------------------------------------------------

    fallback = UnstructuredPDFParser()

    records = fallback.parse(pdf_path)

    if not records:
        raise RuntimeError(
            f"No content extracted from {pdf_path}"
        )

    return records, "unstructured"


def process_pdf(
    pdf_path: Path,
    manifest_store: ManifestStore,
    parsed_store: ParsedDocumentStore,
) -> None:

    document_id = build_document_id(
        pdf_path
    )

    file_hash = calculate_sha256(
        pdf_path
    )

    specification = extract_specification(
        pdf_path.name
    )

    version = extract_version(
        pdf_path.name
    )

    print("\n" + "=" * 70)
    print(
        f"Processing: {pdf_path.name}"
    )
    print("=" * 70)

    # --------------------------------------------------
    # Check previous ingestion
    # --------------------------------------------------

    previous = manifest_store.load(
        document_id
    )

    if (
        previous
        and previous.get("sha256") == file_hash
    ):
        parsed_path = parsed_store.path_for(
            document_id
        )

        if parsed_path.exists():
            print(
                "[SKIP] PDF unchanged."
            )
            print(
                f"[LOAD] {parsed_path}"
            )
            return

    # --------------------------------------------------
    # Parse
    # --------------------------------------------------

    page_records, parser_name = (
        parse_with_fallback(pdf_path)
    )

    # --------------------------------------------------
    # Add permanent document metadata
    # --------------------------------------------------

    for record in page_records:

        record["document_id"] = document_id
        record["specification"] = specification
        record["version"] = version
        record["source_file"] = pdf_path.name
        record["source_path"] = str(pdf_path)
        record["sha256"] = file_hash

    # --------------------------------------------------
    # Section enrichment
    # --------------------------------------------------

    enriched_records = enrich_with_sections(
        page_records
    )

    # --------------------------------------------------
    # Save canonical parsed representation
    # --------------------------------------------------

    parsed_path = parsed_store.save(
        document_id,
        enriched_records,
    )

    # --------------------------------------------------
    # Manifest
    # --------------------------------------------------

    manifest_store.save(
        document_id,
        {
            "document_id": document_id,
            "filename": pdf_path.name,
            "specification": specification,
            "version": version,
            "sha256": file_hash,
            "parser": parser_name,
            "records": len(enriched_records),
            "parsed_file": str(parsed_path),
        },
    )

    print(
        f"[DONE] Parser: {parser_name}"
    )

    print(
        f"[DONE] Records: {len(enriched_records)}"
    )

    print(
        f"[DONE] Saved: {parsed_path}"
    )


def main() -> None:

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf_files = sorted(
        RAW_DIR.glob("*.pdf")
    )

    if not pdf_files:
        print(
            "No PDF files found in data/raw/"
        )
        print(
            "Add the four 3GPP PDFs first."
        )
        sys.exit(1)

    manifest_store = ManifestStore()

    parsed_store = ParsedDocumentStore()

    print(
        f"Found {len(pdf_files)} PDF file(s)."
    )

    for pdf_path in pdf_files:

        try:
            process_pdf(
                pdf_path,
                manifest_store,
                parsed_store,
            )

        except Exception as exc:

            print(
                f"\n[ERROR] {pdf_path.name}"
            )

            print(
                f"Reason: {exc}"
            )

    print(
        "\nIngestion phase complete."
    )


if __name__ == "__main__":
    main()