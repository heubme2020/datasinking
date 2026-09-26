# Doubao Work / 豆包工作 (ByteDance)

Connect ByteDance's office agent to the DataSinking MCP server.

> **There is no config file.** Doubao Work has no `mcp.json` to edit — custom connectors live entirely inside the app. Don't go looking for a path to paste JSON into.

---

## Hosted — via the UI

1. Open the **desktop** client and go to the sidebar entry:
   **技能 · 连接器 · 伙伴** (Skills · Connectors · Partners)
2. Switch to the **连接器** (Connectors) tab, then click **新建** top-right → **新建自定义连接器** (New custom connector).
3. Fill in:

   | Field | Value |
   |---|---|
   | 服务器名称 (Name) | `datasinking` — anything you like |
   | 传输类型 (Transport) | **HTTP** |
   | 服务器 URL | `https://api.datasink.ing/mcp` |
   | 自定义 Headers | `Authorization` = `Bearer YOUR_KEY` |

4. **保存** (Save), wait for install, and confirm the toggle reads as enabled.

**No restart needed** — the connector appears in your skills list immediately.

Doubao sets custom headers, so use the `Authorization` header above rather than the `?apikey=` URL form. Don't set both.

## Local — via STDIO

The same dialog also offers **STDIO**, if you'd rather keep the key on your machine and run the server yourself. Point it at:

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

Requires Node 18+. Prefer Python? Swap in `uvx`:

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

## Limits worth knowing

- **Desktop only.** Custom MCP connectors are loaded by the desktop client and ignored by the browser and mobile builds.
- **No config file** means no dotfile to check into a repo and no `--scope` precedence to reason about. It also means you can't script the setup; it's per-machine, per-account.
- **OAuth is optional.** DataSinking authenticates with the header you set in step 3, so an auth prompt means something upstream is misconfigured.

---

## Try it

```
Which exchanges does DataSinking cover?
List Moutai's annual reports.
What does TSMC's latest annual report say in the management discussion and analysis?
```

Ask the first one as a smoke test: `list_exchanges` needs no arguments, so if it answers, the whole chain works.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Connector saves but no tools appear | Toggle is off, or you're in the browser build — custom connectors only load in the desktop client. |
| Header rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` when nothing was sent, or `{"detail":"无效的 API key"}` for a bad key. Check for a stray space or a missing `Bearer `. |
| Works on desktop, missing on mobile | Expected. Custom MCP connectors are desktop-only. |
| Asking for a tool does nothing | Try the `list_exchanges` smoke test above — it separates "connector not connected" from "model didn't pick the tool". |

To tell "my client is misconfigured" apart from "my key is wrong", skip the app entirely:

```bash
curl -s -X POST https://api.datasink.ing/mcp \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

This returns an unauthenticated `401` if the key is the problem and a tool list if it isn't.

## Keep the attribution

Keep the `source` field on every response — it names the official platform (cninfo.com.cn, EDINET, DART, MOPS) the data came from.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
