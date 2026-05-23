"""Managed ontology resource downloads and indexes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from omicsmeta.ontologies.cache import OntologyCache
from omicsmeta.ontologies.loader import load_obo

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "omicsmeta" / "ontologies"
DEFAULT_INDEX_NAME = "ontology_terms.sqlite"


class HTTPSession(Protocol):
    """Small protocol matching requests-like sessions."""

    def get(self, url: str, *, timeout: float):
        """Issue an HTTP GET request."""


@dataclass(frozen=True)
class OntologyResource:
    """A known ontology download source."""

    name: str
    url: str
    filename: str
    description: str


RESOURCE_REGISTRY: dict[str, OntologyResource] = {
    "doid": OntologyResource(
        name="doid",
        url="https://purl.obolibrary.org/obo/doid.obo",
        filename="doid.obo",
        description="Disease Ontology",
    ),
    "uberon": OntologyResource(
        name="uberon",
        url="https://purl.obolibrary.org/obo/uberon.obo",
        filename="uberon.obo",
        description="Uber-anatomy ontology",
    ),
    "cl": OntologyResource(
        name="cl",
        url="https://purl.obolibrary.org/obo/cl.obo",
        filename="cl.obo",
        description="Cell Ontology",
    ),
    "efo": OntologyResource(
        name="efo",
        url="https://www.ebi.ac.uk/efo/efo.obo",
        filename="efo.obo",
        description="Experimental Factor Ontology",
    ),
    "ncbitaxon": OntologyResource(
        name="ncbitaxon",
        url="https://purl.obolibrary.org/obo/ncbitaxon.obo",
        filename="ncbitaxon.obo",
        description="NCBI organismal classification",
    ),
}


def list_resources() -> list[OntologyResource]:
    """Return known ontology resources in stable name order."""

    return [RESOURCE_REGISTRY[name] for name in sorted(RESOURCE_REGISTRY)]


def get_resource(name: str) -> OntologyResource:
    """Return one resource by registry name."""

    key = name.strip().lower()
    try:
        return RESOURCE_REGISTRY[key]
    except KeyError as exc:
        known = ", ".join(sorted(RESOURCE_REGISTRY))
        raise ValueError(f"Unknown ontology resource {name!r}. Known resources: {known}") from exc


def resource_path(name: str, *, cache_dir: str | Path = DEFAULT_CACHE_DIR) -> Path:
    """Return the on-disk path for a managed ontology resource."""

    return Path(cache_dir) / get_resource(name).filename


def resource_status(cache_dir: str | Path = DEFAULT_CACHE_DIR) -> list[dict[str, object]]:
    """Return cache status rows for all known ontology resources."""

    rows: list[dict[str, object]] = []
    for resource in list_resources():
        path = Path(cache_dir) / resource.filename
        rows.append(
            {
                "name": resource.name,
                "description": resource.description,
                "cached": path.exists(),
                "path": str(path),
                "size_bytes": path.stat().st_size if path.exists() else 0,
                "url": resource.url,
            }
        )
    return rows


def download_resource(
    name: str,
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    session: HTTPSession | None = None,
    overwrite: bool = False,
    timeout: float = 120.0,
) -> Path:
    """Download one known ontology resource into the local cache."""

    resource = get_resource(name)
    destination = Path(cache_dir) / resource.filename
    if destination.exists() and not overwrite:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    http = session or _requests_session()
    response = http.get(resource.url, timeout=timeout)
    response.raise_for_status()
    content = _response_content(response)
    if not content.strip():
        raise ValueError(f"Downloaded ontology resource {resource.name!r} was empty.")

    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(destination)
    return destination


def download_resources(
    names: Sequence[str],
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    session: HTTPSession | None = None,
    overwrite: bool = False,
    timeout: float = 120.0,
) -> list[Path]:
    """Download multiple resources and return their local paths."""

    return [
        download_resource(
            name,
            cache_dir=cache_dir,
            session=session,
            overwrite=overwrite,
            timeout=timeout,
        )
        for name in names
    ]


def cached_resource_paths(
    names: Sequence[str],
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    require_exists: bool = True,
) -> list[Path]:
    """Resolve known resource names to cached OBO paths."""

    paths = [resource_path(name, cache_dir=cache_dir) for name in names]
    if require_exists:
        missing = [path for path in paths if not path.exists()]
        if missing:
            missing_text = ", ".join(str(path) for path in missing)
            raise FileNotFoundError(
                f"Ontology resources are not cached: {missing_text}. "
                "Run 'omicsmeta ontologies download' first."
            )
    return paths


def build_ontology_index(
    ontology_paths: Sequence[str | Path],
    *,
    output_path: str | Path,
) -> int:
    """Build a SQLite synonym index from local OBO files."""

    cache = OntologyCache(output_path)
    count = 0
    try:
        for path in ontology_paths:
            terms = load_obo(path)
            cache.add_terms(terms)
            count += len(terms)
    finally:
        cache.close()
    return count


def default_index_path(cache_dir: str | Path = DEFAULT_CACHE_DIR) -> Path:
    """Return the default SQLite ontology index path for a cache directory."""

    return Path(cache_dir) / DEFAULT_INDEX_NAME


def all_resource_names() -> list[str]:
    """Return all resource names in stable order."""

    return [resource.name for resource in list_resources()]


def _requests_session() -> HTTPSession:
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            "Downloading ontology resources requires the 'requests' dependency. "
            "Install omicsmeta with its default dependencies."
        ) from exc
    return requests.Session()


def _response_content(response: object) -> bytes:
    content = getattr(response, "content", None)
    if content is not None:
        return bytes(content)
    text = getattr(response, "text", "")
    return str(text).encode("utf-8")

