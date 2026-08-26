# -*- coding: utf-8 -*-
"""
入门示例：列交易所 → 列股票 → 查报告列表 → 拉单篇正文

用法：
    python examples/01_quickstart.py YOUR_API_KEY
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sdk.finreport import FinReport

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATASINK_API_KEY", "YOUR_API_KEY")

fr = FinReport(API_KEY)

# ① 列交易所
exchanges = fr.get_exchanges()
print("① 交易所:", exchanges)

# ② 列上交所的股票（前 5 只）
stocks = fr.get_symbols("sse")
print(f"\n② 上交所共 {len(stocks)} 只股票，前 5 只：")
for s in stocks[:5]:
    print(f"   {s['stock_code']}  {s['stock_name']}  ({s['report_count']} 篇)")

# ③ 查茅台的报告列表（最近 5 篇）
print("\n③ 贵州茅台(600519.SS)最近 5 篇：")
reports = fr.get_symbol_reports(symbol="600519.SS", limit=5)
for r in reports:
    print(f"   {r['report_period']}  {r['title'][:30]}  ({len(r['content'])} 字)")

# ④ 拉单篇正文（含完整 markdown）
doc = fr.get_symbol_reports(doc_id=1)
print(f"\n④ 单篇示例：{doc['title']}")
print(f"   正文前 200 字：\n{doc['content'][:200]}")
