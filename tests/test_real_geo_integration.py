from pathlib import Path

from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.io.readers import read_geo_soft


FIXTURE = Path(__file__).parent / "fixtures" / "GSE154243_soft_snippet.txt"


def test_harmonizer_maps_real_geo_soft_snippet():
    rows = read_geo_soft(FIXTURE)

    result = Harmonizer().from_rows(rows)

    assert [row["geo_accession"] for row in rows] == ["GSM4667502", "GSM4667503"]
    mapped_ids = {record["ontology_id"] for record in result.harmonized}
    assert "NCBITaxon:9606" in mapped_ids
    assert "UBERON:0002048" in mapped_ids
    assert "CVCL:0023" in mapped_ids
    assert "DOID:299" in mapped_ids
    assert result.qc_summary["mapped_terms"] >= 8
    assert result.unmapped


def test_real_geo_source_name_typo_is_normalized_for_review():
    result = Harmonizer().from_file(str(FIXTURE), file_type="geo_soft")

    source_records = [
        record
        for record in result.unmapped
        if record["column"] == "source_name_ch1"
    ]

    assert source_records
    assert all("caner" not in record["normalized_term"] for record in source_records)
    assert all("cancer" in record["normalized_term"] for record in source_records)
