"""Deterministic per-number feature vectors from a pre-sliced history."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.cooccurrence import cooccurrence_table
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.leak import assert_no_future_leak
from vietlott_quant_lab.features.mean_reversion import mean_reversion_table
from vietlott_quant_lab.features.momentum import momentum_table
from vietlott_quant_lab.features.recency import recency_table
from vietlott_quant_lab.features.shrinkage import shrinkage_table
from vietlott_quant_lab.features.stability import stability_table
from vietlott_quant_lab.features.windows import MULTI_SCALE_WINDOWS, WindowSpec, slice_window

FREQ_WINDOWS: tuple[WindowSpec, ...] = MULTI_SCALE_WINDOWS


@dataclass(frozen=True)
class NumberFeatureVector:
    """Descriptive feature bundle for one ball. Scores are not probabilities."""

    number: int
    history_size: int
    freq: dict[str, float]
    z_freq: dict[str, float]
    gap: int
    gap_z: float
    gap_percentile: float
    momentum_short: float
    momentum_medium: float
    mean_reversion_score: float
    stability: float
    pair_signal: float
    shrinkage_signal: float


def _window_key(window: WindowSpec) -> str:
    return "ALL" if window == "ALL" else str(window)


def build_feature_vector(
    history: Sequence[DrawRecord],
    number: int,
    *,
    target_date: date | None = None,
) -> NumberFeatureVector:
    """Build features for ``number`` using only the provided history slice.

    If ``target_date`` is given, runs the leak tripwire first.
    """
    if not (NUMBER_MIN <= number <= NUMBER_MAX):
        msg = f"number out of range: {number}"
        raise ValueError(msg)
    if target_date is not None:
        assert_no_future_leak(history, target_date)

    freq: dict[str, float] = {}
    z_freq: dict[str, float] = {}
    for window in FREQ_WINDOWS:
        key = _window_key(window)
        ft = frequency_table(slice_window(history, window))
        freq[key] = ft[number].rate
        z_freq[key] = ft[number].z_freq

    rec = recency_table(history)[number]
    mom = momentum_table(history)[number]
    mr = mean_reversion_table(history)[number]
    stab = stability_table(history)[number]
    co = cooccurrence_table(history)[number]
    sh = shrinkage_table(history)[number]

    return NumberFeatureVector(
        number=number,
        history_size=len(history),
        freq=freq,
        z_freq=z_freq,
        gap=rec.gap,
        gap_z=rec.gap_z,
        gap_percentile=rec.gap_percentile,
        momentum_short=mom.momentum_short,
        momentum_medium=mom.momentum_medium,
        mean_reversion_score=mr.mean_reversion_score,
        stability=stab.stability,
        pair_signal=co.pair_signal,
        shrinkage_signal=sh.shrinkage_signal,
    )


def build_all_feature_vectors(
    history: Sequence[DrawRecord],
    *,
    target_date: date | None = None,
) -> dict[int, NumberFeatureVector]:
    """Deterministic feature map for numbers 01–45."""
    if target_date is not None:
        assert_no_future_leak(history, target_date)
    return {
        n: build_feature_vector(history, n, target_date=None)
        for n in range(NUMBER_MIN, NUMBER_MAX + 1)
    }
