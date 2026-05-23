from pathlib import Path

from omicsmeta.cli import main


def test_cli_harmonize_from_tabular_file(tmp_path):
    input_path = tmp_path / "metadata.tsv"
    input_path.write_text(
        "sample_id\torganism\tdisease\ttissue\n"
        "S1\tHomo sapiens\tNSCLC\tlung\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "harmonized.tsv"
    unmapped_path = tmp_path / "unmapped.tsv"
    report_path = tmp_path / "report.html"

    exit_code = main(
        [
            "harmonize",
            str(input_path),
            "--output",
            str(output_path),
            "--unmapped",
            str(unmapped_path),
            "--report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert "DOID:3908" in output_path.read_text(encoding="utf-8")
    assert "mapping_rate" in report_path.read_text(encoding="utf-8")


def test_cli_harmonize_with_custom_obo(tmp_path):
    input_path = tmp_path / "metadata.tsv"
    input_path.write_text(
        "sample_id\tdisease\n"
        "S1\tExample syndrome\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "harmonized.tsv"
    unmapped_path = tmp_path / "unmapped.tsv"
    report_path = tmp_path / "report.html"
    obo_path = Path(__file__).parent / "fixtures" / "custom_doid.obo"

    exit_code = main(
        [
            "harmonize",
            str(input_path),
            "--ontology-obo",
            str(obo_path),
            "--no-default-terms",
            "--output",
            str(output_path),
            "--unmapped",
            str(unmapped_path),
            "--report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert "DOID:9999999" in output_path.read_text(encoding="utf-8")
