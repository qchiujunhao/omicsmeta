from pathlib import Path

from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.io.readers import read_biosample_xml, read_sra_xml


FIXTURES = Path(__file__).parent / "fixtures"


def test_read_biosample_xml_returns_attribute_rows():
    rows = read_biosample_xml(FIXTURES / "biosample_snippet.xml")

    assert [row["sample_id"] for row in rows] == ["SAMN000001", "SAMN000002"]
    assert rows[0]["organism"] == "Homo sapiens"
    assert rows[0]["taxonomy_id"] == "9606"
    assert rows[0]["cell line"] == "A549"


def test_harmonizer_maps_biosample_xml():
    result = Harmonizer().from_file(str(FIXTURES / "biosample_snippet.xml"), file_type="biosample_xml")
    mapped_ids = {record["ontology_id"] for record in result.harmonized}

    assert {"NCBITaxon:9606", "UBERON:0002048", "DOID:3908", "CVCL:0023"} <= mapped_ids
    assert result.sample_table[0]["sample_id"] == "SAMN000001"


def test_read_sra_xml_returns_sample_attribute_rows():
    rows = read_sra_xml(FIXTURES / "sra_snippet.xml")

    assert [row["sample_id"] for row in rows] == ["SRS000001", "SRS000002"]
    assert rows[1]["organism"] == "Homo sapiens"
    assert rows[1]["disease state"] == "breast cancer"


def test_harmonizer_maps_sra_xml():
    result = Harmonizer().from_file(str(FIXTURES / "sra_snippet.xml"), file_type="sra_xml")
    mapped_ids = {record["ontology_id"] for record in result.harmonized}

    assert {"NCBITaxon:9606", "UBERON:0000310", "DOID:1612", "CVCL:0031"} <= mapped_ids
    assert result.sample_table[1]["sample_id"] == "SRS000002"
