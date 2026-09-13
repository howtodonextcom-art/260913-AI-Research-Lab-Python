"""Mandatory multi-scale lookback windows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from vietlott_quant_lab.config.constants import LOOKBACK_WINDOWS

WindowSpec = int | Literal["ALL"]

MULTI_SCALE_WINDOWS: tuple[WindowSpec, ...] = LOOKBACK_WINDOWS


def resolve_window_size(history_len: int, window: WindowSpec) -> int:
    """Return how many trailing draws a window covers (capped by history length)."""
    if window == "ALL":
        return history_len
    if not isinstance(window, int) or window < 1:
        msg = f"invalid window: {window!r}"
        raise ValueError(msg)
    return min(window, history_len)


def slice_window[T](history: Sequence[T], window: WindowSpec) -> list[T]:
    """Take the trailing ``window`` draws from ``history`` (or all if ``ALL``)."""
    n = resolve_window_size(len(history), window)
    if n == 0:
        return []
    return list(history[-n:])
