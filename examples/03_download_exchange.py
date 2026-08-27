# -*- coding: utf-8 -*-
"""
Download EVERY report of an entire exchange (all stocks, full Markdown) to local files.

Usage:
    python examples/03_download_exchange.py YOUR_API_KEY szse ./downloads/szse

Notes:
    - Pulls the full text of every report on the exchange. For SZSE that's
      130k+ documents / tens of GB — it runs for a while.
    - Requires a paid (yearly) key: batch download is not available on the free plan.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sdk.datasinking import DataSinking

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

API_KEY = sys.argv[1]
EXCHANGE = sys.argv[2]  # sse / szse / bj
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else f"./downloads/{EXCHANGE}"

ds = DataSinking(API_KEY)

# Pull every report of the exchange with full content (auto-paginated + batched)
reports = ds.get_exchange_reports(exchange=EXCHANGE, all=True)
print(f"{EXCHANGE}: {len(reports)} reports fetched")

for r in reports:
    code = r["stock_code"]
    doc_type = r["doc_type"]
    period = r.get("report_period")
    year = str(period)[:4] if period else "unknown"
    ann = r.get("announcement_time")
    date = datetime.fromtimestamp(ann / 1000).strftime("%Y%m%d") if ann else "unknown"

    # group by stock code: downloads/szse/{code}/{code}_{year}_{type}_{date}.md
    d = os.path.join(OUT_DIR, code)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{code}_{year}_{doc_type}_{date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(r["content"])

print(f"Saved to {OUT_DIR}/{{stock_code}}/...")
