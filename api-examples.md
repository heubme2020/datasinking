# API Examples

Five functions cover everything — curl, Python, and an LLM all map to the same five.

## The five functions

| Function | What it does | curl |
|---|---|---|
| `list_exchanges()` | List exchanges | `GET /exchanges` |
| `list_stocks(exchange)` | List stocks in an exchange | `GET /stocks?exchange=sse` |
| `list_reports(symbol)` | List a stock's reports (metadata) | `GET /documents?symbol=600519.SS` |
| `get_report(doc_id)` | Fetch one report (full text) | `GET /documents/42` |
| `get_stock_reports(symbol, ...)` | Fetch a stock's reports (full text) | `GET /documents + with_content=1` |

Python (`pip install datasinking`):

```python
from datasinking import DataSinking
ds = DataSinking("YOUR_API_KEY")

ds.list_exchanges()                    # ['bj', 'sse', 'szse']
ds.list_stocks("sse")                  # list of stocks
ds.list_reports("600519.SS")           # metadata (no content)
ds.get_report(42)                      # single report, full text
ds.get_stock_reports("600519.SS")      # full text, latest 7 (default)
```

## `get_stock_reports` — three filters

| Filter | Python | curl |
|---|---|---|
| Latest N (default 7) | `limit=7` | `?order=desc&size=7` |
| By reporting period | `period_from`, `period_to` | `?report_period_from=&report_period_to=` |
| All | `limit=-1` | paginate `page=1..N` |

```python
ds.get_stock_reports("600519.SS", limit=7)                                    # latest 7
ds.get_stock_reports("600519.SS", period_from="2023-01-01", period_to="2023-12-31")  # by period
ds.get_stock_reports("600519.SS", limit=-1)                                   # all
```

## Ask an LLM instead

Point any LLM at [datasink.ing](https://datasink.ing), give it your key, and ask in plain language:

- "Which exchanges does this cover?" → `list_exchanges`
- "What stocks are on the Shanghai exchange?" → `list_stocks`
- "List Moutai's annual reports." → `list_reports`
- "Give me document 42." → `get_report`
- "Moutai's 2023 revenue — don't get the unit wrong." → `get_stock_reports`

Full end-to-end prompts: [`llm-examples.md`](llm-examples.md).
