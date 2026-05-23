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


def test_harmonizer_tracks_unmapped_terms():
    rows = [{"sample_id": "S1", "disease": "not a real disease term"}]
    result = Harmonizer().from_rows(rows)
    assert result.unmapped
    assert result.unmapped[0]["accepted"] is False

