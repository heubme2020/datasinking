# -*- coding: utf-8 -*-
"""DataSinking Python client — 5 个核心函数。

    list_exchanges()                         列交易所
    list_stocks(exchange)                    列某交易所的股票
    list_reports(symbol, doc_type=?)         列某股票的报告列表(元数据, 无全文)
    get_report(doc_id)                       拉指定报告(全文)
    get_stock_reports(symbol, ..., limit=7)  拉某股票的报告(全文)

返回类型约定: list_* 一律返回 list, get_report 返回单个 dict, get_stock_reports 返回 list。

零第三方依赖, 只用标准库 urllib。
"""
import json
import time
import urllib.request
import urllib.error
import urllib.parse


class DataSinking:
    def __init__(self, api_key, base_url="https://api.datasink.ing"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    # ---- 内部: HTTP ----
    def _request(self, method, path, params=None, body=None, retries=5):
        p = dict(params or {})
        p["apikey"] = self.api_key
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(p)}"
        data = None
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DataSinking/0.1.0)"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        last = None
        for i in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 429:  # 限流, 稍等重试
                    time.sleep(2)
                    continue
                raise  # 其他 HTTP 错误(401/403/404...)直接抛给上层
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                time.sleep(1 + i)
                last = e
        raise RuntimeError(f"Request failed after retries: {last}")

    def _get(self, path, params=None):
        return self._request("GET", path, params)

    def _post(self, path, body=None):
        return self._request("POST", path, body=body)

    def _fetch_all_meta(self, params):
        """分页拉全 metadata(无 content), 200/页"""
        items = []
        page = 1
        while True:
            d = self._get("/documents", dict(params, page=page, size=200))
            items.extend(d["items"])
            if not d["items"] or len(items) >= d["total"]:
                break
            page += 1
        return items

    def _batch_content(self, ids, batch_size=127):
        """批量拉全文; free 计划 batch 返回 403 时自动回退逐篇拉取"""
        items = []
        batch_ok = True
        for i in range(0, len(ids), batch_size):
            chunk = ids[i : i + batch_size]
            if batch_ok:
                try:
                    b = self._post("/documents/batch", {"doc_ids": chunk})
                    items.extend(b["items"])
                    continue
                except urllib.error.HTTPError as e:
                    if e.code == 403:
                        batch_ok = False
                    else:
                        raise
            for did in chunk:
                items.append(self._get(f"/documents/{did}"))
        return items

    # ---- 5 个核心函数 ----
    def list_exchanges(self):
        """列交易所 -> list[str], 如 ['bj', 'sse', 'szse']"""
        return self._get("/exchanges")["exchanges"]

    def list_stocks(self, exchange):
        """列某交易所的股票 -> list[dict] (stock_code / stock_name / report_count)"""
        return self._get("/stocks", {"exchange": exchange})["items"]

    def list_reports(self, symbol, doc_type=None):
        """列某股票的报告列表(元数据, 无全文) -> list[dict]

        doc_type: annual / semiannual / q1 / q3 / amendment
        """
        params = {"symbol": symbol}
        if doc_type:
            params["doc_type"] = doc_type
        return self._fetch_all_meta(params)

    def get_report(self, doc_id):
        """拉指定报告(全文) -> dict, 含 content"""
        return self._get(f"/documents/{doc_id}")

    def get_stock_reports(self, symbol, period_from=None, period_to=None, limit=7, doc_type=None):
        """拉某股票的报告(全文) -> list[dict]

        period_from / period_to: 按报告期(report_period, YYYY-MM-DD), 不是发布日。
        limit: 最近 N 篇(按报告期倒序); -1 = 全部(自动分页拉全)。
        doc_type: annual / semiannual / q1 / q3 / amendment
        """
        params = {"symbol": symbol}
        if period_from:
            params["report_period_from"] = period_from
        if period_to:
            params["report_period_to"] = period_to
        if doc_type:
            params["doc_type"] = doc_type
        if limit == -1:
            ids = [m["id"] for m in self._fetch_all_meta(params)]
        else:
            d = self._get("/documents", dict(params, size=limit, order="desc"))
            ids = [it["id"] for it in d["items"]]
        return self._batch_content(ids)
