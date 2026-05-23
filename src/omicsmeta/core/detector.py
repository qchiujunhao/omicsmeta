"""Heuristic detection of metadata field types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Iterable, Mapping

from omicsmeta.core.normalizer import normalize_text
from omicsmeta.core.types import FieldType


@dataclass(frozen=True)
class NameHint:
    """A weighted column-name signal for field detection."""

    text: str
    weight: float


FIELD_NAME_HINTS: dict[FieldType, tuple[NameHint, ...]] = {
    FieldType.DISEASE: (
        NameHint("disease state", 0.82),
        NameHint("disease", 0.78),
        NameHint("diagnosis", 0.78),
        NameHint("pathology", 0.72),
        NameHint("tumor type", 0.72),
        NameHint("tumour type", 0.72),
        NameHint("cancer", 0.72),
        NameHint("condition", 0.48),
        NameHint("phenotype", 0.24),
    ),
    FieldType.TISSUE: (
        NameHint("body site", 0.82),
        NameHint("tissue", 0.78),
        NameHint("organ", 0.72),
        NameHint("anatomy", 0.72),
        NameHint("sample type", 0.42),
    ),
    FieldType.CELL_LINE: (
        NameHint("cell line", 0.84),
        NameHint("cellline", 0.84),
        NameHint("cell_line", 0.84),
        NameHint("cell", 0.35),
    ),
    FieldType.SEX: (
        NameHint("sex", 0.84),
        NameHint("gender", 0.84),
    ),
    FieldType.AGE: (
        NameHint("age at", 0.84),
        NameHint("age", 0.78),
        NameHint("developmental stage", 0.48),
    ),
    FieldType.TREATMENT: (
        NameHint("treatment", 0.84),
        NameHint("treated", 0.72),
        NameHint("drug", 0.72),
        NameHint("compound", 0.72),
        NameHint("stimulus", 0.72),
        NameHint("exposure", 0.72),
    ),
    FieldType.SPECIES: (
        NameHint("organism", 0.84),
        NameHint("species", 0.78),
        NameHint("taxon", 0.78),
        NameHint("taxid", 0.78),
    ),
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
            hint_norm = normalize_text(hint.text, expand_abbreviations=False)
            if hint_norm and hint_norm in normalized_name:
                scores[field_type] += hint.weight
                signals[field_type].append(f"name:{hint.text}:{hint.weight:.2f}")
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
        tokens = set(re.split(r"[^a-z0-9-]+", value))
        return value in KNOWN_CELL_LINES or bool(tokens & KNOWN_CELL_LINES)
    if field_type == FieldType.AGE:
        return bool(AGE_RE.match(value))
    if field_type == FieldType.DISEASE:
        return any(marker in value for marker in DISEASE_MARKERS)
    if field_type == FieldType.TISSUE:
        return value in TISSUE_MARKERS or value.endswith(" tissue")
    if field_type == FieldType.TREATMENT:
        return any(marker in value for marker in TREATMENT_MARKERS)
    return False
