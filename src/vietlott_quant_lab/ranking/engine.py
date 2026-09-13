"""Ranking engine — dispatch Round 1 models A/B/C + controls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.models.controls import (
    rank_shuffled_history,
    reverse_peek,
)
from vietlott_quant_lab.ranking.models.hot import DEFAULT_LOOKBACK, rank_hot
from vietlott_quant_lab.ranking.models.multi_scale_shrinkage import rank_multi_scale_shrinkage
from vietlott_quant_lab.ranking.models.random_rank import rank_random
from vietlott_quant_lab.ranking.types import RankingResult

MODEL_HOT = "hot"
MODEL_MULTI_SCALE_SHRINKAGE = "multi_scale_shrinkage"
MODEL_RANDOM = "random"
MODEL_REVERSE_PEEK = "reverse_peek"
MODEL_SHUFFLED_HISTORY = "shuffled_history"

ROUND1_MODELS = (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
)


def rank_all(
    history: Sequence[DrawRecord],
    model_id: str,
    *,
    seed: int = 0,
    lookback: int = DEFAULT_LOOKBACK,
    winners: Sequence[int] | None = None,
    **_: Any,
) -> RankingResult:
    """Rank all numbers 01–45 with the selected model.

    Scores are ranking signals only — never labeled as probabilities.
    """
    if model_id == MODEL_HOT:
        return rank_hot(history, lookback=lookback, seed=seed)
    if model_id == MODEL_MULTI_SCALE_SHRINKAGE:
        return rank_multi_scale_shrinkage(history, seed=seed)
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
