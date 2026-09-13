"""Model G — Pure mean-reversion ranking (opposite of momentum)."""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.mean_reversion import mean_reversion_table
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "mean_reversion"


def rank_mean_reversion(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
) -> RankingResult:
    """Higher mean-reversion score (short below long-run) → better rank."""
    mr = mean_reversion_table(history)
    scores = {
        n: float(mr[n].mean_reversion_score) for n in range(NUMBER_MIN, NUMBER_MAX + 1)
    }
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
