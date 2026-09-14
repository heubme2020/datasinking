# Product Hunt Launch 备料（DataSinking）

> 一次性事件，等素材备齐再发。这里是所有要提前准备的文案和截图清单。

---

## 1. 产品名 & Tagline

**产品名**：DataSinking

**Tagline**（PH 上显示在产品名下面，一句话，首选第一个）：

> **Full-text financial reports — China, Korea & Japan — as clean Markdown, for RAG & AI agents.**

备选（挑一个顺口的）：

- Annual reports from China, Korea & Japan as clean Markdown — one API call, no PDF scraping.
- The full-text financial data API for Asia — no OCR, no table cleanup.
- Feed your LLM full annual reports, not just numbers — China · Korea · Japan.

---

## 2. Topics / 分类（PH 最多选 3-4 个）

- **API**
- **Developer Tools**
- **Fintech**
- **Artificial Intelligence**

---

## 3. 截图清单（至少 1 张缩略图，建议 5-6 张）

| # | 图 | 内容 | 作用 |
|---|---|---|---|
| 1 | **缩略图（必传，最重要）** | 「DataSinking」字标 + 一句 tagline + 一小段代码/三面国旗（中韩日）。干净、高对比、小图能看清字 | 首页 feed 第一眼，决定点不点 |
| 2 | **API 返回示例** | 终端 curl 返回的 Markdown（带 YAML frontmatter + 表格），或 docs 页的 response example | 直观展示「全文 + 干净 Markdown」 |
| 3 | **官网首页** | datasink.ing 首页 | 产品全貌 |
| 4 | **覆盖页** | `/exchange` 或 `/browse` 页，显示 8 个交易所（沪深北 + 韩国 + 日本） | 展示「亚洲覆盖」 |
| 5 | **MCP 实战** | Claude Desktop / Cursor 里调用 `list_reports` → `get_section`，返回茅台某章节 | 对 AI 开发者的「wow」点 |
| 6 | **定价页** | `/pricing`（free 档 + $31/年） | 透明的定价，加分 |

> 缩略图建议尺寸：正方形或 1200×630 都行，PH 会裁剪。文字要够大。

---

## 4. Maker Comment（发布后第一个评论，必写）

```text
Hey Product Hunt! 👋

I built DataSinking because I kept hitting the same wall building RAG apps on Asian
equities: annual reports are PDFs on cninfo/DART/EDINET, and turning them into clean
Markdown — tables intact, chapters separated — is a whole pipeline, not an API call.

DataSinking gives you full-text financial reports from China, Korea & Japan as clean
Markdown, over a simple REST API (or an MCP server for AI agents):

- Full text, not just numbers — the MD&A, risk factors and notes that RAG needs.
- Chapter-level access (?section=MD&A) so you pull one section instead of 300 pages.
- FMP-style symbols: 600519.SS (Moutai), 005930.KS (Samsung), 7203.T (Toyota).
- Free key by email, no signup.

Try it:
curl "https://api.datasink.ing/documents?symbol=600519.SS&with_content=1&apikey=YOUR_KEY"

Happy to answer questions — and I'd love feedback on which markets/formats to add next! 🙏
```

---

## 5. 发布时机建议

- **别周一早上发**（PH 竞争最激烈），选 **周二~周四** 的 **美东时间凌晨（北京时间下午）** 发，覆盖欧美白天。
- 发布后**第一时间**自己发 Maker Comment（上面那段）+ 在朋友圈/群/Reddit 拉票。
- 提前准备：注册好 PH 账号、把 `datasink.ing` 设为产品链接、图片提前压好尺寸。

---

## 6. 完成标准

- [ ] 缩略图 + 5 张截图备齐
- [ ] Tagline 定稿
- [ ] Maker Comment 定稿
- [ ] PH 账号注册好、产品链接填好
- [ ] 选好发布日（周二~周四）
