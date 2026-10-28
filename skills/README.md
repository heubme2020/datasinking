# DataSinking Skills

Cross-platform **Agent Skills** (the `SKILL.md` format) for AI assistants (Kimi / Claude / Codex / Cursor) to query DataSinking full-text financial reports.

Unlike the MCP connectors elsewhere in this repo, these skills call the DataSinking REST API directly over HTTP — no MCP server required, just an API key.

## Skills

- [`financial-reports`](financial-reports/SKILL.md) — query full-text financial reports (annual / semi-annual / quarterly) from the US, China, UK, Japan, Korea and Taiwan as clean Markdown, by symbol and section.

## Get a free API key

`POST https://api.datasink.ing/free-key` with `{"email": "you@example.com"}` — a free key is emailed to you (free tier: 8191 reports / 7 days).
