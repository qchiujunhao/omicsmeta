# omicsmeta

`omicsmeta` is an early-stage Python package for harmonizing public omics
metadata from GEO, SRA, BioSample, and tabular exports.

The central design choice is to make ontology mapping pluggable. Generic
mapping tools such as `text2term` are useful, but public omics metadata also
needs domain-specific preprocessing, field-type detection, confidence-aware
routing, and cross-field validation. `omicsmeta` is intended to provide that
pipeline.

Current implementation status:

- string normalization and biomedical abbreviation expansion
- heuristic metadata field detection
- lightweight built-in ontology mapper for common terms
- simple OBO loader and SQLite ontology cache
- tabular and minimal GEO SOFT readers
- harmonization orchestrator and CLI

Example:

```bash
omicsmeta harmonize metadata.tsv \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --report qc_report.html
```

Direct GEO fetching is also available:

```bash
omicsmeta harmonize \
  --geo-accession GSE123456 \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --report qc_report.html
```

Custom local OBO files can be added to the built-in mapper:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-obo disease_slim.obo \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --report qc_report.html
```

This repository is not yet JOSS-ready. The immediate next milestones are
broader ontology resources, real-data integration tests, CI, documentation, and
benchmarking against `text2term` alone.

Run tests locally with:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```
