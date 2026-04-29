from prisma.ingest.dedup import deduplicate

RIS_A = """\
TY  - JOUR
TI  - Forecasting demand with Google Trends
DO  - 10.1234/abc
ER  -
TY  - JOUR
TI  - Unique to A
DO  - 10.1111/aa
ER  -
"""

RIS_B = """\
TY  - JOUR
TI  - Forecasting demand with Google Trends
DO  - https://doi.org/10.1234/abc
ER  -
TY  - JOUR
TI  - Forecasting Demand With Google Trends!
DO  -
ER  -
TY  - JOUR
TI  - Unique to B
DO  - 10.2222/bb
ER  -
"""


def test_dedup_removes_doi_match_and_fuzzy_title(tmp_path):
    a = tmp_path / "a.ris"
    b = tmp_path / "b.ris"
    a.write_text(RIS_A, encoding="utf-8")
    b.write_text(RIS_B, encoding="utf-8")

    res = deduplicate({"scopus-A": a, "openalex-A": b})

    assert res.raw_total == 5
    # 3 unique: Forecasting demand (one copy), Unique to A, Unique to B
    assert len(res.unique) == 3
    reasons = {d["reason"] for d in res.duplicates}
    assert any("DOI" in r for r in reasons)
    assert any("fuzzy" in r for r in reasons)
