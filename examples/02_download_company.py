# -*- coding: utf-8 -*-
"""
下载某家公司全部财报到本地 Markdown 文件

用法：
    python examples/02_download_company.py YOUR_API_KEY 600519.SS ./downloads/600519
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sdk.finreport import FinReport

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

API_KEY = sys.argv[1]
SYMBOL = sys.argv[2]
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else f"./downloads/{SYMBOL.replace('.', '_')}"

fr = FinReport(API_KEY)

# 全量拉取某只股票所有报告（含正文，自动分页 + batch）
reports = fr.get_symbol_reports(symbol=SYMBOL, all=True)
print(f"{SYMBOL} 共 {len(reports)} 篇报告")

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

print(f"已保存到 {OUT_DIR}/，文件名格式：股票代码_年份_类型_公告日期.md")
