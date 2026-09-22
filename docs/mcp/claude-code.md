# Claude Code

Connect [Claude Code](https://code.claude.com/docs/en/mcp) to the DataSinking MCP server.

**One line, hosted — nothing to install:**

```bash
claude mcp add --transport http datasinking https://api.datasink.ing/mcp \
  --header "Authorization: Bearer YOUR_KEY"
```

Then verify:

```bash
claude mcp list        # → datasinking: ✔ Connected
```

In a session, `/mcp` shows the same thing, and the six `datasinking` tools appear.

---

## Where the config actually goes

`claude mcp add` defaults to `--scope local`. Pick deliberately:

| `--scope` | Stored in | Use when |
|---|---|---|
| `local` *(default)* | `~/.claude.json` → `projects."<your project path>".mcpServers` | Just you, just this project |
| `user` | `~/.claude.json` → top-level `mcpServers` | You, in every project |
| `project` | `.mcp.json` in the repo root (**commit it**) | The whole team |

On Windows `~/.claude` means `%USERPROFILE%\.claude`. `CLAUDE_CONFIG_DIR` relocates the whole thing.

> A `project`-scoped server starts as `⏸ Pending approval` until you launch `claude` interactively in a trusted workspace and approve it. That's a security feature, not a failure.

## Hosted vs local

| | Hosted | Local (stdio) |
|---|---|---|
| Install | none | Node 18+ or Python 3.8+ |
| Config | URL + header | `command` + `env` |
| Works offline | no | yes (past quota checks) |
| Key lands in | shell history / `~/.claude.json` | same |

### Local — stdio

```bash
# Node (no Python needed)
claude mcp add --env DATASINK_API_KEY=YOUR_KEY --transport stdio datasinking -- npx -y datasinking-mcp

# Python, no install
claude mcp add --env DATASINK_API_KEY=YOUR_KEY --transport stdio datasinking -- uvx --from "datasinking[mcp]" datasinking-mcp
```

Two things about that command that bite people:

- **The `--` separator is mandatory.** Everything after it is passed to the server untouched. Without it Claude Code tries to parse your server command as its own flags.
- **Keep `--transport stdio` between `--env` and the name.** `--env` is variadic, so `--env DATASINK_API_KEY=YOUR_KEY datasinking` swallows `datasinking` as a second `KEY=value` pair and then complains about a missing server name.

## Equivalent JSON

If you'd rather edit the file (or you're writing `.mcp.json` for a team):

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

- **`"type": "http"` is not optional.** An entry with a `url` but no `type` is read as stdio and skipped with: `MCP server "datasinking" has a "url" but no "type"`. `"streamable-http"` is accepted as an alias; `sse` and `ws` also exist.
- `${VAR}` and `${VAR:-default}` expand inside `command`, `args`, `env`, `url` and `headers`.
- **Gotcha:** a short allowlist of credential names (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK`, `HTTPS_PROXY`, `NPM_TOKEN`, …) is deliberately blanked inside a *remote* server's `url`/`headers` — even with a `:-default`. `DATASINK_API_KEY` and `API_KEY` are unaffected, so use one of those.

You can also register straight from JSON:

```bash
claude mcp add-json --scope user datasinking \
  '{"type":"http","url":"https://api.datasink.ing/mcp","headers":{"Authorization":"Bearer YOUR_KEY"}}'
```

## Try it

```
Which exchanges does DataSinking cover?
List Moutai's annual reports.
What does Toyota's latest annual report say about risks?
```

`list_exchanges` is the natural first call — it's how the model discovers that `sse`, `jpx`, `koe` and friends exist.

## Troubleshooting

Claude Code health-checks the server itself, so `claude mcp get datasinking` is the first thing to
run — it reports the status *and* the server's error body.

```bash
claude mcp get datasinking
```

With a bad key it prints, verbatim:

```
Status: ✘ Failed to connect
Issue: Server rejected the configured Authorization header (HTTP 401). Check that the token is
valid for this MCP endpoint — OAuth fallback is disabled when headers.Authorization is set.
Error detail: {"detail":"无效的 API key"}
```

| Symptom | Cause |
|---|---|
| `✘ Failed to connect` … `Server rejected the configured Authorization header (HTTP 401)` | The key is wrong or expired. The server returns `{"detail":"Missing API key"}` when nothing is sent, `{"detail":"无效的 API key"}` when the key isn't recognised. |
| `MCP server has a "url" but no "type"` | Add `"type": "http"` to the JSON entry — the server is skipped entirely otherwise. |
| Tools don't show up after editing JSON | Restart the session. `/mcp` re-lists; `claude mcp get datasinking` shows the stored config. |
| `⏸ Pending approval` | Project-scoped server — approve it by running `claude` interactively in that workspace. |
| Header arrives blank | You used an allowlisted env var name for a remote server. Rename it to `DATASINK_API_KEY`. |
| Need wire-level logs | `claude --debug='mcp'` |

Ground truth is one command away, if you want to check the endpoint yourself without Claude Code
in the picture:

```bash
curl -s -X POST https://api.datasink.ing/mcp \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Keep the attribution

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART, MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md) · Tools reference: there too.
