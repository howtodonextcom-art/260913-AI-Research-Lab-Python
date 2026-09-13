"""Model B — multi-scale frequency + gap + momentum + stability + shrinkage."""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.momentum import momentum_table
from vietlott_quant_lab.features.recency import recency_table
from vietlott_quant_lab.features.shrinkage import shrinkage_table
from vietlott_quant_lab.features.stability import stability_table
from vietlott_quant_lab.features.windows import WindowSpec, slice_window
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "multi_scale_shrinkage"

MODEL_B_WINDOWS: tuple[WindowSpec, ...] = (30, 60, 90, 180, 365, "ALL")


def rank_multi_scale_shrinkage(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
) -> RankingResult:
    """Combine multi-scale z-freq, gap, momentum, stability, shrinkage into a score.

    The returned score is a descriptive ranking signal — never a probability.
    """
    z_acc = {n: 0.0 for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    for window in MODEL_B_WINDOWS:
        ft = frequency_table(slice_window(history, window))
        for n in range(NUMBER_MIN, NUMBER_MAX + 1):
            z_acc[n] += ft[n].z_freq
    n_windows = len(MODEL_B_WINDOWS)
    for n in z_acc:
        z_acc[n] /= n_windows

    rec = recency_table(history)
    mom = momentum_table(history)
    stab = stability_table(history)
    sh = shrinkage_table(history, local_window=30, prior_window="ALL")

    scores: dict[int, float] = {}
    for n in range(NUMBER_MIN, NUMBER_MAX + 1):
        gap_term = -0.01 * rec[n].gap
        score = (
            1.0 * z_acc[n]
            + 0.5 * mom[n].momentum_short
            + 0.25 * mom[n].momentum_medium
            + 0.5 * stab[n].stability
            + 2.0 * sh[n].shrinkage_signal
            + gap_term
        )
        scores[n] = score

    return ranking_from_scores(
        scores, model_id=MODEL_ID, seed=seed, higher_is_better=True
    )
