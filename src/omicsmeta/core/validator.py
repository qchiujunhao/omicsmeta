"""Cross-field validation for harmonized metadata."""

from __future__ import annotations

from collections.abc import Mapping

from omicsmeta.core.mapper import MappingResult
from omicsmeta.core.types import FieldType, ValidationIssue


CELL_LINE_EXPECTATIONS: dict[str, dict[FieldType, tuple[str, ...]]] = {
    "CVCL:0031": {
        FieldType.SPECIES: ("NCBITaxon:9606",),
        FieldType.TISSUE: ("UBERON:0000310",),
        FieldType.DISEASE: ("DOID:1612",),
    },
    "CVCL:0030": {
        FieldType.SPECIES: ("NCBITaxon:9606",),
    },
    "CVCL:0023": {
        FieldType.SPECIES: ("NCBITaxon:9606",),
        FieldType.TISSUE: ("UBERON:0002048",),
    },
}


def validate_row(
    row_index: int,
    mappings_by_column: Mapping[str, list[MappingResult]],
) -> list[ValidationIssue]:
    """Return consistency warnings for one harmonized row."""

    accepted = [
        mapping
        for mappings in mappings_by_column.values()
        for mapping in mappings
        if mapping.accepted and mapping.ontology_id
    ]
    issues: list[ValidationIssue] = []

    for cell_line in (m for m in accepted if m.field_type == FieldType.CELL_LINE):
        expected = CELL_LINE_EXPECTATIONS.get(cell_line.ontology_id or "")
        if not expected:
            continue
        for expected_field, expected_ids in expected.items():
            observed = [m for m in accepted if m.field_type == expected_field]
            if observed and all(m.ontology_id not in expected_ids for m in observed):
                issues.append(
                    ValidationIssue(
                        row_index=row_index,
                        severity="warning",
                        message=(
                            f"{cell_line.label} implies {expected_field.value} "
                            f"{', '.join(expected_ids)}, but observed "
                            f"{', '.join(str(m.ontology_id) for m in observed)}."
                        ),
                        fields=(FieldType.CELL_LINE.value, expected_field.value),
                    )
                )

    return issues

