# 文章标题

> 一句话摘要：这篇文章研究什么、得出什么结论。

- **日期**：2026-XX-XX
- **数据**：DataSinking（A 股财报 Markdown API）
- **相关论文**：（可选，标注你在复现/借鉴哪篇论文的呈现方式）

---

## 背景

为什么研究这个问题。可以复现某篇论文里的一个问题/图表，说明它与原论文的关系。

## 数据

数据来源、覆盖范围、怎么用 DataSinking 获取：

```python
from sdk.finreport import FinReport
fr = FinReport("YOUR_KEY")
# 拉取分析所需的数据
reports = fr.get_symbol_reports(symbol="600519.SS", all=True)
```

数据范围：覆盖沪深北三交易所、年报/半年报/季报/修订公告，Markdown 全文。

## 方法

分析步骤、指标定义、代码逻辑。可以贴关键代码块：

```python
# 示例：从 markdown 正文提取关键财务指标
import re
def extract_metric(content, pattern):
    m = re.search(pattern, content)
    return m.group(1) if m else None
```

## 结果

图表的呈现（这里放生成的图，或描述图表）。配合文字解读。

## 结论

核心发现、局限、后续可以做什么。

---

## 数据引用

> 本文数据来自 [DataSinking](https://datasink.ing)（A 股财报 Markdown API），原始财报源自[巨潮资讯网](http://www.cninfo.com.cn)。
