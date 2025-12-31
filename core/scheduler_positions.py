# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import discord

log = logging.getLogger("scheduler_positions")
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# --- projektowe zależności, defensywnie ---
try:
    from providers.orders.router import list_positions, close_position  # noqa: F401
except Exception:
    list_positions = None  # type: ignore
    close_position = None  # type: ignore

try:
    from providers.price_router import fetch_ticker_unified  # noqa: F401
except Exception:
    fetch_ticker_unified = None  # type: ignore


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default

def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name, str(int(default))).strip().lower()
    return v in ("1", "true", "yes", "y", "on")

POS_EVERY_S         = _env_int("POS_EVERY_S", 30)           # co ile sekund monitoring pozycji
ALERT_CHANNEL_ID    = _env_int("DISCORD_ALERT_CHANNEL", 0)  # kanał alertów
PIPE_CHANNEL_ID     = _env_int("PIPE_CHANNEL_ID", 0)        # kanał z logami pozycji
TRAILING_ENABLE     = _env_bool("TRAILING_ENABLE", True)
TRAILING_ATR_K      = float(os.getenv("TRAILING_ATR_K", "1.5") or "1.5")

async def _send_discord(bot: discord.Client, channel_id: int, content: str) -> None:
    if not channel_id:
        return
    try:
        ch = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
        if ch:
            await ch.send(content=content)
    except Exception as e:
        log.warning("send_discord failed: %s", e)

def _price(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _fmt_pos(p: Dict[str, Any]) -> str:
    sym = p.get("symbol") or p.get("ticker")
    side = p.get("side") or p.get("dir")
    qty  = p.get("qty") or p.get("size")
    ep   = _price(p.get("entry_price") or p.get("ep"))
    sl   = p.get("sl")
    tp   = p.get("tp")
    pnl  = _price(p.get("pnl"))
    return f"{sym} {side} qty={qty} EP={ep} SL={sl} TP={tp} PnL={pnl}"

async def _fetch_price(symbol: str) -> Optional[float]:
    if fetch_ticker_unified is None:
        return None
    try:
        tick = await fetch_ticker_unified(symbol)
        if isinstance(tick, dict):
            for k in ("last", "price", "close"):
                if k in tick:
                    return _price(tick[k], None)  # type: ignore[arg-type]
    except Exception as e:
        log.debug("fetch price failed for %s: %s", symbol, e)
    return None

class PositionsMonitor:
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self._task: Optional[asyncio.Task] = None
        self._stopping = asyncio.Event()

    def start(self) -> None:
        if self._task and not self._task.done():
            log.info("positions scheduler already running")
            return
        self._task = asyncio.create_task(self._runner(), name="positions-scheduler")
        log.info("positions scheduler started")

    async def stop(self) -> None:
        self._stopping.set()
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        log.info("positions scheduler stopped")

    async def _runner(self) -> None:
        backoff = 3
        while not self._stopping.is_set():
            t0 = time.time()
            try:
                await self._cycle()
                backoff = 3
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.exception("positions loop error: %s", e)
                await _send_discord(self.bot, ALERT_CHANNEL_ID, f"ALERT positions: `{e}`")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            dt = max(0.0, POS_EVERY_S - (time.time() - t0))
            await asyncio.sleep(dt)

    async def _cycle(self) -> None:
        if list_positions is None:
            return
        pos_list = await self._safe_list_positions()
        if not pos_list:
            return

        for p in pos_list:
            await self._handle_position(p)

    async def _safe_list_positions(self) -> List[Dict[str, Any]]:
        try:
            res = list_positions()  # może być sync/async
            if asyncio.iscoroutine(res):
                res = await res  # type: ignore[assignment]
            if not isinstance(res, list):
                return []
            return [x for x in res if isinstance(x, dict)]
        except Exception as e:
            log.debug("list_positions error: %s", e)
            return []

    async def _handle_position(self, p: Dict[str, Any]) -> None:
        symbol = str(p.get("symbol") or p.get("ticker") or "")
        if not symbol:
            return

        last = await _fetch_price(symbol)
        if last is None:
            return

        side = str(p.get("side") or p.get("dir") or "").upper()
        sl   = p.get("sl")
        tp   = p.get("tp")

        # SL / TP check
        closed_reason = None
        if tp and ((side == "LONG" and last >= _price(tp)) or (side == "SHORT" and last <= _price(tp))):
            closed_reason = "TP"
        if not closed_reason and sl and ((side == "LONG" and last <= _price(sl)) or (side == "SHORT" and last >= _price(sl))):
            closed_reason = "SL"

        if closed_reason and close_position is not None:
            try:
                r = close_position(p)  # projektowy router zamknięcia
                if asyncio.iscoroutine(r):
                    await r
                await _send_discord(self.bot, PIPE_CHANNEL_ID, f"**Close {closed_reason}**: {_fmt_pos(p)}  last={last}")
            except Exception as e:
                await _send_discord(self.bot, ALERT_CHANNEL_ID, f"ALERT close {closed_reason} failed: {e}")
            return

        # Trailing SL (opcjonalnie)
        if TRAILING_ENABLE:
            await self._maybe_trail_sl(p, last)

    async def _maybe_trail_sl(self, p: Dict[str, Any], last: float) -> None:
        """
        Prosty trailing: jeśli cena odjechała o X*ATR od EP w kierunku zysku,
        podciągnij SL do (last -/+ K*ATR). Wymaga by w pozycji był 'atr' / 'ep'.
        """
        side = str(p.get("side") or p.get("dir") or "").upper()
        ep   = _price(p.get("entry_price") or p.get("ep"))
        atr  = _price(p.get("atr") or 0.0)
        if atr <= 0.0 or ep <= 0.0:
            return

        desired = None
        if side == "LONG" and last > ep:
            desired = max(_price(p.get("sl") or 0.0), last - TRAILING_ATR_K * atr)
        elif side == "SHORT" and last < ep:
            desired = min(_price(p.get("sl") or 10**18), last + TRAILING_ATR_K * atr)

        if desired is None:
            return

        # Jeśli nowy SL faktycznie poprawia ochronę – ustaw
        cur_sl = _price(p.get("sl"), 0.0)
        do_update = (side == "LONG" and desired > cur_sl) or (side == "SHORT" and (cur_sl == 0.0 or desired < cur_sl))
        if not do_update:
            return

        # Zakładamy istnienie projektu funkcji: close_position(..., update_only=True, sl=...)
        if close_position is None:
            return
        try:
            r = close_position(p, update_only=True, sl=desired)  # type: ignore[call-arg]
            if asyncio.iscoroutine(r):
                await r
            await _send_discord(self.bot, PIPE_CHANNEL_ID, f"**Trailing SL**: {_fmt_pos(p)}  new_SL={desired}  last={last}")
        except Exception as e:
            await _send_discord(self.bot, ALERT_CHANNEL_ID, f"ALERT trailing failed: {e}")


# ====== API do wpięcia w bota ================================================

import contextlib

_positions_singleton: Optional[PositionsMonitor] = None

def attach(bot: discord.Client) -> None:
    global _positions_singleton
    if _positions_singleton is None:
        _positions_singleton = PositionsMonitor(bot)
    _positions_singleton.start()
    log.info("positions scheduler attached")

async def detach() -> None:
    global _positions_singleton
    if _positions_singleton:
        await _positions_singleton.stop()
        _positions_singleton = None







