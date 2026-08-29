# API Examples — 7 examples × 3 interfaces

Seven examples covering the five operations (the fifth has three variants).
Pick your interface: **curl**, **Python**, or **an LLM**.

| # | Operation | curl | Python |
|---|---|---|---|
| 1 | List exchanges | `GET /exchanges` | `list_exchanges()` |
| 2 | List stocks in an exchange | `GET /stocks` | `list_stocks(exchange)` |
| 3 | List a stock's reports (metadata) | `GET /documents` | `list_reports(symbol)` |
| 4 | Fetch one report (full text) | `GET /documents/:id` | `get_report(doc_id)` |
| 5 | Stock's reports — latest N | `GET /documents + size` | `get_stock_reports(symbol, limit)` |
| 6 | Stock's reports — by reporting period | `GET /documents + from/to` | `get_stock_reports(symbol, period_from, period_to)` |
| 7 | Stock's reports — all | `GET /documents` (paginate) | `get_stock_reports(symbol, limit=-1)` |

---

## curl

### 1. List exchanges
```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
# → {"exchanges": ["bj", "sse", "szse"]}
```

### 2. List stocks in an exchange
```bash
curl "https://api.datasink.ing/stocks?exchange=sse&apikey=YOUR_KEY"
```

### 3. List a stock's reports (metadata)
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&doc_type=annual&apikey=YOUR_KEY"
```

### 4. Fetch one report (full text)
```bash
curl "https://api.datasink.ing/documents/42?apikey=YOUR_KEY"
```

### 5. Stock's reports — latest 7 (full text)
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&order=desc&size=7&with_content=1&apikey=YOUR_KEY"
```

### 6. Stock's reports — by reporting period (full text)
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&report_period_from=2023-01-01&report_period_to=2023-12-31&with_content=1&apikey=YOUR_KEY"
```

### 7. Stock's reports — all (full text, paginate)
```bash
# 纯 curl 需手动翻 page 拉全; 或直接用 Python SDK 的 limit=-1
curl "https://api.datasink.ing/documents?symbol=600519.SS&page=1&size=200&with_content=1&apikey=YOUR_KEY"
```

---

## Python

```bash
pip install datasinking
```

```python
from datasinking import DataSinking
ds = DataSinking("YOUR_API_KEY")
```

### 1. List exchanges
```python
ds.list_exchanges()          # ['bj', 'sse', 'szse']
```

### 2. List stocks in an exchange
```python
ds.list_stocks("sse")
```

### 3. List a stock's reports (metadata)
```python
ds.list_reports("600519.SS", doc_type="annual")
```

### 4. Fetch one report (full text)
```python
ds.get_report(42)
```

### 5. Stock's reports — latest 7 (full text)
```python
ds.get_stock_reports("600519.SS", limit=7)
```

### 6. Stock's reports — by reporting period (full text)
```python
ds.get_stock_reports("600519.SS", period_from="2023-01-01", period_to="2023-12-31")
```

### 7. Stock's reports — all (full text)
```python
ds.get_stock_reports("600519.SS", limit=-1)
```

---

## LLM (ask in plain language)

Point any LLM at [datasink.ing](https://datasink.ing), give it your key, and ask:

1. "Which exchanges does this cover?"
2. "What stocks are on the Shanghai exchange?"
3. "List Moutai's annual reports."
4. "Give me document 42."
5. "Moutai's latest 7 reports, full text."
6. "Moutai's 2023 reports, by reporting period, full text."
7. "All of Moutai's reports, full text."

Full end-to-end LLM prompts (with responses): see [`llm-examples.md`](llm-examples.md).
