# Basic Example

This example demonstrates local, offline harmonization of a small tabular
metadata file.

Run from the repository root:

```bash
omicsmeta harmonize examples/basic/metadata.tsv \
  --output examples/basic/harmonized.tsv \
  --unmapped examples/basic/unmapped.tsv \
  --unmapped-summary-output examples/basic/unmapped_summary.tsv \
  --sample-output examples/basic/samples.tsv \
  --report examples/basic/qc_report.html
```

The compact `expected_harmonized.tsv` file lists the ontology mappings that
should appear in the full output. Treatment terms are intentionally left
unmapped by the seed vocabulary so they can be reviewed.

The `expected_samples.tsv` file shows the sample-wide output shape used by
downstream analysis workflows.

The `expected_unmapped_summary.tsv` file shows the compact manual-review table
for repeated unmapped terms.
