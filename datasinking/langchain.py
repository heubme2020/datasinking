# -*- coding: utf-8 -*-
"""DataSinking LangChain Loader —— 把财报全文变成 LangChain 的 `Document`。

用法（先 `pip install langchain-core`）:

    from datasinking.langchain import DataSinkingLoader

    loader = DataSinkingLoader(api_key="你的 key", symbol="AAPL", doc_type="annual", limit=1)
    docs = loader.load()            # List[langchain_core.documents.Document]

    loader = DataSinkingLoader(api_key="你的 key", symbol="AAPL", split_by_section=True)
    docs = loader.load()            # 一章一个 Document，更适合 RAG

LangChain 是可选依赖，import 本模块、真正调 `load` 时才要求已安装。
"""
from .client import DataSinking


def _meta(symbol, report, section=None):
    m = {
        "symbol": symbol,
        "doc_id": report.get("id"),
        "title": report.get("title") or "",
        "report_period": report.get("report_period") or "",
        "doc_type": report.get("doc_type") or "",
        "source": report.get("source") or "",
    }
    if section:
        m["section"] = section
    return m


class DataSinkingLoader:
    """把 DataSinking 的财报全文加载成 LangChain `Document` 列表（鸭子类型 loader，实现 load）。"""

    def __init__(self, api_key, symbol, doc_type=None, limit=1, split_by_section=False,
                 base_url="https://api.datasink.ing"):
        self._client = DataSinking(api_key, base_url)
        self.symbol = symbol
        self.doc_type = doc_type
        self.limit = limit
        self.split_by_section = split_by_section

    def _build(self):
        from langchain_core.documents import Document  # 懒加载，避免硬依赖

        reports = self._client.get_stock_reports(self.symbol, doc_type=self.doc_type, limit=self.limit)
        docs = []
        for r in reports:
            if not self.split_by_section:
                docs.append(Document(page_content=r.get("content") or "",
                                     metadata=_meta(self.symbol, r)))
                continue
            for sec in self._client.list_sections(r["id"]):
                s = self._client.get_section(r["id"], sec)
                docs.append(Document(page_content=s.get("content") or "",
                                     metadata=_meta(self.symbol, r, section=sec)))
        return docs

    def load(self):
        """加载 -> List[langchain_core.documents.Document]"""
        return self._build()

    def lazy_load(self):
        """兼容 LangChain 的 lazy_load 约定，直接返回同一个列表。"""
        return self._build()
