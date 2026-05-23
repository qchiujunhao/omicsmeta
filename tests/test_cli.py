from pathlib import Path

from omicsmeta.cli import main
from omicsmeta.ontologies.resources import resource_path


def test_cli_harmonize_from_tabular_file(tmp_path):
    input_path = tmp_path / "metadata.tsv"
    input_path.write_text(
        "sample_id\torganism\tdisease\ttissue\n"
        "S1\tHomo sapiens\tNSCLC\tlung\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "harmonized.tsv"
    unmapped_path = tmp_path / "unmapped.tsv"
    sample_path = tmp_path / "samples.tsv"
    report_path = tmp_path / "report.html"

    exit_code = main(
        [
            "harmonize",
            str(input_path),
            "--output",
            str(output_path),
            "--unmapped",
            str(unmapped_path),
            "--sample-output",
            str(sample_path),
            "--report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert "DOID:3908" in output_path.read_text(encoding="utf-8")
    assert "disease_id" in sample_path.read_text(encoding="utf-8")
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


def test_cli_lists_ontology_resources(tmp_path, capsys):
    exit_code = main(["ontologies", "list", "--cache-dir", str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "name\tcached\tsize_bytes\tpath\turl\tdescription" in captured.out
    assert "doid\tfalse\t0\t" in captured.out


def test_cli_indexes_local_obo(tmp_path, capsys):
    obo_path = Path(__file__).parent / "fixtures" / "custom_doid.obo"
    index_path = tmp_path / "terms.sqlite"

    exit_code = main(
        [
            "ontologies",
            "index",
            "--ontology-obo",
            str(obo_path),
            "--output",
            str(index_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Indexed 1 terms into" in captured.out
    assert index_path.exists()


def test_cli_harmonize_with_cached_resource(tmp_path):
    obo_path = resource_path("doid", cache_dir=tmp_path)
    obo_path.parent.mkdir(parents=True, exist_ok=True)
    obo_path.write_text(
        """format-version: 1.2

[Term]
id: DOID:9999998
name: Cached disease
synonym: "Cached syndrome" EXACT []
""",
        encoding="utf-8",
    )
    input_path = tmp_path / "metadata.tsv"
    input_path.write_text("sample_id\tdisease\nS1\tCached syndrome\n", encoding="utf-8")
    output_path = tmp_path / "harmonized.tsv"
    unmapped_path = tmp_path / "unmapped.tsv"
    report_path = tmp_path / "report.html"

    exit_code = main(
        [
            "harmonize",
            str(input_path),
            "--ontology-resource",
            "doid",
            "--ontology-cache-dir",
            str(tmp_path),
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
    assert "DOID:9999998" in output_path.read_text(encoding="utf-8")
