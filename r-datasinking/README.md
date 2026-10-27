# datasinking

An R client for the [DataSinking](https://datasink.ing) API — full-text
financial reports (annual, semi-annual and quarterly filings across the US,
UK, China, Japan, Korea, Taiwan and more) as clean, section-addressable
Markdown.

## Installation

The package is on CRAN:

```r
install.packages("datasinking")
```

## Setup

Get an API key at <https://datasink.ing>, then set it once per session:

```r
library(datasinking)
ds_set_key("your-api-key")
```

## Usage

```r
# Exchanges served by the API
ds_exchanges()

# Stocks on an exchange
ds_stocks("szse")

# Search documents for a company (FMP-style ticker)
ds_documents(symbol = "600519.SS", doc_type = "annual")

# Full text of one report (Markdown in $content)
doc <- ds_report(id = 123456)
cat(doc$content)

# Just the MD&A section
mdna <- ds_report(id = 123456, section = "MD&A")

# List a report's sections
ds_sections(123456)

# Batch-fetch up to 31 documents
ds_batch(c(123456, 123457, 123458))
```

## Return shapes

- `ds_exchanges()`, `ds_sections()` → character vector
- `ds_stocks()`, `ds_documents()` → data.frame
- `ds_report(id)` → list (metadata + `content`); `ds_report(id, section = "…")` → character
- `ds_batch()` → list (`count`, `missing`, `items`)

## Rate limits

The free tier is 3 requests/sec and ~8,000 reports/week; the yearly tier
($31/year) is 31 requests/sec and 524,287 reports/week. See
<https://datasink.ing> for details and upgrade options.
