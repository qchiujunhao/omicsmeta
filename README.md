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
- optional `text2term` mapper adapter
- simple OBO loader and SQLite ontology cache
- tabular, minimal GEO SOFT, BioSample XML, and SRA XML readers
- harmonization orchestrator and CLI
- real GEO SOFT snippet test coverage
- conservative field routing for ambiguous metadata columns
- transparent cell-line inference for missing species/tissue/disease fields
- deduplicated unmapped-term summaries for manual curation
- sample-wide output tables
- batch harmonization
- known-answer benchmark helper and CLI script

## Install

Install the published package from PyPI:

```bash
python -m pip install omicsmeta
```

Confirm the command-line interface is available:

```bash
omicsmeta --help
```

For contributor setup from a source checkout, install the development extras:

```bash
python -m pip install -e ".[dev,docs]"
```

## Quick Use

Create a small CSV or TSV metadata table:

```bash
cat > metadata.tsv <<'EOF'
sample_id,species,tissue,disease,cell line,sex
sample_1,Homo sapiens,lung,NSCLC,A549,female
sample_2,Homo sapiens,breast,breast cancer,MCF-7,female
EOF
```

Harmonize the file and write reviewable output tables:

```bash
omicsmeta harmonize metadata.tsv \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Direct GEO fetching is also available:

```bash
omicsmeta harmonize \
  --geo-accession GSE123456 \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Custom local OBO files can be added to the built-in mapper:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-obo disease_slim.obo \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Managed ontology resources can be cached locally:

```bash
omicsmeta ontologies list
omicsmeta ontologies download doid uberon cl
omicsmeta ontologies index --resource doid --resource uberon
omicsmeta harmonize metadata.tsv \
  --ontology-resource doid \
  --ontology-resource uberon \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Multiple files can be harmonized in one run:

```bash
omicsmeta batch \
  --input metadata_a.tsv \
  --input metadata_b.tsv \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Known-answer fixtures can be benchmarked:

```bash
python scripts/benchmark_mapping.py \
  --input examples/basic/metadata.tsv \
  --truth examples/basic/expected_harmonized.tsv
```

Run the bundled multi-fixture benchmark suite:

```bash
python scripts/benchmark_mapping.py \
  --manifest benchmarks/known_answer_suite.tsv \
  --output-json benchmark_suite.json
```

## Documentation

- [Documentation site](https://qchiujunhao.github.io/omicsmeta/)
- [Quickstart](docs/quickstart.md)
- [API reference](docs/api.md)
- [Design notes](docs/design.md)
- [Release readiness checklist](docs/release_readiness.md)
- [Basic fixture tutorial](docs/tutorials/basic_fixture.md)
- [Galaxy wrapper scaffold](galaxy-omicsmeta/omicsmeta_harmonize.xml)

## Maturity

This repository is pre-alpha and not yet JOSS-ready. Version `0.1.0` is
published on PyPI for early testing, but the project still needs
publication-scale curated benchmarks, external user feedback, and Galaxy Tool
Shed validation before submission.

Run tests locally with:

```bash
python -m pip install -e ".[dev,docs]"
python -m pytest
```
