"""Pipeline orchestration for metadata harmonization."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from omicsmeta.core.detector import FieldDetection, detect_fields
from omicsmeta.core.fetcher import HTTPSession, fetch_geo_rows
from omicsmeta.core.mapper import BuiltinMapper, Mapper, MappingResult
from omicsmeta.core.normalizer import split_terms
from omicsmeta.core.types import FieldType, ValidationIssue
from omicsmeta.core.validator import validate_row
from omicsmeta.io.readers import read_geo_soft, read_tabular


@dataclass(frozen=True)
class HarmonizationResult:
    """Output tables and QC data from a harmonization run."""

    harmonized: list[dict[str, object]]
    unmapped: list[dict[str, object]]
    qc_summary: dict[str, object]
    detections: dict[str, FieldDetection]
    issues: list[ValidationIssue]


class Harmonizer:
    """Run detection, normalization, mapping, and validation."""

    def __init__(
        self,
        *,
        mapper: Mapper | None = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        self.mapper = mapper or BuiltinMapper(confidence_threshold=confidence_threshold)
        self.confidence_threshold = confidence_threshold

    def from_file(self, path: str, *, file_type: str = "tabular") -> HarmonizationResult:
        """Read metadata from a supported file and harmonize it."""

        if file_type == "tabular":
            rows = read_tabular(path)
        elif file_type == "geo_soft":
            rows = read_geo_soft(path)
        else:
            raise ValueError(f"Unsupported file_type: {file_type}")
        return self.from_rows(rows)

    def from_geo(
        self,
        accession: str,
        *,
        session: HTTPSession | None = None,
        timeout: float = 30.0,
    ) -> HarmonizationResult:
        """Fetch a GEO accession and harmonize its sample metadata."""

        return self.from_rows(fetch_geo_rows(accession, session=session, timeout=timeout))

    def from_rows(self, rows: list[Mapping[str, object]]) -> HarmonizationResult:
        """Harmonize an in-memory row-oriented metadata table."""

        row_list = list(rows)
        detections = detect_fields(row_list)
        harmonized: list[dict[str, object]] = []
        unmapped: list[dict[str, object]] = []
        issues: list[ValidationIssue] = []

        for row_index, row in enumerate(row_list):
            mappings_by_column: dict[str, list[MappingResult]] = defaultdict(list)
            sample_id = _sample_id(row, row_index)

            for column, value in row.items():
                detection = detections.get(column, FieldDetection(FieldType.UNKNOWN, 0.0))
                terms = split_terms(value)
                if not terms:
                    continue

                for term in terms:
                    mapping = self.mapper.map_term(term.normalized, detection.field_type)
                    mappings_by_column[column].append(mapping)
                    record = _record(row_index, sample_id, column, value, term.original, detection, mapping)
                    if mapping.accepted:
                        harmonized.append(record)
                    else:
                        unmapped.append(record)

            issues.extend(validate_row(row_index, mappings_by_column))

        return HarmonizationResult(
            harmonized=harmonized,
            unmapped=unmapped,
            qc_summary=_qc_summary(harmonized, unmapped, issues),
            detections=detections,
            issues=issues,
        )


def _record(
    row_index: int,
    sample_id: str,
    column: str,
    raw_value: object,
    term: str,
    detection: FieldDetection,
    mapping: MappingResult,
) -> dict[str, object]:
    return {
        "row_index": row_index,
        "sample_id": sample_id,
        "column": column,
        "field_type": detection.field_type.value,
        "field_confidence": round(detection.confidence, 4),
        "raw_value": raw_value,
        "term": term,
        "normalized_term": mapping.normalized_text,
        "ontology": mapping.ontology or "",
        "ontology_id": mapping.ontology_id or "",
        "label": mapping.label or "",
        "mapping_confidence": mapping.confidence,
        "matched_text": mapping.matched_text or "",
        "accepted": mapping.accepted,
        "backend": mapping.backend,
    }


def _sample_id(row: Mapping[str, object], row_index: int) -> str:
    for key in ("sample_id", "sample", "geo_accession", "run", "gsm", "title"):
        for column, value in row.items():
            if column.lower() == key and str(value).strip():
                return str(value)
    return f"row_{row_index + 1}"


def _qc_summary(
    harmonized: list[dict[str, object]],
    unmapped: list[dict[str, object]],
    issues: list[ValidationIssue],
) -> dict[str, object]:
    total = len(harmonized) + len(unmapped)
    mapped_by_field: dict[str, int] = defaultdict(int)
    total_by_field: dict[str, int] = defaultdict(int)

    for record in harmonized:
        field = str(record["field_type"])
        mapped_by_field[field] += 1
        total_by_field[field] += 1
    for record in unmapped:
        total_by_field[str(record["field_type"])] += 1

    mapping_rate_by_field = {
        field: round(mapped_by_field[field] / total_by_field[field], 4)
        for field in sorted(total_by_field)
        if total_by_field[field]
    }

    return {
        "total_terms": total,
        "mapped_terms": len(harmonized),
        "unmapped_terms": len(unmapped),
        "mapping_rate": round(len(harmonized) / total, 4) if total else 0.0,
        "mapping_rate_by_field": mapping_rate_by_field,
        "validation_issue_count": len(issues),
        "validation_issues": [
            {
                "row_index": issue.row_index,
                "severity": issue.severity,
                "message": issue.message,
                "fields": ", ".join(issue.fields),
            }
            for issue in issues
        ],
    }
