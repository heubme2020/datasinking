# Gemini CLI

Connect [Gemini CLI](https://github.com/google-gemini/gemini-cli) to the DataSinking MCP server.

> There are three "Gemini" surfaces and they configure MCP differently. This guide covers the
> **CLI** (the one that takes a bearer token cleanly) and the **consumer app** (OAuth-only — see the
> caveat at the bottom).

## Gemini CLI — streamable HTTP

One command:

```
gemini mcp add --transport http datasinking https://api.datasink.ing/mcp \
  --header "Authorization: Bearer YOUR_KEY"

gemini mcp list        # → datasinking
```

Or the config file — `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "datasinking": {
      "httpUrl": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer YOUR_KEY" }
    }
  }
}
```

**`httpUrl` is streamable HTTP; `url` means SSE.** Don't set both. Newer gemini-cli releases
consolidate this to `"url": "…", "type": "http"` — both still work, but `httpUrl` is unambiguous on
every released version, so it's the safe choice.

`--transport` defaults to `stdio`, so the `--transport http` flag is required for a hosted URL —
omit it and Gemini tries to launch a subprocess.

Headers can reference an environment variable instead of hard-coding the key (`$VAR_NAME` or
`${VAR_NAME}` both work):

```json
{ "headers": { "Authorization": "Bearer ${DATASINK_API_KEY}" } }
```

Verify with `gemini mcp list` outside a session, or `/mcp` inside one. Restart the CLI after editing
`settings.json` — config is read at launch.

## Gemini CLI — stdio

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

Or Python: `"command": "uvx"`, `"args": ["--from", "datasinking[mcp]", "datasinking-mcp"]`.

## Gemini app (consumer — gemini.google.com)

The consumer app connects MCP servers at **Settings & help → Connected Apps → Add a custom app**.
Two things to know:

- The app's connector UI is **OAuth-only** — there is no field for a custom API key or header.
- DataSinking has no OAuth; it takes a bearer token. So put the key in the URL instead:
  `https://api.datasink.ing/mcp?apikey=YOUR_KEY` — the same trick as Claude Desktop, which also
  treats a bare URL as "go do OAuth".

If the app doesn't accept query-string auth on a custom connector, use the CLI above — it's the
reliable path for a bearer-token server.

## Try it

```
Which exchanges does DataSinking cover?
List Toyota's annual reports.
Summarize the MD&A section of Samsung's latest annual report.
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| 401 `{"detail":"Missing API key"}` | The header/env var wasn't set before the CLI launched. |
| 401 `{"detail":"无效的 API key"}` | Key is wrong — check for a stray space or a missing `Bearer `. |
| Server connects but no tools | Restart the CLI — config is read at launch. |
| `url` treated as SSE | Use `httpUrl` for streamable HTTP (older releases), or `url` + `"type": "http"` on the consolidation. |
| Call times out on a big report | Add `"timeout": 300000` to the server entry (milliseconds). |

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you
cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
