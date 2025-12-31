
# -*- coding: utf-8 -*-
import logging, logging.handlers, os, sys, json, time, pathlib

def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> None:
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root = logging.getLogger()
    root.setLevel(level)
    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    ch.setLevel(level)
    root.addHandler(ch)
    # Rotating file
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(level)
    root.addHandler(fh)

if __name__ == "__main__":
    setup_logging()
    logging.getLogger(__name__).info("Logging initialized.")







