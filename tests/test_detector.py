from omicsmeta.core.detector import detect_field, detect_fields
from omicsmeta.core.types import FieldType


def test_detect_field_uses_column_name_and_values():
    detection = detect_field("disease state", ["BRCA", "lung carcinoma"])
    assert detection.field_type == FieldType.DISEASE
    assert detection.confidence > 0.7
    assert any(signal.startswith("name:disease state") for signal in detection.signals)


def test_detect_field_identifies_cell_line_values():
    detection = detect_field("source_name", ["MCF-7", "MCF-7"])
    assert detection.field_type == FieldType.CELL_LINE


def test_detect_field_identifies_cell_line_variant_values():
    detection = detect_field("source_name", ["A549/DDP", "A549/DDP"])
    assert detection.field_type == FieldType.CELL_LINE


def test_detect_field_does_not_overroute_vague_phenotype_name():
    detection = detect_field("phenotype", ["parental cell line", "chemoresistant"])
    assert detection.field_type == FieldType.UNKNOWN


def test_detect_field_uses_phenotype_when_values_support_disease():
    detection = detect_field("phenotype", ["adenocarcinoma", "adenocarcinoma"])
    assert detection.field_type == FieldType.DISEASE


def test_detect_field_routes_source_name_from_value_evidence():
    detection = detect_field("source_name_ch1", ["Non-small cell lung caner cells cultured in vitro"])
    assert detection.field_type == FieldType.DISEASE
    assert any(signal.startswith("values:") for signal in detection.signals)


def test_detect_field_routes_treatment_columns_from_name():
    detection = detect_field("treatment", ["cisplatin", "vehicle"])
    assert detection.field_type == FieldType.TREATMENT


def test_detect_fields_across_rows():
    rows = [
        {"organism": "Homo sapiens", "sex": "female"},
        {"organism": "Homo sapiens", "sex": "male"},
    ]
    detections = detect_fields(rows)
    assert detections["organism"].field_type == FieldType.SPECIES
    assert detections["sex"].field_type == FieldType.SEX
