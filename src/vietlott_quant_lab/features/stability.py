"""Stability / volatility features across fixed windows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.recency import gap_map
from vietlott_quant_lab.features.windows import WindowSpec, slice_window

_DEFAULT_STABILITY_WINDOWS: tuple[WindowSpec, ...] = (30, 60, 90, 180)



@dataclass(frozen=True)
class StabilityRow:
    number: int
    freq_volatility: float
    gap_volatility: float
    rank_stability: float
    stability: float


def stability_table(
    history: Sequence[DrawRecord],
    windows: Sequence[WindowSpec] = _DEFAULT_STABILITY_WINDOWS,
) -> dict[int, StabilityRow]:
    rates_by_window: list[dict[int, float]] = []
    for w in windows:
        ft = frequency_table(slice_window(history, w))
        rates_by_window.append({n: ft[n].rate for n in range(NUMBER_MIN, NUMBER_MAX + 1)})

    # Gap volatility: compare gaps on successive half-histories when possible.
    mid = len(history) // 2
    gaps_full = gap_map(history)
    gaps_recent = gap_map(history[mid:] if mid > 0 else history)

    # Rank stability: Spearman-like agreement of frequency ranks across windows.
    ranks_by_window: list[dict[int, int]] = []
    for rate_map in rates_by_window:
        ordered = sorted(rate_map.keys(), key=lambda n: (-rate_map[n], n))
        ranks_by_window.append({n: i + 1 for i, n in enumerate(ordered)})

    rows: dict[int, StabilityRow] = {}
    for number in range(NUMBER_MIN, NUMBER_MAX + 1):
        rate_series = [rw[number] for rw in rates_by_window]
        mean_r = sum(rate_series) / len(rate_series) if rate_series else 0.0
        freq_vol = (
            (sum((r - mean_r) ** 2 for r in rate_series) / len(rate_series)) ** 0.5
            if rate_series
            else 0.0
        )
        gap_vol = abs(float(gaps_full[number] - gaps_recent[number]))
        if len(ranks_by_window) >= 2:
            rank_diffs = [
                abs(ranks_by_window[i][number] - ranks_by_window[i - 1][number])
                for i in range(1, len(ranks_by_window))
            ]
            mean_diff = sum(rank_diffs) / len(rank_diffs)
            rank_stability = 1.0 / (1.0 + mean_diff)
        else:
            rank_stability = 1.0
        # Higher stability = lower volatility + higher rank agreement.
        stability = rank_stability / (1.0 + freq_vol + 0.01 * gap_vol)
        rows[number] = StabilityRow(
            number=number,
            freq_volatility=freq_vol,
            gap_volatility=gap_vol,
            rank_stability=rank_stability,
            stability=stability,
        )
    return rows
