from omicsmeta.core.harmonizer import Harmonizer


def test_harmonizer_reports_cell_line_conflicts():
    rows = [
        {
            "sample_id": "S1",
            "organism": "Mus musculus",
            "cell line": "MCF-7",
            "tissue": "lung",
        }
    ]

    result = Harmonizer().from_rows(rows)

    assert result.issues
    assert result.qc_summary["validation_issue_count"] == len(result.issues)
    messages = " ".join(issue.message for issue in result.issues)
    assert "MCF-7 implies species" in messages

