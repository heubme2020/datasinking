# -*- coding: utf-8 -*-
"""DataSinking LlamaIndex Reader —— 把财报全文变成 LlamaIndex 的 `Document`。

用法（先 `pip install llama-index`）:

    from datasinking.llama_index import DataSinkingReader

    reader = DataSinkingReader(api_key="你的 DataSinking key")
    docs = reader.load_data(symbol="AAPL", doc_type="annual", limit=1)

    # 按章节拆成多个 Document（更适合 RAG，省 token）:
    docs = reader.load_data(symbol="AAPL", doc_type="annual", split_by_section=True)

LlamaIndex 是可选依赖，不在核心包安装里 —— 只有 import 这个模块、真正调 `load_data`
时才要求已安装，避免给不用 RAG 的用户硬塞一个重依赖。
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


class DataSinkingReader:
    """把 DataSinking 的财报全文加载成 LlamaIndex `Document` 列表。"""

    def __init__(self, api_key, base_url="https://api.datasink.ing"):
        self._client = DataSinking(api_key, base_url)

    def load_data(self, symbol, doc_type=None, limit=1, split_by_section=False, **kwargs):
        """加载某股票的报告 -> List[llama_index.core.schema.Document]。

        参数:
          symbol            FMP 风格代码，如 AAPL / 600519.SS / 7203.T / 005930.KS
          doc_type          annual / semiannual / q1 / q3（None = 不限）
          limit             取最近 N 份（按报告期倒序）；-1 = 全部
          split_by_section  False=一份报告一个 Document（全文）；True=一章一个 Document

        其它 kwargs 透传给 LlamaIndex 的 Document（如 extra_info），但 metadata 固定由本方法生成。
        """
        from llama_index.core.schema import Document  # 懒加载，避免硬依赖

        reports = self._client.get_stock_reports(symbol, doc_type=doc_type, limit=limit)
        docs = []
        for r in reports:
            if not split_by_section:
                docs.append(Document(
                    text=r.get("content") or "",
                    metadata=_meta(symbol, r),
                    doc_id=f"datasinking:{r.get('id')}",
                ))
                continue
            for sec in self._client.list_sections(r["id"]):
                s = self._client.get_section(r["id"], sec)
                docs.append(Document(
                    text=s.get("content") or "",
                    metadata=_meta(symbol, r, section=sec),
                    doc_id=f"datasinking:{r.get('id')}:{sec}",
                ))
        return docs
