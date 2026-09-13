"""Model H — Recency / empirical waiting-time (hazard-style) ranking.

Uses empirical gap features. Does NOT call overdue numbers "due".
Hypothesis under test: larger empirical gap predicts higher next-draw chance
(or the opposite — either direction is falsifiable via tournament).

Default direction: larger gap → higher score (classic "overdue" hypothesis).
"""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.recency import recency_table
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "hazard"


def rank_hazard(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
    favor_long_gap: bool = True,
) -> RankingResult:
    """Rank by empirical gap / gap_z. Ranking signal only — not a probability."""
    rec = recency_table(history)
    scores: dict[int, float] = {}
    for n in range(NUMBER_MIN, NUMBER_MAX + 1):
        # Mix raw gap and standardized gap for scale stability.
        raw = float(rec[n].gap) + 0.5 * float(rec[n].gap_z)
        scores[n] = raw if favor_long_gap else -raw
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
