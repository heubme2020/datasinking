# OpenCode

Connect [OpenCode](https://opencode.ai) to the DataSinking MCP server.

**One block of JSON, hosted — nothing to install:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "datasinking": {
      "type": "remote",
      "url": "https://api.datasink.ing/mcp",
      "oauth": false,
      "headers": { "Authorization": "Bearer {env:DATASINK_API_KEY}" }
    }
  }
}
```

Verify:

```bash
export DATASINK_API_KEY=YOUR_KEY     # Windows: $env:DATASINK_API_KEY="YOUR_KEY"
opencode mcp list                    # → datasinking
```

---

## The config file

OpenCode reads **`opencode.json`** (or `opencode.jsonc`) from three places, and **merges them** —
later sources override earlier ones only for conflicting keys:

| Order | Where |
|---|---|
| 1 | Org defaults from your `.well-known/opencode` (if you have one) |
| 2 | **Global** — `~/.config/opencode/opencode.json` |
| 3 | `$OPENCODE_CONFIG` (if set) |
| 4 | **Project** — `opencode.json` in the project root |

On Windows the global path is `%USERPROFILE%\.config\opencode\opencode.json`.

Merging is why an org can ship a default server with `"enabled": false` and you can switch it on
locally with `"enabled": true` — your config doesn't have to restate the whole entry.

## Hosted — streamable HTTP

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "datasinking": {
      "type": "remote",
      "url": "https://api.datasink.ing/mcp",
      "oauth": false,
      "headers": { "Authorization": "Bearer {env:DATASINK_API_KEY}" }
    }
  }
}
```

`enabled` defaults to on; add `"enabled": false` to keep the entry but take the tools out of context.
OpenCode warns that every MCP server adds to the context window, so it's worth disabling servers you
aren't using.

### Four things that are easy to get wrong

1. **The key is `mcp`, not `mcpServers`.** Claude Code, Cursor and Qoder all use `mcpServers`;
   OpenCode doesn't. A config copied from one of those silently defines nothing.
2. **`"type": "remote"` is required.** Without it OpenCode treats the entry as a local server and
   tries to spawn a process, so a valid URL fails with a spawn error instead of a connection error.
3. **Set `"oauth": false`.** This server authenticates with a static bearer key. OpenCode, though,
   auto-detects a 401 and starts an OAuth flow — dynamic client registration, then a browser — which
   this server has no endpoints for. Leave it on and you get an OAuth error rather than a missing-key
   error, which sends you looking in the wrong place. `"oauth": false` keeps the `headers` entry
   authoritative.
4. **Environment interpolation is `{env:NAME}`, not `${NAME}`.** Claude Code and Cursor use
   `${NAME}`; Qoder uses `${NAME}`. OpenCode uses `{env:NAME}`. A `${...}` here is passed through
   literally and the server sees the string `${DATASINK_API_KEY}` as the bearer token.

### `timeout`

```json
"timeout": 30000
```

The documented default is **5000 ms**, and it covers *fetching the tool list* from the server — not
the length of an individual tool call. If `opencode mcp list` shows the server but the tools never
appear on a slow link, this is the knob.

For the calls themselves the relevant advice is different: `get_report` returns a whole annual report
and is deliberately expensive in tokens. Prefer `list_sections` + `get_section` and pull one chapter.

## Local — stdio

If you'd rather not send the key to a hosted endpoint, the same six tools run on your machine.
Note the local shape is **not** the remote shape: `command` is an array and the env block is
`environment`, not `env`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "datasinking": {
      "type": "local",
      "command": ["npx", "-y", "datasinking-mcp"],
      "environment": { "DATASINK_API_KEY": "YOUR_KEY" },
      "enabled": true
    }
  }
}
```

Or with Python, without installing anything:

```json
"command": ["uvx", "--from", "datasinking[mcp]", "datasinking-mcp"]
```

## Try it

```
Which exchanges does DataSinking cover?
List Toyota's annual reports.
Summarize the MD&A section of Samsung's latest annual report.
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Server doesn't appear in `opencode mcp list` | The key is `mcpServers` or `mcp_servers` — it must be `mcp`. |
| Spawn/exec error instead of a connection error | Missing `"type": "remote"`. |
| OAuth or "authorization failed" error | `"oauth": false` is missing, so OpenCode tried OAuth against a static-key server. |
| 401 with `Bearer ${DATASINK_API_KEY}` literally in it | Wrong interpolation syntax — use `{env:DATASINK_API_KEY}`. |
| Server listed, tools missing | Raise `timeout` (default 5000 ms covers the tool-list fetch). |
| Key rejected | The endpoint returns 401 `{"detail":"Missing API key"}` with no key, and `{"detail":"无效的 API key"}` with a bad one — both are visible in `opencode mcp debug datasinking`. |

`opencode mcp debug <name>` shows auth status, tests HTTP connectivity, and attempts OAuth discovery;
`opencode mcp auth list` shows auth status across servers.

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you
cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
