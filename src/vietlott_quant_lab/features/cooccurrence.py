"""Pair co-occurrence features normalized to fair null expectation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord


@dataclass(frozen=True)
class PairStats:
    a: int
    b: int
    count: int
    expected: float
    lift: float
    residual: float


@dataclass(frozen=True)
class CooccurrenceRow:
    number: int
    pair_signal: float
    mean_lift: float
    mean_residual: float


def _pair_null_p() -> float:
    """P(both a and b appear in one fair 6/45 draw) = C(43,4)/C(45,6)."""
    from math import comb

    return comb(NUMBER_MAX - 2, DRAW_SIZE - 2) / comb(NUMBER_MAX, DRAW_SIZE)


def pair_table(history: Sequence[DrawRecord]) -> dict[tuple[int, int], PairStats]:
    n = len(history)
    counts: dict[tuple[int, int], int] = {}
    for draw in history:
        nums = sorted(int(x) for x in draw.numbers)
        for a, b in combinations(nums, 2):
            counts[(a, b)] = counts.get((a, b), 0) + 1

    p = _pair_null_p()
    expected = n * p
    out: dict[tuple[int, int], PairStats] = {}
    for a in range(NUMBER_MIN, NUMBER_MAX + 1):
        for b in range(a + 1, NUMBER_MAX + 1):
            c = counts.get((a, b), 0)
            lift = (c / expected) if expected > 0 else 0.0
            residual = c - expected
            out[(a, b)] = PairStats(
                a=a, b=b, count=c, expected=expected, lift=lift, residual=residual
            )
    return out


def cooccurrence_table(history: Sequence[DrawRecord]) -> dict[int, CooccurrenceRow]:
    """Per-number pair signal = mean residual of pairs involving the number."""
    pairs = pair_table(history)
    rows: dict[int, CooccurrenceRow] = {}
    for number in range(NUMBER_MIN, NUMBER_MAX + 1):
        related = [
            stats
            for (a, b), stats in pairs.items()
            if a == number or b == number
        ]
        if not related:
            rows[number] = CooccurrenceRow(
                number=number, pair_signal=0.0, mean_lift=0.0, mean_residual=0.0
            )
            continue
        mean_lift = sum(p.lift for p in related) / len(related)
        mean_residual = sum(p.residual for p in related) / len(related)
        # Normalized residual (not raw count) as the descriptive pair signal.
        pair_signal = mean_residual
        rows[number] = CooccurrenceRow(
            number=number,
            pair_signal=pair_signal,
            mean_lift=mean_lift,
            mean_residual=mean_residual,
        )
    return rows
