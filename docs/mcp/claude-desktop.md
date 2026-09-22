# Claude Desktop

Connect the Claude Desktop app to the DataSinking MCP server.

Claude Desktop has **two entirely separate paths** depending on whether you run the server locally or connect to ours. They are not interchangeable — the config file does not accept a `url`.

| | Where you set it up | Auth |
|---|---|---|
| **Local (stdio)** | `claude_desktop_config.json` | env var in the file |
| **Hosted (remote)** | Settings UI → Connectors | the UI's auth prompt |

---

## Hosted — via the UI (recommended)

Claude Desktop supports remote MCP servers natively. **Do not** edit the JSON file and **do not** reach for `mcp-remote` — both are outdated advice for this app.

1. **Settings → Connectors → Add → Add custom connector**
2. Paste the URL: `https://api.datasink.ing/mcp`
3. Complete the auth prompt with your DataSinking key

That's it — no restart, no file editing. If you're on a build without the Connectors pane, use the local path below instead.

## Local — stdio

Config file:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

You can also open it from **Settings → Developer → Edit Config**.

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

Or with Python:

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

**Restart Claude Desktop after editing**, then look for the tools icon in the composer. If the server failed to start, the app shows a warning rather than staying silent — that warning is the useful output, so read it.

> This file is a plain `mcpServers` map: `command` / `args` / `env`. There is no `url` key. Pasting a hosted-URL config here is the most common mistake, and it fails without a useful error.

## Try it

```
Which exchanges does DataSinking cover?
List Toyota's annual reports.
What does Moutai's 2025 annual report say in its management discussion and analysis?
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Server doesn't appear | File wasn't valid JSON, or the app wasn't restarted. |
| Server appears, tool calls fail | Bad key. `POST /mcp` returns 401 `{"detail":"无效的 API key"}` for a bad key. |
| `command not found: npx` | Node isn't on the `PATH` Claude Desktop launches with. Use an absolute path to `npx`, or switch to `uvx`. |
| You pasted a `url` config | Claude Desktop's file is stdio-only. Use **Settings → Connectors** for the hosted endpoint. |

## Keep the attribution

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART, MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
