"""Model C — seeded random permutation of 01–45."""

from __future__ import annotations

import random
from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "random"


def rank_random(
    history: Sequence[DrawRecord],
    *,
    seed: int = 0,
) -> RankingResult:
    """Uniform seeded permutation. ``history`` is unused (signature symmetry)."""
    _ = history
    rng = random.Random(seed)
    order = list(range(NUMBER_MIN, NUMBER_MAX + 1))
    rng.shuffle(order)
    scores = {n: float(NUMBER_MAX - i) for i, n in enumerate(order)}
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
