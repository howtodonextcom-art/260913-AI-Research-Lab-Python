"""Model F — Pure momentum ranking (continuation hypothesis).

Competes against mean-reversion; must not be blended before separate measurement.
"""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.momentum import momentum_table
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "momentum"


def rank_momentum(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
) -> RankingResult:
    """Higher short/medium momentum → better rank."""
    mom = momentum_table(history)
    scores: dict[int, float] = {}
    for n in range(NUMBER_MIN, NUMBER_MAX + 1):
        scores[n] = (
            1.0 * mom[n].momentum_short
            + 0.5 * mom[n].momentum_medium
            + 0.25 * mom[n].momentum_long
        )
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
