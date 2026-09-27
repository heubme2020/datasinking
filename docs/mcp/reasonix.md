# Reasonix

Connect [Reasonix](https://github.com/esengine/DeepSeek-Reasonix) to the DataSinking MCP server.

**Fastest path** — Reasonix reads the official MCP Registry, and DataSinking is published there:

```bash
reasonix mcp browse datasinking
reasonix mcp install io.github.heubme2020/datasinking
```

Or in the desktop app: **Settings → MCP servers → Browse registry**.

**Or declare it yourself** — one `[[plugins]]` entry:

```toml
[[plugins]]
name    = "datasinking"
type    = "http"
url     = "https://api.datasink.ing/mcp"
headers = { Authorization = "Bearer ${DATASINK_API_KEY}" }
```

---

## Where the config lives

Resolution order is **flag > `./reasonix.toml` > user config file > built-in defaults**:

| Scope | File |
|---|---|
| Project | `./reasonix.toml` in the project root |
| Project | `./.mcp.json` in the project root |
| Global | `~/.reasonix/config.toml` (macOS / Linux) |
| Global | `%AppData%\reasonix\config.toml` (Windows) |

The global path moved in **v1.8.1** — if you're on an older build it was
`~/.reasonix/config.json`.

A project's `reasonix.toml` and `.mcp.json` are **merged**; on a name collision `reasonix.toml` wins.
Project declarations also override a same-name global install.

## Hosted — Streamable HTTP

```toml
[[plugins]]
name    = "datasinking"
type    = "http"
url     = "https://api.datasink.ing/mcp"
headers = { Authorization = "Bearer ${DATASINK_API_KEY}" }
# optional, per server:
# call_timeout_seconds = 300
```

`headers` supports `${VAR}` and `${VAR:-default}` expansion from the environment, so the key stays
out of the file. Prefer this over putting the literal key in `headers`.

You can also use `?apikey=YOUR_KEY` on the URL, but a key in a URL ends up in logs and screen
shares — the header is the better default.

Because this is an HTTP server there's no subprocess; it reconnects on demand and needs no sandbox
consideration beyond the network.

## Local — stdio

```toml
[[plugins]]
name    = "datasinking"
command = "npx"
args    = ["-y", "datasinking-mcp"]
env     = { DATASINK_API_KEY = "YOUR_KEY" }
```

Or with Python: `command = "uvx"`, `args = ["--from", "datasinking[mcp]", "datasinking-mcp"]`.

`type` is omitted because **`stdio` is the default**. That's also the trap — see below.

## Alternatively: drop in a `.mcp.json`

Reasonix reads a Claude-style `.mcp.json` in the project root as-is. The `mcpServers` spec
(`command`/`args`/`env`, `type`/`url`/`headers`, `${VAR}` expansion) maps field-for-field onto
`[[plugins]]`:

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "http",
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer ${DATASINK_API_KEY}" }
    }
  }
}
```

Handy if you already keep one for another client. Note that a project-level `.mcp.json` is
**lower priority** than the project's `reasonix.toml`.

## Three things that are easy to get wrong

1. **`type` defaults to `stdio`.** A `url` with no `type = "http"` launches a subprocess and fails as
   a spawn error, not a connection error. The `[[plugins]]` table needs `name` too.
2. **Cold servers come online in the background.** MCP servers start connecting asynchronously after
   a session begins, and an interactive caller waits only briefly for a cold server. If that wait
   ends, the launch *continues in the background* rather than being killed — so the right move is to
   **retry the tool after it comes online**, not to assume the config is broken. `mcp_startup_timeout_seconds`
   (default `30`) bounds the whole launch → authorization → `initialize` → `tools/list` sequence;
   `mcp_call_timeout_seconds` applies only after the server is connected.
3. **Installing a server is the authorization decision.** Once installed, all of its tools run
   directly, with no second server-level, per-tool, or destructive-call approval step. That's worth
   knowing before you install something you haven't looked at. Explicit deny rules still win, and a
   tool that declares `readOnlyHint: true` additionally joins parallel dispatch and the strict
   read-only sub-agent surfaces.

## Using it

Tools surface as `mcp__<server>__<tool>`, so ours are `mcp__datasinking__get_section` and friends.
The server's **prompts** become `/mcp__datasinking__<prompt>` commands, its **resources** are pulled
in with `@datasinking:<uri>`, and `/mcp` lists connected servers and what each one exposes.

```
/mcp
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Spawn error instead of a connection error | `type = "http"` is missing — `stdio` is the default. |
| Tools missing right after startup | The server is still connecting in the background. Retry the call; `/mcp` refreshes status. |
| Call fails on a long report | Raise `call_timeout_seconds` on the entry. |
| Config ignored | A `./reasonix.toml` or `./.mcp.json` in the project overrides your global install. |
| Auth error despite a static header | Check the expansion — `${DATASINK_API_KEY}` only resolves if the variable is in the environment Reasonix launched with. A static `Authorization` header always takes precedence over OAuth, so a *wrong* value here fails rather than falling back. |
| Key rejected | The endpoint returns 401 `{"detail":"Missing API key"}` with no key, and `{"detail":"无效的 API key"}` with a bad one. |

For a read-only health report across skills, hooks, packages and MCP, run
`reasonix doctor capabilities` (or **Settings → Diagnostics**). `/reasonix-guide` in a session points
at the same thing.

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you
cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
