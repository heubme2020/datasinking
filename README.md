# DataSinking

**A-share financial reports, as clean Markdown.**

[DataSinking](https://datasink.ing) 提供中国 A 股（沪深北）上市公司财报的 **Markdown 全文**，通过一个简单的 REST API 获取。原始 PDF 来自巨潮资讯网（cninfo.com.cn，证监会指定披露平台），被解析成带 frontmatter、保留标题/段落/表格的结构化 Markdown，直接适合 LLM 阅读和分析。

---

## 这个仓库是什么

这里是 DataSinking 的**示例、研究与教程**，用来演示「怎么用财报数据做分析」，同时复现财报分析相关论文里的呈现方式。

```
datasinking/
├── examples/     # 用 API 拉数据做分析的示例代码
├── research/     # 研究笔记 / 博文（复现论文呈现）
├── sdk/          # Python 客户端库（开箱即用）
└── README.md
```

## 快速开始

1. 去 [datasink.ing](https://datasink.ing) 获取 API key
2. 拉数据（FMP 风格 `?apikey=`）：

```bash
# 列出交易所
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"

# 查茅台的所有财报
curl "https://api.datasink.ing/documents?symbol=600519.SS&apikey=YOUR_KEY"
```

3. 或用 Python SDK：

```python
from sdk.finreport import FinReport

fr = FinReport("YOUR_KEY")

# 拉茅台最近 3 篇（含完整 markdown 正文）
reports = fr.get_symbol_reports(symbol="600519.SS", limit=3)
for r in reports:
    print(r["report_period"], r["title"], len(r["content"]), "字")
```

## 示例（examples/）

| 文件 | 内容 |
|---|---|
| `01_quickstart.py` | 入门：列交易所 / 列股票 / 查报告列表 |
| `02_download_company.py` | 下载某家公司全部财报到本地 Markdown |

每个示例都从真实 API 拉数据，可直接运行。

## 研究（research/）

`research/` 用于发布研究笔记和博文，每篇都基于 DataSinking 的数据，并标注数据来源。可以复现财报分析相关论文里的图表与呈现方式，例如：

- 营收 / 利润的长期趋势
- 行业对比与分布
- 财务指标的时间序列

新文章模板见 [`research/TEMPLATE.md`](research/TEMPLATE.md)。

## 数据说明

| 项 | 说明 |
|---|---|
| 覆盖 | 沪深北三交易所，5,000+ 家 A 股公司 |
| 文档类型 | 年报 / 半年报 / 一季报 / 三季报 / 修订公告 |
| 格式 | Markdown（含 YAML frontmatter） |
| symbol | FMP 风格：`600519.SS` / `000001.SZ` / `830799.BJ` |
| 鉴权 | `?apikey=` 查询参数（FMP 风格） |

## 数据来源

所有财报原文来自 [巨潮资讯网](http://www.cninfo.com.cn)（中国证监会指定的上市公司信息披露平台）。

## License

[MIT](LICENSE)
