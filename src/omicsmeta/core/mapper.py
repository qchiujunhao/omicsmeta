"""Pluggable term-to-ontology mapping backends."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from omicsmeta.core.normalizer import normalize_text
from omicsmeta.core.types import FieldType, ONTOLOGY_BY_FIELD, OntologyTerm
from omicsmeta.ontologies.loader import load_obo


@dataclass(frozen=True)
class MappingResult:
    """Result of mapping one normalized metadata term."""

    source_text: str
    normalized_text: str
    field_type: FieldType
    ontology_id: str | None
    label: str | None
    ontology: str | None
    confidence: float
    matched_text: str | None
    backend: str
    accepted: bool


class Mapper(Protocol):
    """Common mapper interface."""

    confidence_threshold: float

    def map_term(self, term: str, field_type: FieldType = FieldType.UNKNOWN) -> MappingResult:
        """Map one term to an ontology candidate."""


class BuiltinMapper:
    """Small offline mapper based on exact and fuzzy synonym matching."""

    backend_name = "builtin"

    def __init__(
        self,
        terms: list[OntologyTerm] | None = None,
        *,
        confidence_threshold: float = 0.70,
    ) -> None:
        self.terms = terms or default_terms()
        self.confidence_threshold = confidence_threshold
        self._aliases = self._build_alias_index(self.terms)

    def map_term(self, term: str, field_type: FieldType = FieldType.UNKNOWN) -> MappingResult:
        normalized = normalize_text(term)
        if not normalized:
            return self._empty_result(term, normalized, field_type)

        candidates = self._candidate_terms(field_type)
        exact = self._exact_match(normalized, candidates)
        if exact is not None:
            ontology_term, matched_text = exact
            return self._result(term, normalized, field_type, ontology_term, matched_text, 1.0)

        best_term: OntologyTerm | None = None
        best_alias: str | None = None
        best_score = 0.0
        for ontology_term in candidates:
            for alias in self._aliases[ontology_term.term_id]:
                score = _similarity(normalized, alias)
                if score > best_score:
                    best_term = ontology_term
                    best_alias = alias
                    best_score = score

        if best_term is None:
            return self._empty_result(term, normalized, field_type)

        return self._result(term, normalized, field_type, best_term, best_alias, best_score)

    def map_terms(
        self,
        terms: list[str],
        field_type: FieldType = FieldType.UNKNOWN,
    ) -> list[MappingResult]:
        """Map multiple terms with the same semantic field type."""

        return [self.map_term(term, field_type) for term in terms]

    def _candidate_terms(self, field_type: FieldType) -> list[OntologyTerm]:
        if field_type == FieldType.UNKNOWN:
            return self.terms

        ontology = ONTOLOGY_BY_FIELD.get(field_type)
        return [
            term
            for term in self.terms
            if field_type in term.field_types or term.ontology == ontology
        ]

    def _exact_match(
        self,
        normalized: str,
        candidates: list[OntologyTerm],
    ) -> tuple[OntologyTerm, str] | None:
        candidate_ids = {term.term_id for term in candidates}
        for ontology_term in candidates:
            if normalized in self._aliases[ontology_term.term_id]:
                return ontology_term, normalized
        for alias, term in self._alias_to_term.items():
            if alias == normalized and term.term_id in candidate_ids:
                return term, alias
        return None

    def _result(
        self,
        source_text: str,
        normalized: str,
        field_type: FieldType,
        ontology_term: OntologyTerm,
        matched_text: str | None,
        confidence: float,
    ) -> MappingResult:
        return MappingResult(
            source_text=source_text,
            normalized_text=normalized,
            field_type=field_type,
            ontology_id=ontology_term.term_id,
            label=ontology_term.label,
            ontology=ontology_term.ontology,
            confidence=round(confidence, 4),
            matched_text=matched_text,
            backend=self.backend_name,
            accepted=confidence >= self.confidence_threshold,
        )

    def _empty_result(self, source_text: str, normalized: str, field_type: FieldType) -> MappingResult:
        return MappingResult(
            source_text=source_text,
            normalized_text=normalized,
            field_type=field_type,
            ontology_id=None,
            label=None,
            ontology=None,
            confidence=0.0,
            matched_text=None,
            backend=self.backend_name,
            accepted=False,
        )

    def _build_alias_index(self, terms: list[OntologyTerm]) -> dict[str, tuple[str, ...]]:
        self._alias_to_term: dict[str, OntologyTerm] = {}
        aliases: dict[str, tuple[str, ...]] = {}
        for term in terms:
            normalized_aliases = {
                normalize_text(term.label, expand_abbreviations=False),
                *[normalize_text(synonym, expand_abbreviations=False) for synonym in term.synonyms],
            }
            normalized_aliases.discard("")
            aliases[term.term_id] = tuple(sorted(normalized_aliases))
            for alias in normalized_aliases:
                self._alias_to_term.setdefault(alias, term)
        return aliases


class Text2TermMapper:
    """Adapter for the optional text2term dependency."""

    backend_name = "text2term"

    def __init__(self, *, confidence_threshold: float = 0.70, **kwargs: object) -> None:
        try:
            import text2term  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "The text2term backend requires the optional 'text2term' dependency. "
                "Install omicsmeta with the text2term extra."
            ) from exc

        self.text2term = text2term
        self.confidence_threshold = confidence_threshold
        self.kwargs = kwargs

    def map_term(self, term: str, field_type: FieldType = FieldType.UNKNOWN) -> MappingResult:
        normalized = normalize_text(term)
        if not normalized:
            return MappingResult(term, normalized, field_type, None, None, None, 0.0, None, self.backend_name, False)

        if not hasattr(self.text2term, "map_terms"):
            raise RuntimeError("Installed text2term package does not expose map_terms().")

        mapped = self.text2term.map_terms([normalized], **self.kwargs)
        row = _first_mapping_row(mapped)
        if row is None:
            return MappingResult(term, normalized, field_type, None, None, None, 0.0, None, self.backend_name, False)

        confidence = float(row.get("confidence", row.get("score", 0.0)))
        if confidence > 1.0:
            confidence = confidence / 100.0

        ontology_id = row.get("term_id") or row.get("iri") or row.get("ontology_id")
        label = row.get("label") or row.get("term_label")
        ontology = row.get("ontology") or ONTOLOGY_BY_FIELD.get(field_type)
        matched_text = row.get("mapped_term") or row.get("matched_text") or label

        return MappingResult(
            source_text=term,
            normalized_text=normalized,
            field_type=field_type,
            ontology_id=str(ontology_id) if ontology_id else None,
            label=str(label) if label else None,
            ontology=str(ontology) if ontology else None,
            confidence=round(confidence, 4),
            matched_text=str(matched_text) if matched_text else None,
            backend=self.backend_name,
            accepted=confidence >= self.confidence_threshold,
        )


def default_terms() -> list[OntologyTerm]:
    """Return a small offline vocabulary for tests and common metadata."""

    return [
        OntologyTerm("DOID:1612", "breast cancer", "doid", ("breast carcinoma", "mammary carcinoma", "brca"), (FieldType.DISEASE,)),
        OntologyTerm("DOID:3908", "non-small cell lung carcinoma", "doid", ("non-small cell lung cancer", "nsclc"), (FieldType.DISEASE,)),
        OntologyTerm("DOID:3910", "lung adenocarcinoma", "doid", ("lung adenocarcinoma cancer", "luad"), (FieldType.DISEASE,)),
        OntologyTerm("DOID:299", "adenocarcinoma", "doid", (), (FieldType.DISEASE,)),
        OntologyTerm("DOID:1324", "lung cancer", "doid", ("lung carcinoma",), (FieldType.DISEASE,)),
        OntologyTerm("DOID:9256", "colorectal cancer", "doid", ("colon cancer", "crc"), (FieldType.DISEASE,)),
        OntologyTerm("DOID:8552", "acute myeloid leukemia", "doid", ("aml",), (FieldType.DISEASE,)),
        OntologyTerm("UBERON:0000310", "breast", "uberon", ("mammary gland", "breast tissue"), (FieldType.TISSUE,)),
        OntologyTerm("UBERON:0002048", "lung", "uberon", ("lung tissue",), (FieldType.TISSUE,)),
        OntologyTerm("UBERON:0002107", "liver", "uberon", ("hepatic tissue",), (FieldType.TISSUE,)),
        OntologyTerm("UBERON:0000178", "blood", "uberon", ("whole blood",), (FieldType.TISSUE,)),
        OntologyTerm("CVCL:0031", "MCF-7", "cellosaurus", ("mcf7",), (FieldType.CELL_LINE,)),
        OntologyTerm("CVCL:0030", "HeLa", "cellosaurus", (), (FieldType.CELL_LINE,)),
        OntologyTerm("CVCL:0023", "A549", "cellosaurus", (), (FieldType.CELL_LINE,)),
        OntologyTerm("NCBITaxon:9606", "Homo sapiens", "ncbitaxon", ("human",), (FieldType.SPECIES,)),
        OntologyTerm("NCBITaxon:10090", "Mus musculus", "ncbitaxon", ("mouse",), (FieldType.SPECIES,)),
        OntologyTerm("PATO:0000383", "female", "pato", ("f",), (FieldType.SEX,)),
        OntologyTerm("PATO:0000384", "male", "pato", ("m",), (FieldType.SEX,)),
    ]


def load_builtin_terms(
    ontology_paths: Sequence[str | Path] = (),
    *,
    include_defaults: bool = True,
) -> list[OntologyTerm]:
    """Load terms for the built-in mapper from defaults plus local OBO files."""

    terms = default_terms() if include_defaults else []
    for path in ontology_paths:
        terms.extend(load_obo(path))
    return _deduplicate_terms(terms)


def _deduplicate_terms(terms: list[OntologyTerm]) -> list[OntologyTerm]:
    deduplicated: dict[str, OntologyTerm] = {}
    for term in terms:
        deduplicated[term.term_id] = term
    return list(deduplicated.values())


def _similarity(left: str, right: str) -> float:
    try:
        from rapidfuzz import fuzz  # type: ignore[import-not-found]

        return float(fuzz.token_set_ratio(left, right)) / 100.0
    except ImportError:
        token_score = _token_jaccard(left, right)
        sequence_score = SequenceMatcher(None, left, right).ratio()
        return max(token_score, sequence_score)


def _token_jaccard(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _first_mapping_row(mapped: object) -> dict[str, object] | None:
    if mapped is None:
        return None
    if isinstance(mapped, list) and mapped:
        first = mapped[0]
        return first if isinstance(first, dict) else None
    if hasattr(mapped, "to_dict"):
        records = mapped.to_dict("records")
        return records[0] if records else None
    return None
