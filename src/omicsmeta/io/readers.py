"""Readers for metadata input formats."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path


def read_tabular(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV or TSV metadata table as row dictionaries."""

    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t") if sample.strip() else csv.excel_tab
        reader = csv.DictReader(handle, dialect=dialect)
        return [dict(row) for row in reader]


def read_geo_soft(path: str | Path) -> list[dict[str, str]]:
    """Read a minimal subset of GEO SOFT sample metadata."""

    return parse_geo_soft(Path(path).read_text(encoding="utf-8"))


def parse_geo_soft(text: str) -> list[dict[str, str]]:
    """Parse GEO SOFT text into one row per sample."""

    return _parse_geo_soft_lines(text.splitlines())


def _parse_geo_soft_lines(lines: Iterable[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if line.startswith("^SAMPLE"):
            if current:
                rows.append(current)
            current = {}
            continue
        if not line.startswith("!Sample_") or " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        key = key.removeprefix("!Sample_")

        if key == "geo_accession" and current.get("geo_accession"):
            rows.append(current)
            current = {}

        if key == "characteristics_ch1" and ":" in value:
            characteristic_key, characteristic_value = value.split(":", 1)
            _set_or_append(current, characteristic_key.strip(), characteristic_value.strip())
        else:
            _set_or_append(current, key, value.strip())

    if current:
        rows.append(current)
    return rows


def _set_or_append(row: dict[str, str], key: str, value: str) -> None:
    if key not in row:
        row[key] = value
    elif value and value not in row[key].split("; "):
        row[key] = f"{row[key]}; {value}"
