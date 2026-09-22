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

**Restart Cursor** after editing — Cursor's docs are explicit that local file changes need a restart.

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

1. **Interpolation is `${env:NAME}`, not `${NAME}`.** Cursor's own variable syntax differs from Claude Code's, and mixing them up leaves you with a literal string in the `Authorization` header. Cursor also provides `${userHome}`, `${workspaceFolder}`, `${workspaceFolderBasename}` and `${pathSeparator}`. All are valid in `command`, `args`, `env`, `url` and `headers`.
2. **A remote entry needs no `type` field** (unlike Claude Code, where omitting it is a hard error). `type: "stdio"` *is* required for stdio entries.

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

`envFile` is available for stdio servers only — a remote server that carries `envFile` is rejected.

## Verify

**Output panel (`Cmd+Shift+U` / `Ctrl+Shift+U`) → dropdown → "MCP Logs"** is where connection errors actually surface. Per-server on/off toggles live under **Customize** — worth knowing, because a server that's toggled off looks identical to one that failed.

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

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART, MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
