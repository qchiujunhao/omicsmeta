"""Writers for harmonization outputs."""

from __future__ import annotations

import csv
import html
from collections.abc import Mapping, Sequence
from pathlib import Path


DEFAULT_COLUMNS = [
    "row_index",
    "sample_id",
    "column",
    "field_type",
    "field_confidence",
    "raw_value",
    "term",
    "normalized_term",
    "ontology",
    "ontology_id",
    "label",
    "mapping_confidence",
    "matched_text",
    "accepted",
    "backend",
]


def write_tabular(
    records: list[dict[str, object]],
    path: str | Path,
    *,
    delimiter: str = "\t",
    include_unmapped: bool = True,
    default_columns: list[str] | None = None,
) -> None:
    """Write harmonization records to a delimited text file."""

    rows = records if include_unmapped else [record for record in records if record.get("accepted")]
    columns = _columns(rows, default_columns=default_columns if default_columns is not None else DEFAULT_COLUMNS)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=delimiter, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_html_report(summary: dict[str, object], path: str | Path) -> None:
    """Write a compact static HTML QC report."""

    rows = "\n".join(_summary_row(key, value) for key, value in summary.items())
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>omicsmeta QC report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.45; }}
    table {{ border-collapse: collapse; min-width: 32rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }}
    th {{ background: #f7f7f7; }}
  </style>
</head>
<body>
  <h1>omicsmeta QC report</h1>
  <table>
    {rows}
  </table>
</body>
</html>
"""
    Path(path).write_text(document, encoding="utf-8")


def _columns(records: list[dict[str, object]], *, default_columns: list[str]) -> list[str]:
    if not records:
        return default_columns
    columns = list(default_columns)
    for record in records:
        for key in record:
            if key not in columns:
                columns.append(key)
    return columns


def _summary_row(key: str, value: object) -> str:
    return f"<tr><th>{html.escape(str(key))}</th><td>{_html_value(value)}</td></tr>"


def _html_value(value: object) -> str:
    if isinstance(value, Mapping):
        items = "".join(
            f"<li><strong>{html.escape(str(key))}</strong>: {html.escape(str(inner_value))}</li>"
            for key, inner_value in value.items()
        )
        return f"<ul>{items}</ul>"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not value:
            return ""
        items = "".join(f"<li>{_html_value(item)}</li>" for item in value)
        return f"<ul>{items}</ul>"
    return html.escape(str(value))
