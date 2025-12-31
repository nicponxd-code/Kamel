# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as _dt

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

class CandidateStyleFormatter(logging.Formatter):
    """Formatter w stylu services.candidates: krótkie tagi + timestamp + message.

    - Jeśli wiadomość zaczyna się od '[' -> traktujemy ją jako już sformatowaną.
    - W innym wypadku dodajemy prefiks: [<name>] YYYY-MM-DD HH:MM:SS <msg>
    """
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if isinstance(msg, str) and msg.lstrip().startswith("["):
            return msg
        ts = _dt.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        name = (record.name or "app").split(".")[-1]
        return f"[{name}] {ts} {msg}"

def setup_logging() -> None:
    """
    Root -> konsola (LOG_LEVEL, domyślnie INFO) w stylu candidates.
    'pipeline' -> logs/pipeline/YYYYMMDD.log (JSON lines)
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper().strip() or "INFO"
    root = logging.getLogger()
    root.setLevel(level)

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(CandidateStyleFormatter())
        root.addHandler(ch)

    logs_dir = Path(os.getenv("LOGS_DIR", "logs")) / "pipeline"
    try:
        _ensure_dir(logs_dir)
    except Exception:
        return

    plog = logging.getLogger("pipeline")
    plog.propagate = False

    day = _dt.utcnow().strftime("%Y%m%d")
    fname = str(logs_dir / f"{day}.log")

    if not any(isinstance(h, TimedRotatingFileHandler) for h in plog.handlers):
        fh = TimedRotatingFileHandler(
            filename=fname, when="midnight", backupCount=7, utc=True, encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter("%(message)s"))
        fh.setLevel(level)
        plog.addHandler(fh)
        plog.setLevel(level)
