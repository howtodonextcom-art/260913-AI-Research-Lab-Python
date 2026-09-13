"""Ranking engine — Round 1 baselines + Algorithm V2 challengers + controls.

Scores are ranking signals only — never labeled as probabilities.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.models.all_history import rank_all_history
from vietlott_quant_lab.ranking.models.controls import (
    rank_shuffled_history,
    reverse_peek,
)
from vietlott_quant_lab.ranking.models.ewf import DEFAULT_HALF_LIFE, rank_ewf
from vietlott_quant_lab.ranking.models.hazard import rank_hazard
from vietlott_quant_lab.ranking.models.hot import DEFAULT_LOOKBACK, rank_hot
from vietlott_quant_lab.ranking.models.mean_reversion_rank import rank_mean_reversion
from vietlott_quant_lab.ranking.models.momentum_rank import rank_momentum
from vietlott_quant_lab.ranking.models.multi_scale_shrinkage import rank_multi_scale_shrinkage
from vietlott_quant_lab.ranking.models.multi_scale_v2 import rank_multi_scale_v2
from vietlott_quant_lab.ranking.models.random_rank import rank_random
from vietlott_quant_lab.ranking.types import RankingResult

MODEL_HOT = "hot"
MODEL_MULTI_SCALE_SHRINKAGE = "multi_scale_shrinkage"
MODEL_MULTI_SCALE_V2 = "multi_scale_v2"
MODEL_EWF = "ewf"
MODEL_ALL_HISTORY = "all_history"
MODEL_MOMENTUM = "momentum"
MODEL_MEAN_REVERSION = "mean_reversion"
MODEL_HAZARD = "hazard"
MODEL_RANDOM = "random"
MODEL_REVERSE_PEEK = "reverse_peek"
MODEL_SHUFFLED_HISTORY = "shuffled_history"

ROUND1_MODELS = (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
)

V2_CHALLENGER_MODELS = (
    MODEL_ALL_HISTORY,
    MODEL_EWF,
    MODEL_MULTI_SCALE_V2,
    MODEL_MOMENTUM,
    MODEL_MEAN_REVERSION,
    MODEL_HAZARD,
)


def rank_all(
    history: Sequence[DrawRecord],
    model_id: str,
    *,
    seed: int = 0,
    lookback: int = DEFAULT_LOOKBACK,
    winners: Sequence[int] | None = None,
    half_life: int = DEFAULT_HALF_LIFE,
    weights: Mapping[str, float] | None = None,
    favor_long_gap: bool = True,
    **_: Any,
) -> RankingResult:
    """Rank all numbers 01–45 with the selected model."""
    if model_id == MODEL_HOT:
        return rank_hot(history, lookback=lookback, seed=seed)
    if model_id == MODEL_MULTI_SCALE_SHRINKAGE:
        return rank_multi_scale_shrinkage(history, seed=seed)
    if model_id == MODEL_MULTI_SCALE_V2:
        return rank_multi_scale_v2(history, seed=seed, weights=weights)
    if model_id == MODEL_EWF:
        return rank_ewf(history, half_life=half_life, seed=seed)
    if model_id == MODEL_ALL_HISTORY:
        return rank_all_history(history, seed=seed)
    if model_id == MODEL_MOMENTUM:
        return rank_momentum(history, seed=seed)
    if model_id == MODEL_MEAN_REVERSION:
        return rank_mean_reversion(history, seed=seed)
    if model_id == MODEL_HAZARD:
        return rank_hazard(history, seed=seed, favor_long_gap=favor_long_gap)
    if model_id == MODEL_RANDOM:
        return rank_random(history, seed=seed)
    if model_id == MODEL_REVERSE_PEEK:
        if winners is None:
            msg = "reverse_peek requires winners="
            raise ValueError(msg)
        return reverse_peek(winners, seed=seed)
    if model_id == MODEL_SHUFFLED_HISTORY:
        return rank_shuffled_history(list(history), seed=seed, lookback=lookback)

    msg = f"unknown model_id: {model_id!r}"
    raise ValueError(msg)
