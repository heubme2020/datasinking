<!--
发布信息（发布后删除本注释块）
平台：dev.to  →  https://dev.to/new
标题：How to get full-text A-share (China) annual reports as Markdown — Kweichow Moutai example
Tags：ai, rag, finance, python, data
-->

# How to get full-text A-share (China) annual reports as Markdown — Kweichow Moutai example

If you're building RAG or LLM tooling on Chinese equities, you've hit the same wall:
annual reports are published as **PDFs on cninfo.com.cn**, and turning them into clean,
table-preserving Markdown is real work.

## The hard way (what most people do)

1. Query cninfo for the announcement PDF.
2. Download it.
3. Parse the PDF — `pymupdf` gets you ~90% of the way, but scanned pages need OCR,
   and financial tables often come out mangled.
4. Clean headers/footers, restore tables, split chapters.

Doable, but it's a *pipeline*, not a task — and you rebuild it for every company.

## The one-liner

[DataSinking](https://datasink.ing) serves **full-text** annual / semi-annual / quarterly
reports from **China (SSE/SZSE/BSE), Korea and Japan** as clean Markdown, sourced from the
official disclosure platforms, with YAML frontmatter and preserved headings, paragraphs
and tables.

```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&with_content=1&apikey=YOUR_KEY"
```

That returns Kweichow Moutai's latest annual report as Markdown — no PDF, no OCR, no
cleanup. Symbols are FMP-style: `600519.SS` (Moutai), `005930.KS` (Samsung), `7203.T` (Toyota).

## Pull just one chapter (save tokens)

For RAG you rarely want the whole 300-page report:

```bash
# list the sections first
curl "https://api.datasink.ing/documents/3/sections?apikey=YOUR_KEY"
# fetch only the MD&A chapter (the %-string is 管理层讨论与分析, URL-encoded)
curl "https://api.datasink.ing/documents/3?section=%E7%AE%A1%E7%90%86%E5%B1%82%E8%AE%A8%E8%AE%BA%E4%B8%8E%E5%88%86%E6%9E%90&apikey=YOUR_KEY"
```

Chapter-level access is the part most financial APIs miss — and it's the most useful
for feeding an LLM without blowing your context window.

## Why full text beats structured indicators

Structured-finance APIs give you numbers (revenue, margins, ratios). They don't give you
the *narrative* — management discussion, risk factors, notes to the financial statements —
which is exactly what RAG apps and analyst-grade LLM workflows need to answer "why".

## Start free

Get a free key by email (no signup): `POST https://api.datasink.ing/free-key` with
`{"email": "you@example.com"}`.

- Docs: https://datasink.ing/docs
- GitHub: https://github.com/heubme2020/datasinking
