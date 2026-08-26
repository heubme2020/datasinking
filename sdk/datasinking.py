# -*- coding: utf-8 -*-
"""
DataSinking Python client.

Usage:
    from sdk.datasinking import DataSinking
    ds = DataSinking("YOUR_API_KEY")
    ds.get_exchanges()
"""
import time

import requests


class DataSinking:
    def __init__(self, api_key, base_url="https://api.datasink.ing"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = api_key

    # ---- internal helpers ----
    def _get(self, path, params=None, retries=5):
        for i in range(retries):
            try:
                r = self.session.get(f"{self.base_url}{path}", params=params, timeout=60)
                if r.status_code == 429:
                    time.sleep(2)  # rate limited, wait and retry
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                time.sleep(1 + i)
        raise RuntimeError("Request failed after multiple retries")

    def _post(self, path, json=None, retries=5):
        for i in range(retries):
            try:
                r = self.session.post(f"{self.base_url}{path}", json=json, timeout=60)
                if r.status_code == 429:
                    time.sleep(2)  # rate limited, wait and retry
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                time.sleep(1 + i)
        raise RuntimeError("Request failed after multiple retries")

    def _fetch_all(self, params):
        """Paginate through all metadata (id only, no content), 200 per page."""
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
        """Fetch full content (with markdown) in batches via the batch endpoint."""
        items = []
        for i in range(0, len(ids), batch_size):
            chunk = ids[i:i + batch_size]
            b = self._post("/documents/batch", {"doc_ids": chunk})
            items.extend(b["items"])
        return items

    # ---- metadata ----

    def get_exchanges(self):
        """List available exchanges, e.g. ['bj', 'sse', 'szse']."""
        return self._get("/exchanges")["exchanges"]

    def get_symbols(self, exchange):
        """List stocks for an exchange (with report counts)."""
        return self._get("/stocks", {"exchange": exchange})["items"]

    # ---- unified report fetching (returns full markdown content) ----

    def get_symbol_reports(self, symbol=None, doc_id=None, start=None, end=None,
                           limit=None, all=False):
        """Get a symbol's reports (full markdown content included).

        Usage:
            get_symbol_reports(doc_id=1)                                # single document
            get_symbol_reports(symbol='600519.SS', limit=5)             # latest 5
            get_symbol_reports(symbol='600519.SS',
                               start='2023-01-01', end='2023-12-31')    # date range (all)
            get_symbol_reports(symbol='600519.SS', all=True)            # all reports

        When start/end/all are unset, defaults to the latest 10 reports.
        """
        if doc_id is not None:
            return self._get(f"/documents/{doc_id}")
        if not symbol:
            raise ValueError("symbol or doc_id is required")
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
        """Get an exchange's reports (full markdown content included).

        Usage:
            get_exchange_reports('sse', limit=5)                             # latest 5
            get_exchange_reports('sse', start='2023-01-01', end='2023-12-31') # date range
            get_exchange_reports('sse', all=True)                             # all reports

        When start/end/all are unset, defaults to the latest 10 reports.
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
