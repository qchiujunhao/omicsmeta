# Changelog

All notable changes to `omicsmeta` will be documented in this file.

The project is currently pre-alpha.

## 0.1.0 - 2026-06-13

- Added a Python package scaffold with CLI entry point.
- Added normalization, field detection, mapping, validation, and harmonization
  modules.
- Added tabular, minimal GEO SOFT, BioSample XML, and SRA XML readers.
- Added detailed harmonized, unmapped, unmapped-summary, sample-wide, and HTML
  QC outputs.
- Added managed ontology resource download and SQLite indexing commands.
- Added conservative handling for ambiguous metadata fields.
- Added transparent cell-line inference for common cell lines.
- Added batch harmonization for multiple files and GEO accessions.
- Added known-answer benchmark helper and CLI script.
- Added a multi-fixture known-answer benchmark suite.
- Added integration fixtures based on GEO-style metadata snippets.
- Added public documentation, contribution metadata, and a JOSS paper skeleton.
- Added a Galaxy wrapper scaffold with local wrapper smoke test data.
- Added package artifact build validation and a release-readiness checklist.
- Added SRA/BioSample XML edge-case coverage for namespaced documents,
  repeated attributes, and accession fallbacks.
- Added GitHub Pages documentation publishing and a Material for MkDocs site
  theme.
