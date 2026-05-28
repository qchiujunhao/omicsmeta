# Design

`omicsmeta` is built around a narrow pipeline goal: convert messy public omics
metadata into ontology-mapped tables that can be reviewed, benchmarked, and used
by downstream analysis workflows.

## Pipeline

The harmonization pipeline runs these steps:

1. Read metadata from a tabular file, GEO SOFT snippet, BioSample XML file, SRA
   XML file, or fetched GEO accession.
2. Detect the semantic role of each column, such as disease, tissue, cell line,
   species, sex, age, or treatment.
3. Normalize and split values into candidate terms.
4. Map each term to ontology candidates with a pluggable mapper backend.
5. Route confident mappings to the harmonized table and lower-confidence terms
   to manual review outputs.
6. Add transparent inferred terms when a recognized cell line implies species,
   tissue, or disease and the source row lacks those fields.
7. Emit detailed, sample-wide, unmapped-summary, and QC-report outputs.

## Conservative Field Routing

Public metadata often uses vague columns such as `phenotype`, `characteristics`,
or `sample type`. `omicsmeta` avoids treating those names as enough evidence for
ontology routing. Column-name hints are combined with value-level evidence, and
low-confidence or ambiguous terms are kept in the unmapped review outputs.

This design favors reviewable false negatives over silent false positives.

## Mapper Boundaries

Term-to-ontology matching is intentionally pluggable. The built-in mapper is an
offline fallback and test fixture backend. The optional `text2term` adapter lets
users delegate broad biomedical term grounding to an external package while
keeping `omicsmeta` responsible for metadata-specific preprocessing, field
routing, provenance, and output tables.

The package should not become a replacement for mature ontology matching tools.
Its contribution is the metadata harmonization workflow around those tools.

## Output Tables

The detailed harmonized and unmapped tables preserve term-level provenance:
input row, sample identifier, source column, raw value, normalized term,
detected field type, ontology candidate, confidence score, backend, and accepted
status.

The sample-wide table is intended for analysis workflows that need one row per
sample. It aggregates ontology IDs, labels, ontologies, source columns, and
confidence scores by semantic field.

The unmapped summary groups repeated review terms across samples and batch
inputs. It is designed for curator triage: frequent repeated failures appear
first, with sample IDs, source columns, example text, and best candidate
metadata.

## Validation and Inference

Validation is implemented as warnings, not hard failures. Current checks focus
on row-level consistency and missing expected context. Cell-line inference is
explicitly marked with `backend=inference` and includes provenance columns such
as `inferred_from` in the detailed output.

Inference records are useful for downstream completeness but should be treated
separately from direct source metadata during benchmarking.

## Galaxy Wrapper

The repository includes a Galaxy wrapper scaffold under `galaxy-omicsmeta/`.
It wraps the same CLI workflow, emits the same five output files, and includes
small test data for Planemo-oriented validation. The wrapper is not yet a Tool
Shed release because the Python package still needs external packaging through a
Galaxy-compatible channel.

## Current Limitations

- GEO SOFT, tabular, BioSample XML, and SRA XML inputs are supported. The XML
  readers cover common sample attributes but are not complete parsers for every
  NCBI export shape.
- The bundled vocabulary is intentionally small and should be extended with
  managed ontology resources or user-provided OBO files for real projects.
- The benchmark command currently scores known-answer fixtures, not a
  publication-scale curated benchmark set.
- The Galaxy wrapper is a scaffold and has not yet been submitted to the Galaxy
  Tool Shed.
- The project is pre-alpha and not yet ready for JOSS submission.
