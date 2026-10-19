---
name: financial-reports
description: Query full-text financial reports from the US, China, Japan, Korea, Taiwan and UK as clean Markdown, by FMP-style symbol and section.
---

# DataSinking Financial Reports

Use the DataSinking MCP tools to answer questions about company financial reports.

## How to work

1. Map the company to an FMP-style symbol: `AAPL` / `600519.SS` / `7203.T` / `005930.KS` / `2330.TW` / `VOD.L`. If unsure, call `list_exchanges` then `list_stocks` to look it up.
2. Call `list_reports` to find reports — filter by `symbol`, `doc_type` (annual/semiannual/q1/q3), or period.
3. Reports run 300+ pages. Always prefer section-level reads:
   - Call `list_sections` to see the headings first.
   - Then call `get_section` to pull only the part the user asked about (e.g. "MD&A", "risk", "notes", or the local-language heading).

## Rules

- Never fabricate a number, symbol, or filing. If a tool returns nothing, say so and help find the right symbol/period.
- Keep the `source` field (the official disclosure platform) when citing a figure.
- Reply in the user's language. Be concise — show the relevant section text or a short summary with key figures.
