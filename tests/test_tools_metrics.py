import pytest

from dealroom.metrics import extract_metrics, fmt_value
from dealroom.tools import compute_change, get_page, parse_number, search_filings


def test_parse_number():
    assert parse_number("$(1,009.4)") == -1009.4
    assert parse_number("17,455") == 17455
    assert parse_number("—") is None


def test_compute_change():
    assert compute_change(11139, 17455)["pct"] == 56.7


@pytest.mark.parametrize("company,key,fy20,fy21", [
    ("Uber", "revenue", 11139, 17455),
    ("Uber", "adj_ebitda", -2528, -774),
    ("Uber", "users", 93, 118),
    ("Lyft", "revenue", 2364.7, 3208.3),
    ("Lyft", "adj_ebitda", -755.2, 92.9),
    ("Lyft", "op_cash_flow", -1378.9, -101.72),
])
def test_quant_reads_filing_tables(company, key, fy20, fy21):
    m = {(x["company"], x["key"]): x for x in extract_metrics()}[(company, key)]
    assert m["fy2020"] == pytest.approx(fy20, abs=0.06) and m["fy2021"] == pytest.approx(fy21, abs=0.06)
    assert m["page"] > 0 and m["row_text"]


def test_fmt_value():
    assert fmt_value(17455, "$M") == "$17.45B" and fmt_value(-774, "$M") == "-$774M"


def test_search_returns_citations_for_requested_company():
    hits = search_filings("driver classification risk", company="Lyft", k=3)
    assert hits and all(h["company"] == "Lyft" and h["page"] > 0 and h["chunk_id"] for h in hits)


def test_get_page_text():
    assert "17,455" in get_page("Uber", 53)
