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
from typing import Annotated, Optional

import requests
from pydantic import Field

from ._version import __version__  # 版本号唯一来源（原来是硬编码，漂到了 0.2.3）

# mcp v1 uses FastMCP; v2 renamed it to MCPServer. Support both.
try:
    from mcp.server.fastmcp import FastMCP  # mcp v1
except ImportError:  # pragma: no cover
    from mcp.server.mcpserver import MCPServer as FastMCP  # mcp v2

# ⚠️ 参数描述必须写成 `Annotated[T, Field(description=...)]`，**不能只靠 docstring 的 Args 段**。
#    mcp v2（MCPServer）不再解析 docstring 的 Args —— 实测把整段 Args 当散文塞进工具描述，
#    参数级 description 全是空的（2026-09-22 用真实 stdio 握手验证）。v1 两种都认，所以这样写两边通用。


BASE_URL = "https://api.datasink.ing"
API_KEY = os.environ.get("DATASINK_API_KEY", "")

mcp = FastMCP(
    "DataSinking",
    title="DataSinking — Full-text Asian Financial Reports",
    description="Full-text Asian financial reports (China, Korea, Japan, Taiwan) as clean Markdown via API, with chapter-level access for RAG and AI agents.",
    version=__version__,
    instructions=(
        "DataSinking serves full-text financial reports (annual / semi-annual / quarterly) "
        "from China, Korea, Japan and Taiwan as clean Markdown, ready for LLM reading and RAG. "
        "Use FMP-style symbols: 600519.SS (Kweichow Moutai), 005930.KS (Samsung Electronics), "
        "7203.T (Toyota), 2330.TW (TSMC). To save tokens, prefer get_section to pull one chapter "
        "(e.g. MD&A) instead of get_report for the whole document."
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

    Returns exchange codes (sse / szse / bj / ksc / koe / knx / jpx / twse / tpex) with
    the number of reports available per exchange. Call this first to discover coverage.
    Sources: A-shares = cninfo.com.cn, Korea = DART, Japan = EDINET, Taiwan = MOPS.
    """
    return _get("/exchanges").get("exchanges", [])


@mcp.tool()
def list_stocks(
    exchange: Annotated[
        str, Field(description="Exchange code: sse / szse / bj / ksc / koe / knx / jpx / twse / tpex")
    ],
    limit: Annotated[
        int, Field(description="Return only the first N companies (default 20) to keep the response short.")
    ] = 20,
) -> dict:
    """List stocks on an exchange, including the report count per company."""
    data = _get("/stocks", {"exchange": exchange})
    return {"exchange": exchange, "total": data.get("total", 0), "items": data.get("items", [])[:limit]}


@mcp.tool()
def list_reports(
    symbol: Annotated[
        str, Field(description="FMP-style symbol, e.g. 600519.SS / 005930.KS / 7203.T / 2330.TW")
    ],
    doc_type: Annotated[
        str, Field(description="annual / semiannual / q1 / q3")
    ] = "annual",
    size: Annotated[int, Field(description="Number of reports to return (default 10).")] = 10,
) -> dict:
    """List a company's reports — metadata only (id, title, period), no body text.

    Each item carries a ``source`` field naming the official disclosure platform;
    keep that attribution when you cite it.
    """
    return _get("/documents", {"symbol": symbol, "doc_type": doc_type, "size": size})


@mcp.tool()
def get_report(
    document_id: Annotated[int, Field(description="Report id, from list_reports items[].id")],
) -> dict:
    """Fetch a single report's full text (metadata + Markdown body).

    The ``source`` field names the official disclosure platform; keep that attribution
    when you cite it. Expensive in tokens — prefer get_section when you only need one chapter.
    """
    return _get(f"/documents/{document_id}")


@mcp.tool()
def list_sections(
    document_id: Annotated[int, Field(description="Report id, from list_reports items[].id")],
) -> dict:
    """List every section heading in a report (feed the headings to get_section).

    Call this before get_section to see the exact headings — the headings are in the
    report's own language.
    """
    return _get(f"/documents/{document_id}/sections")


@mcp.tool()
def get_section(
    document_id: Annotated[int, Field(description="Report id, from list_reports items[].id")],
    section: Annotated[
        str,
        Field(
            description=(
                "Heading keyword, matched as a substring against the report's OWN headings, "
                "so pass it in the report's language. A-share reports have Chinese headings "
                "(e.g. 第三节管理层讨论与分析) — use 管理层讨论与分析 / 财务报告 there. "
                "For English-language filings, \"MD&A\" / \"financial statements\" / \"notes\" work. "
                "If nothing matches, the API returns 404 with the real headings — retry with one "
                "of those, or call list_sections first."
            )
        ),
    ],
) -> dict:
    """Fetch only one section of a report by keyword — cheaper than get_report for RAG."""
    return _get(f"/documents/{document_id}", {"section": section})


def main() -> None:
    """Entry point for the ``datasinking-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
