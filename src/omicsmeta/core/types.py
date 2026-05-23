"""Shared types used across the harmonization pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FieldType(str, Enum):
    """Supported semantic metadata field types."""

    TISSUE = "tissue"
    DISEASE = "disease"
    CELL_LINE = "cell_line"
    SEX = "sex"
    AGE = "age"
    TREATMENT = "treatment"
    SPECIES = "species"
    UNKNOWN = "unknown"


ONTOLOGY_BY_FIELD: dict[FieldType, str] = {
    FieldType.TISSUE: "uberon",
    FieldType.DISEASE: "doid",
    FieldType.CELL_LINE: "cellosaurus",
    FieldType.SEX: "pato",
    FieldType.SPECIES: "ncbitaxon",
    FieldType.TREATMENT: "efo",
}


@dataclass(frozen=True)
class OntologyTerm:
    """A compact ontology term representation.

    The built-in mapper uses this structure directly. OBO/OWL loaders can also
    emit it so the same mapper can run against user-supplied ontologies.
    """

    term_id: str
    label: str
    ontology: str
    synonyms: tuple[str, ...] = ()
    field_types: tuple[FieldType, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    """A cross-field validation warning for one metadata row."""

    row_index: int
    severity: str
    message: str
    fields: tuple[str, ...] = ()

