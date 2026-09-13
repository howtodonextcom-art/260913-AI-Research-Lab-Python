"""Ranking models package — Round 1 + Algorithm V2 classical challengers."""

from vietlott_quant_lab.ranking.models.all_history import rank_all_history
from vietlott_quant_lab.ranking.models.controls import (
    INVALID_AS_PREDICTIVE_EVIDENCE,
    rank_shuffled_history,
    reverse_peek,
)
from vietlott_quant_lab.ranking.models.ewf import rank_ewf
from vietlott_quant_lab.ranking.models.hazard import rank_hazard
from vietlott_quant_lab.ranking.models.hot import rank_hot
from vietlott_quant_lab.ranking.models.mean_reversion_rank import rank_mean_reversion
from vietlott_quant_lab.ranking.models.momentum_rank import rank_momentum
from vietlott_quant_lab.ranking.models.multi_scale_shrinkage import rank_multi_scale_shrinkage
from vietlott_quant_lab.ranking.models.multi_scale_v2 import rank_multi_scale_v2
from vietlott_quant_lab.ranking.models.random_rank import rank_random

__all__ = [
    "INVALID_AS_PREDICTIVE_EVIDENCE",
    "rank_all_history",
    "rank_ewf",
    "rank_hazard",
    "rank_hot",
    "rank_mean_reversion",
    "rank_momentum",
    "rank_multi_scale_shrinkage",
    "rank_multi_scale_v2",
    "rank_random",
    "rank_shuffled_history",
    "reverse_peek",
]
