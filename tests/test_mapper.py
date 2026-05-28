from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from omicsmeta.core.mapper import BuiltinMapper, Text2TermMapper, load_builtin_terms
from omicsmeta.core.types import FieldType


def test_builtin_mapper_exact_synonym_match():
    mapper = BuiltinMapper()
    result = mapper.map_term("non-small cell lung cancer", FieldType.DISEASE)
    assert result.accepted
    assert result.ontology_id == "DOID:3908"


def test_builtin_mapper_uses_field_type_routing():
    mapper = BuiltinMapper()
    result = mapper.map_term("breast", FieldType.TISSUE)
    assert result.accepted
    assert result.ontology_id == "UBERON:0000310"


def test_builtin_mapper_maps_common_cell_line_synonyms():
    mapper = BuiltinMapper()
    assert mapper.map_term("K562", FieldType.CELL_LINE).ontology_id == "CVCL:0004"
    assert mapper.map_term("U87MG", FieldType.CELL_LINE).ontology_id == "CVCL:0022"


def test_builtin_mapper_rejects_low_confidence_match():
    mapper = BuiltinMapper(confidence_threshold=0.95)
    result = mapper.map_term("totally unrelated metadata", FieldType.DISEASE)
    assert not result.accepted
    assert result.ontology_id is not None


def test_load_builtin_terms_from_obo_file():
    terms = load_builtin_terms(
        [Path(__file__).parent / "fixtures" / "custom_doid.obo"],
        include_defaults=False,
    )
    mapper = BuiltinMapper(terms=terms)

    result = mapper.map_term("Example syndrome", FieldType.DISEASE)

    assert result.accepted
    assert result.ontology_id == "DOID:9999999"


def test_text2term_mapper_reads_list_records(monkeypatch):
    def map_terms(terms, **kwargs):
        assert terms == ["breast cancer"]
        assert kwargs == {"source": "test"}
        return [
            {
                "term_id": "DOID:1612",
                "label": "breast cancer",
                "ontology": "doid",
                "score": 95.0,
                "mapped_term": "breast cancer",
            }
        ]

    monkeypatch.setitem(sys.modules, "text2term", SimpleNamespace(map_terms=map_terms))

    mapper = Text2TermMapper(confidence_threshold=0.9, source="test")
    result = mapper.map_term("Breast Cancer", FieldType.DISEASE)

    assert result.accepted
    assert result.confidence == 0.95
    assert result.ontology_id == "DOID:1612"
    assert result.backend == "text2term"


def test_text2term_mapper_reads_dataframe_like_records(monkeypatch):
    class FakeFrame:
        def to_dict(self, orient):
            assert orient == "records"
            return [{"iri": "UBERON:0002048", "term_label": "lung", "confidence": 0.88}]

    monkeypatch.setitem(sys.modules, "text2term", SimpleNamespace(map_terms=lambda terms: FakeFrame()))

    mapper = Text2TermMapper(confidence_threshold=0.7)
    result = mapper.map_term("lung", FieldType.TISSUE)

    assert result.accepted
    assert result.ontology_id == "UBERON:0002048"
    assert result.label == "lung"
    assert result.ontology == "uberon"


def test_text2term_mapper_rejects_empty_results(monkeypatch):
    monkeypatch.setitem(sys.modules, "text2term", SimpleNamespace(map_terms=lambda terms: []))

    result = Text2TermMapper().map_term("unknown", FieldType.DISEASE)

    assert not result.accepted
    assert result.ontology_id is None


def test_text2term_mapper_requires_map_terms(monkeypatch):
    monkeypatch.setitem(sys.modules, "text2term", SimpleNamespace())

    mapper = Text2TermMapper()
    with pytest.raises(RuntimeError, match="does not expose map_terms"):
        mapper.map_term("breast cancer", FieldType.DISEASE)


def test_text2term_mapper_reports_missing_dependency(monkeypatch):
    monkeypatch.delitem(sys.modules, "text2term", raising=False)

    with pytest.raises(RuntimeError, match="requires the optional 'text2term' dependency"):
        Text2TermMapper()
