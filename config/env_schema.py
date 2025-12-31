# -*- coding: utf-8 -*-
from __future__ import annotations
import os

def as_bool(v, default=False):
    if v is None: return default
    return str(v).lower() in ("1","true","yes","y","on" )

def as_float(name: str, default: float) -> float:
    try: return float(os.getenv(name, default))
    except Exception: return float(default)

def as_int(name: str, default: int) -> int:
    try: return int(os.getenv(name, default))
    except Exception: return int(default)

def validate_required(keys: list[str]) -> list[str]:
    missing = [k for k in keys if not os.getenv(k)]
    return missing







