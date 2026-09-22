# DeepSeek

Connect the **DeepSeek Harness** (`dsh`) to the DataSinking MCP server.

> **Not to be confused with two other things called "DeepSeek agent docs":**
>
> - `api-docs.deepseek.com/.../agent_integrations/claude_code` is about pointing *Claude Code at
>   DeepSeek as a model backend* (`ANTHROPIC_BASE_URL`). It has nothing to do with MCP servers.
> - `deepseek-ai/awesome-deepseek-agent` is a curated list of **third-party** tools. DeepSeek is not
>   the client there — it's the model they talk to.
>
> The harness is a separate thing, and it *is* a real MCP client.

⚠️ **`dsh` is a developer preview.** `@deepseek-ai/dsh` is published as a release candidate
(`0.1.5-rc.2` at the time of writing). Expect the config surface to move; the shape below is
verified against the published config catalog and the harness's own README.

---

## Config file

`dsh` doesn't use JSON or TOML. It composes **YAML patch layers**:

| Scope | Path |
|---|---|
| One profile | `$DSH_HOME/profiles/<name>/cordis.patch.yml` |
| Every profile on this machine | `$DSH_HOME/cordis.patch.yml` |

`DSH_HOME` defaults to `~/.dsh`, so on macOS and Linux that's `~/.dsh/cordis.patch.yml`, and on
Windows `%USERPROFILE%\.dsh\cordis.patch.yml`.

There is **no project-scope config file.** Project scope means passing a `--patch` overlay at
launch, which can point at any file on disk.

## Hosted — streamable HTTP

`streamable-http` is a first-class transport; no `mcp-remote` bridge.

```yaml
- insert:
    - id: mcp-datasinking
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: datasinking
        transport: streamable-http
        url: 'https://api.datasink.ing/mcp?apikey=YOUR_KEY'
        headers:
          Authorization: !!js '`Bearer ${process.env.DATASINK_API_KEY}`'
```

`!!js` is this config system's JavaScript tag — the backtick template is evaluated at load, so the
key is read from the environment rather than written into the file. If you'd rather keep it simple,
the `?apikey=` form on the URL works on its own and you can drop the `headers` block.

## Local — stdio

```yaml
- insert:
    - id: mcp-datasinking
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: datasinking
        transport: stdio
        command: npx
        args: ['-y', 'datasinking-mcp']
        env:
          DATASINK_API_KEY: !!js process.env.DATASINK_API_KEY
        cwd: !!js process.cwd()
```

For Python instead of Node: `command: uvx`, `args: ['--from', 'datasinking[mcp]', 'datasinking-mcp']`.

> **The env gotcha that will cost you an hour.** The stdio bridge **scrubs ambient environment
> variables** before launching the child: any name matching `/KEY|PASSWORD|SECRET|TOKEN/i` is
> dropped, as is everything prefixed `DSH_`. So `DATASINK_API_KEY` will *not* be inherited from your
> shell — it must be listed explicitly under `config.env`, as above. Explicit entries merge on top
> of the scrub and survive.

Useful defaults on the same block: `toolCallTimeoutMs` (60000), `failOnStartupError` (false),
`reconnect.enabled` (true). With `failOnStartupError` left at its default, **a failed MCP connection
does not stop the harness from starting** — it just starts with no tools and logs an error. That
silent-start behaviour is worth knowing before you conclude the config was ignored.

## Run

```bash
npx @deepseek-ai/dsh web                                   # default http://127.0.0.1:3080
npx @deepseek-ai/dsh web --patch ./mcp-datasinking.yml     # with an MCP overlay
```

There is **no `dsh mcp add` command.** Registration means writing the YAML row into a patch layer,
or passing `--patch` at launch. `--dump-config` / `--dump-default-config` print the composed tree
without booting the harness, which is the fastest way to check your patch actually merged.

## Verify

Tools appear in the model's tool list namespaced as `mcp__<serverName>__<tool>` — e.g.
`mcp__datasinking__get_report`, `mcp__datasinking__list_exchanges`.

- Tool discovery is **asynchronous**. Wait for the `mcp__...` tools to appear before sending your
  first prompt, or the model will answer as if it has no tools.
- A **new session is enough** to pick up a config change; restarting the host is not required.
  Editing an entry reloads that server's connection in place.
- Crashed MCP children auto-reconnect with backoff (500 ms doubling to 30 s, 10 attempts).

## Troubleshooting

| Symptom | Cause |
|---|---|
| Harness starts, no `mcp__` tools | Not yet discovered (async) — or the connection failed and was swallowed. Check the log; set `failOnStartupError: true` while debugging to make it fatal. |
| `DATASINK_API_KEY` undefined in the child | Env scrubbing. List it explicitly under `config.env`. |
| Patch seems ignored | It didn't merge into the layer you think it did. `--dump-config` shows the composed result. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Every response carries a `source` field naming the official platform (cninfo.com.cn, EDINET, DART,
MOPS). Keep it when you cite or redistribute the data.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
