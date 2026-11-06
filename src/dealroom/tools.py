"""Tools the agents call. The same functions are exposed to any MCP client by
``dealroom.mcp_server`` (search_filings, get_page, list_companies, compute_change).

Every evidence item carries company, page, 10-K Item and chunk id, so a claim can
always be traced back to the exact filing page it came from.
"""
from __future__ import annotations

import re
import threading
from functools import lru_cache

from filingsight import config as fs_config
from filingsight.index import load_index
from filingsight.pipeline import run_retrieval
from filingsight.retrieval import QueryPlan, plan_query

from .guardrails import sanitize_evidence_text

_COMPANY_NAMES = {c.lower(): c for c in fs_config.COMPANIES}
_INDEX_LOCK = threading.Lock()


def get_index():
    """Load the search index once. Parallel agents must not build it twice at the same time."""
    with _INDEX_LOCK:
        return load_index(fs_config.DEFAULT_CHUNKING)


def _evidence(doc, score: float, topic: str = "") -> dict:
    m = doc.metadata
    return {
        "chunk_id": m["chunk_id"],
        "company": m["company"],
        "page": int(m["page"]),
        "item": m.get("item", ""),
        "item_title": m.get("item_title", ""),
        "header": m.get("header", ""),
        "text": sanitize_evidence_text(doc.page_content),
        "score": round(float(score), 3),
        "topic": topic,
        "source": m.get("source", ""),
    }


def search_filings(query: str, company: str | None = None, k: int = 5, topic: str = "") -> list[dict]:
    """Hybrid search (dense + BM25 + rerank) over the 10-K filings.

    ``company`` restricts the search to one filer ("Uber" or "Lyft"); None searches all
    filers with a fair share per company.
    """
    get_index()
    if company:
        company = _COMPANY_NAMES.get(company.lower(), company)
        plan = QueryPlan(question=query, companies=[company], sub_queries=[(query, company)])
    else:
        plan = plan_query(query)
    result = run_retrieval(query, plan=plan, k=k)
    return [_evidence(d, s, topic) for d, s in result.context]


def list_companies() -> list[dict]:
    """Filers in the knowledge base and the fiscal years their 10-K covers."""
    return [
        {"company": f.company, "ticker": f.ticker, "form": f.form, "fiscal_year": f.fiscal_year,
         "covered_years": list(f.covered_years), "file": f.file}
        for f in fs_config.FILINGS
    ]


_PAGES_LOCK = threading.Lock()


def _docs_by_page() -> dict[tuple[str, int], list]:
    with _PAGES_LOCK:
        return _build_pages()


@lru_cache(maxsize=1)
def _build_pages() -> dict[tuple[str, int], list]:
    index = get_index()
    pages: dict[tuple[str, int], list] = {}
    for d in index.docs:
        pages.setdefault((d.metadata["company"], int(d.metadata["page"])), []).append(d)
    return pages


def get_page(company: str, page: int) -> str:
    """Full text of one filing page (all chunks on that page, in order)."""
    company = _COMPANY_NAMES.get(company.lower(), company)
    docs = _docs_by_page().get((company, int(page)), [])
    return "\n".join(sanitize_evidence_text(d.page_content) for d in docs)


def get_chunk(chunk_id: str) -> dict | None:
    for docs in _docs_by_page().values():
        for d in docs:
            if d.metadata["chunk_id"] == chunk_id:
                return _evidence(d, 1.0)
    return None


def compute_change(old: float, new: float) -> dict:
    """Year-over-year change between two values: absolute and percent."""
    delta = new - old
    pct = None if old == 0 else delta / abs(old) * 100
    return {"old": old, "new": new, "change": round(delta, 2), "pct": None if pct is None else round(pct, 1)}


_NUM = re.compile(r"\(?-?\$?\d[\d,]*(?:\.\d+)?\)?")


def parse_number(cell: str) -> float | None:
    """'$(1,009.4)' -> -1009.4 ; '17,455' -> 17455.0 ; '—' -> None"""
    cell = cell.strip()
    m = _NUM.search(cell)
    if not m:
        return None
    raw = m.group(0)
    neg = raw.startswith("(") or "-" in raw
    val = float(re.sub(r"[^\d.]", "", raw))
    return -val if neg else val


def search_many_via_mcp(requests: list[dict]) -> list[list[dict]]:
    """Run several searches through the MCP server (stdio), one client session for all.

    Each request is {"query", "company", "k", "topic"}. Used by the Researcher when
    DR_RESEARCH_VIA_MCP=1, to show the agent consuming the knowledge base as an MCP tool.
    """
    import asyncio
    import json
    import os
    import sys

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    src = str(fs_config.ROOT / "src")
    env = {**os.environ, "PYTHONPATH": src + os.pathsep + os.environ.get("PYTHONPATH", "")}

    async def run() -> list[list[dict]]:
        params = StdioServerParameters(command=sys.executable, args=["-m", "dealroom.mcp_server"], env=env)
        out = []
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for r in requests:
                    res = await session.call_tool("search_filings", {"query": r["query"], "company": r.get("company"), "k": r.get("k", 4)})
                    if getattr(res, "structuredContent", None) and isinstance(res.structuredContent.get("result"), list):
                        hits = res.structuredContent["result"]
                    else:
                        hits = [json.loads(c.text) for c in res.content if getattr(c, "text", None)]
                    out.append([{**h, "topic": r.get("topic", "")} for h in hits])
        return out

    return asyncio.run(run())
