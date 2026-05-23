from pathlib import Path

import pytest

from omicsmeta.ontologies.cache import OntologyCache
from omicsmeta.ontologies.resources import (
    all_resource_names,
    build_ontology_index,
    cached_resource_paths,
    download_resource,
    download_resources,
    get_resource,
    resource_path,
    resource_status,
)


OBO_TEXT = """format-version: 1.2

[Term]
id: DOID:1234567
name: Cache disease
synonym: "Cache syndrome" EXACT []
"""


class FakeResponse:
    content = OBO_TEXT.encode("utf-8")
    text = OBO_TEXT

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.urls = []

    def get(self, url, *, timeout):
        self.urls.append((url, timeout))
        return FakeResponse()


def test_known_resource_registry_is_stable():
    assert all_resource_names() == ["cl", "doid", "efo", "ncbitaxon", "uberon"]
    assert get_resource("DOID").filename == "doid.obo"
    with pytest.raises(ValueError, match="Unknown ontology resource"):
        get_resource("missing")


def test_download_resource_writes_to_cache(tmp_path):
    session = FakeSession()
    path = download_resource("doid", cache_dir=tmp_path, session=session, timeout=3)

    assert path == tmp_path / "doid.obo"
    assert path.read_text(encoding="utf-8") == OBO_TEXT
    assert session.urls == [(get_resource("doid").url, 3)]


def test_download_resource_reuses_existing_file_without_overwrite(tmp_path):
    path = resource_path("doid", cache_dir=tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("existing", encoding="utf-8")

    returned = download_resource("doid", cache_dir=tmp_path, session=FakeSession())

    assert returned == path
    assert path.read_text(encoding="utf-8") == "existing"


def test_download_resources_downloads_multiple_names(tmp_path):
    paths = download_resources(["doid", "uberon"], cache_dir=tmp_path, session=FakeSession())
    assert paths == [tmp_path / "doid.obo", tmp_path / "uberon.obo"]


def test_cached_resource_paths_require_existing_files(tmp_path):
    with pytest.raises(FileNotFoundError, match="Run 'omicsmeta ontologies download' first"):
        cached_resource_paths(["doid"], cache_dir=tmp_path)

    path = resource_path("doid", cache_dir=tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(OBO_TEXT, encoding="utf-8")

    assert cached_resource_paths(["doid"], cache_dir=tmp_path) == [path]


def test_resource_status_reports_cached_file_size(tmp_path):
    path = resource_path("doid", cache_dir=tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(OBO_TEXT, encoding="utf-8")

    rows = {row["name"]: row for row in resource_status(tmp_path)}

    assert rows["doid"]["cached"] is True
    assert rows["doid"]["size_bytes"] == len(OBO_TEXT)
    assert rows["uberon"]["cached"] is False


def test_build_ontology_index_from_obo(tmp_path):
    obo_path = tmp_path / "custom.obo"
    obo_path.write_text(OBO_TEXT, encoding="utf-8")
    index_path = tmp_path / "index.sqlite"

    count = build_ontology_index([obo_path], output_path=index_path)

    assert count == 1
    cache = OntologyCache(index_path)
    try:
        matches = cache.search_exact("Cache syndrome", ontology="doid")
    finally:
        cache.close()
    assert len(matches) == 1
    assert matches[0].term_id == "DOID:1234567"
