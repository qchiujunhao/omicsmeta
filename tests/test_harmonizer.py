from omicsmeta.core.harmonizer import Harmonizer, merge_results


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
    assert result.unmapped_summary[0]["normalized_term"] == "not a real disease term"
    assert result.unmapped_summary[0]["occurrence_count"] == 1
    assert result.sample_table[0]["mapped_term_count"] == 0
    assert result.sample_table[0]["unmapped_term_count"] == 1


def test_unmapped_summary_groups_repeated_terms():
    rows = [
        {"sample_id": "S1", "treatment": "cisplatin"},
        {"sample_id": "S2", "treatment": "cisplatin"},
        {"sample_id": "S3", "treatment": "vehicle"},
    ]

    result = Harmonizer().from_rows(rows)

    assert result.qc_summary["unique_unmapped_terms"] == 2
    assert result.unmapped_summary[0]["normalized_term"] == "cisplatin"
    assert result.unmapped_summary[0]["occurrence_count"] == 2
    assert result.unmapped_summary[0]["sample_ids"] == "S1; S2"
    assert result.unmapped_summary[0]["columns"] == "treatment"


def test_sample_table_joins_multiple_mappings_per_field():
    rows = [{"sample_id": "S1", "disease": "NSCLC; breast cancer"}]

    result = Harmonizer().from_rows(rows)

    assert result.sample_table[0]["disease_id"] == "DOID:3908; DOID:1612"
    assert result.sample_table[0]["disease_source_columns"] == "disease"


def test_merge_results_adds_batch_source_and_recomputes_summary():
    harmonizer = Harmonizer()
    first = harmonizer.from_rows([{"sample_id": "S1", "treatment": "cisplatin"}])
    second = harmonizer.from_rows([{"sample_id": "S2", "treatment": "cisplatin"}])

    merged = merge_results([("first.tsv", first), ("second.tsv", second)])

    assert {record["batch_source"] for record in merged.unmapped} == {"first.tsv", "second.tsv"}
    assert {row["batch_source"] for row in merged.sample_table} == {"first.tsv", "second.tsv"}
    assert merged.unmapped_summary[0]["normalized_term"] == "cisplatin"
    assert merged.unmapped_summary[0]["occurrence_count"] == 2
    assert merged.unmapped_summary[0]["batch_sources"] == "first.tsv; second.tsv"
