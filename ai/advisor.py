# -*- coding: utf-8 -*-
"""
Stub polityki RL dla modułu candidates.
Uzupełnij rl_policy_decide(state, base), żeby wpiąć wyuczony model π(a|s).
"""
from __future__ import annotations
from typing import Dict


def rl_policy_decide(state: Dict[str, float], base: str) -> str:
    """
    Domyślna polityka: nic nie zmienia, zwraca decyzję bazową.
    - state: spłaszczone cechy (whales, atr, trend, imbalance, itd.)
    - base: decyzja bazowa z candidates._verdict (ENTER/WAIT/SKIP)
    """
    return base
