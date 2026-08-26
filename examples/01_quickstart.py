# -*- coding: utf-8 -*-
"""
Quickstart: list exchanges -> list stocks -> list reports -> fetch a document.

Usage:
    python examples/01_quickstart.py YOUR_API_KEY
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sdk.datasinking import DataSinking

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATASINK_API_KEY", "YOUR_API_KEY")

ds = DataSinking(API_KEY)

# 1. List exchanges
exchanges = ds.get_exchanges()
print("1. Exchanges:", exchanges)

# 2. List stocks on the Shanghai exchange (first 5)
stocks = ds.get_symbols("sse")
print(f"\n2. Shanghai has {len(stocks)} stocks, first 5:")
for s in stocks[:5]:
    print(f"   {s['stock_code']}  {s['stock_name']}  ({s['report_count']} reports)")

# 3. List Kweichow Moutai reports (latest 5)
print("\n3. Kweichow Moutai (600519.SS) latest 5 reports:")
reports = ds.get_symbol_reports(symbol="600519.SS", limit=5)
for r in reports:
    print(f"   {r['report_period']}  {r['title'][:30]}  ({len(r['content'])} chars)")

# 4. Fetch a single document (full markdown)
doc = ds.get_symbol_reports(doc_id=1)
print(f"\n4. Single document: {doc['title']}")
print(f"   First 200 chars:\n{doc['content'][:200]}")
