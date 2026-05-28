# Benchmark Fixtures

This directory contains a small known-answer benchmark suite for regression
testing and development. It is not a publication-scale validation dataset.

`known_answer_suite.tsv` is a manifest with one benchmark case per row:

- `name`: stable case identifier.
- `input_path`: metadata input path, relative to this directory unless absolute.
- `input_type`: `tabular` or `geo_soft`.
- `truth_path`: expected mapping table, relative to this directory unless
  absolute.
- `description`: short human-readable case description.

Truth tables are stored in `truth/`. Each truth row is scored by
`sample_id`, `field_type`, and `ontology_id`; extra columns such as `label` are
for reader context.

Run the suite from the repository root:

```bash
python scripts/benchmark_mapping.py \
  --manifest benchmarks/known_answer_suite.tsv \
  --output-json benchmark_suite.json
```
