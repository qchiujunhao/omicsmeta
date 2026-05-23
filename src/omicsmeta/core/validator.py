"""Cross-field validation for harmonized metadata."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from omicsmeta.core.mapper import MappingResult
from omicsmeta.core.types import FieldType, ValidationIssue


@dataclass(frozen=True)
class ExpectedTerm:
    """A known consequent term implied by an accepted mapping."""

    field_type: FieldType
    ontology_id: str
    label: str
    ontology: str
    compatible_ids: tuple[str, ...] = ()


CELL_LINE_EXPECTATIONS: dict[str, tuple[ExpectedTerm, ...]] = {
    "CVCL:0031": (
        ExpectedTerm(FieldType.SPECIES, "NCBITaxon:9606", "Homo sapiens", "ncbitaxon"),
        ExpectedTerm(FieldType.TISSUE, "UBERON:0000310", "breast", "uberon"),
        ExpectedTerm(FieldType.DISEASE, "DOID:1612", "breast cancer", "doid"),
    ),
    "CVCL:0030": (
        ExpectedTerm(FieldType.SPECIES, "NCBITaxon:9606", "Homo sapiens", "ncbitaxon"),
    ),
    "CVCL:0023": (
        ExpectedTerm(FieldType.SPECIES, "NCBITaxon:9606", "Homo sapiens", "ncbitaxon"),
        ExpectedTerm(FieldType.TISSUE, "UBERON:0002048", "lung", "uberon"),
        ExpectedTerm(
            FieldType.DISEASE,
            "DOID:3910",
            "lung adenocarcinoma",
            "doid",
            compatible_ids=("DOID:299", "DOID:1324", "DOID:3908"),
        ),
    ),
}


def validate_row(
    row_index: int,
    mappings_by_column: Mapping[str, list[MappingResult]],
) -> list[ValidationIssue]:
    """Return consistency warnings for one harmonized row."""

    accepted = _accepted_mappings(mappings_by_column)
    issues: list[ValidationIssue] = []

    for cell_line in (m for m in accepted if m.field_type == FieldType.CELL_LINE):
        expected = CELL_LINE_EXPECTATIONS.get(cell_line.ontology_id or "")
        if not expected:
            continue
        for expected_term in expected:
            observed = [m for m in accepted if m.field_type == expected_term.field_type]
            allowed_ids = {expected_term.ontology_id, *expected_term.compatible_ids}
            if observed and all(m.ontology_id not in allowed_ids for m in observed):
                issues.append(
                    ValidationIssue(
                        row_index=row_index,
                        severity="warning",
                        message=(
                            f"{cell_line.label} implies {expected_term.field_type.value} "
                            f"{expected_term.ontology_id}, but observed "
                            f"{', '.join(str(m.ontology_id) for m in observed)}."
                        ),
                        fields=(FieldType.CELL_LINE.value, expected_term.field_type.value),
                    )
                )

    return issues


def infer_expected_terms(
    row_index: int,
    sample_id: str,
    mappings_by_column: Mapping[str, list[MappingResult]],
    *,
    confidence: float = 0.85,
) -> list[dict[str, object]]:
    """Infer missing terms implied by accepted cell-line mappings."""

    accepted = _accepted_mappings(mappings_by_column)
    observed_fields = {mapping.field_type for mapping in accepted}
    inferred: list[dict[str, object]] = []

    for cell_line in (m for m in accepted if m.field_type == FieldType.CELL_LINE):
        expected_terms = CELL_LINE_EXPECTATIONS.get(cell_line.ontology_id or "")
        if not expected_terms:
            continue
        for expected in expected_terms:
            if expected.field_type in observed_fields:
                continue
            inferred.append(
                {
                    "row_index": row_index,
                    "sample_id": sample_id,
                    "column": "__inferred__",
                    "field_type": expected.field_type.value,
                    "field_confidence": 1.0,
                    "raw_value": cell_line.label or cell_line.source_text,
                    "term": expected.label,
                    "normalized_term": expected.label.lower(),
                    "ontology": expected.ontology,
                    "ontology_id": expected.ontology_id,
                    "label": expected.label,
                    "mapping_confidence": confidence,
                    "matched_text": expected.label,
                    "accepted": True,
                    "backend": "inference",
                    "inferred_from": cell_line.ontology_id,
                    "inferred_from_label": cell_line.label or "",
                }
            )
            observed_fields.add(expected.field_type)

    return inferred


def _accepted_mappings(mappings_by_column: Mapping[str, list[MappingResult]]) -> list[MappingResult]:
    return [
        mapping
        for mappings in mappings_by_column.values()
        for mapping in mappings
        if mapping.accepted and mapping.ontology_id
    ]
