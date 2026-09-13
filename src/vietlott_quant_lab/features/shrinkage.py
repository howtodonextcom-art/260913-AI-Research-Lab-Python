"""Empirical-Bayes / weighted shrinkage toward a long-run prior."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.windows import WindowSpec, slice_window


@dataclass(frozen=True)
class ShrinkageRow:
    number: int
    local_rate: float
    prior_rate: float
    reliability: float
    shrinkage_signal: float


def _fair_rate() -> float:
    return DRAW_SIZE / float(NUMBER_MAX)


def shrinkage_table(
    history: Sequence[DrawRecord],
    *,
    local_window: WindowSpec = 30,
    prior_window: WindowSpec = "ALL",
    prior_strength: float = 50.0,
) -> dict[int, ShrinkageRow]:
    """Shrink local rate toward long-run prior (or fair rate if prior empty).

    ``reliability`` rises with local sample size so short windows cannot dominate.
    """
    local_hist = slice_window(history, local_window)
    prior_hist = slice_window(history, prior_window)

    f_local = frequency_table(local_hist)
    f_prior = frequency_table(prior_hist)
    n_local = len(local_hist)
    fair = _fair_rate()

    # Reliability in (0, 1): more local draws → trust local more, but capped.
    reliability = n_local / (n_local + prior_strength) if (n_local + prior_strength) > 0 else 0.0

    rows: dict[int, ShrinkageRow] = {}
    for number in range(NUMBER_MIN, NUMBER_MAX + 1):
        local_rate = f_local[number].rate
        prior_rate = f_prior[number].rate if len(prior_hist) > 0 else fair
        shrunk = reliability * local_rate + (1.0 - reliability) * prior_rate
        # Signal relative to fair null (descriptive score, not a probability).
        shrinkage_signal = shrunk - fair
        rows[number] = ShrinkageRow(
            number=number,
            local_rate=local_rate,
            prior_rate=prior_rate,
            reliability=reliability,
            shrinkage_signal=shrinkage_signal,
        )
    return rows
