"""Structured logging for the supply-chain analytics pipeline."""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional


_CONFIGURED = False


def setup_logging(level: Optional[str] = None) -> None:
    """Configure root logging once. Subsequent calls only adjust the level."""
    global _CONFIGURED
    resolved = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    numeric = getattr(logging, resolved, logging.INFO)

    if _CONFIGURED:
        logging.getLogger().setLevel(numeric)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(numeric)
    root.handlers.clear()
    root.addHandler(handler)
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    logging.getLogger("prophet").setLevel(logging.WARNING)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)
