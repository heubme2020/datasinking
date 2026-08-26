# Title

> One-sentence summary: what this note studies and what it concludes.

- **Date**: 2026-XX-XX
- **Data**: DataSinking (A-share financial reports Markdown API)
- **Related paper**: (optional) note which paper's presentation you reproduce / adapt

---

## Background

Why this question matters. You may reproduce a question or a chart from an existing paper, and state the relationship to it.

## Data

Source, coverage, and how to fetch it with DataSinking:

```python
from sdk.datasinking import DataSinking
ds = DataSinking("YOUR_KEY")
reports = ds.get_symbol_reports(symbol="600519.SS", all=True)
```

Coverage: SSE / SZSE / BSE, annual / semiannual / quarterly / amendment reports, full Markdown.

## Method

Analysis steps, metric definitions, and code logic. Include key code blocks:

```python
# Example: extract a key financial metric from markdown content
import re
def extract_metric(content, pattern):
    m = re.search(pattern, content)
    return m.group(1) if m else None
```

## Results

Charts (generated figures or descriptions) together with the interpretation.

## Conclusion

Key findings, limitations, and what could be done next.

---

## Data citation

> Data in this note comes from [DataSinking](https://datasink.ing) (A-share financial reports Markdown API); the original reports originate from [cninfo.com.cn](http://www.cninfo.com.cn).
