from pathlib import Path

from omicsmeta.core.mapper import BuiltinMapper, load_builtin_terms
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
