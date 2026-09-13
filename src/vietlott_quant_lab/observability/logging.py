"""Structured logging helper."""

from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str, *, level: str | int | None = None) -> logging.Logger:
    """Return a module logger with a simple structured format.

    Idempotent: attaching handlers only when the logger has none yet.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.propagate = False

    if level is not None:
        logger.setLevel(level if isinstance(level, int) else getattr(logging, level.upper()))
    elif logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)

    return logger


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Log a key=value style event line for later grepping."""
    parts = [f"event={event}"]
    for key, value in fields.items():
        parts.append(f"{key}={value!r}")
    logger.info(" ".join(parts))
