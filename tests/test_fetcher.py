import pytest

from omicsmeta.core.fetcher import fetch_geo_rows, fetch_geo_soft
from omicsmeta.io.readers import parse_geo_soft


SOFT_TEXT = """^SAMPLE = GSM1
!Sample_title = sample one
!Sample_geo_accession = GSM1
!Sample_organism_ch1 = Homo sapiens
!Sample_characteristics_ch1 = disease: NSCLC
!Sample_characteristics_ch1 = tissue: lung
^SAMPLE = GSM2
!Sample_title = sample two
!Sample_geo_accession = GSM2
!Sample_organism_ch1 = Homo sapiens
!Sample_characteristics_ch1 = disease: breast cancer
!Sample_characteristics_ch1 = tissue: breast
"""


class FakeResponse:
    text = SOFT_TEXT
    url = "https://example.test/geo"

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return FakeResponse()


def test_parse_geo_soft_returns_sample_rows():
    rows = parse_geo_soft(SOFT_TEXT)
    assert len(rows) == 2
    assert rows[0]["geo_accession"] == "GSM1"
    assert rows[0]["disease"] == "NSCLC"
    assert rows[1]["tissue"] == "breast"


def test_fetch_geo_soft_uses_expected_query_parameters():
    session = FakeSession()
    fetched = fetch_geo_soft("gse123", session=session, timeout=5)
    assert fetched.accession == "GSE123"
    assert session.calls[0][1]["form"] == "text"
    assert session.calls[0][1]["view"] == "full"


def test_fetch_geo_rows_parses_response():
    rows = fetch_geo_rows("GSE123", session=FakeSession())
    assert [row["geo_accession"] for row in rows] == ["GSM1", "GSM2"]


def test_fetch_geo_soft_rejects_invalid_accession():
    with pytest.raises(ValueError, match="Invalid GEO accession"):
        fetch_geo_soft("not_geo", session=FakeSession())

