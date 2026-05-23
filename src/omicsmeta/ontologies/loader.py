"""Lightweight OBO parser for offline ontology indexes."""

from __future__ import annotations

import re
from pathlib import Path

from omicsmeta.core.types import OntologyTerm

SYNONYM_RE = re.compile(r'^synonym:\s+"(?P<text>.+?)"')


def load_obo(path: str | Path, *, ontology: str | None = None) -> list[OntologyTerm]:
    """Parse a subset of OBO sufficient for labels and synonyms."""

    terms: list[OntologyTerm] = []
    current: dict[str, object] | None = None

    with Path(path).open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line == "[Term]":
                if current:
                    term = _term_from_stanza(current, ontology)
                    if term is not None:
                        terms.append(term)
                current = {"synonyms": []}
                continue
            if current is None:
                continue
            if line.startswith("["):
                term = _term_from_stanza(current, ontology)
                if term is not None:
                    terms.append(term)
                current = None
                continue
            if line.startswith("id: "):
                current["id"] = line.removeprefix("id: ").strip()
            elif line.startswith("name: "):
                current["name"] = line.removeprefix("name: ").strip()
            elif line.startswith("namespace: "):
                current["namespace"] = line.removeprefix("namespace: ").strip()
            elif line.startswith("is_obsolete: true"):
                current["obsolete"] = True
            else:
                match = SYNONYM_RE.match(line)
                if match:
                    synonyms = current.setdefault("synonyms", [])
                    assert isinstance(synonyms, list)
                    synonyms.append(match.group("text"))

    if current:
        term = _term_from_stanza(current, ontology)
        if term is not None:
            terms.append(term)

    return terms


def _term_from_stanza(stanza: dict[str, object], ontology: str | None) -> OntologyTerm | None:
    if stanza.get("obsolete"):
        return None

    term_id = str(stanza.get("id", "")).strip()
    label = str(stanza.get("name", "")).strip()
    if not term_id or not label:
        return None

    inferred_ontology = ontology or _ontology_from_id(term_id) or str(stanza.get("namespace", "")).lower()
    synonyms = tuple(str(value) for value in stanza.get("synonyms", ()) if str(value).strip())
    return OntologyTerm(term_id=term_id, label=label, ontology=inferred_ontology, synonyms=synonyms)


def _ontology_from_id(term_id: str) -> str:
    prefix = term_id.split(":", 1)[0].lower()
    return {"doid": "doid", "uberon": "uberon", "cl": "cl", "efo": "efo"}.get(prefix, prefix)

