# datasinking (R client)

An R client for the DataSinking API — full-text financial reports (annual, semi-annual
and quarterly filings) as clean, section-addressable Markdown, for reading and RAG pipelines.

## Install (GitHub, no CRAN)

```r
install.packages("remotes")                 # first time only
remotes::install_github("heubme2020/datasinking", subdir = "r-datasinking")
```

Then `library(datasinking)`.

## Quick start

```r
library(datasinking)

ds <- datasinking("YOUR_API_KEY")            # free key at https://datasink.ing

ds$list_exchanges()                          # exchange codes, e.g. "szse"
ds$list_stocks("szse")                       # stocks on one exchange

ds$list_reports("000006.SZ")                 # report metadata for a symbol (no full text)
r <- ds$get_report(12345)                    # one report's full record (incl. Markdown body)

ds$list_sections(12345)                      # section headings of a report
s <- ds$get_section(12345, "MD&A")           # one section only (cheap, RAG-friendly)

ds$get_stock_reports("000006.SZ", limit = 3) # latest 3 full reports
```

## Functions

| Function | Description |
|---|---|
| `list_exchanges()` | Exchange codes |
| `list_stocks(exchange)` | Stocks on one exchange |
| `list_reports(symbol, doc_type)` | Report metadata (paginated) |
| `get_report(doc_id)` | One report's full record |
| `get_stock_reports(symbol, period_from, period_to, limit, doc_type)` | Latest N full reports (`limit = -1` = all) |
| `list_sections(doc_id)` | Section headings |
| `get_section(doc_id, section)` | One section (RAG-friendly) |
| `submit_feedback(exchange, stock_code)` | Queue a re-parse |
| `get_feedback_status(feedback_id)` | Poll a feedback job |

## Dependencies

- R >= 3.6
- `httr`, `jsonlite`

## License

MIT
