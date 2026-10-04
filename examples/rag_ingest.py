# -*- coding: utf-8 -*-
"""把 DataSinking 财报全文切成 RAG chunk，喂进向量库。

演示「卖基底给 RAG」的三个关键点：

1. **章节级访问** —— `get_section` 只取 MD&A 等单个章节，不用拉整份 300 页报告（省 token）。
2. **块级锚点** —— 正文里的 `<!-- ds:block:N -->` 就是天然的 chunk 边界，不用自己猜怎么切。
3. **source 溯源** —— 每个 chunk 的 metadata 都带 `source`（SEC EDGAR / cninfo / DART / EDINET / MOPS）
   和 `block` 号，AI 引用时能精确指回「哪份报告、哪一章、哪一段/哪张表」。

依赖：
    pip install datasinking chromadb             # chromadb 可选，不装则只打印 chunk

用法：
    export DATASINK_API_KEY=xxx
    python rag_ingest.py AAPL                          # 苹果最近一份年报，按块切好、打印
    python rag_ingest.py AAPL --section "MD&A"         # 只切 MD&A 一章
    python rag_ingest.py 600519.SS --doc-type annual --limit 3
    python rag_ingest.py AAPL --collection apple       # 指定 chroma collection 名（会真的入库）
"""
import argparse
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from datasinking import DataSinking

# 块级锚点：`<!-- ds:block:N -->`，N 是该块在章节/全文里的序号（从 1 开始）
_BLOCK_RE = re.compile(r"<!-- ds:block:(\d+) -->")


def chunk_markdown(content: str) -> list[dict]:
    """按 `<!-- ds:block:N -->` 锚点把正文切成块。

    返回 [{block: int, text: str}]。锚点前的 frontmatter（若有）直接跳过 ——
    那些字段 API 已经作为独立字段返回了，不需要再解析一遍。
    """
    parts = _BLOCK_RE.split(content)
    chunks = []
    # parts = [锚点前的内容, "1", 块1, "2", 块2, ...]
    for i in range(1, len(parts), 2):
        block_num = parts[i]
        block_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if block_text:
            chunks.append({"block": int(block_num), "text": block_text})
    return chunks


def _meta(doc: dict, section: str | None, block: int) -> dict:
    """构造 chunk 的 metadata（chromadb 要求值必须是 str/int/float/bool，None 归零成空串）。"""
    m = {
        "symbol": doc.get("symbol", ""),
        "source": doc.get("source") or "",
        "report_period": doc.get("report_period") or "",
        "doc_type": doc.get("doc_type") or "",
        "title": doc.get("title", "") or "",
        "section": section or "full",
        "block": block,
    }
    return m


def build_chunks(doc: dict, content: str, section: str | None) -> list[dict]:
    """把一个报告的正文切成带元数据的 chunk。

    chunk 的 id 是稳定且可复现的：`{document_id}-{section}-{block}`。
    """
    out = []
    for c in chunk_markdown(content):
        out.append(
            {
                "id": f"{doc['id']}-{section or 'full'}-{c['block']}",
                "text": c["text"],
                "metadata": _meta(doc, section, c["block"]),
            }
        )
    return out


def to_chroma(chunks: list[dict], collection_name: str):
    """把 chunk 写入 chromadb（可选依赖）。"""
    import chromadb  # 延迟导入，不装也不影响 chunk 逻辑

    client = chromadb.Client()
    collection = client.get_or_create_collection(collection_name)
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    return collection


def main():
    ap = argparse.ArgumentParser(description="把 DataSinking 财报全文切成 RAG chunk")
    ap.add_argument("symbol", help="FMP 风格代码，如 AAPL / 600519.SS / 7203.T")
    ap.add_argument("--doc-type", default="annual", help="annual / semiannual / q1 / q3")
    ap.add_argument("--section", default=None, help="只切某一章（如 MD&A）；不填则切整份")
    ap.add_argument("--limit", type=int, default=1, help="处理最近 N 份报告")
    ap.add_argument("--collection", default=None, help="chroma collection 名；给了就真入库")
    args = ap.parse_args()

    key = os.environ.get("DATASINK_API_KEY")
    if not key:
        sys.exit("先 export DATASINK_API_KEY=xxx（免费 key 在 https://datasink.ing 申请）")

    ds = DataSinking(key)
    reports = ds.list_reports(args.symbol, doc_type=args.doc_type)[: args.limit]
    if not reports:
        sys.exit(f"{args.symbol} 没有 {args.doc_type} 报告")

    all_chunks = []
    for doc in reports:
        if args.section:
            # 章节级访问：只取一章，省 token
            got = ds.get_section(doc["id"], args.section)
            content = got.get("content", "")
            sec = got.get("section") or args.section
        else:
            got = ds.get_report(doc["id"])
            content = got.get("content", "")
            sec = None
        chunks = build_chunks(doc, content, sec)
        all_chunks.extend(chunks)
        print(f"{doc['symbol']} {doc['report_period']} [{sec or '全文'}]：{len(chunks)} 个 chunk")

    # 展示前 3 个 chunk（text 截断，别刷屏）
    for c in all_chunks[:3]:
        preview = c["text"][:160].replace("\n", " ")
        print(f"\n  chunk {c['id']}  source={c['metadata']['source']}")
        print(f"    {preview}…")

    if args.collection:
        collection = to_chroma(all_chunks, args.collection)
        print(f"\n已写入 chroma collection `{args.collection}`，共 {len(all_chunks)} 个 chunk")
        # 演示带溯源检索：问一句，看命中的 chunk 能不能指回来源
        res = collection.query(query_texts=["revenue"], n_results=2)
        for doc_id, src in zip(res["ids"][0], [c for c in all_chunks if c["id"] in res["ids"][0]]):
            print(f"  命中 {doc_id}  来源 {src['metadata']['source']}  block {src['metadata']['block']}")
    else:
        print(f"\n共 {len(all_chunks)} 个 chunk（加 --collection xxx 可写入 chromadb 真入库）")


if __name__ == "__main__":
    main()
