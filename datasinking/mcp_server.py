# -*- coding: utf-8 -*-
"""DataSinking MCP server (Model Context Protocol).

Expose the DataSinking API — full-text financial reports across Asia
(China, Korea, Japan, Taiwan) as clean Markdown — to AI agents (Claude, Cursor,
Codex, DeepSeek, Devin Desktop, …).

Install the MCP extra::

    pip install "datasinking[mcp]"

Then run::

    datasinking-mcp

or add to any MCP client with ``command: datasinking-mcp`` (stdio). Requires
the environment variable ``DATASINK_API_KEY`` (get a free key at
https://datasink.ing).
"""

import json
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

# ⚠️ **工具里必须抛 ToolError，不能抛 RuntimeError。**
#
# mcp v2（实测 2.2.0）对两者的处理完全不同：
#     抛 RuntimeError  → 客户端收到 isError:true，但文本是**通用句**
#                         「Error executing tool <名字>」，**消息内容被剥掉**，只进 stderr
#     抛 ToolError     → 客户端收到 isError:true，文本带上你的原话
#                         「Error executing tool <名字>: <你的消息>」
#
# 这不是细节：get_section 的描述让模型「用真实标题重试」，标题列表就在消息里；
# 缺 API key 的提示也只在这里。用 RuntimeError 的话，模型看到的是一个**没有任何线索**的
# 失败 —— 2026-09-22 用真 key 走 uvx 发布版实测确认（`Error executing tool get_section`，32 字符）。
try:
    from mcp.server.fastmcp.exceptions import ToolError  # mcp v1
except ImportError:  # pragma: no cover
    try:
        from mcp.server.mcpserver.exceptions import ToolError  # mcp v2
    except ImportError:  # 极老的 mcp 没有这个类：退回普通异常（消息会丢，但不至于起不来）
        ToolError = RuntimeError  # type: ignore[assignment,misc]

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
    """Call the DataSinking API, carrying the API key automatically.

    出错时**把服务端 body 原文带出去**。它写的不是「失败了」，而是「该怎么办」：

      ``detail``     一句人话（「未找到章节「X」」）
      ``available``  那份报告的**全部真实标题**

    ``get_section`` 的工具描述明确让模型「retry with one of those」，所以这个列表
    必须跟着异常走。原来这里是一句 ``r.raise_for_status()``，body 整个丢掉 ——
    模型只看到裸的 ``404 Client Error: Not Found for url: ...``，既不知道错在哪，
    也没有可重试的标题（2026-09-22 用真 key 实测，三份实现里这份丢得最干净）。
    """
    if not API_KEY:
        raise ToolError(
            "Missing DATASINK_API_KEY environment variable (get a free key at https://datasink.ing)"
        )
    p = dict(params or {})
    p["apikey"] = API_KEY
    r = requests.get(f"{BASE_URL}{path}", params=p, timeout=90)
    if not r.ok:
        try:
            body = r.json()
        except ValueError:
            body = None
        if not isinstance(body, dict):
            body = {}
        msg = f"HTTP {r.status_code}: {body.get('detail') or r.text[:2000]}"
        available = body.get("available")
        if isinstance(available, list):
            msg += "\nAvailable sections: " + json.dumps(available, ensure_ascii=False)
        # ToolError 而非 RuntimeError —— 否则 mcp v2 把 msg 剥成通用句，见文件顶部注释
        raise ToolError(msg)
    return r.json()


@mcp.tool()
def list_exchanges() -> list:
    """List the exchanges DataSinking covers.

    Returns exchange codes (sse / szse / bj / ksc / koe / knx / jpx / twse / tpex) with
    the number of reports available per exchange. Call this first to discover coverage.
    Sources: A-shares = cninfo.com.cn, Korea = DART, Japan = EDINET, Taiwan = MOPS.
    """
    return _get("/exchanges").get("exchanges", [])


@mcp.tool()
def list_stocks(
    exchange: Annotated[
        str, Field(description="Exchange code, e.g. sse / szse / bj / ksc / koe / knx / jpx / twse / tpex")
    ],
    limit: Annotated[
        int, Field(description="Return only the first N companies (default 20) to keep the response short.")
    ] = 20,
) -> dict:
    """List the stocks on one exchange, including the report count per company."""
    data = _get("/stocks", {"exchange": exchange})
    return {"exchange": exchange, "total": data.get("total", 0), "items": data.get("items", [])[:limit]}


@mcp.tool()
def list_reports(
    symbol: Annotated[
        str, Field(description="FMP-style symbol, e.g. 600519.SS / 005930.KS / 7203.T / 2330.TW")
    ],
    doc_type: Annotated[
        str, Field(description="Report type to filter on. Defaults to annual.")
    ] = "annual",
    size: Annotated[int, Field(description="Number of reports to return (default 10).")] = 10,
) -> dict:
    """List a company's reports — metadata only (id, title, period), no body text.

    Each item carries a `source` field naming the official disclosure platform;
    keep that attribution when you cite it.
    """
    return _get("/documents", {"symbol": symbol, "doc_type": doc_type, "size": size})


@mcp.tool()
def get_report(
    document_id: Annotated[int, Field(description="Report id, from list_reports items[].id")],
) -> dict:
    """Fetch one report's full text (metadata + Markdown body).

    The `source` field names the official disclosure platform; keep that attribution
    when you cite it. Expensive in tokens — prefer get_section when you only need one chapter.
    """
    return _get(f"/documents/{document_id}")


@mcp.tool()
def list_sections(
    document_id: Annotated[int, Field(description="Report id, from list_reports items[].id")],
) -> dict:
    """List every section of a report with its size, before you decide what to pull.

    Returns `sections` (titles, in order) plus `section_details` — same order, one entry
    per section with `title`, `has_tables`, `chars` and `estimated_tokens`.

    Use `estimated_tokens` to avoid pulling a chapter that would blow your context,
    and `has_tables` to know whether the chapter needs special handling (tables are the
    part RAG pipelines usually get wrong). Then call get_section with a heading keyword —
    the headings are in the report's own language.
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
    """Fetch only one section of a report by keyword — much cheaper than get_report, best for RAG."""
    return _get(f"/documents/{document_id}", {"section": section})


def main() -> None:
    """Entry point for the ``datasinking-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
