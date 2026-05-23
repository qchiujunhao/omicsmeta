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
