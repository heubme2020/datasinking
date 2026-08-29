# -*- coding: utf-8 -*-
"""
Quickstart: 演示 5 个核心函数.

Usage:
    python examples/01_quickstart.py YOUR_API_KEY
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datasinking import DataSinking

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATASINK_API_KEY", "YOUR_API_KEY")

ds = DataSinking(API_KEY)

# 1. 列交易所
exchanges = ds.list_exchanges()
print("1. Exchanges:", exchanges)

# 2. 列某交易所的股票
stocks = ds.list_stocks("sse")
print(f"\n2. Shanghai has {len(stocks)} stocks, first 5:")
for s in stocks[:5]:
    print(f"   {s['stock_code']}  {s['stock_name']}  ({s['report_count']} reports)")

# 3. 列某股票的报告列表(元数据, 无全文)
print("\n3. Kweichow Moutai (600519.SS) reports (metadata, first 5):")
reports = ds.list_reports("600519.SS")
for r in reports[:5]:
    print(f"   {r['report_period']}  {r['doc_type']}  {r['title'][:30]}")

# 4. 拉指定报告(全文)
doc = ds.get_report(reports[0]["id"])
print(f"\n4. Single report: {doc['title']}")
print(f"   First 200 chars:\n{doc['content'][:200]}")

# 5. 拉某股票的报告(全文, 最近 3 篇)
print("\n5. Kweichow Moutai latest 3 full reports:")
for r in ds.get_stock_reports("600519.SS", limit=3):
    print(f"   {r['report_period']}  ({len(r['content'])} chars)")
