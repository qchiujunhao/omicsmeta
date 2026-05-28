"""Readers for metadata input formats."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
import xml.etree.ElementTree as ET


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


def read_biosample_xml(path: str | Path) -> list[dict[str, str]]:
    """Read a minimal subset of NCBI BioSample XML metadata."""

    return parse_biosample_xml(Path(path).read_text(encoding="utf-8"))


def read_sra_xml(path: str | Path) -> list[dict[str, str]]:
    """Read a minimal subset of SRA XML sample metadata."""

    return parse_sra_xml(Path(path).read_text(encoding="utf-8"))


def parse_geo_soft(text: str) -> list[dict[str, str]]:
    """Parse GEO SOFT text into one row per sample."""

    return _parse_geo_soft_lines(text.splitlines())


def parse_biosample_xml(text: str) -> list[dict[str, str]]:
    """Parse NCBI BioSample XML into one row per BioSample."""

    root = ET.fromstring(text)
    rows: list[dict[str, str]] = []
    for biosample in _iter_tag(root, "BioSample"):
        row: dict[str, str] = {}
        accession = biosample.attrib.get("accession") or _first_descendant_text(biosample, "Id")
        if accession:
            row["sample_id"] = accession.strip()
            row["biosample_accession"] = accession.strip()

        title = _first_descendant_text(biosample, "Title")
        if title:
            row["title"] = title

        organism = _first_descendant(biosample, "Organism")
        if organism is not None:
            organism_name = organism.attrib.get("taxonomy_name") or _clean_text(organism.text)
            taxonomy_id = organism.attrib.get("taxonomy_id")
            if organism_name:
                row["organism"] = organism_name
            if taxonomy_id:
                row["taxonomy_id"] = taxonomy_id

        for attribute in _iter_tag(biosample, "Attribute"):
            key = (
                attribute.attrib.get("attribute_name")
                or attribute.attrib.get("harmonized_name")
                or attribute.attrib.get("display_name")
            )
            value = _clean_text(attribute.text)
            if key and value:
                _set_or_append(row, key.strip(), value)

        if row:
            rows.append(row)
    return rows


def parse_sra_xml(text: str) -> list[dict[str, str]]:
    """Parse SRA XML into one row per SAMPLE element."""

    root = ET.fromstring(text)
    rows: list[dict[str, str]] = []
    for sample in _iter_tag(root, "SAMPLE"):
        row: dict[str, str] = {}
        accession = sample.attrib.get("accession") or sample.attrib.get("alias")
        if accession:
            row["sample_id"] = accession.strip()
            row["sra_sample_accession"] = accession.strip()

        title = _first_child_text(sample, "TITLE")
        if title:
            row["title"] = title

        sample_name = _first_child(sample, "SAMPLE_NAME")
        if sample_name is not None:
            organism = _first_child_text(sample_name, "SCIENTIFIC_NAME")
            taxonomy_id = _first_child_text(sample_name, "TAXON_ID")
            if organism:
                row["organism"] = organism
            if taxonomy_id:
                row["taxonomy_id"] = taxonomy_id

        for sample_attribute in _iter_tag(sample, "SAMPLE_ATTRIBUTE"):
            key = _first_child_text(sample_attribute, "TAG")
            value = _first_child_text(sample_attribute, "VALUE")
            if key and value:
                _set_or_append(row, key, value)

        if row:
            rows.append(row)
    return rows


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


def _iter_tag(element: ET.Element, tag_name: str) -> Iterable[ET.Element]:
    for child in element.iter():
        if _local_name(child.tag) == tag_name:
            yield child


def _first_descendant(element: ET.Element, tag_name: str) -> ET.Element | None:
    for child in element.iter():
        if child is not element and _local_name(child.tag) == tag_name:
            return child
    return None


def _first_descendant_text(element: ET.Element, tag_name: str) -> str:
    child = _first_descendant(element, tag_name)
    return _clean_text(child.text) if child is not None else ""


def _first_child(element: ET.Element, tag_name: str) -> ET.Element | None:
    for child in element:
        if _local_name(child.tag) == tag_name:
            return child
    return None


def _first_child_text(element: ET.Element, tag_name: str) -> str:
    child = _first_child(element, tag_name)
    return _clean_text(child.text) if child is not None else ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _clean_text(value: object) -> str:
    return str(value).strip() if value is not None else ""
