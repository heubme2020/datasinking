# -*- coding: utf-8 -*-
"""DataSinking MCP server (Model Context Protocol).

Expose the DataSinking API — full-text financial reports across Asia
(China, Korea, Japan) as clean Markdown — to AI agents (Claude, Cursor,
Codex, DeepSeek, Windsurf, …).

Install the MCP extra::

    pip install "datasinking[mcp]"

Then run::

    datasinking-mcp

or add to any MCP client with ``command: datasinking-mcp`` (stdio). Requires
the environment variable ``DATASINK_API_KEY`` (get a free key at
https://datasink.ing).
"""

import os
from typing import Optional

import requests

# mcp v1 uses FastMCP; v2 renamed it to MCPServer. Support both.
try:
    from mcp.server.fastmcp import FastMCP  # mcp v1
except ImportError:  # pragma: no cover
    from mcp.server.mcpserver import MCPServer as FastMCP  # mcp v2

BASE_URL = "https://api.datasink.ing"
API_KEY = os.environ.get("DATASINK_API_KEY", "")

mcp = FastMCP(
    "DataSinking",
    version="0.2.1",
    instructions=(
        "DataSinking serves full-text financial reports (annual / semi-annual / quarterly) "
        "from China, Korea and Japan as clean Markdown, ready for LLM reading and RAG. "
        "Use FMP-style symbols: 600519.SS (Kweichow Moutai), 005930.KS (Samsung Electronics), "
        "7203.T (Toyota). To save tokens, prefer get_section to pull one chapter (e.g. MD&A) "
        "instead of get_report for the whole document."
    ),
)


def _get(path: str, params: Optional[dict] = None) -> dict:
    """Call the DataSinking API, carrying the API key automatically."""
    if not API_KEY:
        raise RuntimeError(
            "Missing DATASINK_API_KEY environment variable (get a free key at https://datasink.ing)"
        )
    p = dict(params or {})
    p["apikey"] = API_KEY
    r = requests.get(f"{BASE_URL}{path}", params=p, timeout=90)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def list_exchanges() -> list:
    """List the exchanges DataSinking covers and their report counts.

    Returns exchange codes (sse / szse / bj / ksc / koe / knx / jpx) with the number
    of reports available per exchange. Call this first to discover coverage.
    """
    return _get("/exchanges").get("exchanges", [])


@mcp.tool()
def list_stocks(exchange: str, limit: int = 20) -> dict:
    """List stocks on an exchange, including the report count per company.

    Args:
        exchange: Exchange code, e.g. sse / szse / bj / ksc / koe / knx / jpx
        limit: Return the first N companies (default 20) to keep responses short.
    """
    data = _get("/stocks", {"exchange": exchange})
    return {"exchange": exchange, "total": data.get("total", 0), "items": data.get("items", [])[:limit]}


@mcp.tool()
def list_reports(symbol: str, doc_type: str = "annual", size: int = 10) -> dict:
    """List a company's reports — metadata only (id, title, period), no body text.

    Args:
        symbol: FMP-style symbol, e.g. 600519.SS / 005930.KS / 7203.T
        doc_type: annual / semiannual / q1 / q3
        size: Number of reports to return (default 10).
    """
    return _get("/documents", {"symbol": symbol, "doc_type": doc_type, "size": size})


@mcp.tool()
def get_report(document_id: int) -> dict:
    """Fetch a single report's full text (metadata + Markdown body).

    Args:
        document_id: Report id, from list_reports items[].id
    """
    return _get(f"/documents/{document_id}")


@mcp.tool()
def list_sections(document_id: int) -> dict:
    """List every section heading in a report (feed the headings to get_section).

    Args:
        document_id: Report id
    """
    return _get(f"/documents/{document_id}/sections")


@mcp.tool()
def get_section(document_id: int, section: str) -> dict:
    """Fetch only one section of a report by keyword — cheaper than get_report for RAG.

    Args:
        document_id: Report id
        section: Heading keyword, e.g. "management discussion" / "MD&A" / "financial statements" / "notes"
    """
    return _get(f"/documents/{document_id}", {"section": section})


def main() -> None:
    """Entry point for the ``datasinking-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
