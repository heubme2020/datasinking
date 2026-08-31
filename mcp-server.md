# DataSinking MCP Server

把 [DataSinking](https://datasink.ing) 的亚洲财报全文 API 暴露给 AI agent。通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 这个开放标准，任何支持 MCP 的 AI 客户端都能直接调用工具取财报，无需写代码。

## 支持的客户端（不止 Claude）

MCP 是开放标准，以下 AI 客户端 / agent 都能接：

- **Claude**（Desktop / Code，Anthropic）
- **Cursor**
- **OpenAI Codex**（CLI / app）
- **DeepSeek**（harness / CLI）
- **Windsurf**
- 其他支持 MCP 的 agent / 框架

## 安装

```bash
pip install mcp requests
```

> 需要一个 DataSinking API key（[datasink.ing](https://datasink.ing) 免费领取）。

## 配置（通用）

MCP 的核心配置结构在所有客户端里是一样的（`command` + `args` + `env`），只是各客户端把它写进各自的配置文件：

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "python",
      "args": ["/绝对路径/mcp_server.py"],
      "env": { "DATASINK_API_KEY": "你的key" }
    }
  }
}
```

各客户端添加方式：

| 客户端 | 添加方式 |
|--------|---------|
| **Claude Desktop** | `Settings → Developer → Edit Config`，编辑 `claude_desktop_config.json`（JSON 格式，同上） |
| **Claude Code** | `claude mcp add datasinking -- python /绝对路径/mcp_server.py` |
| **Cursor** | `Settings → MCP → Add new MCP server`（粘贴 JSON） |
| **OpenAI Codex** | 编辑 `~/.codex/config.toml`，加 `[mcp_servers.datasinking]` 段（TOML 格式，字段同上） |
| **DeepSeek** | 通过其 MCP 配置接入（JSON 同上） |
| **Windsurf** | `Settings → MCP` |

配置好后，就能直接问：

> "DataSinking 覆盖了哪些交易所？茅台 2025 年报的管理层讨论与分析讲了什么？"

## 设置 API key 环境变量

如果不在配置里写 `env` 字段（比如用 `claude mcp add` 加、或想全局设），需要先把 key 设进环境变量。三种 shell 的命令：

**Linux / macOS（bash / zsh）**：

```bash
export DATASINK_API_KEY="你的key"
```

**Windows PowerShell**：

```powershell
$env:DATASINK_API_KEY="你的key"
```

**Windows CMD**：

```cmd
set DATASINK_API_KEY=你的key
```

## 工具清单

| 工具 | 作用 | 对应 API |
|------|------|---------|
| `list_exchanges` | 列出覆盖的交易所 | `/exchanges` |
| `list_stocks(exchange)` | 列某交易所的股票 | `/stocks` |
| `list_reports(symbol, doc_type, size)` | 列某公司的报告（元数据） | `/documents` |
| `get_report(document_id)` | 拿单篇报告全文 | `/documents/{id}` |
| `list_sections(document_id)` | 列报告的章节标题 | `/documents/{id}/sections` |
| `get_section(document_id, section)` | 只取某一章（省 token，适合 RAG） | `/documents/{id}?section=` |

## 提示

- **symbol 用 FMP 风格**：`600519.SS`（茅台）、`005930.KS`（三星）、`7203.T`（丰田）。
- **要省 token 用 `get_section`** 只取某章（如「管理层讨论与分析」），而不是 `get_report` 拿整篇。
