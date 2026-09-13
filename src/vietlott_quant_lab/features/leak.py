"""Anti-leak tripwire for feature / ranking pipelines."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from vietlott_quant_lab.data.schema import DrawRecord


def assert_no_future_leak(history: Sequence[DrawRecord], target_date: date) -> None:
    """Raise if any draw in ``history`` has ``draw_date >= target_date``.

    Callers must cut history strictly before the target (``draw_date < target``).
    This function never silently drops offenders.
    """
    for draw in history:
        if draw.draw_date >= target_date:
            msg = (
                f"Future leak: draw_date {draw.draw_date} >= target_date {target_date}. "
                "History must be sliced strictly before the target."
            )
            raise ValueError(msg)
