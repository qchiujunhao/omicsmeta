# Quickstart

This page shows the shortest path from installation to harmonized metadata
tables. It assumes no prior knowledge of the repository.

## Install From PyPI

Install the current pre-alpha release:

```bash
python -m pip install omicsmeta
```

Check that the command-line interface is available:

```bash
omicsmeta --help
```

For an isolated command-line install, `pipx install omicsmeta` is also a good
option if `pipx` is available on your system.

## Create A Tiny Input File

`omicsmeta` reads CSV or TSV files with column names in the first row. The
column names do not need to be standardized, but useful names such as
`species`, `tissue`, `disease`, `cell line`, and `sex` help the field detector.

```bash
cat > metadata.tsv <<'EOF'
sample_id,species,tissue,disease,cell line,sex
sample_1,Homo sapiens,lung,NSCLC,A549,female
sample_2,Homo sapiens,breast,breast cancer,MCF-7,female
EOF
```

## Harmonize The File

Run the default offline mapper and write the main output tables:

```bash
omicsmeta harmonize metadata.tsv \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

The command produces:

- `harmonized.tsv`: accepted ontology mappings with confidence scores and
  source-column provenance.
- `unmapped.tsv`: candidate terms that were not accepted automatically.
- `unmapped_summary.tsv`: deduplicated review terms, useful for manual curation.
- `samples.tsv`: one row per sample with sample-wide ontology columns.
- `qc_report.html`: a compact HTML summary of mapping rates and warnings.

The built-in mapper covers common demonstration terms and works without network
access. For real projects, add managed ontology resources or local OBO files as
described below.

## Fetch Metadata From GEO

Use `--geo-accession` to fetch GEO SOFT metadata directly from NCBI GEO:

```bash
omicsmeta harmonize \
  --geo-accession GSE123456 \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Network access is required for direct GEO fetching. If you already have a SOFT
snippet on disk, use `--input-type geo_soft`.

## Read BioSample Or SRA XML

Use `--input-type biosample_xml` for NCBI BioSample XML exports:

```bash
omicsmeta harmonize biosample.xml \
  --input-type biosample_xml \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

Use `--input-type sra_xml` for SRA XML files that contain `SAMPLE` and
`SAMPLE_ATTRIBUTE` blocks:

```bash
omicsmeta harmonize sra.xml \
  --input-type sra_xml \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

## Add Ontology Resources

List managed ontology resources:

```bash
omicsmeta ontologies list
```

Download selected OBO resources and build a local SQLite synonym index:

```bash
omicsmeta ontologies download doid uberon cl
omicsmeta ontologies index --resource doid --resource uberon --resource cl
```

Use cached resources during harmonization:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-resource doid \
  --ontology-resource uberon \
  --ontology-resource cl \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

By default, resources are stored under `~/.cache/omicsmeta/ontologies`. Use
`--cache-dir` with `omicsmeta ontologies download` or `omicsmeta ontologies
index` to choose another cache location, and use `--ontology-cache-dir` with
`omicsmeta harmonize` to read from that location.

You can also load local OBO files directly:

```bash
omicsmeta harmonize metadata.tsv \
  --ontology-obo disease_slim.obo \
  --output harmonized.tsv \
  --unmapped unmapped.tsv \
  --unmapped-summary-output unmapped_summary.tsv \
  --sample-output samples.tsv \
  --report qc_report.html
```

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

## Python API

Use the API when harmonization is part of a larger workflow:

```python
from omicsmeta.core.harmonizer import Harmonizer

result = Harmonizer(confidence_threshold=0.70).from_file(
    "metadata.tsv",
    file_type="tabular",
)

print(result.qc_summary)
print(result.sample_table)
```

See the [API reference](api.md) for result objects, mapper backends, and output
writers.

## Development Install

Use the editable install only when working from a source checkout:

```bash
git clone https://github.com/qchiujunhao/omicsmeta.git
cd omicsmeta
python -m pip install -e ".[dev,docs]"
python -m pytest
```

The repository includes `examples/basic/` and `benchmarks/` fixtures for local
development, documentation checks, and known-answer benchmark runs.
