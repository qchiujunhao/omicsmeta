"""Ontology loading and caching helpers."""

from omicsmeta.ontologies.cache import OntologyCache
from omicsmeta.ontologies.loader import load_obo
from omicsmeta.ontologies.resources import (
    DEFAULT_CACHE_DIR,
    OntologyResource,
    all_resource_names,
    build_ontology_index,
    cached_resource_paths,
    default_index_path,
    download_resource,
    download_resources,
    get_resource,
    list_resources,
    resource_path,
    resource_status,
)

__all__ = [
    "DEFAULT_CACHE_DIR",
    "OntologyCache",
    "OntologyResource",
    "all_resource_names",
    "build_ontology_index",
    "cached_resource_paths",
    "default_index_path",
    "download_resource",
    "download_resources",
    "get_resource",
    "list_resources",
    "load_obo",
    "resource_path",
    "resource_status",
]
