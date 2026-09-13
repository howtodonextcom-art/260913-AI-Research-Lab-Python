"""Per-number frequency features from a pre-sliced history."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord


@dataclass(frozen=True)
class FrequencyRow:
    number: int
    count: int
    expected: float
    rate: float
    z_freq: float


def _fair_p() -> float:
    return DRAW_SIZE / float(NUMBER_MAX)


def frequency_table(history: Sequence[DrawRecord]) -> dict[int, FrequencyRow]:
    """Count appearances of each number 01–45 in ``history`` only."""
    n = len(history)
    counts = {k: 0 for k in range(NUMBER_MIN, NUMBER_MAX + 1)}
    for draw in history:
        for num in draw.numbers:
            counts[int(num)] += 1

    p = _fair_p()
    expected = n * p
    # Binomial variance under independent fair draws.
    var = n * p * (1.0 - p) if n > 0 else 0.0
    std = var**0.5

    rows: dict[int, FrequencyRow] = {}
    for number, count in counts.items():
        rate = count / n if n > 0 else 0.0
        z = (count - expected) / std if std > 0 else 0.0
        rows[number] = FrequencyRow(
            number=number,
            count=count,
            expected=expected,
            rate=rate,
            z_freq=z,
        )
    return rows


def count_map(history: Sequence[DrawRecord]) -> dict[int, int]:
    return {n: frequency_table(history)[n].count for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
