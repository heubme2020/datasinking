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

from ._version import __version__


class QuotaExceeded(RuntimeError):
    """额度用尽（HTTP 429 + 服务端返回的 `code`）。

    和「限流」不是一回事：限流等几秒就好（客户端自己会重试），
    额度类要等**日/月窗口滚动**才有用 —— 重试没有意义，所以直接抛出来，不再重试。

    常见 code：
      quota_day          年费 key 当日额度用尽（UTC 次日 00:00 恢复）
      quota_month        年费 key 最近 31 天额度用尽
      free_quota_key     免费 key 当日额度用尽
      free_quota_global  免费共享池 当日额度用尽（所有免费用户合计）
      free_quota_month   免费共享池 最近 31 天额度用尽（所有免费用户合计）
    """

    def __init__(self, code=None, detail=None):
        super().__init__(detail or code or "Quota exceeded")
        self.code = code
        self.detail = detail


def _error_info(e):
    """从错误响应体里取 (code, detail)。

    服务端把 `code` 留给**非瞬时**的错误：限流（等几秒就好）不带 code，
    额度类（要等窗口滚动）才带。所以「有没有 code」就是「该不该重试」的判据。
    """
    try:
        body = json.loads(e.read().decode("utf-8"))
        return body.get("code"), body.get("detail")
    except Exception:
        return None, None


class DataSinking:
    def __init__(self, api_key, base_url="https://api.datasink.ing"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        # batch 探测出来的可用块大小（免费档 3 / 年费 31）。首次调用后缓存，之后不再试错。
        self._batch_size = None

    # ---- 内部: HTTP ----
    def _request(self, method, path, params=None, body=None, retries=5):
        p = dict(params or {})
        p["apikey"] = self.api_key
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(p)}"
        data = None
        headers = {"User-Agent": f"Mozilla/5.0 (compatible; DataSinking/{__version__})"}
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
                if e.code != 429:
                    raise  # 401/403/404/400… 直接抛给上层
                code, detail = _error_info(e)
                if code:
                    # 额度类 429：要等日/月窗口滚动，重试没有意义 —— 立刻抛，并带上服务端的原因。
                    # （以前这里不分青红皂白 sleep(2) 重试，月度额度打满时会空转，
                    #   最后还抛出一句 "Request failed after retries: None" —— last 变量
                    #   只在网络异常分支被赋值，429 分支根本不赋值。）
                    raise QuotaExceeded(code, detail)
                # 纯限流：等一下再试
                last = RuntimeError(detail or "Rate limit exceeded (HTTP 429)")
                time.sleep(2)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                time.sleep(1 + i)
                last = e
        raise RuntimeError(f"Request failed after {retries} retries: {last}")

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

    def _batch_content(self, ids, batch_size=None):
        """批量拉全文。

        服务端**按档位**限制 batch 单次篇数（免费 3 / 年费 31），而客户端事先不知道自己
        是哪档，所以先按 31 发；被拒（400 / 403）就把块缩小重试，最终退化成逐篇拉取。
        31 → 10 → 3，免费档试错两次后稳定在 3；**探测出的可用大小会缓存到实例上**，
        同一个 client 之后的调用不再重复试错。

        旧版这里只认 403，而免费档超限返回的是 **400** —— 会直接 raise 把整个任务打断。
        """
        if batch_size is None:
            batch_size = self._batch_size or 31
        items = []
        i = 0
        while i < len(ids):
            n = min(batch_size, len(ids) - i)
            chunk = ids[i : i + n]

            if n == 1:  # 块已经缩到 1 篇，batch 没意义，直接走单篇接口
                items.append(self._get(f"/documents/{chunk[0]}"))
                i += 1
                continue

            try:
                items.extend(self._post("/documents/batch", {"doc_ids": chunk})["items"])
                self._batch_size = n  # 记住这个大小，下次直接用
                i += n
            except QuotaExceeded:
                raise  # 额度用尽，缩块也没用
            except urllib.error.HTTPError as e:
                if e.code not in (400, 403):
                    raise
                # 被拒 → 缩块重试。大于 6 就除以 3（收敛快），小了就减一（保证能到 1、
                # 且不会跳过服务端真实允许的大小，比如 12 → 4 → 3 而不是 12 → 4 → 1）。
                batch_size = n // 3 if n > 6 else n - 1
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

    def list_sections(self, doc_id):
        """列出报告的章节标题 -> list[str]（供 get_section 用）"""
        return self._get(f"/documents/{doc_id}/sections")["sections"]

    def get_section(self, doc_id, section):
        """只取报告的某一章（省 token，适合 RAG）-> dict，含 content 和 section

        section: 章节标题关键词，如 "管理层讨论与分析" / "财务报告" / "MD&A"
        """
        return self._get(f"/documents/{doc_id}", {"section": section})
