# MUTCD / OTTCH / TPAR Reference Library

Shared traffic-control reference documents for Oregon work, including Eugene temporary pedestrian accessible routes (TPARs).

Repository: <https://github.com/westates/AI-TCS>

GitHub holds the shared reference library. Save working documents and project deliverables locally in `Work/`, which is excluded from Git. Only share those deliverables if explicitly requested.

## Start here

- [Document catalog](REFERENCES.md): filenames, document labels, editions/dates, page counts, and links.
- [Original PDFs](Rulebooks/): the complete original files, preserved under their existing filenames.
- [Searchable text](Text/): generated text copies with a marker for every PDF page.
- [Project instructions](AGENTS.md): how to use the library for traffic-control research.
- [File manifest](reference-manifest.json): SHA-256 checksums and extraction statistics.

The PDFs are the reference originals. Text copies make passages easier to find in repository searches, but may omit diagrams, symbols, table structure, and scanned text. Verify measurements, drawings, signs, and quoted requirements on the original PDF pages. PDF page numbers in text markers count from the first physical page; the document's printed page numbers may differ.

## Use from another computer

```sh
git clone https://github.com/westates/AI-TCS.git
cd AI-TCS
```

Open that checkout as the project folder in Codex or another repository-aware tool. The project instructions and reference files travel with the checkout. Update a clean checkout with:

```sh
git pull --ff-only
```

In a ChatGPT experience with GitHub access, connect and authorize `westates/AI-TCS`, and identify this repository in your request. Start with `README.md`, `AGENTS.md`, and `REFERENCES.md`; use the `Text/` files to locate passages and consult the PDFs for visual details. A link alone does not establish a tool's access to private files or its ability to render PDFs.

Suggested project instructions to copy into a new reference project:

> Use https://github.com/westates/AI-TCS as the reference library. Read AGENTS.md and REFERENCES.md first. Search the Text folder to locate passages, then verify relevant pages, figures, tables, and requirements in the original Rulebooks PDFs. Cite the document, edition/date, section, and printed page when available. Establish the road authority and applicable permit or contract before applying a requirement. Distinguish mandatory standards, guidance, options, and local requirements. Check current official sources when currency matters, and identify any difference from the stored copies.

## Document versions

This is a versioned collection of supplied documents, not an automatically updated standards service. The included federal MUTCD full volume and chapter extracts identify December 2023; the supplied Oregon Supplement identifies January 2026. The OTTCH is the 2026 edition, and the Eugene TPAR manual is dated January 28, 2026. These labels identify the stored copies, not a finding that they are the latest governing versions.

Keep road-authority requirements, Oregon amendments, local standards, project contracts, and permit conditions in view when applying a document. A typical application is a planning reference; site conditions and agency acceptance determine its use on a particular project.

## Add or replace documents

1. Put the original PDF in `Rulebooks/`. Keep a distinct filename for a different edition when both must remain available.
2. Review the document label and edition/date in the script's `LABELS` mapping when adding a document or changing editions. Use Python 3.11 or newer, install the extraction dependency if needed, then rebuild the catalog, manifest, and text copies:

   ```sh
   python -m pip install pypdf
   python scripts/update_reference_index.py
   ```

3. Review the changes, including document dates and any pages with little or no extractable text.
4. Commit and push the originals and the regenerated reference files together.

The source documents retain their publishers' notices and terms. This repository does not grant a new license to the source publications.
