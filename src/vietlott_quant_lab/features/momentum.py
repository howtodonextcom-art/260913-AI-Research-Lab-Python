"""Momentum features across multi-scale frequency windows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.windows import slice_window


@dataclass(frozen=True)
class MomentumRow:
    number: int
    momentum_short: float
    momentum_medium: float
    momentum_long: float


def momentum_table(
    history: Sequence[DrawRecord],
    *,
    short: int = 30,
    medium: int = 90,
    long: int = 180,
) -> dict[int, MomentumRow]:
    """Short−medium and medium−long rate divergences (descriptive only)."""
    short_hist = slice_window(history, short)
    medium_hist = slice_window(history, medium)
    long_hist = slice_window(history, long)

    f_s = frequency_table(short_hist)
    f_m = frequency_table(medium_hist)
    f_l = frequency_table(long_hist)

    rows: dict[int, MomentumRow] = {}
    for number in range(NUMBER_MIN, NUMBER_MAX + 1):
        rs = f_s[number].rate
        rm = f_m[number].rate
        rl = f_l[number].rate
        rows[number] = MomentumRow(
            number=number,
            momentum_short=rs - rm,
            momentum_medium=rm - rl,
            momentum_long=rl - (f_l[number].expected / max(len(long_hist), 1)),
        )
    return rows
