# Cursor

Connect [Cursor](https://cursor.com/docs/mcp) to the DataSinking MCP server.

Cursor speaks streamable HTTP natively — **no `mcp-remote` bridge**, no local process.

| Scope | Path |
|---|---|
| Global | `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`) |
| Project | `<project>/.cursor/mcp.json` |

```json
{
  "mcpServers": {
    "datasinking": {
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer ${env:DATASINK_API_KEY}" }
    }
  }
}
```

**Restart Cursor after editing.**

Write the key inline instead if you'd rather not manage an env var:

```json
{
  "mcpServers": {
    "datasinking": {
      "url": "https://api.datasink.ing/mcp?apikey=YOUR_KEY"
    }
  }
}
```

### Two Cursor-specific details

1. **Interpolation is `${env:NAME}`, not `${NAME}`.** Getting it wrong leaves a literal string in the `Authorization` header. Valid in `command`, `args`, `env`, `url` and `headers`.
2. **A remote entry needs no `type` field.** `type: "stdio"` *is* required for stdio entries.

## Local — stdio

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "datasinking-mcp"],
      "env": { "DATASINK_API_KEY": "YOUR_KEY" }
    }
  }
}
```

## Verify

**Output panel (`Cmd+Shift+U` / `Ctrl+Shift+U`) → dropdown → "MCP Logs"** is where connection errors actually surface. Per-server on/off toggles live under **Customize** — a server that's toggled off looks identical to one that failed.

There is no CLI for registering MCP servers in Cursor.

## Try it

In Cursor's chat, with the server enabled:

```
Which exchanges does DataSinking cover?
List Samsung Electronics' annual reports.
Find the revenue figure in Moutai's latest annual report — and get the unit right.
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| No tools in chat | Server toggled off under **Customize**. |
| Connected but 401 | Bad key. `POST /mcp` returns `{"detail":"无效的 API key"}`. |
| `Bearer ${DATASINK_API_KEY}` arrives literally | Cursor needs `${env:DATASINK_API_KEY}`. |
| Edited the file, nothing changed | Restart Cursor. |
| Want the actual error | Output panel → MCP Logs. |

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
