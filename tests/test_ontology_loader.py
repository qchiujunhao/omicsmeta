from pathlib import Path

from omicsmeta.ontologies.cache import OntologyCache
from omicsmeta.ontologies.loader import load_obo


def test_load_obo_reads_terms_and_synonyms():
    terms = load_obo(Path(__file__).parent / "fixtures" / "tiny.obo")
    assert len(terms) == 1
    assert terms[0].term_id == "TEST:0001"
    assert terms[0].synonyms == ("Example synonym",)


def test_ontology_cache_exact_search(tmp_path):
    terms = load_obo(Path(__file__).parent / "fixtures" / "tiny.obo")
    cache = OntologyCache(tmp_path / "ontology.sqlite")
    try:
        cache.add_terms(terms)
        matches = cache.search_exact("example synonym")
    finally:
        cache.close()
    assert len(matches) == 1
    assert matches[0].term_id == "TEST:0001"

