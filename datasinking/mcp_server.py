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
    instructions=(
        "DataSinking 提供亚洲（中国/韩国/日本）上市公司财报的全文 Markdown。"
        "symbol 用 FMP 风格：600519.SS（茅台）、005930.KS（三星）、7203.T（丰田）。"
        "要省 token 时用 get_section 只取某一章（如 MD&A），而不是 get_report 拿整篇。"
    ),
)


def _get(path: str, params: Optional[dict] = None) -> dict:
    """Call the DataSinking API, carrying the API key automatically."""
    if not API_KEY:
        raise RuntimeError("缺少 DATASINK_API_KEY 环境变量（去 datasink.ing 免费拿一个）")
    p = dict(params or {})
    p["apikey"] = API_KEY
    r = requests.get(f"{BASE_URL}{path}", params=p, timeout=90)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def list_exchanges() -> list:
    """列出 DataSinking 覆盖的交易所代码（sse/szse/bj/ksc/koe/knx/jpx）。"""
    return _get("/exchanges").get("exchanges", [])


@mcp.tool()
def list_stocks(exchange: str, limit: int = 20) -> dict:
    """列出某交易所的股票（含每家公司的报告数）。

    Args:
        exchange: 交易所代码，如 sse / szse / ksc / koe / jpx
        limit: 返回前 N 家（默认 20，防止列表过长）
    """
    data = _get("/stocks", {"exchange": exchange})
    return {"exchange": exchange, "total": data.get("total", 0), "items": data.get("items", [])[:limit]}


@mcp.tool()
def list_reports(symbol: str, doc_type: str = "annual", size: int = 10) -> dict:
    """列出某公司的报告（元数据，不含正文）。

    Args:
        symbol: FMP 风格代码，如 600519.SS / 005930.KS / 7203.T
        doc_type: annual / semiannual / q1 / q3
        size: 返回条数（默认 10）
    """
    return _get("/documents", {"symbol": symbol, "doc_type": doc_type, "size": size})


@mcp.tool()
def get_report(document_id: int) -> dict:
    """获取单篇报告的全文（元数据 + Markdown 正文）。

    Args:
        document_id: 报告 ID，从 list_reports 的 items[].id 拿
    """
    return _get(f"/documents/{document_id}")


@mcp.tool()
def list_sections(document_id: int) -> dict:
    """列出某报告的所有章节标题（供 get_section 用）。"""
    return _get(f"/documents/{document_id}/sections")


@mcp.tool()
def get_section(document_id: int, section: str) -> dict:
    """只取报告的某一章（省 token，适合 RAG）。

    Args:
        document_id: 报告 ID
        section: 章节标题的关键词，如 "管理层讨论与分析" / "MD&A" / "财务报告"
    """
    return _get(f"/documents/{document_id}", {"section": section})


def main() -> None:
    """Entry point for the ``datasinking-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
