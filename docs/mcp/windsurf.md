# Windsurf / Devin

Connect Windsurf's Cascade to the DataSinking MCP server.

> **The docs have been rebranded.** The page still lives at
> `docs.windsurf.com/windsurf/cascade/mcp` and is still titled "Cascade MCP Integration", but its
> content is now Devin documentation — the body mentions Devin roughly 18× as often as Windsurf.
> That matters here for one concrete reason: **the config path changed.** The old
> `~/.codeium/windsurf/mcp_config.json` is no longer the file Cascade reads.

---

## Config file

| OS | Path (Cortex-managed — this is the one that counts) |
|---|---|
| macOS / Linux | `~/.config/devin/mcp_config.json` (or `$XDG_CONFIG_HOME/devin/mcp_config.json`) |
| Windows | `%APPDATA%\devin\mcp_config.json` |

There is **no project-scope config file** — Cascade's is user-level only.

The easiest way to land on the right file is the **Actions (`...`) menu in the Cascade panel →
"Open MCP config file"**. Use whatever that opens. This also sidesteps the fact that isolated-config
builds may use a different path.

> **About `~/.codeium/windsurf/mcp_config.json`:** it still exists, and it's still what a lot of
> blog posts tell you to edit — but in current builds it's the *editor's MCP discovery* file,
> surfaced through the `chat.mcp.discovery.enabled` setting ("Devin configurations" source). The
> discovery setting does **not** change the Cortex-managed file that Cascade actually opens and
> reads. Editing it and seeing nothing happen is the expected outcome.

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

- **The remote field is `serverUrl`** (or `url` — both are accepted). This is a genuinely different
  shape from every other client here, which use `url` alone.
- **There is no `type` field.** Cascade documents three transports (`stdio`, `Streamable HTTP`,
  `SSE`), but it infers which one you mean from the fields you wrote. Don't add `type: "http"`.
- **No `mcp-remote` bridge.** `mcp-remote` is not mentioned anywhere in Cascade's docs — remote
  HTTP is native.
- Interpolation works in `serverUrl`, `url`, `headers`, `command`, `args` and `env`, using
  `${env:VAR_NAME}` (the Cursor-style syntax, not Claude Code's `${VAR}`). `${file:/path/to/file}`
  is also supported, tilde paths included.

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

Standard input servers have **no OAuth** — Cascade's docs are explicit that credentials go through
`env` or `args` instead. The hosted endpoint above doesn't have that limitation.

## Verify

1. Save the file.
2. **Press the refresh button** in the Cascade panel. There is no documented restart step — the
   docs say refresh, and "restart" doesn't appear on the page at all.
3. Open the MCPs section of the Cascade panel's `...` (Actions) menu. It lists each configured
   server **and its tool count**, which is the fastest confirmation that the six DataSinking tools
   registered.

There is **no CLI** for adding MCP servers to Cascade, and no MCP marketplace — servers are added by
editing the file or through the GUI (JetBrains plugin: `Settings > Tools > Windsurf Settings > Add
Server`).

> **100-tool ceiling.** Cascade caps the total number of MCP tools at 100 across all servers.
> DataSinking uses 6. If you're near the cap, the per-server `disabledTools: [...]` array turns off
> individual tools.

## Using the Devin CLI instead?

New tabs now default to the **Devin Local agent**, which reads its own config files — not Cascade's:

| Scope | Path |
|---|---|
| Project (committed) | `.devin/mcp_config.json` |
| Project (gitignored) | `.devin/mcp_config.local.json` |
| User | `~/.config/devin/mcp_config.json` · `%APPDATA%\devin\mcp_config.json` |

This one **does** have a CLI, and it's the only Windsurf/Devin surface where a `transport` field
exists:

```bash
devin mcp add -s user datasinking https://api.datasink.ing/mcp?apikey=YOUR_KEY
devin mcp add -s user datasinking -- npx -y datasinking-mcp     # stdio
devin mcp list | get datasinking | remove datasinking
```

Without `-s`, the default scope is `local`, which writes to `.devin/mcp_config.local.json`.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Edited the config, nothing changed | You edited `~/.codeium/windsurf/mcp_config.json`. That's the discovery file now — use the **Actions → Open MCP config file** path. |
| Added the server, no tools | Press the refresh button. |
| `type: "http"` rejected or ignored | Cascade has no `type` field. Use `serverUrl`. |
| `Bearer ${DATASINK_API_KEY}` arrives literally | Cascade uses `${env:DATASINK_API_KEY}`. |
| Tools missing near the 100 cap | Check the per-server tool count in the MCPs menu; use `disabledTools` to trim. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART,
MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
