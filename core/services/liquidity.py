# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
def ensure_min_candles(ohlcv: List[List[float]], min_n: int = 200) -> bool:
    return isinstance(ohlcv, list) and len(ohlcv) >= int(min_n)
