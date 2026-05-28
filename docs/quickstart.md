# Quickstart

## Install for development

```bash
python -m pip install -e ".[dev]"
```

## Harmonize a tabular metadata file

Input files can be CSV or TSV. The first row must contain column names.

```bash
omicsmeta harmonize metadata.tsv \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

## Fetch metadata from GEO

Use `--geo-accession` to fetch SOFT metadata directly from GEO.

```bash
omicsmeta harmonize \
  --geo-accession GSE123456 \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

## Outputs

- `harmonized.tsv`: accepted ontology mappings with confidence scores
- `unmapped.tsv`: terms below the confidence threshold for review
- `unmapped_summary.tsv`: deduplicated unmapped terms prioritized for manual curation
- `samples.tsv`: one row per sample with sample-wide ontology columns
- `qc_report.html`: mapping rates and validation warning summaries

See `examples/basic/` for a small input file and expected mappings.

Column routing is conservative for vague fields. For example, a GEO
`phenotype` column is only routed to disease when the values contain disease
evidence; otherwise, the terms stay unmapped for review instead of being forced
into an ontology.

Recognized cell lines can add inferred species, tissue, and disease terms when
those fields are missing. Inferred records are marked with `backend=inference`
and include `inferred_from` provenance in the detailed output.

## Mapper backends

The built-in backend is the default and works offline for common terms. The
optional `text2term` backend is intended for broader ontology mapping once the
dependency and ontology sources are configured.

Add local OBO files to the built-in backend with `--ontology-obo`:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-obo disease_slim.obo \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

## Managed Ontology Resources

List known resources and cache selected OBO files:

```bash
omicsmeta ontologies list
omicsmeta ontologies download doid uberon cl
```

Build a SQLite synonym index from cached resources:

```bash
omicsmeta ontologies index --resource doid --resource uberon
```

Use cached resources during harmonization:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-resource doid \
  --ontology-resource uberon \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

By default, resources are stored under `~/.cache/omicsmeta/ontologies`. Use
`--ontology-cache-dir` or `--cache-dir` to choose another location.

## Batch Harmonization

Use `batch` for multiple files or GEO accessions:

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

Batch outputs include a `batch_source` column so rows can be traced back to
their input file or accession.
