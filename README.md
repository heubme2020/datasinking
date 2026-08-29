# DataSinking

**Full-text A-share financial reports, as clean Markdown.**

[DataSinking](https://datasink.ing) is a **China stock market data API** that serves
**full-text A-share financial reports** — annual, semi-annual and quarterly — as clean
**Markdown**. Download China A-share financial statements (balance sheet, income statement,
cash flow) by FMP-style symbol (`600519.SS`) or filter by exchange / report period, through a
simple REST API. Raw PDFs are sourced from [cninfo.com.cn](http://www.cninfo.com.cn) (the
officially designated disclosure platform) and parsed into structured Markdown with YAML
frontmatter, preserved headings, paragraphs and tables — ready for LLM reading and analysis.

---

## What this repo is

Examples, research and tutorials showing how to work with financial report data, including reproducing the presentation styles found in financial-report research papers.

```
datasinking/
├── examples/     # Example scripts: pull data from the API and analyze it
├── research/     # Research notes / blog posts (reproducing paper-style presentation)
├── datasinking/  # Python client — pip install datasinking
├── llm-examples.md  # Ask an LLM — no code needed (3 end-to-end examples)
└── README.md
```

## Quick start

1. Get an API key at [datasink.ing](https://datasink.ing)
2. Pull data (FMP-style `?apikey=`):

```bash
# List exchanges
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"

# List all of Kweichow Moutai's reports
curl "https://api.datasink.ing/documents?symbol=600519.SS&apikey=YOUR_KEY"
```

3. Or use the Python client:

```bash
pip install datasinking
```

```python
from datasinking import DataSinking

ds = DataSinking("YOUR_KEY")

# Latest 3 reports of Kweichow Moutai (full markdown content included)
for r in ds.get_stock_reports("600519.SS", limit=3):
    print(r["report_period"], r["title"], len(r["content"]), "chars")
```

## Ask an LLM (no code)

Don't want to write code? Point any LLM at [datasink.ing](https://datasink.ing),
give it your API key, and ask in plain language. See
[`llm-examples.md`](llm-examples.md) for three end-to-end examples — explore
coverage, list a company's reports, and extract a figure with correct units.

## Examples (`examples/`)

| File | What it does |
|---|---|
| `01_quickstart.py` | The 5 core functions: list exchanges / stocks / reports / fetch a report / fetch a stock's reports |
| `02_download_company.py` | Download a company's full reports to local Markdown files |
| `03_download_exchange.py` | Download an entire exchange's reports (all stocks) to local Markdown files |

Every example pulls from the live API and runs as-is.

> `03_download_exchange.py` fetches every report on an exchange (e.g. all of Shenzhen — 130k+ documents). Free keys work too, but fall back to slow per-document fetching (1 req/s + shared daily quota); a **paid (yearly)** key is strongly recommended for full-exchange downloads.

## Research (`research/`)

`research/` hosts research notes and blog posts, each based on DataSinking data with the source cited. You can reproduce charts and presentations found in financial-report research papers, e.g.:

- Long-term revenue / profit trends
- Industry comparison and distribution
- Time series of financial metrics

Start from [`research/TEMPLATE.md`](research/TEMPLATE.md).

## Data overview

| | |
|---|---|
| Coverage | SSE / SZSE / BSE, 5,000+ A-share companies |
| Document types | annual / semiannual / q1 / q3 / amendment |
| Format | Full-text Markdown (with YAML frontmatter) |
| API | REST — `GET /documents`, batch download, `with_content=1` for full text |
| Symbols | FMP style: `600519.SS` / `000001.SZ` / `830799.BJ` |
| Auth | `?apikey=` query parameter (FMP style) |

## Data source

All reports originate from [cninfo.com.cn](http://www.cninfo.com.cn), the officially designated information disclosure platform of China's listed companies.

## License

[MIT](LICENSE)
