# Claude Desktop

Connect the Claude Desktop app to the DataSinking MCP server.

Claude Desktop has **two entirely separate paths** depending on whether you run the server locally or connect to ours. They are not interchangeable — the config file does not accept a `url`.

| | Where you set it up | Auth |
|---|---|---|
| **Local (stdio)** | `claude_desktop_config.json` | env var in the file |
| **Hosted (remote)** | Settings UI → Connectors | key in the URL (`?apikey=`) |

---

## Hosted — via the UI

Claude Desktop supports remote MCP servers natively, but **its connector auth is OAuth-only and this server has no OAuth.** That mismatch is the most common failure here.

1. **Settings → Connectors → Add → Add custom connector**
2. Paste the URL **with your key already in it**:

   ```
   https://api.datasink.ing/mcp?apikey=YOUR_KEY
   ```

3. Save. There is no auth prompt to complete.

### Why the bare URL fails

Paste `https://api.datasink.ing/mcp` on its own and Claude Desktop receives a `401`, assumes OAuth, and tries to register itself as a client. There is nothing to register *against* — every `/.well-known/...` discovery path returns `401`, and that `401` carries no `WWW-Authenticate` header — so the attempt can never succeed, and the app reports:

> Couldn't register with datasink's sign-in service

With the key in the URL the server returns `200` on the first request, so no `401` ever appears and OAuth is never attempted. That is precisely what `?apikey=` is for.

**`mcp-remote` is not needed.** It exists for clients that can't speak remote MCP at all; Claude Desktop can. Adding it only creates a second process to babysit.

> The key ends up inside the connector URL, which the app stores in its config. If that isn't acceptable to you, use the local stdio path below — it keeps the key in an env var on your own machine.

## Local — stdio

Config file:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows (installer) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Windows (Microsoft Store) | `%LOCALAPPDATA%\Packages\Claude_<hash>\LocalCache\Roaming\Claude\claude_desktop_config.json` |

**The Microsoft Store build is packaged (MSIX)**, so Windows silently redirects `%APPDATA%` into a per-package container. On those machines `%APPDATA%\Claude` **does not exist** — write a config there and nothing reads it. That same build also keeps its own application state inside this file under a `preferences` key, so **merge into it; never overwrite it wholesale**, or you'll wipe the user's settings.

You can also open it from **Settings → Developer → Edit Config**. The app's log prints the config file it loads at startup:

```
%LOCALAPPDATA%\Claude\logs\main.log
# → Reading claude_desktop_config.json from C:\Users\...\Packages\Claude_<hash>\LocalCache\Roaming\Claude\...
```

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

**Quit Claude Desktop from the tray (tray icon → Quit) and reopen it after editing** — closing the window is not enough. Then look for the tools icon in the composer. If the server failed to start, the app shows a warning rather than staying silent — that warning is the useful output, so read it.

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
| "Couldn't register with …'s sign-in service" (`ofid_…`) | You pasted a **bare** URL into the connector. It tried OAuth; this server has none. Append `?apikey=YOUR_KEY`. |
| Connector saved, but no tools appear | Connectors load at launch — quit the app fully (tray icon → Quit), then reopen. Closing the window is not enough. |
| Windows: config edits change nothing | Store/MSIX build — the file it actually reads is under `%LOCALAPPDATA%\Packages\…`. See the path table above. |

## Keep the attribution

Every response carries a `source` field naming the official disclosure platform — keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
