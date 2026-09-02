# Using DataSinking with an LLM

The fastest way to use DataSinking is to **not write code at all**. Point any LLM
(ChatGPT, Claude, an agent, …) at the site — `https://datasink.ing` (human docs at
`/docs`, machine-readable spec at `https://api.datasink.ing/openapi.json`) — give it
your API key, and ask for what you want in plain language. The model reads the API,
calls it, and hands you the answer.

Seven end-to-end examples below. Each shows **what you say**, the **API call the
model makes**, the **key part of the response**, and the **answer you get back**.

---

## Example 1 — Explore: what does this cover?

**You say:**

> "This is DataSinking's API — docs at https://datasink.ing/docs. I have a key.
> First tell me: which exchanges does it cover and roughly how many companies?"

**The model calls:**

```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
# → {"exchanges":["bj","jpx","knx","koe","ksc","sse","szse"]}

curl "https://api.datasink.ing/stocks?exchange=sse&apikey=YOUR_KEY"
# → {"exchange":"sse","total":2306,
#    "items":[{"stock_code":"600000","stock_name":"浦发银行","report_count":103}, …]}
```

**The answer you get:**

> It covers China (SSE / SZSE / BSE), Korea (KOSPI / KOSDAQ / KONEX) and
> Japan (TSE) — 7 exchanges, 9,700+ listed companies in total. Each has
> full-text reports as Markdown.

---

## Example 2 — List stocks in an exchange

**You say:**

> "What stocks are on the Shanghai exchange?"

**The model calls:**

```bash
curl "https://api.datasink.ing/stocks?exchange=sse&apikey=YOUR_KEY"
```

**Response (key part):**

```json
{ "exchange": "sse", "total": 2304, "items": [
  { "stock_code": "600000", "stock_name": "浦发银行", "report_count": 103 },
  { "stock_code": "600519", "stock_name": "贵州茅台", "report_count": 108 }
] }
```

**The answer you get:**

> The Shanghai exchange has 2,304 stocks. Each item carries a `stock_code`,
> `stock_name`, and `report_count`.

---

## Example 3 — List a company's reports

**You say:**

> "List Kweichow Moutai's (600519) annual reports — just the period and title."

**The model calls:**

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&doc_type=annual&apikey=YOUR_KEY"
```

**Response (key part):**

```json
{ "total": 30, "items": [
  { "report_period": "2023-12-31", "doc_type": "annual", "title": "贵州茅台2023年年度报告" },
  { "report_period": "2022-12-31", "doc_type": "annual", "title": "贵州茅台2022年年度报告" }
] }
```

**The answer you get:**

> Moutai has 30 annual reports, latest first: 2023, 2022, …

---

## Example 4 — Fetch one report

**You say:**

> "Give me document 12, full text."

**The model calls:**

```bash
curl "https://api.datasink.ing/documents/12?apikey=YOUR_KEY"
```

**Response (key part):**

```json
{ "id": 12, "symbol": "600519.SS", "report_period": "2023-12-31",
  "title": "贵州茅台2023年年度报告",
  "content": "---\nstock_code: \"600519\"\nreport_period: \"2023-12-31\"\n...\n" }
```

**The answer you get:**

> Document 12 is Moutai's 2023 annual report, full Markdown in the `content` field.

---

## Example 5 — Latest N reports, full text

**You say:**

> "Moutai's latest 7 reports, full text."

**The model calls:**

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&order=desc&size=7&with_content=1&apikey=YOUR_KEY"
```

**Response (key part):** 7 items, each with `report_period`, `doc_type`, `title`, and `content`.

**The answer you get:**

> Here are Moutai's latest 7 reports (most recent report period first): 2024 Q1,
> 2023 annual, 2023 Q3, … — each with the full Markdown body.

---

## Example 6 — By reporting period, and extract a number with units

This is where it matters: filter by **reporting period** (not disclosure date), then
read a specific figure with the correct unit.

**You say:**

> "What was Kweichow Moutai's revenue in the 2023 annual report? Don't get the unit wrong."

**The model calls:**

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&doc_type=annual&report_period=2023-12-31&with_content=1&size=1&apikey=YOUR_KEY"
```

**Response (key part)** — every document opens with YAML frontmatter and marks
unit rows, so the model doesn't have to guess identity, period, or unit:

```markdown
---
stock_code: "600519"
stock_name: "贵州茅台"
report_period: "2023-12-31"
announcement_date: "2024-04-03"
doc_type: "annual"
title: "贵州茅台2023年年度报告"
---

> 单位：元  币种：人民币

| 项目                     | 本期发生额        |
| 营业总收入               | 150,560,000,000  |
| 归属于母公司股东的净利润  |  74,734,000,000  |
```

**The answer you get:**

> For the 2023 annual report (report_period 2023-12-31, unit = 元 / RMB):
> revenue 营业总收入 ≈ 150.56 billion yuan, net profit attributable to parent
> ≈ 74.73 billion yuan.

*(Figures above are illustrative — actual values come straight from the API.)*

---

## Example 7 — All reports, full text

**You say:**

> "All of Moutai's reports, full text."

**The model calls:**

```bash
# 分页拉全(page=1..N, size=200); SDK 的 limit=-1 会自动翻页
curl "https://api.datasink.ing/documents?symbol=600519.SS&page=1&size=200&with_content=1&apikey=YOUR_KEY"
```

**The answer you get:**

> Moutai has 108 reports in total (annual, semi-annual, and quarterly) — here they
> all are, full Markdown. (Pulled across pages; the SDK's `limit=-1` does this in one call.)

---

## Example 8 — Pull one section (for RAG)

Building a RAG pipeline? Don't feed a whole 140k-character report into your vector DB —
pull just the sections you need. Each report is structured into chapters, so you can
fetch a single chapter and chunk/embed it directly.

**You say:**

> "I'm building a RAG app over financial reports. Give me only the MD&A section of Moutai's
> 2025 annual report — don't waste tokens on the whole thing."

**The model calls:**

```bash
# 1) List the chapters first
curl "https://api.datasink.ing/documents/3/sections?apikey=YOUR_KEY"
# → {"id":3,"symbol":"600519.SS","total":11,
#    "sections":["重要提示","第一节释义","第二节公司简介和主要财务指标",
#                "第三节管理层讨论与分析","第四节公司治理、环境和社会",
#                "第五节重要事项","第六节股份变动及股东情况",
#                "第七节债券相关情况","第八节财务报告"]}

# 2) Pull just the MD&A chapter
curl "https://api.datasink.ing/documents/3?section=管理层讨论与分析&apikey=YOUR_KEY"
# → {"id":3,"symbol":"600519.SS","section":"第三节管理层讨论与分析",
#    "content":"### 一、报告期内公司从事的业务情况\n公司主要业务是…"}
```

**The answer you get:**

> Here's the MD&A chapter (第三节 管理层讨论与分析, ~23k chars) alone — sub-headings and
> tables preserved, ready to chunk and embed. You got the analysis you need without
> downloading the full 142k-char report.

The same `sections` + `section=` pattern works across markets: Korea (`사업보고서`) and
Japan (`有価証券報告書`) reports are also chapter-structured.

---

## Example 9 — Get the notes (附注) and a specific line item (在建工程)

A common analyst ask: "give me the notes, and the construction-in-progress (在建工程)
balance." The notes live inside the financial-report chapter — pull that chapter, then let
the model zero in on the specific line item.

**You say:**

> "I need the financial statement notes for this company, and specifically the 在建工程
> (construction-in-progress) balance."

**The model calls:**

```bash
# 1) List the chapters, find the financial-report chapter
curl "https://api.datasink.ing/documents/65062/sections?apikey=YOUR_KEY"
# → ... "第八节财务报告" ...

# 2) Pull just that chapter — it contains all the notes
curl "https://api.datasink.ing/documents/65062?section=财务报告&apikey=YOUR_KEY"
# → {"section":"第八节财务报告","content":"... 在建工程 | 七、22 | 121,858,867.39 | ..."}
```

**The answer you get:**

> The notes are in the 财务报告 (financial report) chapter. Within it, the 在建工程
> (construction-in-progress) note shows a balance of ¥121.86 million.

Pulling the chapter (~160k chars) instead of the whole report (~240k chars) saves ~33% of
tokens; the model then searches within that chapter for the exact note.

---

## Example 10 — Use it through MCP (no REST, no SDK)

For AI agents that speak MCP (Claude, Cursor, Codex, Windsurf, …), point them at the
hosted endpoint — no REST calls, no SDK, the agent calls the tools itself:

```bash
# List the available tools (JSON-RPC over the MCP streamable-HTTP endpoint)
curl -s -X POST "https://api.datasink.ing/mcp?apikey=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# → 6 tools: list_exchanges, list_stocks, list_reports, get_report, list_sections, get_section

# Call one tool — list covered exchanges
curl -s -X POST "https://api.datasink.ing/mcp?apikey=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_exchanges","arguments":{}}}'
# → {"content":[{"type":"text","text":"[\"bj\",\"jpx\",\"knx\",\"koe\",\"ksc\",\"sse\",\"szse\",\"twse\"]"}]}
```

Or configure an MCP client directly (Claude Desktop, etc.):

```json
{ "mcpServers": { "datasinking": { "type": "http", "url": "https://api.datasink.ing/mcp?apikey=YOUR_KEY" } } }
```

Prefer running it locally instead of the hosted endpoint? `uvx --from "datasinking[mcp]" datasinking-mcp` — see [`mcp-server.md`](mcp-server.md).
