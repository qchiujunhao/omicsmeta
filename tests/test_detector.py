from omicsmeta.core.detector import detect_field, detect_fields
from omicsmeta.core.types import FieldType


def test_detect_field_uses_column_name_and_values():
    detection = detect_field("disease state", ["BRCA", "lung carcinoma"])
    assert detection.field_type == FieldType.DISEASE
    assert detection.confidence > 0.7


def test_detect_field_identifies_cell_line_values():
    detection = detect_field("source_name", ["MCF-7", "MCF-7"])
    assert detection.field_type == FieldType.CELL_LINE


def test_detect_fields_across_rows():
    rows = [
        {"organism": "Homo sapiens", "sex": "female"},
        {"organism": "Homo sapiens", "sex": "male"},
    ]
    detections = detect_fields(rows)
    assert detections["organism"].field_type == FieldType.SPECIES
    assert detections["sex"].field_type == FieldType.SEX

