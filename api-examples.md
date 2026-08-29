# API Examples

Seven examples — the five operations (the fifth has three variants). Each shows
**curl**, **Python**, and **an LLM** side by side.

```bash
pip install datasinking   # for the Python examples
```

---

## 1. List exchanges

**curl**
```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
# → {"exchanges": ["bj", "sse", "szse"]}
```

**Python**
```python
from datasinking import DataSinking
ds = DataSinking("YOUR_API_KEY")

ds.list_exchanges()          # → ['bj', 'sse', 'szse']
```

**LLM** — point it at https://datasink.ing and ask:
> "Which exchanges does this cover?"

---

## 2. List stocks in an exchange

**curl**
```bash
curl "https://api.datasink.ing/stocks?exchange=sse&apikey=YOUR_KEY"
# → {"exchange":"sse","total":2300,"items":[{"stock_code":"600000","stock_name":"浦发银行","report_count":30}, …]}
```

**Python**
```python
ds.list_stocks("sse")        # → list[dict] (stock_code / stock_name / report_count)
```

**LLM**
> "What stocks are on the Shanghai exchange?"

---

## 3. List a stock's reports (metadata)

**curl**
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&doc_type=annual&apikey=YOUR_KEY"
```

**Python**
```python
ds.list_reports("600519.SS", doc_type="annual")   # → list[dict], metadata (no content)
```

**LLM**
> "List Moutai's annual reports."

---

## 4. Fetch one report (full text)

**curl**
```bash
curl "https://api.datasink.ing/documents/42?apikey=YOUR_KEY"
```

**Python**
```python
ds.get_report(42)            # → dict, single report (full content)
```

**LLM**
> "Give me document 42."

---

## 5. Stock's reports — latest N (full text)

**curl**
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&order=desc&size=7&with_content=1&apikey=YOUR_KEY"
```

**Python**
```python
ds.get_stock_reports("600519.SS", limit=7)   # → list[dict], full content
```

**LLM**
> "Moutai's latest 7 reports, full text."

---

## 6. Stock's reports — by reporting period (full text)

`report_period` = the fiscal period (not the disclosure date).

**curl**
```bash
curl "https://api.datasink.ing/documents?symbol=600519.SS&report_period_from=2023-01-01&report_period_to=2023-12-31&with_content=1&apikey=YOUR_KEY"
```

**Python**
```python
ds.get_stock_reports("600519.SS", period_from="2023-01-01", period_to="2023-12-31")
```

**LLM**
> "Moutai's 2023 reports, by reporting period, full text."

---

## 7. Stock's reports — all (full text)

**curl**
```bash
# 纯 curl 需手动翻 page 拉全; Python 的 limit=-1 会自动分页
curl "https://api.datasink.ing/documents?symbol=600519.SS&page=1&size=200&with_content=1&apikey=YOUR_KEY"
```

**Python**
```python
ds.get_stock_reports("600519.SS", limit=-1)   # → all reports, full content
```

**LLM**
> "All of Moutai's reports, full text."
