# -*- coding: utf-8 -*-
"""版本号的**唯一来源**。

pyproject.toml 用 `dynamic = ["version"]` 从这里读，`client.py` 的 User-Agent 也读它。

为什么单独抽一个文件：之前 pyproject.toml 和 `__init__.py` 各写各的版本号，
结果 `__version__` 长期停在 0.1.0 没跟上（发 0.2.4 时才发现，User-Agent 里也一直
写着旧版本）。现在只有这一处需要改。
"""

__version__ = "0.2.9"
