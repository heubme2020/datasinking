# -*- coding: utf-8 -*-
"""DataSinking Python client.

Usage:
    from datasinking import DataSinking
    ds = DataSinking("YOUR_API_KEY")
    ds.list_exchanges()
"""
from .client import DataSinking

__version__ = "0.1.0"
__all__ = ["DataSinking"]
