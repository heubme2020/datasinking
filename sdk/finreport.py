# -*- coding: utf-8 -*-
"""
FinReport API Python 客户端库

用法:
    from finreport import FinReport
    fr = FinReport("你的api_key")
    fr.get_exchanges()
"""
import time

import requests


class FinReport:
    def __init__(self, api_key, base_url="https://api.datasink.ing"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = api_key

    # ---- 内部工具 ----
    def _get(self, path, params=None, retries=5):
        for i in range(retries):
            try:
                r = self.session.get(f"{self.base_url}{path}", params=params, timeout=60)
                if r.status_code == 429:
                    time.sleep(2)  # 限流，等待后重试
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                time.sleep(1 + i)
        raise RuntimeError("请求失败：多次重试后仍失败")

    def _post(self, path, json=None, retries=5):
        for i in range(retries):
            try:
                r = self.session.post(f"{self.base_url}{path}", json=json, timeout=60)
                if r.status_code == 429:
                    time.sleep(2)  # 限流，等待后重试
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                time.sleep(1 + i)
        raise RuntimeError("请求失败：多次重试后仍失败")

    def _fetch_all(self, params):
        """内部: 分页拿所有元数据(含 id, 不含正文), 每页 200 条"""
        items = []
        page = 1
        while True:
            d = self._get("/documents", dict(params, page=page, size=200))
            items.extend(d["items"])
            if not d["items"] or len(items) >= d["total"]:
                break
            page += 1
        return items

    def _batch_content(self, ids, batch_size=100):
        """内部: 按 id 分批调用 batch 端点拉正文(含 content), 服务端并行处理"""
        items = []
        for i in range(0, len(ids), batch_size):
            chunk = ids[i:i + batch_size]
            b = self._post("/documents/batch", {"doc_ids": chunk})
            items.extend(b["items"])
        return items

    # ---- 元信息 ----

    def get_exchanges(self):
        """列出有哪几个交易所, 如 ['bj', 'sse', 'szse']"""
        return self._get("/exchanges")["exchanges"]

    def get_symbols(self, exchange):
        """列出某交易所下有哪些股票(含每只的 report 数量)"""
        return self._get("/stocks", {"exchange": exchange})["items"]

    # ---- 统一报告拉取(返回完整正文) ----

    def get_symbol_reports(self, symbol=None, doc_id=None, start=None, end=None,
                           limit=None, all=False):
        """拉取某只股票的报告(统一入口, 均含完整 markdown 正文)

        用法:
            get_symbol_reports(doc_id=1)                              # 拉指定单篇
            get_symbol_reports(symbol='600519.SS', limit=5)           # 最近 5 篇
            get_symbol_reports(symbol='600519.SS',
                               start='2023-01-01', end='2023-12-31')  # 指定时间范围(全量)
            get_symbol_reports(symbol='600519.SS', all=True)          # 全量

        start/end/all 都不设时, 默认返回最新 10 篇。返回的都是完整数据(含 content)。
        """
        if doc_id is not None:
            return self._get(f"/documents/{doc_id}")
        if not symbol:
            raise ValueError("需要提供 symbol 或 doc_id")
        params = {"symbol": symbol}
        if start:
            params["report_period_from"] = start
        if end:
            params["report_period_to"] = end
        if all or start or end:
            ids = [m["id"] for m in self._fetch_all(params)]
            return self._batch_content(ids)
        n = limit if limit is not None else 10
        d = self._get("/documents", dict(params, size=n, order="desc"))
        ids = [it["id"] for it in d["items"]]
        return self._batch_content(ids)

    def get_exchange_reports(self, exchange, start=None, end=None,
                             limit=None, all=False):
        """拉取某交易所的报告(统一入口, 均含完整 markdown 正文)

        用法:
            get_exchange_reports('sse', limit=5)                              # 最近 5 篇
            get_exchange_reports('sse', start='2023-01-01', end='2023-12-31')  # 时间范围(全量)
            get_exchange_reports('sse', all=True)                              # 全量

        start/end/all 都不设时, 默认返回最新 10 篇。返回的都是完整数据(含 content)。
        """
        params = {"exchange": exchange}
        if start:
            params["report_period_from"] = start
        if end:
            params["report_period_to"] = end
        if all or start or end:
            ids = [m["id"] for m in self._fetch_all(params)]
            return self._batch_content(ids)
        n = limit if limit is not None else 10
        d = self._get("/documents", dict(params, size=n, order="desc"))
        ids = [it["id"] for it in d["items"]]
        return self._batch_content(ids)
