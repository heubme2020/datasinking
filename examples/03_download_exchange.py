# -*- coding: utf-8 -*-
"""
Download EVERY report of an entire exchange (all stocks, full Markdown) to local files.

NOTE: 拉整个交易所 = list_stocks 列股票 + 逐个 get_stock_reports(limit=-1) 拉全。
      非常重、慢(SZSE 130k+ 文档 / 几十 GB)。付费(yearly) key 强烈建议(31 req/s + batch)。

Usage:
    python examples/03_download_exchange.py YOUR_API_KEY szse ./downloads/szse
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datasinking import DataSinking

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

API_KEY = sys.argv[1]
EXCHANGE = sys.argv[2]  # sse / szse / bj
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else f"./downloads/{EXCHANGE}"

ds = DataSinking(API_KEY)

# 列交易所所有股票, 逐个拉全
stocks = ds.list_stocks(EXCHANGE)
print(f"{EXCHANGE}: {len(stocks)} stocks")

for s in stocks:
    code = s["stock_code"]
    try:
        reports = ds.get_stock_reports(code, limit=-1)
    except Exception as e:
        print(f"  skip {code}: {e}")
        continue
    d = os.path.join(OUT_DIR, code)
    os.makedirs(d, exist_ok=True)
    for r in reports:
        doc_type = r["doc_type"]
        period = r.get("report_period")
        year = str(period)[:4] if period else "unknown"
        ann = r.get("announcement_time")
        date = datetime.fromtimestamp(ann / 1000).strftime("%Y%m%d") if ann else "unknown"
        path = os.path.join(d, f"{code}_{year}_{doc_type}_{date}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(r["content"])
    print(f"  {code} {s['stock_name']}: {len(reports)} reports")

print(f"Saved to {OUT_DIR}/{{stock_code}}/...")
