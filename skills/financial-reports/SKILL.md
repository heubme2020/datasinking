---
name: datasinking-reports
description: Query full-text financial reports (annual, semi-annual, quarterly) from US, China, Europe, Japan, Korea and Taiwan companies as clean Markdown via the DataSinking REST API. Use for MD&A, risk factors, financial statements, notes and any filing text. Use this skill when the user asks for a company's report content or narrative — e.g. "查一下茅台的年报", "show Apple's MD&A and risk factors", "拉一下丰田最近的季度报告", "台积电年报里的附注". Not for quotes/ratios (use a market-data API). Requires a free API key in DATASINKING_API_KEY.
---

# DataSinking Financial Reports

Fetch full-text financial reports as clean Markdown. Covers 6 markets / 13 exchanges (NYSE, NASDAQ, CBOE, SSE, SZSE, BSE, TSE, KOSPI, KOSDAQ, KONEX, TWSE, TPEx, LSE). A bundled zero-dependency client (`datasinking_client.py`) does the HTTP for you — no need to hand-write requests.

## When to use

Use when the user asks for report **content / narrative**, not quotes or ratios:

- 「贵州茅台 2024 年报的 MD&A 讲了什么」
- "Show Apple's risk factors from the latest 10-K"
- 「丰田最近的季度报告营收分析」
- 「台积电年报里的关联交易附注」
- "compare Samsung and SK Hynix's 2024 MD&A"

If they only want 行情/涨跌/市盈率, point them to a market-data API — this skill is full-text filings.

## Install (one time)

Put these two files in `.claude/skills/datasinking/`:

- `SKILL.md` (this file)
- `datasinking_client.py` (bundled client)

Then set the key:

```bash
export DATASINKING_API_KEY="your_key_here"
```

Get a free key: `POST https://api.datasink.ing/free-key` with body `{"email": "you@example.com"}` — the key is emailed to that address. Free tier: 8,191 reports / 7 days.

## ⚠️ Symbol format (极易踩坑)

DataSinking uses **FMP-style symbols WITH an exchange suffix**. A bare code returns nothing.

| Market | Format | Example |
|---|---|---|
| US | `TICKER` | `AAPL` |
| China A股 | `CODE.SS` (上交所) / `CODE.SZ` (深交所) | `600519.SS` |
| Japan | `CODE.T` | `7203.T` |
| Korea | `CODE.KS` (KOSPI) / `CODE.KQ` (KOSDAQ) | `005930.KS` |
| Taiwan | `CODE.TW` | `2330.TW` |
| UK | `TICKER.L` | `VOD.L` |

Don't write `600519` (bare) — it won't match. If unsure, call `list_exchanges()` then `list_stocks(exchange)` to look up the exact code.

## ⚠️ Read sections, not whole reports (省 token 的关键)

Full reports are 300+ pages / hundreds of KB. **Always** prefer section-level reads:

1. `list_section_details(doc_id)` → get each section's **standard concept** (`concept_name`): MD&A / Risk Factors / Financial Statements / Notes / Audit Report / Corporate Governance… mapped across all markets.
2. `get_section(doc_id, "MD&A")` → pull that chapter by **standard name** (or the report's own heading).

Standard names are cross-market: A股「管理层讨论与分析」、美股「Item 7」、韩「II. 사업의 내용」all map to `MD&A`. Section matching is keyword-based (substring); if a standard name doesn't hit, fall back to `list_sections(doc_id)` for the report's real headings and retry with one of those. The bundled client URL-encodes the section name for you; when hand-writing HTTP, encode `&` → `%26` and spaces → `%20` (e.g. `section=MD%26A`).

## Client

The bundled client is stdlib-only. Import and call:

```python
from datasinking_client import DataSinking
ds = DataSinking()  # 自动读环境变量 DATASINKING_API_KEY
```

Methods (all on `DataSinking`):

| Task | Method |
|---|---|
| List exchanges | `list_exchanges()` |
| List stocks on an exchange | `list_stocks(exchange)` |
| List a stock's reports (metadata) | `list_reports(symbol, doc_type=None)` |
| Search reports by keyword (title/name/code) | `search(query, doc_type=None)` |
| Get one report (full text) | `get_report(doc_id)` |
| Get recent reports (full text) | `get_stock_reports(symbol, limit=7, doc_type=None)` |
| List a report's sections | `list_sections(doc_id)` |
| List sections + standard concepts | `list_section_details(doc_id)` |
| Get one section only | `get_section(doc_id, "MD&A")` |
| Request a backfill (补全) | `submit_feedback(exchange, stock_code)` |
| Check backfill status | `get_feedback_status(feedback_id)` |

`doc_type` is one of `annual` / `semiannual` / `q1` / `q3` / `amendment`.

## Examples

```python
from datasinking_client import DataSinking
ds = DataSinking()

# 茅台 2024 年报的 MD&A（中文标题，按关键词匹配）
reports = ds.list_reports("600519.SS", doc_type="annual")
doc = next(r for r in reports if (r.get("report_period") or "").startswith("2024"))
md = ds.get_section(doc["id"], "管理层讨论与分析")
print(md["content"][:1000])

# Apple 最新 10-K 的风险因素
r = ds.get_stock_reports("AAPL", doc_type="annual", limit=1)
print(ds.get_section(r[0]["id"], "risk factors")["content"][:800])
```

### Raw REST (no client, zero deps)

The same flow with plain `requests` — full text comes back in **one step** (no download-URL hop):

```python
import requests

API_KEY = "your_api_key"

r = requests.get("https://api.datasink.ing/documents",
                 params={"symbol": "600519.SS", "doc_type": "annual", "apikey": API_KEY}).json()
for d in r["items"][:3]:
    print(d["stock_name"], d["report_period"])

doc_id = r["items"][0]["id"]
full = requests.get(f"https://api.datasink.ing/documents/{doc_id}",
                    params={"apikey": API_KEY}).json()
print(full["content"][:500])          # 干净 Markdown 全文

sec = requests.get(f"https://api.datasink.ing/documents/{doc_id}",
                   params={"section": "MD&A", "apikey": API_KEY}).json()
print(sec["content"][:500])           # 只拉一章，省 token
```

## Empty results (怎么读)

- `list_reports` 返回空 → symbol 写错（多半缺后缀）或该股该 doc_type 没报告。先 `list_stocks(exchange)` 确认代码。
- `get_section` 返回空 content 或报错 → 章节名没命中。先 `list_sections(doc_id)` 拿真实标题，再用真实标题重试。
- HTTP 404 → `doc_id` 错或报告不存在。

## Common errors

- `401` → key 无效/缺失，检查 `DATASINKING_API_KEY`。
- `429` 带 `code` → 额度用尽（free 8,191 / 7 天），抛 `QuotaExceeded`，等 7 天窗口滚动。
- `429` 不带 `code` → 纯限流，客户端自动退避重试。
- `400` → 参数非法（symbol 缺后缀 / doc_type 不在枚举里）。

## Rules

- Never fabricate a number, symbol, or filing. If empty, say so and help find the right symbol/period.
- Keep the `source` field (SEC EDGAR / cninfo / EDINET / DART / MOPS) when citing a figure.
- Reply in the user's language; prefer a short summary with key figures over dumping the full text.
