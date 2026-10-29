# DataSinking — Claude plugin

Query full-text financial reports from the US, China, Europe, Japan, Korea and Taiwan as clean Markdown, ready for RAG and analysis.

## What it installs

- **Skill** `financial-reports` — teaches Claude to map companies to FMP-style symbols and prefer section-level reads over full filings.
- **MCP server** `datasinking` — 8 tools (`list_exchanges`, `list_stocks`, `list_reports`, `get_report`, `list_sections`, `get_section`, `submit_feedback`, `get_feedback_status`) at `https://api.datasink.ing/mcp`.

## Install (Claude Code)

```
/plugin marketplace add heubme2020/datasinking
/plugin install datasinking@datasinking
```

No API key needed for the public preview tier (31 reports / 7 days / IP). Get a free key at https://datasink.ing for higher limits.
