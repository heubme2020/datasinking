# Demo 截图清单（DataSinking MCP）

> 目标：截一张「AI 在 Claude Desktop / Cursor 里调 DataSinking MCP → 返回财报章节」的图，
> 放进 GitHub README 顶部，作为落地页的视觉说服力。

---

## 前置准备（一次性）

1. **装包**（让 `datasinking-mcp` 命令可用）：

```bash
pip install "datasinking[mcp]"
```

2. **确认有 API key**（free 档就行）。没有就邮箱免费拿：

```bash
curl -X POST "https://api.datasink.ing/free-key" -H "Content-Type: application/json" -d "{\"email\":\"你的邮箱\"}"
```

---

## 配置 MCP（二选一）

### 方式 A：Claude Desktop（推荐，截图效果最好）

- 打开 Claude Desktop → Settings → **Developer** → **Edit Config**（打开 `claude_desktop_config.json`）。
- 加入：

```json
{
  "mcpServers": {
    "datasinking": {
      "command": "datasinking-mcp",
      "env": { "DATASINK_API_KEY": "你的key" }
    }
  }
}
```

- 保存 → 重启 Claude Desktop。

### 方式 B：Cursor

- Cursor Settings → **MCP** → **Add new MCP server** → 类型选 stdio：
  - Name：`datasinking`
  - Command：`datasinking-mcp`
  - Env：`DATASINK_API_KEY` = 你的key

---

## 要问 AI 的那句话（照抄）

> **Get Kweichow Moutai's (600519.SS) latest annual report, and show me the Management Discussion & Analysis section.**

（中文版：`查一下贵州茅台 600519.SS 最新年报的管理层讨论与分析章节。`）

这一步会触发 AI 依次调用 `list_reports` → `get_section`，正好展示你「按章节取全文」的卖点。

---

## 截什么（关键）

截**一张完整界面图**，要包含三样东西：

1. **AI 的工具调用过程**（能看到它调用了 `list_reports`、`get_section`）——证明「AI 真的在调你的 MCP」。
2. **返回的干净 Markdown 内容**（MD&A 章节的正文，最好有标题/段落）——证明「拿到的是全文，不是数字」。
3. **你的问题**（顶部那句英文）——让看图的人一眼知道在干嘛。

> 如果一张截不全，可以截两张：一张「调用过程」，一张「返回结果」，上下拼一起。

---

## 放哪里

1. **GitHub README**（`github-repo/README.md`）——「## MCP server」那一节下面，加一句 + 图片：

```markdown
## MCP server
...（现有文字）

![DataSinking MCP in Claude](docs/images/mcp-demo.png)
```

2. **`mcp-server.md`** —— 顶部也放一张。

> 图片先存到 `github-repo/docs/images/mcp-demo.png`，README 用相对路径引用。

---

## 验收标准

- [ ] Claude/Cursor 里成功配好 MCP，能看到 `datasinking` 的 6 个工具
- [ ] 问那句话后，AI 能调 `list_reports` → `get_section` 并返回茅台 MD&A 的 Markdown
- [ ] 截好图，放进 README 顶部 + 提交 push
