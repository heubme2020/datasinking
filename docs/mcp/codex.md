# OpenAI Codex CLI

Connect the [Codex CLI](https://github.com/openai/codex) to the DataSinking MCP server.

**One line, hosted — nothing to install:**

```bash
export DATASINK_API_KEY=YOUR_KEY
codex mcp add datasinking --url https://api.datasink.ing/mcp \
  --bearer-token-env-var DATASINK_API_KEY
```

Verify:

```bash
codex mcp list          # → datasinking
codex mcp get datasinking
```

---

## The config file

Codex keeps everything in **`~/.codex/config.toml`** — on Windows, `C:\Users\<you>\.codex\config.toml`. Codex's own `--help` names this path, so if you ever doubt it, ask the binary.

Everything below is a `[mcp_servers.<name>]` table appended to that file. Existing tables (other servers, project settings) are left alone.

## Hosted — streamable HTTP

```toml
[mcp_servers.datasinking]
url = "https://api.datasink.ing/mcp"
bearer_token_env_var = "DATASINK_API_KEY"
```

`bearer_token_env_var` reads the key from the environment at launch, so the secret never sits in the file. Set it first:

```bash
export DATASINK_API_KEY=YOUR_KEY            # macOS / Linux
$env:DATASINK_API_KEY="YOUR_KEY"            # Windows PowerShell
set DATASINK_API_KEY=YOUR_KEY               # Windows CMD
```

Alternatives, if you'd rather not manage an env var:

```toml
[mcp_servers.datasinking]
url = "https://api.datasink.ing/mcp?apikey=YOUR_KEY"
# or a static header:
# http_headers = { "Authorization" = "Bearer YOUR_KEY" }
```

### Three things that are easy to get wrong

These are the shapes you'll find in blog posts that **do not work** on current Codex:

1. **There is no `type` field.** Transport is inferred — a `url` means streamable HTTP, a `command` means stdio. The widely copied `type = "streamable-http"` line is not part of the schema.
2. **`bearer_token` inline is explicitly rejected.** Codex refuses to load the config at all:
   `bearer_token is not supported for streamable_http` / `in mcp_servers.<name>` (verified on
   codex-cli `0.156.1`; older builds phrased it `uses unsupported 'bearer_token'; set bearer_token_env_var`).
   Use `bearer_token_env_var`, or `http_headers`.
3. **The field is `http_headers`, not `headers`.** An old `[mcp_servers.X.headers]` block is silently dead.

Also: don't add `experimental_use_rmcp_client`. It gated streamable HTTP on older builds (≈v0.46.0) and is gone from the current config schema — adding it is at best noise. On a very old Codex build you may still need it; check `codex --version` if the URL form is rejected outright.

## Local — stdio

```toml
[mcp_servers.datasinking]
command = "npx"
args = ["-y", "datasinking-mcp"]
env = { "DATASINK_API_KEY" = "YOUR_KEY" }
```

Or with Python, without installing anything:

```toml
[mcp_servers.datasinking]
command = "uvx"
args = ["--from", "datasinking[mcp]", "datasinking-mcp"]
env = { "DATASINK_API_KEY" = "YOUR_KEY" }
```

The same thing from the CLI:

```bash
codex mcp add datasinking --env DATASINK_API_KEY=YOUR_KEY -- npx -y datasinking-mcp
```

**`codex mcp add` has no `--header` flag.** Custom headers only exist in `config.toml` via `http_headers`. And **Codex does not support SSE** — streamable HTTP or a stdio bridge, nothing else.

Handy extras on the same table: `cwd`, `startup_timeout_sec` (default 10), `tool_timeout_sec` (default 60), `enabled`, `required`, `enabled_tools` / `disabled_tools`, `env_vars = ["VAR"]`.

## Try it

```
Which exchanges does DataSinking cover?
List Toyota's annual reports.
Summarize the MD&A section of Samsung's latest annual report.
```

## Troubleshooting

| Symptom | Cause |
|---|---|
| Server listed but every call fails | Key missing from the environment Codex launched with. `codex mcp get datasinking` shows what it thinks the config is. |
| `bearer_token is not supported for streamable_http` | Replace it with `bearer_token_env_var`. |
| `http_headers` ignored | You wrote `headers`. The key is `http_headers`. |
| URL form rejected | Very old Codex build — add `experimental_use_rmcp_client = true`. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, or `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART, MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
