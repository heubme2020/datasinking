# dev.to 使用指南（推广渠道）

> DataSinking 长尾推广 —— dev.to 是什么、为什么有用、怎么发。配合 `en-longtail.md` 使用。

## dev.to 是什么

**dev.to**（DEV Community，网址 https://dev.to）是全球最大的开发者技术社区/博客平台，
2016 年创立，Forem 开源框架搭建。用户在上面写技术文章、教程、经验分享，靠「标签 + 社区热度」
分发，**免费、注册即发、不需要审核**。

## 为什么对推广有用（重点）

1. **Google 收录极快、权重极高** —— dev.to 域名权威度（DA）很高，新帖通常几天内就被 Google
   收录，长尾词容易排进去。8673 个落地页要等几周，dev.to 一篇帖子几天就能上。
2. **大模型爱引用** —— ChatGPT / Claude / Perplexity 联网搜索时，dev.to 是高频引用源。这正是
   GEO（大模型搜索可见性）方案要的：让大模型在「A股财报 markdown」这类问题上搜到并引用。
3. **免费、Markdown、零门槛** —— 比 Medium 更友好（Medium 有付费墙，dev.to 没有）。

## 核心机制

| 特性 | 说明 |
|---|---|
| 标签（tags） | 每篇最多 4 个，决定文章进哪个板块 + 站内搜索发现。选「有人看但不过度拥挤」的 |
| canonical URL | 若内容同时发官网，可设 canonical 指回自己，避免重复内容被判抄 |
| Markdown 编辑器 | 直接写 MD，支持代码块、表格、图片 |
| 热度算法 | 点赞/评论/浏览驱动推荐，上首页能带来大量曝光 |
| RSS / API | 有公开 API 和 RSS，被各种工具抓取 |

## 注册 + 发帖流程

1. **注册**：https://dev.to/enter → 用 GitHub / Google / 邮箱登录（推荐 GitHub，一键）。
2. **发帖**：点右上角 **Create Post**（或 https://dev.to/new）→ Markdown 编辑器。
3. **填标题 + 正文 + 标签** → 点 **Publish**（可先 Preview）。
4. 发布后可随时编辑。

## 发英文篇的实操要点

1. **标题**：用 `en-longtail.md` 里写的那句（长尾问题句式），别改。
2. **首段 2-3 行最关键**：dev.to 列表和 Google 摘要会显示开头，开篇直接点痛点。
3. **标签**：`ai` `rag` `finance` `python`（`data` 可选）。别堆热门大标签（如 `javascript`，竞争太激烈）。
4. **封面图**：可选。没有的话 dev.to 会自动生成默认封面，不影响收录。

## 注意点（别抱错期待）

正文里的外链是 **nofollow**（dev.to 防垃圾机制）。指向 `datasink.ing` 的链接不会直接给官网传权重。

dev.to 的价值不是外链权重，而是：
- ✅ 帖子本身排长尾词（「full-text A-share annual report markdown」）
- ✅ 被大模型联网搜索引用
- ✅ 品牌曝光 + 自然导流

这跟 GEO 目标完全吻合 —— 要的是「被搜到、被引用」，不是「传权重」。
