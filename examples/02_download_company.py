# -*- coding: utf-8 -*-
"""
Download all reports of a company to local Markdown files.

Usage:
    python examples/02_download_company.py YOUR_API_KEY 600519.SS ./downloads/600519
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
SYMBOL = sys.argv[2]
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else f"./downloads/{SYMBOL.replace('.', '_')}"

ds = DataSinking(API_KEY)

# Fetch all reports of the symbol (full content, auto-paginated + batched)
reports = ds.get_symbol_reports(symbol=SYMBOL, all=True)
print(f"{SYMBOL} has {len(reports)} reports")

os.makedirs(OUT_DIR, exist_ok=True)
for r in reports:
    code = r["stock_code"]
    doc_type = r["doc_type"]
    period = r.get("report_period")
    year = str(period)[:4] if period else "unknown"
    ann = r.get("announcement_time")
    date = datetime.fromtimestamp(ann / 1000).strftime("%Y%m%d") if ann else "unknown"

    fname = f"{code}_{year}_{doc_type}_{date}.md"
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r["content"])

print(f"Saved to {OUT_DIR}/, filename format: code_year_type_date.md")
