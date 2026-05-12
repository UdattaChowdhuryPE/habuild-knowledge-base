#!/usr/bin/env python3
"""Bulk ingest documents from a local directory into Supabase."""

import argparse
import sys
from pathlib import Path
from io import BytesIO

from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv("backend/.env")
load_dotenv("frontend-next/.env", override=False)

import PyPDF2
from docx import Document

from backend.services.rag import index_document
from backend.services.db import db

VALID_LOCATIONS = {"Gurugram", "Nagpur", "Bangalore", "Remote"}
VALID_CATEGORIES = {
    "Health Insurance",
    "Leave Policy",
    "Employee Handbook",
    "Benefits Guide",
    "Claims & Reimbursement",
    "Onboarding",
    "Payroll & Tax",
    "Compliance",
    "General",
}


def extract_text(path: Path) -> str:
    """Extract text from PDF, DOCX, or TXT file."""
    data = path.read_bytes()
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PyPDF2.PdfReader(BytesIO(data))
        return "\n\n".join(
            page.extract_text() or "" for page in reader.pages
        )
    elif suffix in (".docx", ".doc"):
        doc = Document(BytesIO(data))
        return "\n".join(para.text for para in doc.paragraphs)
    else:  # .txt
        return data.decode("utf-8", errors="ignore")


def main():
    parser = argparse.ArgumentParser(description="Bulk ingest documents into Supabase.")
    parser.add_argument(
        "--dir", default=".", help="Directory to scan for documents (default: .)"
    )
    parser.add_argument(
        "--locations",
        nargs="+",
        default=["Gurugram", "Nagpur", "Bangalore", "Remote"],
        help="Locations to apply (default: all four)",
    )
    parser.add_argument(
        "--category", default="General", help="Category for all documents (default: General)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview files without ingesting"
    )
    args = parser.parse_args()

    # Normalize and validate locations
    locations = [loc.strip().title() for loc in args.locations]
    invalid = set(locations) - VALID_LOCATIONS
    if invalid:
        sys.exit(f"Invalid locations: {invalid}. Valid: {VALID_LOCATIONS}")

    # Validate category
    if args.category not in VALID_CATEGORIES:
        sys.exit(f"Invalid category. Valid: {VALID_CATEGORIES}")

    # Find all eligible files
    exts = {".pdf", ".docx", ".doc", ".txt"}
    dir_path = Path(args.dir)
    files = sorted(
        [p for p in dir_path.rglob("*") if p.suffix.lower() in exts and p.is_file()]
    )

    print(f"Found {len(files)} file(s) in '{args.dir}'")

    if args.dry_run:
        for f in files:
            print(f"  {f.relative_to(dir_path)}")
        return

    if not files:
        print("No files to ingest.")
        return

    ok = 0
    failed = []

    for path in files:
        # Derive title from filename
        title = (
            path.stem.replace("_", " ")
            .replace("-", " ")
            .replace("/", " ")
            .title()
        )

        print(f"  Ingesting: {path.name} ...", end=" ", flush=True)

        try:
            # Extract text
            text = extract_text(path)
            if not text.strip():
                print("SKIP (no text extracted)")
                failed.append((path.name, "empty text"))
                continue

            # Create document metadata
            doc = db.create_document(
                title=title,
                category=args.category,
                file_name=path.name,
                file_url="",
                locations=locations,
            )

            # Index content (chunk, embed, store)
            index_document(
                source_id=doc["id"],
                source_type="document",
                source_title=title,
                text=text,
                locations=locations,
            )

            print("OK")
            ok += 1

        except Exception as e:
            print(f"FAIL ({e})")
            failed.append((path.name, str(e)))

    # Summary
    print(f"\nDone: {ok} ingested, {len(failed)} failed")
    if failed:
        for name, err in failed:
            print(f"  FAIL {name}: {err}")


if __name__ == "__main__":
    main()
