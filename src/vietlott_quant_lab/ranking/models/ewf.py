"""Model D — Exponentially Weighted Frequency (EWF).

Score for number n is sum over past draws of w(age) * 1{n in draw},
where w(age) = exp(-lambda * age) and age is draws since the event (0 = most recent).

Half-life h (in draws) maps to lambda = ln(2) / h.
Scores are ranking signals only — never probabilities.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

MODEL_ID = "ewf"

# Pre-registered half-lives (draws). Selection must use Development only.
EWF_HALF_LIVES: tuple[int, ...] = (30, 60, 90, 180)
DEFAULT_HALF_LIFE = 90


def _lambda_from_half_life(half_life: int) -> float:
    if half_life <= 0:
        msg = f"half_life must be positive, got {half_life}"
        raise ValueError(msg)
    return math.log(2.0) / float(half_life)


def rank_ewf(
    history: Sequence[DrawRecord],
    *,
    half_life: int = DEFAULT_HALF_LIFE,
    seed: int | None = None,
) -> RankingResult:
    """Higher exponentially-weighted frequency → better (lower) rank."""
    lam = _lambda_from_half_life(half_life)
    scores = {n: 0.0 for n in range(NUMBER_MIN, NUMBER_MAX + 1)}
    n = len(history)
    for age, draw in enumerate(reversed(history)):
        weight = math.exp(-lam * age)
        for num in draw.numbers:
            scores[int(num)] += weight
    # Tiny deterministic tie-break by number id.
    for num in scores:
        scores[num] += (NUMBER_MAX - num) * 1e-12
    # Encode half_life in unused seed channel via model_id suffix? Keep model_id fixed;
    # half_life is passed via engine kwargs and recorded in config hash.
    _ = n
    return ranking_from_scores(scores, model_id=MODEL_ID, seed=seed, higher_is_better=True)
