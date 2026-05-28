---
title: 'omicsmeta: Automated Harmonization of Public Omics Metadata'
tags:
  - Python
  - bioinformatics
  - metadata
  - ontology
  - GEO
  - SRA
authors:
  - name: omicsmeta contributors
    affiliation: 1
affiliations:
  - name: To be completed before submission
    index: 1
date: 28 May 2026
bibliography: paper.bib
---

## Summary

`omicsmeta` is an open-source Python package for converting public omics
metadata into ontology-mapped tables. It combines metadata-specific string
normalization, semantic field detection, pluggable ontology mapping, validation,
cell-line consequent inference, and review-oriented outputs. The package can be
used from a command-line interface or Python API and currently supports tabular
metadata files, GEO SOFT snippets, and direct GEO accession fetching.

## Statement of Need

Public repositories such as GEO, SRA, and BioSample are essential resources for
secondary omics analysis, but their sample metadata are frequently encoded as
heterogeneous key-value pairs, inconsistent column names, abbreviations,
spelling variants, and free text. Researchers who want to compare studies often
need to normalize disease, tissue, organism, treatment, and cell-line metadata
before downstream analysis can begin.

Existing tools cover important parts of this workflow. `text2term` provides
general-purpose biomedical term-to-ontology mapping [@goncalves2024text2term].
MetaSRA demonstrated the value of ontology-normalized sample metadata for the
Sequence Read Archive [@bernstein2017metasra]. GEOfetch and pysradb focus on
retrieving public metadata and sequencing data [@khoroshevskyi2023geofetch;
@choudhary2019pysradb]. `omicsmeta` targets the gap between retrieval and
analysis: it adds a reusable, metadata-aware harmonization layer that routes
fields, normalizes terms, invokes mapper backends, preserves provenance, emits
manual-review tables, and summarizes sample-level outputs.

The intended audience includes bioinformaticians preparing cross-study
analyses, data curators building reusable metadata resources, and workflow
developers who need a scriptable harmonization step.

## State of the Field

The core design assumption is that ontology matching alone is not sufficient for
public omics metadata. A mapper receives isolated strings; a harmonization
pipeline also needs to know whether a column is describing tissue, disease,
species, treatment, or another biological context. It also needs to preserve
source columns, confidence scores, and unmapped terms so curators can review the
result.

`omicsmeta` therefore complements general-purpose mappers rather than replacing
them. The built-in mapper provides an offline fallback and testable baseline,
while the optional `text2term` adapter allows users to rely on a broader
external mapping tool. The package contribution is the domain-specific pipeline
around mapping: conservative field routing, omics abbreviation handling,
cross-field validation, transparent inference, batch outputs, and benchmarkable
known-answer fixtures.

## Software Design

The package is organized as a small set of composable modules:

- `io.readers` loads tabular metadata and GEO SOFT records.
- `core.detector` assigns semantic field types to metadata columns.
- `core.normalizer` cleans strings and splits multi-value fields.
- `core.mapper` defines the mapper protocol and backend implementations.
- `core.validator` emits row-level consistency warnings and inferred terms.
- `core.harmonizer` orchestrates the full pipeline.
- `io.writers` emits detailed TSV outputs and an HTML QC report.
- `ontologies` manages OBO loading, local resource downloads, and SQLite
  synonym indexes.

The command-line interface exposes single-input harmonization, batch
harmonization, and ontology resource management. The Python API returns a
`HarmonizationResult` containing detailed accepted mappings, unmapped records,
deduplicated unmapped summaries, sample-wide outputs, QC summaries, detected
fields, and validation issues.

Defaults are conservative. Low-confidence or ambiguous mappings are sent to
review outputs instead of being silently accepted. Inferred records are marked
with `backend=inference` so they can be separated from direct source metadata
when benchmarking or auditing.

## Research Impact Statement

Metadata harmonization is a recurring bottleneck in public omics reuse.
`omicsmeta` is designed to make this step reproducible, auditable, and easier to
embed in larger workflows. Its review tables help curators focus on repeated
unmapped terms, and its sample-wide outputs are shaped for downstream analysis
tables. A future Galaxy wrapper is planned so non-programming users can run the
same harmonization workflow through a browser-based interface.

The current implementation should be treated as pre-alpha. Before publication,
the project needs larger curated benchmark datasets, broader SRA/BioSample input
coverage, hosted CI, packaging releases, and external user feedback.

## AI Usage Disclosure

Initial scaffolding was assisted by an AI coding assistant. All scientific
claims, validation data, and release artifacts require maintainer review before
publication.

## References
