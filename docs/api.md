# API Reference

This page documents the stable public API surface currently intended for users
who want to call `omicsmeta` from Python. The package is still pre-alpha, so
minor names may change before the first release.

## Harmonizer

`omicsmeta.core.harmonizer.Harmonizer` is the main entry point. It accepts an
optional mapper backend and a confidence threshold.

```python
from omicsmeta.core.harmonizer import Harmonizer

harmonizer = Harmonizer(confidence_threshold=0.70)
result = harmonizer.from_file("metadata.tsv", file_type="tabular")
```

Supported input methods:

- `from_file(path, file_type="tabular")`: read CSV/TSV metadata or a GEO SOFT
  snippet from disk.
- `from_geo(accession)`: fetch a GEO accession and harmonize its sample
  metadata.
- `from_rows(rows)`: harmonize an in-memory list of row dictionaries.

`file_type` is either `tabular` or `geo_soft`.

## HarmonizationResult

`Harmonizer` returns a `HarmonizationResult` dataclass with these attributes:

- `harmonized`: accepted ontology mappings, one row per mapped metadata term.
- `unmapped`: candidate mappings below the confidence threshold or fields that
  could not be routed confidently.
- `unmapped_summary`: deduplicated manual-review table grouped by field type and
  normalized term.
- `sample_table`: one row per input sample with sample-wide ontology summaries.
- `qc_summary`: aggregate counts, mapping rates, and validation warnings.
- `detections`: semantic field detection result for each input column.
- `issues`: row-level validation warnings.

## Mapping Backends

The default backend is `BuiltinMapper`, an offline exact and fuzzy synonym
matcher. It includes a small seed vocabulary for common test and demonstration
terms and can load additional OBO files.

```python
from omicsmeta.core.mapper import BuiltinMapper, load_builtin_terms
from omicsmeta.core.harmonizer import Harmonizer

terms = load_builtin_terms(["disease_slim.obo"])
mapper = BuiltinMapper(terms=terms, confidence_threshold=0.75)
result = Harmonizer(mapper=mapper).from_file("metadata.tsv")
```

`Text2TermMapper` adapts the optional `text2term` package. It is useful when
users want broader ontology mapping from a maintained general-purpose mapper.

```python
from omicsmeta.core.mapper import Text2TermMapper
from omicsmeta.core.harmonizer import Harmonizer

mapper = Text2TermMapper(confidence_threshold=0.70)
result = Harmonizer(mapper=mapper).from_file("metadata.tsv")
```

## Output Writers

Use `omicsmeta.io.writers` to write result tables and the compact HTML QC
report:

```python
from omicsmeta.io.writers import write_html_report, write_tabular

write_tabular(result.harmonized, "harmonized.tsv")
write_tabular(result.unmapped, "unmapped.tsv")
write_tabular(result.sample_table, "samples.tsv")
write_html_report(result.qc_summary, "qc_report.html")
```

## Benchmark Helpers

Known-answer fixtures can be scored from Python with
`omicsmeta.benchmark.benchmark_file`:

```python
from omicsmeta.benchmark import benchmark_file

summary = benchmark_file(
    "examples/basic/metadata.tsv",
    "examples/basic/expected_harmonized.tsv",
)
print(summary["overall"])
```

The benchmark compares accepted direct mappings to expected
`sample_id`, `field_type`, and `ontology_id` triples. Inferred mappings are
excluded so benchmark scores reflect direct term mapping behavior.

Run a TSV manifest of benchmark cases with `benchmark_suite`:

```python
from omicsmeta.benchmark import benchmark_suite

summary = benchmark_suite("benchmarks/known_answer_suite.tsv")
print(summary["case_count"], summary["overall"]["f1"])
```
