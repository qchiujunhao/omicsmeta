"""Metadata fetchers for public omics repositories."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from omicsmeta.io.readers import parse_geo_soft

GEO_ACCESSION_RE = re.compile(r"^(GSE|GSM|GPL|GDS)\d+$", re.IGNORECASE)
GEO_ACC_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"


class HTTPSession(Protocol):
    """Small protocol matching requests-like sessions."""

    def get(self, url: str, *, params: dict[str, str], timeout: float):
        """Issue an HTTP GET request."""


@dataclass(frozen=True)
class GeoSoftFetch:
    """Fetched GEO SOFT text and provenance."""

    accession: str
    text: str
    url: str


def fetch_geo_soft(
    accession: str,
    *,
    session: HTTPSession | None = None,
    timeout: float = 30.0,
) -> GeoSoftFetch:
    """Fetch full GEO SOFT text for a GEO accession."""

    normalized_accession = accession.strip().upper()
    if not GEO_ACCESSION_RE.match(normalized_accession):
        raise ValueError(f"Invalid GEO accession: {accession!r}")

    http = session or _requests_session()
    response = http.get(
        GEO_ACC_URL,
        params={
            "acc": normalized_accession,
            "targ": "self",
            "form": "text",
            "view": "full",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    text = response.text
    if "!Sample_" not in text and "!Series_" not in text:
        raise ValueError(f"GEO response for {normalized_accession} did not contain SOFT metadata.")
    return GeoSoftFetch(accession=normalized_accession, text=text, url=response.url)


def fetch_geo_rows(
    accession: str,
    *,
    session: HTTPSession | None = None,
    timeout: float = 30.0,
) -> list[dict[str, str]]:
    """Fetch GEO metadata and parse sample rows."""

    fetched = fetch_geo_soft(accession, session=session, timeout=timeout)
    rows = parse_geo_soft(fetched.text)
    if not rows:
        raise ValueError(f"No sample metadata rows found in GEO response for {fetched.accession}.")
    return rows


def _requests_session() -> HTTPSession:
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            "Fetching GEO metadata requires the 'requests' dependency. "
            "Install omicsmeta with its default dependencies."
        ) from exc
    return requests.Session()

