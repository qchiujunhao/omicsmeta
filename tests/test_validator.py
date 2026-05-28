from omicsmeta.core.harmonizer import Harmonizer


def test_harmonizer_reports_cell_line_conflicts():
    rows = [
        {
            "sample_id": "S1",
            "organism": "Mus musculus",
            "cell line": "MCF-7",
            "tissue": "lung",
        }
    ]

    result = Harmonizer().from_rows(rows)

    assert result.issues
    assert result.qc_summary["validation_issue_count"] == len(result.issues)
    messages = " ".join(issue.message for issue in result.issues)
    assert "MCF-7 implies species" in messages


def test_harmonizer_infers_missing_terms_from_cell_line():
    rows = [{"sample_id": "S1", "cell line": "A549"}]

    result = Harmonizer().from_rows(rows)

    inferred = [record for record in result.harmonized if record["backend"] == "inference"]
    inferred_ids = {record["ontology_id"] for record in inferred}
    assert inferred_ids == {"NCBITaxon:9606", "UBERON:0002048", "DOID:3910"}
    assert result.qc_summary["mapped_terms"] == 1
    assert result.qc_summary["inferred_terms"] == 3
    assert result.sample_table[0]["mapped_term_count"] == 1
    assert result.sample_table[0]["inferred_term_count"] == 3
    assert result.sample_table[0]["species_id"] == "NCBITaxon:9606"
    assert result.sample_table[0]["tissue_id"] == "UBERON:0002048"
    assert result.sample_table[0]["disease_id"] == "DOID:3910"


def test_harmonizer_infers_extended_cell_line_contexts():
    rows = [
        {"sample_id": "S1", "cell line": "HEK293"},
        {"sample_id": "S2", "cell line": "U87MG"},
        {"sample_id": "S3", "cell line": "Jurkat"},
    ]

    result = Harmonizer().from_rows(rows)

    by_sample = {row["sample_id"]: row for row in result.sample_table}
    assert by_sample["S1"]["tissue_id"] == "UBERON:0002113"
    assert by_sample["S2"]["tissue_id"] == "UBERON:0000955"
    assert by_sample["S2"]["disease_id"] == "DOID:3068"
    assert by_sample["S3"]["tissue_id"] == "UBERON:0000178"


def test_harmonizer_does_not_infer_over_observed_conflict():
    rows = [{"sample_id": "S1", "cell line": "MCF-7", "tissue": "lung"}]

    result = Harmonizer().from_rows(rows)

    tissue_records = [
        record
        for record in result.harmonized
        if record["field_type"] == "tissue"
    ]
    assert {record["ontology_id"] for record in tissue_records} == {"UBERON:0002048"}
    assert result.issues
