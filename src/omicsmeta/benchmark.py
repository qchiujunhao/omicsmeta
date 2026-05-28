"""Benchmark helpers for known-answer metadata harmonization fixtures."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from omicsmeta.core.harmonizer import Harmonizer


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Precision/recall/F1 summary for ontology mappings."""

    true_positive: int
    false_positive: int
    false_negative: int
    precision: float
    recall: float
    f1: float

    def as_dict(self) -> dict[str, object]:
        return {
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


MappingKey = tuple[str, str, str]


def benchmark_file(
    input_path: str | Path,
    truth_path: str | Path,
    *,
    input_type: str = "tabular",
    confidence_threshold: float = 0.70,
) -> dict[str, object]:
    """Run harmonization and compare accepted direct mappings to truth."""

    result = Harmonizer(confidence_threshold=confidence_threshold).from_file(str(input_path), file_type=input_type)
    observed = _observed_mappings(result.harmonized)
    expected = _truth_mappings(truth_path)
    overall = _metrics(observed, expected)
    fields = sorted({field for _, field, _ in observed | expected})
    by_field = {
        field: _metrics(
            {mapping for mapping in observed if mapping[1] == field},
            {mapping for mapping in expected if mapping[1] == field},
        ).as_dict()
        for field in fields
    }

    return {
        "input_path": str(input_path),
        "truth_path": str(truth_path),
        "confidence_threshold": confidence_threshold,
        "overall": overall.as_dict(),
        "by_field": by_field,
        "observed_count": len(observed),
        "expected_count": len(expected),
    }


def benchmark_suite(
    manifest_path: str | Path,
    *,
    confidence_threshold: float = 0.70,
) -> dict[str, object]:
    """Run a TSV manifest of known-answer benchmark cases."""

    manifest = Path(manifest_path)
    base_dir = manifest.parent
    cases: list[dict[str, object]] = []
    total_true_positive = 0
    total_false_positive = 0
    total_false_negative = 0
    field_counts: dict[str, dict[str, int]] = {}

    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        for row in rows:
            name = row["name"].strip()
            input_path = _resolve_manifest_path(base_dir, row["input_path"])
            truth_path = _resolve_manifest_path(base_dir, row["truth_path"])
            summary = benchmark_file(
                input_path,
                truth_path,
                input_type=row.get("input_type", "tabular") or "tabular",
                confidence_threshold=confidence_threshold,
            )
            case_summary = {
                "name": name,
                "description": row.get("description", ""),
                **summary,
            }
            cases.append(case_summary)

            overall = summary["overall"]
            if isinstance(overall, dict):
                total_true_positive += int(overall["true_positive"])
                total_false_positive += int(overall["false_positive"])
                total_false_negative += int(overall["false_negative"])

            by_field = summary["by_field"]
            if isinstance(by_field, dict):
                for field, metrics in by_field.items():
                    if not isinstance(metrics, dict):
                        continue
                    counts = field_counts.setdefault(
                        str(field),
                        {"true_positive": 0, "false_positive": 0, "false_negative": 0},
                    )
                    counts["true_positive"] += int(metrics["true_positive"])
                    counts["false_positive"] += int(metrics["false_positive"])
                    counts["false_negative"] += int(metrics["false_negative"])

    overall_metrics = _metrics_from_counts(
        total_true_positive,
        total_false_positive,
        total_false_negative,
    )
    by_field_summary = {
        field: _metrics_from_counts(
            counts["true_positive"],
            counts["false_positive"],
            counts["false_negative"],
        ).as_dict()
        for field, counts in sorted(field_counts.items())
    }

    return {
        "manifest_path": str(manifest),
        "confidence_threshold": confidence_threshold,
        "case_count": len(cases),
        "overall": overall_metrics.as_dict(),
        "by_field": by_field_summary,
        "cases": cases,
    }


def write_benchmark_json(summary: dict[str, object], path: str | Path) -> None:
    """Write benchmark summary JSON."""

    Path(path).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _observed_mappings(records: list[dict[str, object]]) -> set[MappingKey]:
    return {
        (str(record["sample_id"]), str(record["field_type"]), str(record["ontology_id"]))
        for record in records
        if record.get("accepted") and record.get("ontology_id") and record.get("backend") != "inference"
    }


def _truth_mappings(path: str | Path) -> set[MappingKey]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        return {
            (row["sample_id"], row["field_type"], row["ontology_id"])
            for row in rows
            if row.get("sample_id") and row.get("field_type") and row.get("ontology_id")
        }


def _metrics(observed: set[MappingKey], expected: set[MappingKey]) -> BenchmarkMetrics:
    true_positive = len(observed & expected)
    false_positive = len(observed - expected)
    false_negative = len(expected - observed)
    return _metrics_from_counts(true_positive, false_positive, false_negative)


def _metrics_from_counts(
    true_positive: int,
    false_positive: int,
    false_negative: int,
) -> BenchmarkMetrics:
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return BenchmarkMetrics(
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
    )


def _resolve_manifest_path(base_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path
