# DataSinking MCP Server

Expose the [DataSinking](https://datasink.ing) Asian financial-report API to AI agents. Through [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — an open standard — any MCP-compatible AI client can call our tools to fetch financial reports, no code required.

## Supported clients (not just Claude)

MCP is an open standard, so all of these AI clients / agents can connect:

- **Claude** (Desktop / Code, Anthropic)
- **Cursor**
- **OpenAI Codex** (CLI / app)
- **DeepSeek** (harness / CLI)
- **Windsurf**
- Other MCP-compatible agents / frameworks

## Install

```bash
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

How to add it per client:

| Client | How to add |
|--------|------------|
| **Claude Desktop** | `Settings → Developer → Edit Config`, edit `claude_desktop_config.json` (JSON, as above) |
| **Claude Code** | `claude mcp add datasinking -- datasinking-mcp` |
| **Cursor** | `Settings → MCP → Add new MCP server` (paste the JSON) |
| **OpenAI Codex** | Edit `~/.codex/config.toml`, add a `[mcp_servers.datasinking]` section (TOML, same fields) |
| **DeepSeek** | Add via its MCP config (JSON, as above) |
| **Windsurf** | `Settings → MCP` |

Once configured, ask in plain language:

> "Which exchanges does DataSinking cover? What does Moutai's 2025 annual report say in its management discussion and analysis?"

## Set the API key environment variable

If you don't put `env` in the config (e.g. you used `claude mcp add`, or want to set it globally), set the key first. Three shells:

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
