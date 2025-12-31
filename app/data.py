# app/data.py
# Unified OHLCV access for the rest of the app.
from __future__ import annotations

import logging
from typing import Any, List, Sequence

log = logging.getLogger(__name__)

try:
    # Primary backend in this project
    from services.market.ohlcv import get_ohlcv as _backend_get_ohlcv
except Exception as e:  # pragma: no cover - defensive
    _backend_get_ohlcv = None  # type: ignore[assignment]
    log.warning("services.market.ohlcv.get_ohlcv not available: %s", e)


def get_ohlcv(
    symbol: str,
    tf: str = "1m",
    limit: int = 500,
    only_closed: bool = True,
) -> List[List[float]]:
    """
    Główny punkt dostępu do danych OHLCV dla reszty aplikacji.

    Zwraca listę świec:
        [[ts_ms, open, high, low, close, volume], ...]
    posortowaną rosnąco po ts_ms.

    Jeśli backend zawiedzie – zwraca pustą listę, logując błąd.
    """
    if _backend_get_ohlcv is None:
        log.error("get_ohlcv backend is not available; returning empty series")
        return []

    try:
        rows: Sequence[Sequence[Any]] = _backend_get_ohlcv(
            symbol,
            timeframe=tf,
            limit=limit,
            only_closed=only_closed,
        )
    except TypeError:
        # Sygnatura może się różnić – spróbuj bez only_closed
        try:
            rows = _backend_get_ohlcv(symbol, timeframe=tf, limit=limit)  # type: ignore[call-arg]
        except Exception as e:  # pragma: no cover
            log.exception(
                "get_ohlcv failed (fallback) for %s tf=%s limit=%s: %s",
                symbol,
                tf,
                limit,
                e,
            )
            return []
    except Exception as e:
        log.exception(
            "get_ohlcv failed for %s tf=%s limit=%s only_closed=%s: %s",
            symbol,
            tf,
            limit,
            only_closed,
            e,
        )
        return []

    out: List[List[float]] = []
    for r in rows:
        if not r or len(r) < 6:
            continue
        try:
            ts, o, h, l, c, v = r[:6]
            out.append([int(ts), float(o), float(h), float(l), float(c), float(v)])
        except Exception:
            # pojedyncza świeca uszkodzona – pomijamy, nie zabijamy całości
            continue

    out.sort(key=lambda x: x[0])
    return out
