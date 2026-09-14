# Awesome List 提 PR 套件（DataSinking）

> 目标：把 DataSinking 塞进高权重的 awesome 列表，被大模型联网引用 + 开发者发现。
> 调研结论：`awesome-quant`（29.4k 星）规则严、进 Commercial 分类；`awesome-ai-in-finance`（6.5k 星）正对口、好进。

---

## 目标 1：awesome-ai-in-finance（首选，好进）

- 仓库：https://github.com/georgezouq/awesome-ai-in-finance （6.5k 星）
- 分类：`## MCP Servers` → `### Research & Analysis`
- 条目格式：`- [owner/repo](url) - 描述。`（这个列表不带反引号标签）

**要加的条目：**

```markdown
- [heubme2020/datasinking](https://github.com/heubme2020/datasinking) - Full-text financial reports (China A-share, Korea, Japan) as Markdown via MCP: 6 tools for listings, reports, and chapter-level access (MD&A, notes) for RAG.
```

---

## 目标 2：awesome-quant（29.4k 星，严）

- 仓库：https://github.com/wilsonfreitas/awesome-quant （29.4k 星）
- 分类：`## Commercial & Proprietary Services`（⚠️ 不是 Market Data，因为商业 API + 薄公开 repo）
- 硬规则：商业项目必须有「真实永久免费档」+「公开定价/文档」，描述要事实性、非推广。DataSinking 有 free key（邮箱即可）+ /pricing + /docs，符合。

**要加的条目：**

```markdown
- [DataSinking](https://datasink.ing) - Full-text financial reports (China A-share, Korea, Japan) as clean Markdown via REST API and MCP server, with chapter-level access for RAG. Free tier available.
```

（该分类反引号标签可选，这里省略；结尾句号必须有。）

---

## 提 PR 步骤（每个仓库一遍，GitHub Web UI 即可，无需命令行）

1. 打开仓库页 → 右上角 **Fork** 到自己账号。
2. 进你自己的 fork → 点 `README.md` → 右上角铅笔图标 **Edit**。
3. 找到对应分类（目标1找 `### Research & Analysis`，目标2找 `## Commercial & Proprietary Services`），在列表合适位置粘上上面的条目。
4. 页面底部 Commit：选 **「Create a new branch for this commit and start a pull request」** → 起个分支名 → Propose changes。
5. 填 PR 标题/描述（可参考：
   `Add DataSinking — full-text Asian financial reports MCP server`）→ **Create pull request**。

---

## 注意

- **别一次 PR 塞多个仓库/多条**，一个 PR 只加一条（维护者好审）。
- awesome-quant 那条**描述必须事实性**，别写「best」「insanely awesome」这类推广词，否则被打回。
- 提交后通常几天到几周才合并（维护者慢），这是正常的，别催。
