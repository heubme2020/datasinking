# -*- coding: utf-8 -*-
"""DataSinking Haystack Fetcher —— 把财报全文变成 Haystack 的 `Document`。

用法（先 `pip install haystack-ai`）:

    from datasinking.haystack import DataSinkingFetcher

    fetcher = DataSinkingFetcher(api_key="你的 key", symbol="AAPL", doc_type="annual", limit=1)
    docs = fetcher.run()["documents"]       # List[haystack.dataclasses.Document]

    # 在 Haystack pipeline 里:
    # pipeline.add_component("fetcher", DataSinkingFetcher(api_key=..., symbol=...))

    # 按章节拆（更适合 RAG）:
    fetcher = DataSinkingFetcher(api_key="你的 key", symbol="AAPL", split_by_section=True)
    docs = fetcher.run()["documents"]

Haystack 是可选依赖，import 本模块、真正调 `run` 时才要求已安装。
"""
from .client import DataSinking


def _meta(symbol, report, section=None):
    """把一份报告（或其中的一章）的元数据打包，保留官方披露平台署名。"""
    m = {
        "symbol": symbol,
        "doc_id": report.get("id"),
        "title": report.get("title") or "",
        "report_period": report.get("report_period") or "",
        "doc_type": report.get("doc_type") or "",
        "source": report.get("source") or "",  # SEC EDGAR / cninfo / EDINET / DART / MOPS…
    }
    if section:
        m["section"] = section
    return m


class DataSinkingFetcher:
    """把 DataSinking 的财报全文加载成 Haystack `Document`（鸭子类型组件，实现 run）。"""

    def __init__(self, api_key, symbol, doc_type=None, limit=1, split_by_section=False,
                 base_url="https://api.datasink.ing"):
        self._client = DataSinking(api_key, base_url)
        self.symbol = symbol
        self.doc_type = doc_type
        self.limit = limit
        self.split_by_section = split_by_section

    def run(self):
        """返回 {"documents": [Document, ...]}（Haystack 组件约定）。"""
        try:
            from haystack.dataclasses import Document  # 懒加载，避免硬依赖
        except ImportError:
            from haystack import Document  # 兼容部分版本的顶层导出

        reports = self._client.get_stock_reports(self.symbol, doc_type=self.doc_type, limit=self.limit)
        docs = []
        for r in reports:
            if not self.split_by_section:
                docs.append(Document(content=r.get("content") or "", meta=_meta(self.symbol, r)))
                continue
            for sec in self._client.list_sections(r["id"]):
                s = self._client.get_section(r["id"], sec)
                docs.append(Document(content=s.get("content") or "",
                                     meta=_meta(self.symbol, r, section=sec)))
        return {"documents": docs}
