# -*- coding: utf-8 -*-
"""RAG 接入示例：财报分章节拉取 → 切块 → 输出 JSONL（喂向量库）。

DataSinking 服务 RAG 的正确姿势：
  1. list_sections 看章节
  2. get_section 只拉需要的章节（MD&A / 财务报告），省 token
  3. 切块（带标题 + overlap，标题作为 chunk 元数据便于溯源）
  4. 输出 JSONL，直接喂给任何 embedding / 向量库

用法:
    python examples/rag_ingest.py YOUR_API_KEY [document_id]

依赖: 无（复用 datasinking SDK 的零依赖；切块只用标准库）
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datasinking import DataSinking


def chunk_text(title, text, chunk_size=800, overlap=100):
    """把一段文本按 chunk_size 切块，相邻块 overlap 个字符重叠。

    每块返回 {"title": 章节标题, "text": 块文本}，标题作为 chunk 的元数据，
    检索时能追溯到「这段来自哪份报告的哪一章」。
    """
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # 尽量在句号/换行处断开，避免切坏句子
        if end < len(text):
            for sep in ["\n\n", "\n", "。", ".", "；", ";"]:
                idx = text.rfind(sep, start + chunk_size // 2, end)
                if idx > 0:
                    end = idx + len(sep)
                    break
        chunks.append({"title": title, "text": text[start:end].strip()})
        start = end - overlap
    return chunks


def main():
    api_key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATASINK_API_KEY", "")
    if not api_key:
        print("用法: python examples/rag_ingest.py YOUR_API_KEY [document_id]")
        return

    ds = DataSinking(api_key)

    # 1. 拿一个文档。默认茅台 2025 年报(id=3)；也可传 document_id。
    doc_id = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    doc = ds.get_report(doc_id)
    print(f"报告: {doc['title']} ({doc['symbol']})")
    print(f"全文: {doc['word_count']} 字\n")

    # 2. 看章节
    sections = ds.list_sections(doc_id)
    print(f"章节({len(sections)} 个): {sections[:5]}{'...' if len(sections) > 5 else ''}\n")

    # 3. 只拉需要的章节（省 token，RAG 的关键）
    target = "管理层讨论与分析"  # 换成你需要的：财务报告 / 重要事项 / MD&A
    sec = ds.get_section(doc_id, target)
    saved = 100 - 100 * len(sec["content"]) // max(doc["word_count"], 1)
    print(f"拉取章节「{sec['section']}」: {len(sec['content'])} 字（全文 {doc['word_count']} 字，省 ~{saved}%）\n")

    # 4. 切块
    chunks = chunk_text(sec["section"], sec["content"])
    print(f"切出 {len(chunks)} 个 chunk（chunk_size=800, overlap=100）")

    # 5. 输出 JSONL，喂向量库（chromadb / faiss / pinecone / 任何 embedding 工具）
    out_path = f"rag_chunks_{doc_id}.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for c in chunks:
            c["doc_id"] = doc_id
            c["symbol"] = doc["symbol"]
            c["section"] = sec["section"]
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"已输出 {out_path}，每行一个 chunk，可直接喂 embedding")


if __name__ == "__main__":
    main()
