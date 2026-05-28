from pathlib import Path

from omicsmeta.benchmark import benchmark_file, write_benchmark_json


EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "basic"


def test_benchmark_file_scores_example_truth(tmp_path):
    summary = benchmark_file(
        EXAMPLE_DIR / "metadata.tsv",
        EXAMPLE_DIR / "expected_harmonized.tsv",
    )

    assert summary["overall"]["precision"] == 1.0
    assert summary["overall"]["recall"] == 1.0
    assert summary["overall"]["f1"] == 1.0
    assert summary["by_field"]["disease"]["true_positive"] == 2

    output_path = tmp_path / "benchmark.json"
    write_benchmark_json(summary, output_path)
    assert '"f1": 1.0' in output_path.read_text(encoding="utf-8")

