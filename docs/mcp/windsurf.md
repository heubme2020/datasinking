# Devin Desktop (formerly Windsurf)

Connect Cascade in Devin Desktop to the DataSinking MCP server.

> **Windsurf is now Devin Desktop**, and the config file moved with the name — the old
> `~/.codeium/windsurf/mcp_config.json` is no longer the file Cascade reads.

---

## Config file

| OS | Path |
|---|---|
| macOS / Linux | `~/.config/devin/mcp_config.json` (or `$XDG_CONFIG_HOME/devin/mcp_config.json`) |
| Windows | `%APPDATA%\devin\mcp_config.json` |

There is **no project-scope config file** — Cascade's is user-level only.

The easiest way to land on the right file is the **Actions (`...`) menu in the Cascade panel →
"Open MCP config file"**. Use whatever that opens.

`~/.codeium/windsurf/mcp_config.json` (or `~/.codeium/windsurf-next/mcp_config.json` on Next) is a
separate file used only for editor discovery — Cascade does not read it.

## Hosted — streamable HTTP

```json
{
  "mcpServers": {
    "datasinking": {
      "serverUrl": "https://api.datasink.ing/mcp?apikey=YOUR_KEY",
      "headers": { "Authorization": "Bearer ${env:DATASINK_API_KEY}" }
    }
  }
}
```

- **The remote field is `serverUrl`**, not `url`.
- **There is no `type` field.** Cascade documents three transports (`stdio`, `Streamable HTTP`,
  `SSE`) and infers which one you mean from the fields you wrote. Don't add `type: "http"`.
- **No `mcp-remote` bridge** — remote HTTP is native.
- Interpolation works in `command`, `args`, `env`, `serverUrl`, `url` and `headers`, using
  `${env:VAR_NAME}` (the Cursor-style syntax, not Claude Code's `${VAR}`).

## Local — stdio

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

Standard input servers have **no OAuth** — credentials go through `env` or `args`. The hosted
endpoint above doesn't have that limitation.

## Verify

1. Save the file.
2. **Press the refresh button** in the Cascade panel. If nothing changes, restart the app — most
   clients read MCP config at launch.
3. Open the MCPs section of the Cascade panel's `...` (Actions) menu. It lists each configured
   server **and its tool count**, which is the fastest confirmation that the six DataSinking tools
   registered.

There is **no CLI** for adding MCP servers to Cascade, and no MCP marketplace — servers are added by
editing the file or through the GUI (JetBrains plugin: `Settings > Tools > Windsurf Settings > Add
Server`).

> **100-tool ceiling.** Cascade allows at most 100 tools at once across all servers. DataSinking uses
> 6. Near the cap, the per-server `disabledTools: [...]` array turns individual tools off.

## Using the Devin CLI instead?

The **Devin Local agent** reads its own config files — not Cascade's:

| Scope | Path |
|---|---|
| Project (committed) | `.devin/mcp_config.json` |
| Project (gitignored) | `.devin/mcp_config.local.json` |
| User | `~/.config/devin/mcp_config.json` · `%APPDATA%\devin\mcp_config.json` |

This one **does** have a CLI, and it's the only Devin surface where a `transport` field exists:

```bash
devin mcp add -s user datasinking https://api.datasink.ing/mcp?apikey=YOUR_KEY
devin mcp add -s user datasinking -- npx -y datasinking-mcp     # stdio
devin mcp list
devin mcp remove datasinking
```

Without `-s`, the default scope is `local`, which writes to `.devin/mcp_config.local.json`.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Edited the config, nothing changed | You edited `~/.codeium/windsurf/mcp_config.json`. That's the editor-discovery file — use the **Actions → Open MCP config file** path. |
| Added the server, no tools | Press the refresh button in the Cascade panel; if nothing changes, restart the app. |
| `type: "http"` rejected or ignored | Cascade has no `type` field. Use `serverUrl`. |
| `Bearer ${DATASINK_API_KEY}` arrives literally | Cascade uses `${env:DATASINK_API_KEY}`. |
| Tools missing near the 100 cap | Check the per-server tool count in the MCPs menu; use `disabledTools` to trim. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Keep the `source` field on every response — it names the official platform (cninfo.com.cn, EDINET,
DART, MOPS) the data came from.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
