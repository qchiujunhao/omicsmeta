import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parents[1]
WRAPPER = REPO_ROOT / "galaxy-omicsmeta" / "omicsmeta_harmonize.py"
TEST_DATA = REPO_ROOT / "galaxy-omicsmeta" / "test-data" / "raw_metadata.tsv"


def test_galaxy_wrapper_runs_harmonization_outputs(tmp_path):
    harmonized = tmp_path / "harmonized.tsv"
    unmapped = tmp_path / "unmapped.tsv"
    unmapped_summary = tmp_path / "unmapped_summary.tsv"
    samples = tmp_path / "samples.tsv"
    report = tmp_path / "report.html"

    subprocess.run(
        [
            sys.executable,
            str(WRAPPER),
            "--input",
            str(TEST_DATA),
            "--input-type",
            "tabular",
            "--output-harmonized",
            str(harmonized),
            "--output-unmapped",
            str(unmapped),
            "--output-unmapped-summary",
            str(unmapped_summary),
            "--output-samples",
            str(samples),
            "--output-report",
            str(report),
        ],
        check=True,
    )

    assert "DOID:3908" in harmonized.read_text(encoding="utf-8")
    assert "occurrence_count" in unmapped_summary.read_text(encoding="utf-8")
    assert "disease_id" in samples.read_text(encoding="utf-8")
    assert "mapping_rate" in report.read_text(encoding="utf-8")
