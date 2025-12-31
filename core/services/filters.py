
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
from typing import List, Dict
from services.utils.percentiles import percentile

def adapt_threshold(rows: List[Dict]) -> float:
    if not isinstance(rows, list) or not rows:
        return 0.0
    qs = float(os.getenv("CODEV2_SELECT_Q", "0.60"))
    floor = float(os.getenv("CODEV2_SELECT_FLOOR", "0.50"))
    cap   = float(os.getenv("CODEV2_SELECT_CAP", "0.80"))
    probs = []
    for r in rows:
        try:
            probs.append(float(r.get("prob", 0.0)))
        except Exception:
            continue
    if not probs:
        return floor
    qv = percentile(probs, qs)
    return max(floor, min(cap, qv))

def select(rows: List[Dict]) -> List[Dict]:
    thr = adapt_threshold(rows)
    # jeśli wszystko poniżej, wybierz top-k wg prob, gdzie k = max(1, len*0.05)
    selected = [r for r in rows if isinstance(r, dict) and float(r.get("prob", 0.0)) >= thr]
    if selected:
        return selected
    k = max(1, int(len(rows) * float(os.getenv("CODEV2_SELECT_MIN_FRAC", "0.05"))))
    rows = sorted([r for r in rows if isinstance(r, dict)], key=lambda r: float(r.get("prob", 0.0)), reverse=True)
    return rows[:k]
