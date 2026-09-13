"""Ranking result types. Score is never a probability."""

from __future__ import annotations

from dataclasses import dataclass

from vietlott_quant_lab.config.constants import NUMBER_MAX, NUMBER_MIN


@dataclass(frozen=True)
class RankedNumber:
    number: int
    score: float
    rank: int  # 1 = best


@dataclass(frozen=True)
class RankingResult:
    """Full permutation of numbers 01–45 by rank."""

    model_id: str
    ranked: tuple[RankedNumber, ...]
    seed: int | None = None
    label: str | None = None  # e.g. INVALID_AS_PREDICTIVE_EVIDENCE

    def __post_init__(self) -> None:
        numbers = [r.number for r in self.ranked]
        ranks = [r.rank for r in self.ranked]
        if len(self.ranked) != NUMBER_MAX:
            msg = f"ranking must have {NUMBER_MAX} entries, got {len(self.ranked)}"
            raise ValueError(msg)
        if sorted(numbers) != list(range(NUMBER_MIN, NUMBER_MAX + 1)):
            msg = "ranking must be a permutation of 1..45"
            raise ValueError(msg)
        if sorted(ranks) != list(range(1, NUMBER_MAX + 1)):
            msg = "ranks must be a permutation of 1..45"
            raise ValueError(msg)

    def by_rank(self) -> tuple[RankedNumber, ...]:
        return tuple(sorted(self.ranked, key=lambda r: r.rank))

    def number_to_rank(self) -> dict[int, int]:
        return {r.number: r.rank for r in self.ranked}

    def number_to_score(self) -> dict[int, float]:
        return {r.number: r.score for r in self.ranked}

    def top_m(self, m: int) -> tuple[int, ...]:
        if m < 1 or m > NUMBER_MAX:
            msg = f"m out of range: {m}"
            raise ValueError(msg)
        return tuple(r.number for r in self.by_rank()[:m])


def ranking_from_scores(
    scores: dict[int, float],
    *,
    model_id: str,
    seed: int | None = None,
    label: str | None = None,
    higher_is_better: bool = True,
) -> RankingResult:
    """Build a full RankingResult from per-number scores (deterministic ties by number)."""
    if set(scores) != set(range(NUMBER_MIN, NUMBER_MAX + 1)):
        msg = "scores must cover every number 1..45"
        raise ValueError(msg)

    def sort_key(n: int) -> tuple[float, int]:
        s = scores[n]
        # Ascending number breaks ties for determinism.
        return (-s if higher_is_better else s, n)

    ordered = sorted(scores.keys(), key=sort_key)
    ranked = tuple(
        RankedNumber(number=n, score=float(scores[n]), rank=i + 1) for i, n in enumerate(ordered)
    )
    return RankingResult(model_id=model_id, ranked=ranked, seed=seed, label=label)
