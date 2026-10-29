# datasinking (R client)

R 语言的 DataSinking API 客户端 —— 把上市公司的年报 / 半年报 / 季报全文，转成干净、可按章节取用的 Markdown，给阅读和 RAG 管道用。

## 安装（不经过 CRAN，直接装 GitHub）

```r
install.packages("remotes")                 # 第一次先装 remotes
remotes::install_github("heubme2020/datasinking", subdir = "r-datasinking")
```

> 装完 `library(datasinking)` 即可。不经过 CRAN，直接装 GitHub 上的源码。

## 快速上手

```r
library(datasinking)

ds <- datasinking("你的_api_key")            # 免费 key 在 https://datasink.ing 领取

ds$list_exchanges()                           # 列出交易所代码，如 "szse"
ds$list_stocks("szse")                        # 某交易所的股票清单

ds$list_reports("000006.SZ")                  # 某股票的报告元数据（无全文）
r <- ds$get_report(12345)                     # 单篇报告全文（含 Markdown）

ds$list_sections(12345)                       # 报告的章节标题
s <- ds$get_section(12345, "MD&A")            # 只取某一章（省 token，适合 RAG）

ds$get_stock_reports("000006.SZ", limit = 3)  # 最近 3 篇全文
```

## 主要函数

| 函数 | 说明 |
|---|---|
| `list_exchanges()` | 交易所代码 |
| `list_stocks(exchange)` | 某交易所股票 |
| `list_reports(symbol, doc_type)` | 报告元数据（分页拉全） |
| `get_report(doc_id)` | 单篇全文 |
| `get_stock_reports(symbol, period_from, period_to, limit, doc_type)` | 某股票最近 N 篇全文（`limit=-1` 拉全部）|
| `list_sections(doc_id)` | 报告章节标题 |
| `get_section(doc_id, section)` | 某一章（RAG 友好）|
| `submit_feedback(exchange, stock_code)` | 反馈重转个股 |
| `get_feedback_status(feedback_id)` | 查反馈进度 |

## 依赖

- R >= 3.6
- `httr`、`jsonlite`

## 许可证

MIT
