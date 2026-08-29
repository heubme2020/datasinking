# Using DataSinking with an LLM

The fastest way to use DataSinking is to **not write code at all**. Point any LLM
(ChatGPT, Claude, an agent, …) at the site — `https://datasink.ing` (human docs at
`/docs`, machine-readable spec at `https://api.datasink.ing/openapi.json`) — give it
your API key, and ask for what you want in plain language. The model reads the API,
calls it, and hands you the answer.

**Prerequisite — get a key (no signup):**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email": "you@example.com"}' \
  "https://api.datasink.ing/free-key"
```

A free key is emailed to you instantly. (Free = 1 req/s + a shared daily quota;
batch download and higher limits require a yearly key.)

Three end-to-end examples below. Each shows **what you say**, the **API call the
model makes**, the **key part of the response**, and the **answer you get back**.

---

## Example 1 — Explore: what does this cover?

**You say:**

> "This is DataSinking's API — docs at https://datasink.ing/docs. I have a key.
> First tell me: which exchanges does it cover and roughly how many companies?"

**The model calls:**

```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
# → {"exchanges":["bj","sse","szse"]}

curl "https://api.datasink.ing/stocks?exchange=sse&apikey=YOUR_KEY"
# → {"exchange":"sse","total":2200,
#    "items":[{"stock_code":"600000","stock_name":"浦发银行","report_count":30}, …]}
```

**The answer you get:**

> It covers all three mainland exchanges — Shanghai (sse), Shenzhen (szse) and
> Beijing (bj) — 5,000+ A-share companies in total, each with full-text reports
> as Markdown.

---

## Example 2 — List a company's reports

**You say:**

> "List Kweichow Moutai's (600519) latest 5 reports — just the period and title."

**The model calls:**

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&order=desc&size=5&apikey=YOUR_KEY"
```

**Response (key part):**

```json
{ "total": 108, "items": [
  { "report_period": "2024-06-30", "doc_type": "semiannual", "title": "贵州茅台2024年半年度报告" },
  { "report_period": "2024-03-31", "doc_type": "q1",         "title": "贵州茅台2024年第一季度报告" },
  { "report_period": "2023-12-31", "doc_type": "annual",     "title": "贵州茅台2023年年度报告" }
] }
```

**The answer you get:**

> 600519.SS has 108 reports. Latest three: the 2024 half-year report, 2024 Q1,
> and the 2023 annual report.

---

## Example 3 — Extract a number with the right units (the whole point)

This is where it matters: the model reads the full Markdown, confirms the
reporting period and the unit, then pulls a specific figure.

**You say:**

> "What were Kweichow Moutai's revenue and net profit attributable to shareholders
> in the 2023 annual report? Don't get the unit wrong."

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
> revenue 营业总收入 ≈ 150.56 billion yuan, and net profit attributable to
> parent ≈ 74.73 billion yuan.

*(Figures above are illustrative — actual values come straight from the API.)*
