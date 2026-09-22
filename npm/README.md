# datasinking-mcp

MCP server for **[DataSinking](https://datasink.ing)** — full-text financial reports from
**China A-shares, Korea, Japan and Taiwan** (annual / semi-annual / quarterly) as clean Markdown,
ready for LLM reading and RAG.

Turns *"what were Toyota's FY2025 results?"* into a real answer: the agent finds the filing on
EDINET, pulls just the chapter it needs, and cites the source.

```
npx -y datasinking-mcp
```

No Python, no `uv`, no build step — just Node 18+.

## Setup

Get a free API key at **<https://datasink.ing>** (free tier: 3 requests/second, thousands of
documents per month), then add this to your MCP client:

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "npx",
      "args": ["-y", "datasinking-mcp"],
      "env": {
        "DATASINK_API_KEY": "<your-key>"
      }
    }
  }
}
```

Works with Claude Desktop, Claude Code, Cursor, Windsurf, Codex, and anything else that speaks
MCP over stdio.

> Prefer the remote endpoint? DataSinking also serves MCP over streamable HTTP at
> `https://api.datasink.ing/mcp` — no local process, same six tools.
> Prefer Python? `pip install "datasinking[mcp]"` gives you the identical server.

## Tools

| Tool | What it does |
|---|---|
| `list_exchanges` | Coverage per exchange (`sse` / `szse` / `bj` / `ksc` / `koe` / `knx` / `jpx` / `twse` / `tpex`) with report counts |
| `list_stocks` | Companies on an exchange, with report count each |
| `list_reports` | A company's reports — metadata only (id, title, period, `source`) |
| `list_sections` | Every section of one report, with `chars` / `estimated_tokens` / `has_tables` |
| `get_section` | **One chapter, by heading keyword** — the token-cheap path for RAG |
| `get_report` | A whole report (metadata + Markdown body) — expensive, use sparingly |

### Symbols are FMP-style

`600519.SS` (Kweichow Moutai) · `005930.KS` (Samsung Electronics) · `7203.T` (Toyota) ·
`2330.TW` (TSMC)

### Chapter-level access is the point

A full annual report can be 500k+ characters. `list_sections` tells the agent what's inside and
what it will cost in context, so it pulls one chapter instead of the whole document:

```jsonc
// 1. list_reports   → { "symbol": "7203.T" }              → id = 12345
// 2. list_sections  → { "document_id": 12345 }            → sections: ["事業の概況", ...]
// 3. get_section    → { "document_id": 12345, "section": "事業の概況" }
```

`section` is substring-matched against the report's **own** headings, so pass it in the report's
language: `管理层讨论与分析` for A-shares, `MD&A` for English-language filings, `事業の概況` for
Japanese. If nothing matches, the API returns 404 together with the real headings — retry with
one of those.

## Data sources

Every response carries a `source` field naming the official disclosure platform — keep that
attribution when you cite a report.

| Market | Source | Coverage |
|---|---|---|
| China A-shares | [cninfo.com.cn](http://www.cninfo.com.cn) (巨潮资讯网) | 5,500+ companies |
| Korea | [DART](https://dart.fss.or.kr) (전자공시시스템) | KOSPI / KOSDAQ / KONEX |
| Japan | [EDINET](https://disclosure2.edinet-fsa.go.jp) (金融庁) | from 2016 — annual, semi-annual and quarterly *securities reports* (有価証券報告書). Note: 決算短信 are filed on TDnet and are not in EDINET, so they are not here either. |
| Taiwan | [MOPS](https://mops.twse.com.tw) (公開資訊觀測站) | TWSE / TPEx |

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `DATASINK_API_KEY` | *(required)* | Your key. Without it every tool call returns a clear error naming this variable. |
| `DATASINK_API_URL` | `https://api.datasink.ing` | Override the API base URL (self-hosted / testing). |

## Develop

```bash
cd npm
npm install
npm run smoke                                  # handshake + tools/list, no key needed
DATASINK_API_KEY=xxx npm run smoke             # full round-trip against the live API
```

The smoke test drives this server with a **real MCP client over stdio** rather than calling the
functions directly — tool descriptions and parameter schemas only matter if they actually reach
the client, and that has silently broken here before.

## License

MIT. See [LICENSE](../LICENSE).
