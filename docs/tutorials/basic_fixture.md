# Tutorial: Harmonize the Basic Fixture

This tutorial uses the small fixture in `examples/basic/` to show the full local
workflow without requiring network access. Run it from a clone of the
`omicsmeta` repository so the example files are available.

## Install

```bash
python -m pip install omicsmeta
```

If you are editing the repository, install from the source checkout instead:

```bash
python -m pip install -e ".[dev,docs]"
```

## Run Harmonization

```bash
omicsmeta harmonize examples/basic/metadata.tsv \
  --output examples/basic/harmonized.tsv \
  --unmapped examples/basic/unmapped.tsv \
  --unmapped-summary-output examples/basic/unmapped_summary.tsv \
  --sample-output examples/basic/samples.tsv \
  --report examples/basic/qc_report.html
```

## Inspect Outputs

The detailed output contains accepted ontology mappings:

```bash
head examples/basic/harmonized.tsv
```

The sample-wide table contains one row per input sample:

```bash
head examples/basic/samples.tsv
```

The unmapped summary is the best starting point for manual curation:

```bash
cat examples/basic/unmapped_summary.tsv
```

## Benchmark the Fixture

Compare accepted direct mappings against the expected known-answer table:

```bash
python scripts/benchmark_mapping.py \
  --input examples/basic/metadata.tsv \
  --truth examples/basic/expected_harmonized.tsv \
  --output-json examples/basic/benchmark.json
```

The benchmark reports precision, recall, and F1 overall and by semantic field.
Inferred terms are excluded from this score so the metric reflects direct
mapping behavior.

## Run the Bundled Suite

The repository also includes a manifest of known-answer cases that covers the
basic fixture and several GEO-style snippets:

```bash
python scripts/benchmark_mapping.py \
  --manifest benchmarks/known_answer_suite.tsv \
  --output-json benchmark_suite.json
```
