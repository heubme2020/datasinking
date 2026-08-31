# DataSinking MCP Server

把 [DataSinking](https://datasink.ing) 的亚洲财报全文 API 暴露给 AI agent（Claude Desktop、Claude Code、Cursor 等）。通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io)，AI 直接调用工具来取财报，无需写代码。

## 安装

```bash
pip install mcp requests
```

> 需要一个 DataSinking API key（[datasink.ing](https://datasink.ing) 免费领取）。

## 在 Claude Desktop 里配置

编辑 Claude Desktop 的配置（`Settings → Developer → Edit Config` → `claude_desktop_config.json`）：

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

重启 Claude Desktop 后，就能直接问：

> "DataSinking 覆盖了哪些交易所？茅台 2025 年报的管理层讨论与分析讲了什么？"

## 在 Claude Code 里配置

```bash
claude mcp add datasinking -- python /绝对路径/mcp_server.py
```

然后把 key 设进环境变量：

```bash
export DATASINK_API_KEY="你的key"
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
