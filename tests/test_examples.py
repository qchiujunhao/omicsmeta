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


def test_basic_example_matches_expected_sample_table_subset():
    result = Harmonizer().from_rows(read_tabular(EXAMPLE_DIR / "metadata.tsv"))
    observed = {
        (
            str(row["row_index"]),
            str(row["sample_id"]),
            str(row["mapped_term_count"]),
            str(row["inferred_term_count"]),
            str(row["unmapped_term_count"]),
            str(row["validation_issue_count"]),
            str(row["tissue_id"]),
            str(row["tissue_label"]),
            str(row["disease_id"]),
            str(row["disease_label"]),
            str(row["cell_line_id"]),
            str(row["cell_line_label"]),
            str(row["sex_id"]),
            str(row["sex_label"]),
            str(row["species_id"]),
            str(row["species_label"]),
        )
        for row in result.sample_table
    }

    expected = {
        (
            row["row_index"],
            row["sample_id"],
            row["mapped_term_count"],
            row["inferred_term_count"],
            row["unmapped_term_count"],
            row["validation_issue_count"],
            row["tissue_id"],
            row["tissue_label"],
            row["disease_id"],
            row["disease_label"],
            row["cell_line_id"],
            row["cell_line_label"],
            row["sex_id"],
            row["sex_label"],
            row["species_id"],
            row["species_label"],
        )
        for row in _read_expected_samples()
    }

    assert expected <= observed


def test_basic_example_matches_expected_unmapped_summary_subset():
    result = Harmonizer().from_rows(read_tabular(EXAMPLE_DIR / "metadata.tsv"))
    observed = {
        (
            str(row["field_type"]),
            str(row["normalized_term"]),
            str(row["occurrence_count"]),
            str(row["sample_ids"]),
            str(row["columns"]),
            str(row["example_terms"]),
        )
        for row in result.unmapped_summary
    }

    expected = {
        (
            row["field_type"],
            row["normalized_term"],
            row["occurrence_count"],
            row["sample_ids"],
            row["columns"],
            row["example_terms"],
        )
        for row in _read_expected_unmapped_summary()
    }

    assert expected <= observed


def _read_expected() -> list[dict[str, str]]:
    with (EXAMPLE_DIR / "expected_harmonized.tsv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_expected_samples() -> list[dict[str, str]]:
    with (EXAMPLE_DIR / "expected_samples.tsv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_expected_unmapped_summary() -> list[dict[str, str]]:
    with (EXAMPLE_DIR / "expected_unmapped_summary.tsv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))
