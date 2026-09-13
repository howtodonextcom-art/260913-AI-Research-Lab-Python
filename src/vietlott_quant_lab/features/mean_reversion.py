"""Mean-reversion style descriptive features (no causal claim)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.windows import WindowSpec, slice_window


@dataclass(frozen=True)
class MeanReversionRow:
    number: int
    distance_from_long_mean: float
    short_extreme_deviation: float
    mean_reversion_score: float


def mean_reversion_table(
    history: Sequence[DrawRecord],
    *,
    short: int = 30,
    long_window: WindowSpec = "ALL",
) -> dict[int, MeanReversionRow]:
    short_hist = slice_window(history, short)
    long_hist = slice_window(history, long_window)

    f_s = frequency_table(short_hist)
    f_l = frequency_table(long_hist)

    rows: dict[int, MeanReversionRow] = {}
    for number in range(NUMBER_MIN, NUMBER_MAX + 1):
        long_rate = f_l[number].rate
        short_rate = f_s[number].rate
        distance = short_rate - long_rate
        extreme = f_s[number].z_freq
        # Positive score when short is below long-run (classic reversion tilt).
        score = -(distance) - 0.25 * extreme
        rows[number] = MeanReversionRow(
            number=number,
            distance_from_long_mean=distance,
            short_extreme_deviation=extreme,
            mean_reversion_score=score,
        )
    return rows
