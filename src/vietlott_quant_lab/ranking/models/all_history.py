"""Model A — All-history long-run frequency baseline."""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "all_history"


def rank_all_history(
    history: Sequence[DrawRecord],
    *,
    seed: int | None = None,
) -> RankingResult:
    """Higher full-history frequency → better rank. Descriptive baseline only."""
    freq = frequency_table(history)
    scores = {
        n: float(freq[n].count) + (NUMBER_MAX - n) * 1e-9
        for n in range(NUMBER_MIN, NUMBER_MAX + 1)
    }
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
