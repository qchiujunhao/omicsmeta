from pathlib import Path

from omicsmeta.benchmark import benchmark_file, benchmark_suite, write_benchmark_json


EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "basic"
BENCHMARK_DIR = Path(__file__).parents[1] / "benchmarks"


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


def test_benchmark_suite_scores_all_known_answer_fixtures(tmp_path):
    summary = benchmark_suite(BENCHMARK_DIR / "known_answer_suite.tsv")

    assert summary["case_count"] == 8
    assert summary["overall"]["precision"] == 1.0
    assert summary["overall"]["recall"] == 1.0
    assert summary["overall"]["f1"] == 1.0
    assert summary["by_field"]["species"]["true_positive"] == 16

    output_path = tmp_path / "suite.json"
    write_benchmark_json(summary, output_path)
    assert '"case_count": 8' in output_path.read_text(encoding="utf-8")
