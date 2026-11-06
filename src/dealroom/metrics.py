"""Quant agent's extraction layer: key figures read from the filings' own tables.

Each spec says which table row to read (company, page, row label) and which column
holds which year. Values are parsed from the indexed filing text at run time, so
every number in the metrics table is backed by a real page citation.
"""
from __future__ import annotations

from dataclasses import dataclass

from .tools import _docs_by_page, compute_change, parse_number


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    company: str
    page: int
    row: str  # line must start with this label
    col_2021: int  # cell index after splitting the row on "|" (0 = label)
    col_2020: int
    unit: str  # "$M", "M", "$"
    scale: float = 1.0  # multiply to convert into the unit (e.g. thousands -> millions)
    higher_is_better: bool = True


SPECS: tuple[MetricSpec, ...] = (
    # Uber: Item 7 MD&A financial highlights (in millions, 2020 then 2021)
    MetricSpec("revenue", "Revenue", "Uber", 53, "Revenue |", 2, 1, "$M"),
    MetricSpec("gross_bookings", "Gross Bookings", "Uber", 53, "Gross Bookings |", 2, 1, "$M"),
    MetricSpec("net_loss", "Net loss attributable to company", "Uber", 53, "Net loss attributable to Uber Technologies, Inc. |", 2, 1, "$M"),
    MetricSpec("adj_ebitda", "Adjusted EBITDA", "Uber", 53, "Adjusted EBITDA |", 2, 1, "$M"),
    MetricSpec("op_cash_flow", "Operating cash flow", "Uber", 65, "Net cash used in operating activities |", 2, 1, "$M"),
    MetricSpec("users", "Monthly Active Platform Consumers", "Uber", 53, 'Monthly Active Platform Consumers ("MAPCs") |', 2, 1, "M"),
    MetricSpec("trips", "Trips", "Uber", 53, "Trips |", 2, 1, "M"),
    # Lyft: Item 7 MD&A (in millions, 2021 then 2020) and cash flow (in thousands)
    MetricSpec("revenue", "Revenue", "Lyft", 69, "Revenue |", 1, 2, "$M"),
    MetricSpec("net_loss", "Net loss", "Lyft", 70, "Net loss |", 1, 2, "$M"),
    MetricSpec("adj_ebitda", "Adjusted EBITDA", "Lyft", 70, "Adjusted EBITDA |", 1, 2, "$M"),
    MetricSpec("op_cash_flow", "Operating cash flow", "Lyft", 71, "Net cash used in operating activities |", 1, 2, "$M", scale=0.001),
    MetricSpec("rev_per_rider_q4", "Revenue per Active Rider (Q4)", "Lyft", 58, "Three Months Ended December 31 |", 1, 2, "$"),
)


def _find_row(spec: MetricSpec) -> tuple[list[str], dict] | None:
    for doc in _docs_by_page().get((spec.company, spec.page), []):
        for line in doc.page_content.split("\n"):
            if line.startswith(spec.row):
                cells = [c.strip() for c in line.split("|")]
                meta = {"chunk_id": doc.metadata["chunk_id"], "page": spec.page, "row_text": line.strip(),
                        "item": doc.metadata.get("item", "")}
                return cells, meta
    return None


def extract_metric(spec: MetricSpec) -> dict | None:
    found = _find_row(spec)
    if not found:
        return None
    cells, meta = found
    try:
        v21 = parse_number(cells[spec.col_2021])
        v20 = parse_number(cells[spec.col_2020])
    except IndexError:
        return None
    if v21 is None or v20 is None:
        return None
    v21, v20 = round(v21 * spec.scale, 2), round(v20 * spec.scale, 2)
    change = compute_change(v20, v21)
    improved = (v21 > v20) == spec.higher_is_better
    return {
        "key": spec.key, "label": spec.label, "company": spec.company, "unit": spec.unit,
        "fy2021": v21, "fy2020": v20, "yoy_pct": change["pct"], "improved": improved, **meta,
    }


def extract_metrics(companies: list[str] | None = None) -> list[dict]:
    out = []
    for spec in SPECS:
        if companies and spec.company not in companies:
            continue
        m = extract_metric(spec)
        if m:
            out.append(m)
    return out


def fmt_value(value: float, unit: str) -> str:
    if unit == "$M":
        sign = "-" if value < 0 else ""
        v = abs(value)
        return f"{sign}${v / 1000:,.2f}B" if v >= 1000 else f"{sign}${v:,.0f}M"
    if unit == "M":
        return f"{value:,.0f}M"
    if unit == "$":
        return f"${value:,.2f}"
    return f"{value:,}"
