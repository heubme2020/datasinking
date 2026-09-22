# DataSinking MCP Server

Expose the [DataSinking](https://datasink.ing) Asian financial-report API to AI agents. Through [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — an open standard — any MCP-compatible AI client can call our tools to fetch financial reports, no code required.

## Per-client setup guides

Every client writes the same idea into a differently-shaped file, and the details that break are
client-specific. Full guides — exact paths, both scopes, verification, and the errors each one
actually produces:

| Client | Guide | Config file |
|---|---|---|
| Claude Code | [`docs/mcp/claude-code.md`](docs/mcp/claude-code.md) | `~/.claude.json`, `.mcp.json` |
| Claude Desktop | [`docs/mcp/claude-desktop.md`](docs/mcp/claude-desktop.md) | `claude_desktop_config.json` + Connectors UI |
| OpenAI Codex CLI | [`docs/mcp/codex.md`](docs/mcp/codex.md) | `~/.codex/config.toml` |
| WorkBuddy / CodeBuddy | [`docs/mcp/workbuddy.md`](docs/mcp/workbuddy.md) | `~/.workbuddy/mcp.json`, `~/.codebuddy/.mcp.json` |
| Cursor | [`docs/mcp/cursor.md`](docs/mcp/cursor.md) | `.cursor/mcp.json` |
| DeepSeek (Harness `dsh`) | [`docs/mcp/deepseek.md`](docs/mcp/deepseek.md) | `~/.dsh/cordis.patch.yml` (YAML) |
| Windsurf / Devin (Cascade) | [`docs/mcp/windsurf.md`](docs/mcp/windsurf.md) | `~/.config/devin/mcp_config.json` |

Any other MCP-compatible client / framework works too — the two config shapes below cover it.

## Remote MCP (streamable HTTP)

Prefer no local install? Use the hosted endpoint — point any MCP client at
`https://api.datasink.ing/mcp`, authenticating with `?apikey=` or an
`Authorization: Bearer` header:

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "http",
      "url": "https://api.datasink.ing/mcp?apikey=YOUR_KEY"
    }
  }
}
```

The six tools are the same as the local (stdio) server below.

## Install

Three ways, same six tools. Pick whichever runtime you already have — nothing needs to be
installed ahead of time for `uvx` or `npx`:

```bash
# Option A — Node 18+ (no Python needed)
npx -y datasinking-mcp

# Option B — one-shot via uvx (no install needed)
uvx --from "datasinking[mcp]" datasinking-mcp

# Option C — pip install, then run `datasinking-mcp`
pip install "datasinking[mcp]"
```

> You need a DataSinking API key ([datasink.ing](https://datasink.ing) — free).

## Configure

The core MCP config structure is the same across clients (`command` + `args` + `env`); each client just writes it into its own config file:

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "datasinking-mcp",
      "args": [],
      "env": { "DATASINK_API_KEY": "YOUR_KEY" }
    }
  }
}
```

To use `npx` (Node) or `uvx` (Python, no install) instead of a pip install, swap the
`command`/`args`:

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "npx",
      "args": ["-y", "datasinking-mcp"],
      "env": { "DATASINK_API_KEY": "YOUR_KEY" }
    }
  }
}
```

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "uvx",
      "args": ["--from", "datasinking[mcp]", "datasinking-mcp"],
      "env": { "DATASINK_API_KEY": "YOUR_KEY" }
    }
  }
}
```

⚠️ **The stdio JSON above is not portable.** Each client's file differs in ways that matter — Codex
is TOML and has no `type` field but does have `bearer_token_env_var`; Cursor interpolates
`${env:NAME}` while Claude Code uses `${NAME}`; Claude Desktop's file is stdio-only and takes no
`url`. Follow the per-client guide rather than adapting this block by eye.

How to add it per client (verify with the guide linked above):

| Client | How to add |
|--------|------------|
| **Claude Code** | `claude mcp add --env DATASINK_API_KEY=YOUR_KEY --transport stdio datasinking -- npx -y datasinking-mcp` |
| **Claude Desktop** | `Settings → Developer → Edit Config`; for the *hosted* endpoint use `Settings → Connectors` instead — the file is stdio-only |
| **Cursor** | Edit `.cursor/mcp.json` (or `~/.cursor/mcp.json`) — the old "Settings → MCP" route is now **Customize** |
| **OpenAI Codex** | `codex mcp add datasinking --url https://api.datasink.ing/mcp --bearer-token-env-var DATASINK_API_KEY` |
| **WorkBuddy / CodeBuddy** | `插件 → MCP 服务器 → 配置 MCP`, or edit `~/.workbuddy/mcp.json` / `~/.codebuddy/.mcp.json` |
| **DeepSeek (Harness `dsh`)** | YAML patch layer — see [`docs/mcp/deepseek.md`](docs/mcp/deepseek.md) |
| **Windsurf / Devin** | **Actions → Open MCP config file** in the Cascade panel — see [`docs/mcp/windsurf.md`](docs/mcp/windsurf.md) |

Once configured, ask in plain language:

> "Which exchanges does DataSinking cover? What does Moutai's 2025 annual report say in its management discussion and analysis?"

## Set the API key environment variable

Needed whenever your config *references* the key instead of containing it — Codex's
`bearer_token_env_var`, or `${DATASINK_API_KEY}` interpolation in a remote server's `headers`. Set
it **before** launching the client, or the header goes out empty. Three shells:

**Linux / macOS (bash / zsh)**:

```bash
export DATASINK_API_KEY="YOUR_KEY"
```

**Windows PowerShell**:

```powershell
$env:DATASINK_API_KEY="YOUR_KEY"
```

**Windows CMD**:

```cmd
set DATASINK_API_KEY=YOUR_KEY
```

## Tools

| Tool | What it does | API |
|------|-------------|-----|
| `list_exchanges` | List covered exchanges | `/exchanges` |
| `list_stocks(exchange)` | List stocks on an exchange | `/stocks` |
| `list_reports(symbol, doc_type, size)` | List a company's reports (metadata) | `/documents` |
| `get_report(document_id)` | Get a report's full text | `/documents/{id}` |
| `list_sections(document_id)` | List a report's section headings | `/documents/{id}/sections` |
| `get_section(document_id, section)` | Get one section only (token-efficient, for RAG) | `/documents/{id}?section=` |

## Tips

- **FMP-style symbols**: `600519.SS` (Moutai), `005930.KS` (Samsung), `7203.T` (Toyota).
- **To save tokens**, use `get_section` to pull one section (e.g. "management discussion and analysis") instead of `get_report` for the whole report.

## Known limits of the hosted endpoint

These are properties of the server, not of your client — they matter because most clients assume
the opposite:

- **`POST /mcp` only.** `GET /mcp` returns `405 Use POST /mcp for MCP streamable HTTP`. There is no
  server-to-client SSE stream. A client that probes with `GET` before `POST` reports a connection
  failure even though `POST` works.
- **Stateless.** No `Mcp-Session-Id` is issued or required, so sessions don't survive a restart and
  there is nothing to reset on the server side.
- **Protocol version `2024-11-05`.** Newer clients negotiate down automatically; you don't need to
  configure anything.
- **Both auth forms work**: `Authorization: Bearer KEY` and `?apikey=KEY`. Prefer the header where
  the client supports it — a key in a URL ends up in logs and screen shares.

### Checking the endpoint without any client

```bash
curl -s -X POST https://api.datasink.ing/mcp \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Six tool definitions come back if the key is good. If it isn't, the body is the error:
`{"detail":"Missing API key"}` (nothing sent) or `{"detail":"无效的 API key"}` (not recognised) —
both HTTP 401. This one command separates "my client is misconfigured" from "my key is wrong".
