"""DealRoom filings as an MCP server.

Exposes the same tools the Researcher and Quant agents use, so any MCP client
(Claude Desktop, Cursor, the MCP Inspector, another agent) can search the 10-K
knowledge base with citations.

Run:  python -m dealroom.mcp_server          (stdio transport)
Test: npx @modelcontextprotocol/inspector python -m dealroom.mcp_server
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `src/` importable when run as a file

from mcp.server.fastmcp import FastMCP  # noqa: E402

from dealroom import tools  # noqa: E402
from dealroom.metrics import extract_metrics  # noqa: E402

mcp = FastMCP("dealroom-filings")


@mcp.tool()
def search_filings(query: str, company: str | None = None, k: int = 5) -> list[dict]:
    """Search the Uber and Lyft FY2021 10-K filings. Returns passages with company, page, 10-K Item and text.

    Args:
        query: what to look for, e.g. "driver classification risk".
        company: optional filter, "Uber" or "Lyft".
        k: number of passages (1-10).
    """
    k = max(1, min(int(k), 10))
    return [{key: e[key] for key in ("chunk_id", "company", "page", "item", "item_title", "header", "text", "score")}
            for e in tools.search_filings(query, company=company, k=k)]


@mcp.tool()
def get_page(company: str, page: int) -> str:
    """Return the full text of one 10-K page, e.g. company="Uber", page=53."""
    return tools.get_page(company, page) or f"No indexed text for {company} p.{page}."


@mcp.tool()
def list_companies() -> list[dict]:
    """List the filers and fiscal years in the knowledge base."""
    return tools.list_companies()


@mcp.tool()
def key_metrics(company: str | None = None) -> list[dict]:
    """Key FY2020 and FY2021 figures read from the filings' tables, with page citations."""
    rows = extract_metrics([company] if company else None)
    return [{k: m[k] for k in ("company", "label", "unit", "fy2020", "fy2021", "yoy_pct", "page")} for m in rows]


@mcp.tool()
def compute_change(old: float, new: float) -> dict:
    """Absolute and percent change between two values (for year-over-year math)."""
    return tools.compute_change(old, new)


if __name__ == "__main__":
    mcp.run()
