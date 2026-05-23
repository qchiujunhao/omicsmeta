"""Heuristic detection of metadata field types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Iterable, Mapping

from omicsmeta.core.normalizer import normalize_text
from omicsmeta.core.types import FieldType


FIELD_NAME_HINTS: dict[FieldType, tuple[str, ...]] = {
    FieldType.DISEASE: (
        "disease",
        "diagnosis",
        "phenotype",
        "pathology",
        "tumor type",
        "tumour type",
        "condition",
        "cancer",
    ),
    FieldType.TISSUE: (
        "tissue",
        "organ",
        "anatomy",
        "body site",
        "sample type",
    ),
    FieldType.CELL_LINE: ("cell line", "cellline", "cell_line", "cell"),
    FieldType.SEX: ("sex", "gender"),
    FieldType.AGE: ("age", "age at", "developmental stage"),
    FieldType.TREATMENT: ("treatment", "treated", "drug", "compound", "stimulus", "exposure"),
    FieldType.SPECIES: ("species", "organism", "taxon", "taxid"),
}

SEX_VALUES = {"male", "female", "m", "f", "man", "woman"}
SPECIES_VALUES = {
    "homo sapiens",
    "human",
    "mus musculus",
    "mouse",
    "rattus norvegicus",
    "rat",
}
KNOWN_CELL_LINES = {"a549", "hela", "hek293", "jurkat", "k562", "mcf-7", "mcf7", "u87"}
DISEASE_MARKERS = {
    "adenocarcinoma",
    "cancer",
    "carcinoma",
    "disease",
    "fibrosis",
    "glioblastoma",
    "leukemia",
    "lymphoma",
    "melanoma",
    "tumor",
    "tumour",
}
TISSUE_MARKERS = {
    "blood",
    "brain",
    "breast",
    "colon",
    "heart",
    "kidney",
    "liver",
    "lung",
    "spleen",
    "tissue",
}
TREATMENT_MARKERS = {"treated", "untreated", "control", "vehicle", "drug", "stimulated"}
AGE_RE = re.compile(r"^\d+(\.\d+)?\s*(day|days|week|weeks|month|months|year|years|yr|yrs|y)?$", re.I)


@dataclass(frozen=True)
class FieldDetection:
    """Detected semantic type for one metadata column."""

    field_type: FieldType
    confidence: float
    signals: tuple[str, ...] = ()


def detect_field(column_name: str, values: Iterable[object] = ()) -> FieldDetection:
    """Detect the semantic role of a metadata column."""

    normalized_name = normalize_text(column_name, expand_abbreviations=False)
    value_list = [normalize_text(value, expand_abbreviations=False) for value in values if str(value).strip()]

    scores: dict[FieldType, float] = {field_type: 0.0 for field_type in FieldType}
    signals: dict[FieldType, list[str]] = {field_type: [] for field_type in FieldType}

    for field_type, hints in FIELD_NAME_HINTS.items():
        for hint in hints:
            hint_norm = normalize_text(hint, expand_abbreviations=False)
            if hint_norm and hint_norm in normalized_name:
                scores[field_type] += 0.72
                signals[field_type].append(f"name:{hint}")
                break

    for field_type in (
        FieldType.DISEASE,
        FieldType.TISSUE,
        FieldType.CELL_LINE,
        FieldType.SEX,
        FieldType.AGE,
        FieldType.TREATMENT,
        FieldType.SPECIES,
    ):
        score = _value_score(field_type, value_list)
        if score:
            scores[field_type] += score
            signals[field_type].append(f"values:{score:.2f}")

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    if best_type == FieldType.UNKNOWN or best_score < 0.35:
        return FieldDetection(FieldType.UNKNOWN, 0.0, ())

    return FieldDetection(best_type, min(best_score, 0.99), tuple(signals[best_type]))


def detect_fields(rows: Iterable[Mapping[str, object]]) -> dict[str, FieldDetection]:
    """Detect field types for all columns in a row-oriented table."""

    row_list = list(rows)
    columns: list[str] = []
    seen: set[str] = set()
    for row in row_list:
        for column in row:
            if column not in seen:
                seen.add(column)
                columns.append(column)

    detections: dict[str, FieldDetection] = {}
    for column in columns:
        detections[column] = detect_field(column, (row.get(column, "") for row in row_list))
    return detections


def _value_score(field_type: FieldType, values: list[str]) -> float:
    if not values:
        return 0.0

    sample = values[:50]
    matches = sum(1 for value in sample if _matches_field(field_type, value))
    if matches == 0:
        return 0.0

    proportion = matches / len(sample)
    return min(0.70, 0.20 + proportion * 0.55)


def _matches_field(field_type: FieldType, value: str) -> bool:
    if field_type == FieldType.SEX:
        return value in SEX_VALUES
    if field_type == FieldType.SPECIES:
        return value in SPECIES_VALUES or value.startswith("ncbitaxon:")
    if field_type == FieldType.CELL_LINE:
        return value in KNOWN_CELL_LINES
    if field_type == FieldType.AGE:
        return bool(AGE_RE.match(value))
    if field_type == FieldType.DISEASE:
        return any(marker in value for marker in DISEASE_MARKERS)
    if field_type == FieldType.TISSUE:
        return value in TISSUE_MARKERS or value.endswith(" tissue")
    if field_type == FieldType.TREATMENT:
        return any(marker in value for marker in TREATMENT_MARKERS)
    return False
