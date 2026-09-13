"""Model A — HOT frequency ranking on a registered lookback."""

from __future__ import annotations

from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.frequency import frequency_table
from vietlott_quant_lab.features.windows import slice_window
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "hot"
DEFAULT_LOOKBACK = 90


def rank_hot(
    history: Sequence[DrawRecord],
    *,
    lookback: int = DEFAULT_LOOKBACK,
    seed: int | None = None,
) -> RankingResult:
    """Higher frequency in the lookback window → better (lower) rank."""
    window = slice_window(history, lookback)
    freq = frequency_table(window)
    scores = {
        n: float(freq[n].count) + (NUMBER_MAX - n) * 1e-9
        for n in range(NUMBER_MIN, NUMBER_MAX + 1)
    }
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
