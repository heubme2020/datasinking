---
name: financial-reports
description: Query full-text financial reports (annual, semi-annual, quarterly — 10-K, 年报, 有価証券報告書, 사업보고서, 年報) from US, China, Japan, Korea, Taiwan and UK companies as clean Markdown, via the DataSinking REST API. Use when the user asks about a company's filings, financial statements, MD&A, risk factors, notes, or report text.
---

# DataSinking Financial Reports

Fetch full-text financial reports as clean Markdown through the DataSinking REST API. Covers 6 markets / 13 exchanges (NYSE, NASDAQ, CBOE, SSE, SZSE, BSE, TSE, KOSPI, KOSDAQ, KONEX, TWSE, TPEx, LSE). No MCP server or SDK required — just an API key and HTTP.

## Setup (one time)

1. Get a free API key: `POST https://api.datasink.ing/free-key` with JSON body `{"email": "user@example.com"}` — the key is emailed to that address.
2. Pass the key as the `apikey` query parameter on every request.

## Endpoints (base `https://api.datasink.ing`)

| Task | Request |
|---|---|
| List exchanges | `GET /exchanges?apikey=KEY` |
| List stocks on an exchange | `GET /stocks?exchange=sse&apikey=KEY` |
| Find reports | `GET /documents?symbol=600519.SS&doc_type=annual&apikey=KEY` |
| Get one report (full text) | `GET /documents/{id}?apikey=KEY` |
| Get one section only | `GET /documents/{id}?section=MD%26A&apikey=KEY` |
| List a report's section headings | `GET /documents/{id}/sections?apikey=KEY` |

Useful `/documents` query params: `symbol`, `exchange`, `doc_type` (`annual`/`semiannual`/`q1`/`q3`), `report_period`, `report_period_from`, `report_period_to`, `order=desc`, `with_content=1`, `page`, `size`.

## How to work

1. Map the company to an FMP-style symbol: `AAPL` / `600519.SS` / `7203.T` / `005930.KS` / `2330.TW` / `VOD.L`. If unsure, call `/exchanges` then `/stocks?exchange=…` to look it up.
2. Call `/documents` filtered by `symbol` + `doc_type` or `report_period` to find the report and its `id`.
3. Reports run 300+ pages. Prefer section-level reads:
   - Call `/documents/{id}/sections` to see the headings first.
   - Then call `/documents/{id}?section=…` to pull only the part the user asked about (e.g. "MD&A", "risk", "notes", or the local-language heading). URL-encode the section name (spaces → `%20`, `&` → `%26`).

## Rules

- Never fabricate a number, symbol, or filing. If the API returns nothing, say so and help find the right symbol/period.
- Keep the `source` field (the official disclosure platform: SEC EDGAR / cninfo / EDINET / DART / MOPS) when citing a figure.
- Reply in the user's language. Be concise — show the relevant section text or a short summary with key figures.
