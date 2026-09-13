"""Negative controls — not valid predictive evidence."""

from __future__ import annotations

import random
from collections.abc import Sequence
from datetime import UTC, date, datetime

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX, NUMBER_MIN
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.types import RankingResult, ranking_from_scores

INVALID_AS_PREDICTIVE_EVIDENCE = "INVALID_AS_PREDICTIVE_EVIDENCE"

MODEL_ID_REVERSE_PEEK = "reverse_peek"
MODEL_ID_SHUFFLED_HISTORY = "shuffled_history"


def reverse_peek(
    winners: Sequence[int],
    *,
    seed: int = 0,
) -> RankingResult:
    """Force the six winners into ranks 1–6 (tautology / leak oracle).

    Labeled ``INVALID_AS_PREDICTIVE_EVIDENCE`` — proves harness containment only.
    """
    win = sorted({int(w) for w in winners})
    if len(win) != DRAW_SIZE:
        msg = f"winners must be {DRAW_SIZE} unique numbers, got {win}"
        raise ValueError(msg)
    for w in win:
        if not (NUMBER_MIN <= w <= NUMBER_MAX):
            msg = f"winner out of range: {w}"
            raise ValueError(msg)

    rng = random.Random(seed)
    complement = [n for n in range(NUMBER_MIN, NUMBER_MAX + 1) if n not in set(win)]
    rng.shuffle(complement)

    order = list(win) + complement
    scores = {n: float(NUMBER_MAX - i) for i, n in enumerate(order)}
    return ranking_from_scores(
        scores,
        model_id=MODEL_ID_REVERSE_PEEK,
        seed=seed,
        label=INVALID_AS_PREDICTIVE_EVIDENCE,
        higher_is_better=True,
    )


def shuffle_history_draws(
    history: Sequence[DrawRecord],
    *,
    seed: int = 0,
) -> list[DrawRecord]:
    """Destroy temporal structure by reshuffling draw results across dates."""
    rng = random.Random(seed)
    results = [tuple(d.numbers) for d in history]
    rng.shuffle(results)
    out: list[DrawRecord] = []
    for draw, nums in zip(history, results, strict=True):
        out.append(
            DrawRecord(
                product=draw.product,
                draw_id=draw.draw_id,
                draw_date=draw.draw_date,
                numbers=nums,
                source_url=draw.source_url,
                fetched_at=draw.fetched_at,
            )
        )
    return out


def rank_shuffled_history(
    history: Sequence[DrawRecord],
    *,
    seed: int = 0,
    lookback: int = 90,
) -> RankingResult:
    """HOT ranking on shuffled history — control labeled invalid as evidence."""
    from vietlott_quant_lab.ranking.models.hot import rank_hot

    shuffled = shuffle_history_draws(list(history), seed=seed)
    result = rank_hot(shuffled, lookback=lookback, seed=seed)
    return RankingResult(
        model_id=MODEL_ID_SHUFFLED_HISTORY,
        ranked=result.ranked,
        seed=seed,
        label=INVALID_AS_PREDICTIVE_EVIDENCE,
    )


def make_synthetic_draw(
    *,
    draw_id: str = "99999",
    draw_date: date | None = None,
    numbers: tuple[int, int, int, int, int, int] = (1, 2, 3, 4, 5, 6),
) -> DrawRecord:
    return DrawRecord(
        product="mega645",
        draw_id=draw_id,
        draw_date=draw_date or date(2099, 1, 1),
        numbers=numbers,
        source_url="https://vietlott.vn/synthetic",
        fetched_at=datetime(2099, 1, 1, tzinfo=UTC),
    )
