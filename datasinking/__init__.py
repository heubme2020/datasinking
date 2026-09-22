# -*- coding: utf-8 -*-
"""DataSinking Python client.

Usage:
    from datasinking import DataSinking
    ds = DataSinking("YOUR_API_KEY")
    ds.list_exchanges()

额度用尽时抛 `QuotaExceeded`（区别于网络/限流错误）:
    from datasinking import DataSinking, QuotaExceeded
    try:
        ds.get_stock_reports("600519.SS", limit=-1)
    except QuotaExceeded as e:
        print(e.code, e)   # e.g. quota_7d / free_quota_key / free_quota_global
"""
from ._version import __version__
from .client import DataSinking, QuotaExceeded

__all__ = ["DataSinking", "QuotaExceeded", "__version__"]
