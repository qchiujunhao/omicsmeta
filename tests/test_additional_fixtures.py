from pathlib import Path

from omicsmeta.core.detector import detect_fields
from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.core.types import FieldType
from omicsmeta.io.readers import read_geo_soft


FIXTURES = Path(__file__).parent / "fixtures"


def test_immune_pbmc_fixture_maps_species_tissue_and_sex():
    rows = read_geo_soft(FIXTURES / "immune_pbmc_soft_snippet.txt")
    result = Harmonizer().from_rows(rows)

    mapped_ids = {record["ontology_id"] for record in result.harmonized}
    assert {"NCBITaxon:9606", "UBERON:0000178", "PATO:0000383", "PATO:0000384"} <= mapped_ids
    assert result.sample_table[0]["tissue_id"] == "UBERON:0000178"
    assert result.unmapped_summary


def test_mouse_liver_fixture_maps_mouse_liver_and_sex():
    rows = read_geo_soft(FIXTURES / "mouse_liver_soft_snippet.txt")
    result = Harmonizer().from_rows(rows)

    mapped_ids = {record["ontology_id"] for record in result.harmonized}
    assert {"NCBITaxon:10090", "UBERON:0002107", "PATO:0000383", "PATO:0000384"} <= mapped_ids
    assert all(row["tissue_id"] == "UBERON:0002107" for row in result.sample_table)


def test_treatment_fixture_keeps_perturbations_in_unmapped_review():
    rows = read_geo_soft(FIXTURES / "treatment_perturbation_soft_snippet.txt")
    result = Harmonizer().from_rows(rows)

    unmapped = {row["normalized_term"] for row in result.unmapped_summary}
    assert {"vehicle", "cisplatin"} <= unmapped
    assert result.sample_table[0]["cell_line_id"] == "CVCL:0023"


def test_ambiguous_phenotype_fixture_stays_unmapped():
    rows = read_geo_soft(FIXTURES / "ambiguous_phenotype_soft_snippet.txt")
    detections = detect_fields(rows)
    result = Harmonizer().from_rows(rows)

    assert detections["phenotype"].field_type == FieldType.UNKNOWN
    assert {"responder", "non-responder"} <= {row["normalized_term"] for row in result.unmapped_summary}

