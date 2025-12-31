# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os
from typing import Iterable

log = logging.getLogger(__name__)


_TRUE = ("1", "true", "yes", "on", "y")
_FALSE = ("0", "false", "no", "off", "n")


def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    return default


def _strip_quotes(v: str | None) -> str | None:
    if v is None:
        return None
    s = v.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        s = s[1:-1].strip()
    return s or None


def _exchange_env_prefix(exchange: str) -> str:
    # Accept values such as: binance, binance_futures, BINANCE-FUTURES, etc.
    ex = (exchange or "").strip().lower().replace("-", "_")
    base = ex.split("_", 1)[0] or "binance"
    return base.upper()


def _map_exchange_keys() -> None:
    """Map exchange-specific env vars into canonical TRADE_* vars.

    Canonical:
      - TRADE_EXCHANGE
      - TRADE_API_KEY
      - TRADE_API_SECRET
      - TRADE_API_PASS (optional; e.g., Coinbase / OKX style)

    Supported inputs (examples):
      - BINANCE_API_KEY / BINANCE_API_SECRET
      - KRAKEN_API_KEY / KRAKEN_API_SECRET
      - COINBASE_API_KEY / COINBASE_API_SECRET / COINBASE_API_PASSPHRASE
      - TRADE_API_KEY / TRADE_API_SECRET / TRADE_API_PASS (already canonical)

    Note: We *do not* infer secrets when they are missing; we only map/normalize names.
    """
    ex = os.getenv("TRADE_EXCHANGE") or os.getenv("DATA_EXCHANGE") or "binance"
    prefix = _exchange_env_prefix(ex)

    # If the user provided exchange keys with quotes (common in .env), normalize them.
    key = _strip_quotes(os.getenv("TRADE_API_KEY") or os.getenv(f"{prefix}_API_KEY"))
    sec = _strip_quotes(os.getenv("TRADE_API_SECRET") or os.getenv(f"{prefix}_API_SECRET"))
    pas = _strip_quotes(
        os.getenv("TRADE_API_PASS")
        or os.getenv(f"{prefix}_API_PASS")
        or os.getenv(f"{prefix}_API_PASSPHRASE")
    )

    # Ensure TRADE_EXCHANGE is set (keeps original casing choices out of downstream code).
    os.environ.setdefault("TRADE_EXCHANGE", str(ex).strip().lower())

    if key:
        os.environ["TRADE_API_KEY"] = key
    if sec:
        os.environ["TRADE_API_SECRET"] = sec
    if pas:
        os.environ["TRADE_API_PASS"] = pas


def _missing(required: Iterable[str]) -> list[str]:
    return [k for k in required if not _strip_quotes(os.getenv(k))]


def load_and_validate() -> None:
    """Load derived env vars and enforce minimum configuration.

    Behavior:
      - Always maps exchange-specific keys into TRADE_*.
      - In MODE=live, missing trading credentials is a hard error (SystemExit).
      - In MODE=paper/backtest, only logs warnings.

    This keeps failures explicit and prevents accidental "live" start without secrets.
    """
    _map_exchange_keys()

    mode = (os.getenv("MODE") or "paper").strip().lower()
    if mode not in {"paper", "live", "backtest"}:
        log.warning("Unknown MODE=%r (expected paper/live/backtest). Using %r.", mode, mode)

    if mode == "live":
        miss = _missing(("TRADE_EXCHANGE", "TRADE_API_KEY", "TRADE_API_SECRET"))
        if miss:
            # Hard-fail: live mode without credentials should never continue.
            msg = f"Missing required LIVE env vars: {', '.join(miss)}"
            log.error(msg)
            raise SystemExit(2)

        # Extra guardrails (optional but helpful)
        if env_bool("DRY_RUN", False):
            log.warning("MODE=live with DRY_RUN=1: orders should not be placed, verify configuration.")

    else:
        miss = _missing(("TRADE_EXCHANGE",))
        if miss:
            log.warning("Missing TRADE_EXCHANGE; default mapping will assume 'binance'.")
