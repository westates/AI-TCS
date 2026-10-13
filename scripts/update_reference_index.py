"""Build a catalog, checksums, and page-marked text without modifying source PDFs."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
# Labels were checked against the supplied copies; review them when editions change.
LABELS = {
    "11thcovtoc.pdf": ("MUTCD cover and table of contents", "December 2023"),
    "appendices.pdf": ("MUTCD appendices", "December 2023"),
    "Chapter2a.pdf": ("MUTCD Chapter 2A - General signs", "December 2023"),
    "Chapter2b.pdf": ("MUTCD Chapter 2B - Regulatory signs, barricades, and gates", "December 2023"),
    "Chapter2c.pdf": ("MUTCD Chapter 2C - Warning signs and object markers", "December 2023"),
    "Chapter2d.pdf": ("MUTCD Chapter 2D - Guide signs, conventional roads", "December 2023"),
    "Chapter2e.pdf": ("MUTCD Chapter 2E - Guide signs, freeways and expressways", "December 2023"),
    "Chapter2f.pdf": ("MUTCD Chapter 2F - Toll road signs", "December 2023"),
    "Chapter2g.pdf": ("MUTCD Chapter 2G - Preferential and managed lane signs", "December 2023"),
    "Chapter2hthu2n.pdf": ("MUTCD Chapters 2H through 2N", "December 2023"),
    "MUTCD11-OR-Supplement.pdf": ("Oregon Supplement to the MUTCD, 11th Edition", "January 2026"),
    "mutcd11thedition.pdf": ("MUTCD, 11th Edition - full volume", "December 2023"),
    "OTTCH-2026.pdf": ("Oregon Temporary Traffic Control Handbook - operations of three days or less", "2026 edition"),
    "part1.pdf": ("MUTCD Part 1 - General", "December 2023"),
    "part3.pdf": ("MUTCD Part 3 - Markings", "December 2023"),
    "part4.pdf": ("MUTCD Part 4 - Highway traffic signals", "December 2023"),
    "part5.pdf": ("MUTCD Part 5 - Traffic control device considerations for automated vehicles", "December 2023"),
    "part6.pdf": ("MUTCD Part 6 - Temporary traffic control", "December 2023"),
    "part7.pdf": ("MUTCD Part 7 - Traffic control for school areas", "December 2023"),
    "part8.pdf": ("MUTCD Part 8 - Railroad and light rail transit grade crossings", "December 2023"),
    "part9.pdf": ("MUTCD Part 9 - Bicycle facilities", "December 2023"),
    "TPAR Manual (1-28-26).pdf": ("Eugene Temporary Pedestrian Accessible Routes Manual: Access for People with Disabilities", "January 28, 2026"),
}


def write_utf8(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    pdfs = sorted((ROOT / "Rulebooks").glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdfs:
        raise SystemExit("No PDFs found in Rulebooks/.")
    text_dir = ROOT / "Text"
    text_dir.mkdir(exist_ok=True)
    entries = []
    for pdf in pdfs:
        reader = PdfReader(pdf)
        metadata = reader.metadata or {}
        title, edition = LABELS.get(pdf.name, (pdf.stem, "Unverified - inspect document"))
        text_path = text_dir / f"{pdf.stem}.txt"
        source = pdf.relative_to(ROOT).as_posix()
        pages = []
        sparse_pages = []
        for page_number, page in enumerate(reader.pages, 1):
            text = unicodedata.normalize("NFKC", page.extract_text() or "").strip()
            if len("".join(text.split())) < 40:
                sparse_pages.append(page_number)
            pages.append(f"=== PDF PAGE {page_number} ===\n{text}\n")
        header = (
            f"Title: {title}\nStored edition/date: {edition}\nSource: {source}\n"
            "Generated text for search. Verify requirements, diagrams, tables, symbols, and quotes in the original PDF.\n"
            "Page markers identify physical PDF pages; printed document page numbers may differ.\n\n"
        )
        write_utf8(text_path, header + "\n".join(pages))
        with pdf.open("rb") as stream:
            checksum = hashlib.file_digest(stream, "sha256").hexdigest()
        entry = {
            "source": source,
            "text": text_path.relative_to(ROOT).as_posix(),
            "title": title,
            "stored_edition_or_date": edition,
            "metadata_title": str(metadata.get("/Title", "")),
            "pages": len(reader.pages),
            "bytes": pdf.stat().st_size,
            "sha256": checksum,
            "pages_with_little_or_no_extracted_text": sparse_pages,
        }
        entries.append(entry)
        print(f"Indexed {pdf.name}: {entry['pages']} pages", flush=True)

    manifest = {
        "schema_version": 1,
        "source_count": len(entries),
        "total_source_bytes": sum(e["bytes"] for e in entries),
        "page_numbering": "Physical PDF pages, counting the first page as 1; printed numbers may differ.",
        "documents": entries,
    }
    write_utf8(ROOT / "reference-manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    lines = [
        "# Reference document catalog", "",
        "Generated from `Rulebooks/` by `scripts/update_reference_index.py`.", "",
        "Edition labels describe the stored copies. Verify current governing editions with the controlling agency.", "",
        "Original PDFs preserve figures and formatting. Text copies are for search and use physical PDF page markers.", "",
        "| Document | Stored edition/date | PDF pages | Original | Searchable text |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['title']} | {entry['stored_edition_or_date']} | {entry['pages']} | "
            f"[{Path(entry['source']).name}]({quote(entry['source'])}) | [Text]({quote(entry['text'])}) |"
        )
    lines += [
        "", f"Total: **{len(entries)} PDFs**, **{manifest['total_source_bytes']:,} bytes**.", "",
        "## Extraction limitations", "",
        "The following physical PDF pages contain fewer than 40 non-whitespace extracted characters. They may be blank, diagram-only, or scanned. Other pages may also contain visual information absent from the text copy.", "",
    ]
    for entry in entries:
        sparse = entry["pages_with_little_or_no_extracted_text"]
        if sparse:
            lines.append(f"- `{Path(entry['source']).name}`: " + ", ".join(map(str, sparse)))
    lines += [
        "", "## Integrity", "",
        "`reference-manifest.json` records each original PDF's SHA-256 checksum, byte count, and page count. Rebuild the manifest and text when a source file changes.", "",
    ]
    write_utf8(ROOT / "REFERENCES.md", "\n".join(lines))


if __name__ == "__main__":
    main()
