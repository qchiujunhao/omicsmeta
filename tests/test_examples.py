import csv
from pathlib import Path

from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.io.readers import read_tabular


EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "basic"


def test_basic_example_matches_expected_mapping_subset():
    result = Harmonizer().from_rows(read_tabular(EXAMPLE_DIR / "metadata.tsv"))
    observed = {
        (
            str(record["sample_id"]),
            str(record["column"]),
            str(record["field_type"]),
            str(record["ontology"]),
            str(record["ontology_id"]),
            str(record["label"]),
        )
        for record in result.harmonized
    }

    expected = {
        (
            row["sample_id"],
            row["column"],
            row["field_type"],
            row["ontology"],
            row["ontology_id"],
            row["label"],
        )
        for row in _read_expected()
    }

    assert expected <= observed


def _read_expected() -> list[dict[str, str]]:
    with (EXAMPLE_DIR / "expected_harmonized.tsv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

