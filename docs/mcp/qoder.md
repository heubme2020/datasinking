# Qoder

Connect [Qoder](https://qoder.com) to the DataSinking MCP server.

> **Qoder CLI and Qoder IDE are configured in two different places.** The CLI reads
> `settings.json`; the IDE has its own MCP pane (and its own marketplace). Editing the CLI file does
> nothing for the IDE and vice versa — that's the single most common way this setup "silently
> doesn't work". Both are below.

**Qoder CLI — one block in `~/.qoder/settings.json`:**

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "http",
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer YOUR_KEY" }
    }
  }
}
```

Verify — Qoder registers tools as `mcp__<server>__<tool>`, so the DataSinking tools show up as
`mcp__datasinking__get_section`:

```
/mcp
```

---

## Qoder CLI

### The config file

MCP servers live under the `mcpServers` key of `settings.json`. There are five scopes, and servers
with the same name are overridden in this order (later wins):

| Level | Location | Notes |
|---|---|---|
| User | `~/.qoder/settings.json` → `mcpServers` | Available to all projects. **Start here.** |
| Project | `<project>/.qoder/settings.json` → `mcpServers` | Requires approval before use |
| Project | `<project>/.mcp.json` | Needs a top-level `mcpServers` key; requires approval |
| Local | `<project>/.qoder/settings.local.json` → `mcpServers` | This machine only; the default scope for `-s` |
| CLI | `--mcp-config <path>` | This session only |

On Windows the user-level path is `C:\Users\<you>\.qoder\settings.json`.

### Hosted — streamable HTTP

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "http",
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer YOUR_KEY" },
      "timeout": 30000
    }
  }
}
```

`"type"` accepts `http`, `streamable-http`, `sse`, `stdio`, `ws` and `sdk`.
Use **`http`** — `sse` is the legacy transport and there's no reason to pick it here.

Useful optional fields:

| Field | Why you'd set it |
|---|---|
| `timeout` | Connection/request timeout in ms. Raise it if a large report times out. |
| `trust` | Skips the confirmation prompt when the server's tools are called |
| `alwaysAllow` | Per-tool allowlist — `["list_sections", "get_section"]` if you only want the cheap reads |
| `includeTools` / `excludeTools` | Register only (or exclude) some tools |
| `disabled` | Keep the entry but turn it off |
| `description` | Label shown in the management view |

### Three things that are easy to get wrong

1. **`stdio` is the default `type`.** Qoder assumes a subprocess unless you say otherwise, so
   omitting `"type"` on a hosted URL gives a launch failure rather than a connection failure.
2. **Project-level servers need approval.** By default Qoder asks before using servers that come
   from a project's files, so a project config can look completely ignored. Either approve it, or set
   `mcp.enableAllProjectMcpServers: true` (or the `mcp.enabledProjectMcpServers` allowlist) under the
   `mcp` group in `settings.json` — **a restart is required** after changing either.
3. **`qoder_url` silently wins.** If a `qoder_url` is present it takes precedence over every other
   transport field and routes through Qoder's managed MCP Gateway using your Qoder sign-in. If you
   set a `url` and the traffic doesn't go where you expect, check for a `qoder_url` you didn't write.

Don't reach for `--strict-mcp-config` to debug: it *skips* servers from `settings.json` and
`.mcp.json` and disables plugin MCP servers, which is the opposite of what you want when the server
isn't showing up. It's for CI, where you want exactly one server from `--mcp-config`.

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

Or with Python: `"command": "uvx"`, `"args": ["--from", "datasinking[mcp]", "datasinking-mcp"]`.

The stdio shape uses `command` + `args` + `env` + `cwd` — a flat layout, not the
`command: [...]` array you may have copied from another client.

## Qoder IDE

The IDE doesn't read the CLI's `settings.json`. Configure it in the app:

1. **Qoder IDE Settings** — click the user icon in the top-right, or `Ctrl` `Shift` `,`
   (`⌘` `⇧` `,` on macOS)
2. Left navigation → **MCP**
3. **My Servers** tab → **+ Add** in the top-right, then fill in the JSON in the editor that appears
   and **Save**

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "sse",
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer YOUR_KEY" }
    }
  }
}
```

The IDE's editor offers STDIO / SSE / **Streamable HTTP**; for Streamable HTTP you configure the
endpoint the same way as SSE and the IDE detects which one it is. A link icon next to the entry
means the connection succeeded — expand it to see the tools.

Two IDE-only things worth knowing:

- **Per-server Request Timeout** is a drop-down in the server details. If a request runs longer, the
  IDE stops the call and shows a timeout message in chat. Raise it before assuming the server broke.
- **MCP Square** is Qoder's built-in marketplace of MCP servers. Browsing it is the fastest way to
  see what else the IDE expects a server to provide.

## Try it

```
Which exchanges does DataSinking cover?
List Toyota's annual reports.
Summarize the MD&A section of Samsung's latest annual report.
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Config seems ignored | You edited `~/.qoder/settings.json` but you're using the IDE — configure it in Settings → MCP instead. |
| Project server never loads | Project-level servers need approval by default; or set `mcp.enableAllProjectMcpServers: true` (restart required). |
| Launch failure instead of a connection failure | Missing `"type": "http"` — `stdio` is the default. |
| Traffic doesn't go to the URL you set | A `qoder_url` is present and takes precedence. |
| Call times out on a big report | Raise `timeout` in the config (CLI) or the Request Timeout drop-down (IDE). |
| Key rejected | The endpoint returns 401 `{"detail":"Missing API key"}` with no key, and `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you
cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
