from omicsmeta.core.harmonizer import Harmonizer


def test_harmonizer_maps_known_metadata_rows():
    rows = [
        {
            "sample_id": "S1",
            "organism": "Homo sapiens",
            "disease": "NSCLC",
            "tissue": "lung",
            "sex": "female",
        }
    ]

    result = Harmonizer().from_rows(rows)

    mapped_ids = {record["ontology_id"] for record in result.harmonized}
    assert "NCBITaxon:9606" in mapped_ids
    assert "DOID:3908" in mapped_ids
    assert "UBERON:0002048" in mapped_ids
    assert result.qc_summary["mapping_rate"] > 0.7
    assert result.sample_table[0]["disease_id"] == "DOID:3908"
    assert result.sample_table[0]["tissue_id"] == "UBERON:0002048"
    assert result.sample_table[0]["species_id"] == "NCBITaxon:9606"


def test_harmonizer_tracks_unmapped_terms():
    rows = [{"sample_id": "S1", "disease": "not a real disease term"}]
    result = Harmonizer().from_rows(rows)
    assert result.unmapped
    assert result.unmapped[0]["accepted"] is False
    assert result.sample_table[0]["mapped_term_count"] == 0
    assert result.sample_table[0]["unmapped_term_count"] == 1


def test_sample_table_joins_multiple_mappings_per_field():
    rows = [{"sample_id": "S1", "disease": "NSCLC; breast cancer"}]

    result = Harmonizer().from_rows(rows)

    assert result.sample_table[0]["disease_id"] == "DOID:3908; DOID:1612"
    assert result.sample_table[0]["disease_source_columns"] == "disease"
