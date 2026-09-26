# DeepSeek

Connect the **DeepSeek Harness** (`dsh`) to the DataSinking MCP server.

> **Not the same as DeepSeek's model-endpoint docs** (`ANTHROPIC_BASE_URL`) or the third-party
> `awesome-deepseek-agent` list — neither of those configures an MCP server.

**`dsh` is a developer preview.**

---

## Config file

`dsh` doesn't use JSON or TOML. It composes **YAML patch layers**:

| Scope | Path |
|---|---|
| One profile — **edit this one** | `~/.dsh/profiles/<name>/cordis.patch.yml` |
| Every profile on this machine | `~/.dsh/cordis.patch.yml` |

On Windows that's `%USERPROFILE%\.dsh\profiles\<name>\cordis.patch.yml`.

Install the MCP client plugin once per profile:

```bash
dsh plugin --profile <name> add @deepseek-ai/dsh-mcp-client
```

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
key is read from the environment rather than written into the file. The `?apikey=` form on the URL
works on its own; if you use it, drop the `headers` block.

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

`failOnStartupError` on the same block defaults to `false`, so **a failed MCP connection does not
stop the harness from starting** — it starts with no tools and logs an error. That is why a broken
config looks like an ignored config.

## Run

```bash
npx @deepseek-ai/dsh web                                   # default http://127.0.0.1:3080
npx @deepseek-ai/dsh web --patch ./mcp-datasinking.yml     # with an MCP overlay
```

There is **no `dsh mcp add` command.** Registration means installing the plugin and writing the YAML
row into a patch layer, or passing `--patch` at launch. `--dump-config` / `--dump-default-config`
print the composed tree without booting the harness, which is the fastest way to check your patch
actually merged.

## Verify

Tools appear in the model's tool list namespaced as `mcp__<serverName>__<rawName>` — e.g.
`mcp__datasinking__get_report`, `mcp__datasinking__list_exchanges`.

- Tool discovery is **asynchronous**. Wait for the `mcp__...` tools to appear before sending your
  first prompt, or the model will answer as if it has no tools.
- **No restart required.** A new session is enough to pick up a config change; editing an entry
  reloads that server's connection in place.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Harness starts, no `mcp__` tools | Not yet discovered (async) — or the connection failed and was swallowed. Check the log; set `failOnStartupError: true` while debugging to make it fatal. |
| `DATASINK_API_KEY` undefined in the child | Env scrubbing. List it explicitly under `config.env`. |
| Patch seems ignored | It didn't merge into the layer you think it did. `--dump-config` shows the composed result. |
| Key rejected | `POST /mcp` returns 401 `{"detail":"Missing API key"}` with no key, `{"detail":"无效的 API key"}` with a bad one. |

## Keep the attribution

Keep the `source` field on every response — it names the official platform (cninfo.com.cn, EDINET,
DART, MOPS) the data came from.

→ All clients: [`mcp-server.md`](../../mcp-server.md)
