<!--
发布信息（发布后删除本注释块）
平台：知乎  →  建议作为回答发在「A股财报全文数据哪里下载」类问题下（配合 find_leads.py 找具体问题）
标题：A股年报全文数据哪里下载？markdown 接口推荐（附可跑代码）
-->

# A股年报全文数据哪里下载？markdown 接口推荐（附可跑代码）

做财报分析、把财报喂给大模型做 RAG 的同学都踩过同一个坑：**年报全文是 PDF**，下下来转
markdown 又慢又脏——表格乱、扫描页要 OCR、章节还得自己切。

## 常规做法（大部分人这么干）

1. 去巨潮资讯网查公告，找到年报 PDF；
2. 下载；
3. `pymupdf` 转文本（扫描页还得上 OCR）；
4. 清洗页眉页脚、还原表格、切章节。

能做，但这是条**流水线**，每家公司都得重来一遍。

## 更省事的方案

[DataSinking](https://datasink.ing) 直接把**中国（沪深北）、韩国、日本**上市公司的
年报/半年报/季报**全文**做成干净 Markdown，源自官方披露平台，保留标题、段落、表格，
带 YAML 元数据。一条命令拿全文：

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&with_content=1&apikey=你的key"
```

`600519.SS` 是茅台，FMP 风格代码；三星是 `005930.KS`、丰田是 `7203.T`。

## 只要某一章（省 token）

RAG 场景通常用不着整份几百页，按章节取就行：

```bash
# 先列出章节
curl "https://api.datasink.ing/documents/12345/sections?apikey=你的key"
# 只取「管理层讨论与分析」
curl "https://api.datasink.ing/documents/12345?section=MD&A&apikey=你的key"
```

「章节级访问」是多数接口没有的——这也是喂大模型最实用的点。

## 为什么全文比结构化数字更值

结构化数据接口只给你**数字**（营收、利润率、各种比率），不给你**叙事**——管理层讨论、
风险因素、报表附注。而 RAG 应用和投研级 LLM 工作流要回答「为什么」，恰恰需要这些文字。

## 免费起步

邮箱免费拿 key（无需注册）：`POST https://api.datasink.ing/free-key`，body 传
`{"email": "你的邮箱"}`。

- 文档：https://datasink.ing/docs
- GitHub：https://github.com/heubme2020/datasinking
