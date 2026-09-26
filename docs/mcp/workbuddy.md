# WorkBuddy / CodeBuddy (Tencent)

Connect Tencent's coding agents to the DataSinking MCP server.

> **First, which one do you have?** These are two different products with two different config files. They are easy to confuse because they share a vendor and an engine.
>
> - **WorkBuddy** — the desktop app. Config lives in `~/.workbuddy/mcp.json`.
> - **CodeBuddy Code** — the terminal CLI, binary name `codebuddy`. Config lives in `~/.codebuddy/.mcp.json`.
>
> Use the section that matches your product. Getting this wrong is the single most common reason "the config doesn't take effect".

---

## WorkBuddy (desktop app)

**Config file:**

| Scope | Path |
|---|---|
| User | `~/.workbuddy/mcp.json` |
| Project | `<project dir>/.workbuddy/mcp.json` |

On Windows `~` is `%USERPROFILE%`, i.e. `C:\Users\<you>\.workbuddy\mcp.json`.

**Or do it in the UI:** sidebar **插件 → MCP 服务器 → 配置 MCP**, paste JSON, then **Try to Run**. A green dot means connected, red (配置异常) means the JSON didn't parse or the command failed to start.

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

**Restart WorkBuddy** after editing the file — it reads MCP config at launch.

---

## CodeBuddy Code (CLI)

**Config file:**

| Scope | Path |
|---|---|
| User | `~/.codebuddy/.mcp.json` · `~/.codebuddy/mcp.json` (deprecated) · `~/.codebuddy.json` (legacy) |
| Project | `<project root>/.mcp.json` · `<project root>/mcp.json` (deprecated) |
| Local | `~/.codebuddy.json#/projects/<workspace path>` |

Precedence is **local > project > user**; within a scope, the first path listed wins. Project-scoped servers need approval on first connection.

**Hosted — streamable HTTP:**

```json
{
  "mcpServers": {
    "datasinking": {
      "type": "http",
      "url": "https://api.datasink.ing/mcp",
      "headers": { "Authorization": "Bearer ${DATASINK_API_KEY}" },
      "description": "Full-text Asian financial reports"
    }
  }
}
```

`${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url` and `headers`. Variable names must match `[A-Z_][A-Z0-9_]*` — **lowercase names are not expanded**, silently.

`type` is inferred from your fields (`command` → stdio, `url` → http), but write it explicitly. Supported transports: **STDIO / SSE / HTTP**.

**From the CLI:**

```bash
# hosted
codebuddy mcp add --scope user --transport http \
  --header "Authorization: Bearer YOUR_KEY" -- \
  datasinking https://api.datasink.ing/mcp

# local
codebuddy mcp add --scope user --transport stdio \
  --env DATASINK_API_KEY=YOUR_KEY -- \
  datasinking npx -y datasinking-mcp

# or from a JSON blob
codebuddy mcp add-json --scope user datasinking \
  '{"type":"http","url":"https://api.datasink.ing/mcp","headers":{"Authorization":"Bearer YOUR_KEY"}}'
```

Scopes are `user` / `project` / `local`. Note the unusual order: `--header` comes **before** the bare `--`.

**Local — stdio:**

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

---

## Try it

```
Which exchanges does DataSinking cover?
List Moutai's annual reports.
What does TSMC's latest annual report say in the management discussion and analysis?
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Red dot / 配置异常 | JSON syntax error, or the command isn't on `PATH`. Run the `command` by hand first — `npx -y datasinking-mcp` prints `datasinking-mcp <version> ready`. |
| Config ignored, and you edited `~/.codebuddy/.mcp.json` | Wrong product's file. The WorkBuddy desktop app reads only `~/.workbuddy/mcp.json`; the CodeBuddy CLI reads only `~/.codebuddy/.mcp.json`. See the note at the top. |
| Config ignored, and both products' files look right | Wrong scope. A project-level file overrides your user-level one: `local > project > user`. |
| Config ignored after changing the file in `~/.workbuddy/mcp.json` | App not restarted. WorkBuddy reads MCP config at launch — quit and reopen it. |
| `${datasink_key}` doesn't expand | Lowercase variable names are not expanded. Use `DATASINK_API_KEY`. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, or `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Keep the `source` field on every response — it names the official platform (cninfo.com.cn, EDINET, DART, MOPS) the data came from.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
