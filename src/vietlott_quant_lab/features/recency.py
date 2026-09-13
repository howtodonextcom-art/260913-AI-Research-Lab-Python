"""Recency / gap features from a pre-sliced history."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord


@dataclass(frozen=True)
class RecencyRow:
    number: int
    gap: int
    gap_z: float
    gap_percentile: float


def gap_map(history: Sequence[DrawRecord]) -> dict[int, int]:
    """Draws since last appearance (0 = in most recent draw). Never seen → len(history)."""
    n = len(history)
    gaps = {k: n for k in range(NUMBER_MIN, NUMBER_MAX + 1)}
    for offset, draw in enumerate(reversed(history)):
        for num in draw.numbers:
            key = int(num)
            if gaps[key] == n:
                gaps[key] = offset
    return gaps


def recency_table(history: Sequence[DrawRecord]) -> dict[int, RecencyRow]:
    gaps = gap_map(history)
    values = list(gaps.values())
    mean = sum(values) / len(values) if values else 0.0
    var = sum((g - mean) ** 2 for g in values) / len(values) if values else 0.0
    std = var**0.5
    sorted_gaps = sorted(values)

    rows: dict[int, RecencyRow] = {}
    for number, gap in gaps.items():
        z = (gap - mean) / std if std > 0 else 0.0
        # Empirical CDF percentile in [0, 1].
        rank = sum(1 for g in sorted_gaps if g <= gap)
        pct = rank / len(sorted_gaps) if sorted_gaps else 0.0
        rows[number] = RecencyRow(
            number=number,
            gap=gap,
            gap_z=z,
            gap_percentile=pct,
        )
    return rows
