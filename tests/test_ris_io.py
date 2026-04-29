from prisma.ingest.ris_io import (
    get_all_fields,
    get_field,
    normalize_doi,
    normalize_title,
    parse_ris,
    record_to_ris,
)

SAMPLE_RIS = """\
TY  - JOUR
TI  - Forecasting demand with Google Trends
AU  - Smith, A.
AU  - Jones, B.
PY  - 2024
JO  - Journal of Forecasting
DO  - https://doi.org/10.1234/abc.def
KW  - search data
KW  - forecasting
AB  - We use Google Trends to forecast retail demand.
ER  -

TY  - JOUR
TI  - Bibliometric review of digital signals
AU  - Lopez, C.
PY  - 2023
DO  - 10.5555/xyz.123
ER  -
"""


def test_parse_ris(tmp_path):
    p = tmp_path / "sample.ris"
    p.write_text(SAMPLE_RIS, encoding="utf-8")
    records = parse_ris(p)
    assert len(records) == 2
    r0 = records[0]
    assert get_field(r0, "TI") == "Forecasting demand with Google Trends"
    assert get_all_fields(r0, "AU") == ["Smith, A.", "Jones, B."]
    assert get_all_fields(r0, "KW") == ["search data", "forecasting"]


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1234/abc") == "10.1234/abc"
    assert normalize_doi("DOI: 10.1234/ABC") == "10.1234/abc"
    assert normalize_doi("10.1234/abc") == "10.1234/abc"


def test_normalize_title():
    assert (
        normalize_title("  Forecasting!! demand: a Study  ")
        == "forecasting demand a study"
    )


def test_record_to_ris_round_trip(tmp_path):
    p = tmp_path / "sample.ris"
    p.write_text(SAMPLE_RIS, encoding="utf-8")
    records = parse_ris(p)
    serialized = record_to_ris(records[0])
    assert "TI  - Forecasting demand with Google Trends" in serialized
    assert "ER  - " in serialized
