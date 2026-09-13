"""Model E — Multi-Scale Shrinkage V2 with per-feature z-normalization.

Normalization at target t uses only history available before t (cross-sectional
z-scores across the 45 numbers at that cutoff — no future/global params).

Weights are pre-registered (not Test-tuned). Development may select among a
small discrete family; the default below is the registered starting point.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.mean_reversion import mean_reversion_table
from vietlott_quant_lab.features.momentum import momentum_table
from vietlott_quant_lab.features.recency import recency_table
from vietlott_quant_lab.features.shrinkage import shrinkage_table
from vietlott_quant_lab.features.stability import stability_table
from vietlott_quant_lab.features.windows import WindowSpec, slice_window
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "multi_scale_v2"

MODEL_V2_WINDOWS: tuple[WindowSpec, ...] = (30, 60, 90, 180, 365, "ALL")

# Pre-registered weight vector (Development-selectable family key "default").
DEFAULT_WEIGHTS: dict[str, float] = {
    "z_freq": 1.0,
    "momentum_short": 0.5,
    "momentum_medium": 0.25,
    "stability": 0.5,
    "shrinkage": 2.0,
    "gap": -0.25,  # applied to cross-sectional z(gap); negative = favor recent
    "mean_reversion": 0.0,  # off by default so momentum/reversion stay separate
}


def _cross_sectional_z(values: Mapping[int, float]) -> dict[int, float]:
    nums = list(range(NUMBER_MIN, NUMBER_MAX + 1))
    arr = [float(values[n]) for n in nums]
    mean = sum(arr) / len(arr)
    var = sum((x - mean) ** 2 for x in arr) / len(arr)
    std = var**0.5
    if std <= 1e-15:
        return {n: 0.0 for n in nums}
    return {n: (float(values[n]) - mean) / std for n in nums}


def rank_multi_scale_v2(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
    weights: Mapping[str, float] | None = None,
) -> RankingResult:
    """Normalized multi-scale ranking signal — never a calibrated probability."""
    w = dict(DEFAULT_WEIGHTS if weights is None else weights)

    z_acc = {n: 0.0 for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    for window in MODEL_V2_WINDOWS:
        ft = frequency_table(slice_window(history, window))
        for n in range(NUMBER_MIN, NUMBER_MAX + 1):
            z_acc[n] += ft[n].z_freq
    n_windows = len(MODEL_V2_WINDOWS)
    for n in z_acc:
        z_acc[n] /= n_windows
    z_freq = _cross_sectional_z(z_acc)

    rec = recency_table(history)
    gap_z = _cross_sectional_z({n: float(rec[n].gap) for n in range(NUMBER_MIN, NUMBER_MAX + 1)})
    mom = momentum_table(history)
    mom_s = _cross_sectional_z(
        {n: mom[n].momentum_short for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    )
    mom_m = _cross_sectional_z(
        {n: mom[n].momentum_medium for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    )
    stab = stability_table(history)
    stab_z = _cross_sectional_z(
        {n: stab[n].stability for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    )
    sh = shrinkage_table(history, local_window=30, prior_window="ALL")
    sh_z = _cross_sectional_z(
        {n: sh[n].shrinkage_signal for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    )
    mr = mean_reversion_table(history)
    mr_z = _cross_sectional_z(
        {n: mr[n].mean_reversion_score for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    )

    scores: dict[int, float] = {}
    for n in range(NUMBER_MIN, NUMBER_MAX + 1):
        scores[n] = (
            w.get("z_freq", 0.0) * z_freq[n]
            + w.get("momentum_short", 0.0) * mom_s[n]
            + w.get("momentum_medium", 0.0) * mom_m[n]
            + w.get("stability", 0.0) * stab_z[n]
            + w.get("shrinkage", 0.0) * sh_z[n]
            + w.get("gap", 0.0) * gap_z[n]
            + w.get("mean_reversion", 0.0) * mr_z[n]
        )
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
