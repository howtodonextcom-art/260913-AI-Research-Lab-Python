"""Research metrics: Mean K, tails, winner ranks, MCP."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX
from vietlott_quant_lab.statistics.hypergeometric import (
    expected_k,
    hypergeometric_pmf,
    hypergeometric_tail_ge,
)


@dataclass(frozen=True)
class NullTailProbabilities:
    """Exact null probabilities for a fixed pool size. Not model scores."""

    mean_k: float
    p_ge_3: float
    p_ge_4: float
    p_ge_5: float
    p_eq_6: float


def null_tail_probabilities(m: int) -> NullTailProbabilities:
    return NullTailProbabilities(
        mean_k=expected_k(m),
        p_ge_3=hypergeometric_tail_ge(m, 3),
        p_ge_4=hypergeometric_tail_ge(m, 4),
        p_ge_5=hypergeometric_tail_ge(m, 5),
        p_eq_6=hypergeometric_pmf(m, 6),
    )


def intersection_k(pool: Sequence[int], winners: Sequence[int]) -> int:
    return len(set(pool) & set(winners))


def mean_k(ks: Sequence[int]) -> float:
    if not ks:
        return 0.0
    return sum(ks) / len(ks)


def winner_ranks(
    ranking: Mapping[int, int],
    winners: Sequence[int],
) -> tuple[int, ...]:
    """Return ranks of the six winners (rank 1 = best).

    ``ranking`` maps number → rank.
    """
    ranks: list[int] = []
    for w in winners:
        if w not in ranking:
            msg = f"winner {w} missing from ranking"
            raise KeyError(msg)
        ranks.append(ranking[w])
    return tuple(ranks)


def max_winner_rank(ranks: Sequence[int]) -> int:
    """MCP = max winner rank (minimum pool that contains all winners)."""
    if len(ranks) != DRAW_SIZE:
        msg = f"expected {DRAW_SIZE} winner ranks, got {len(ranks)}"
        raise ValueError(msg)
    mcp = max(ranks)
    if not (1 <= mcp <= NUMBER_MAX):
        msg = f"MCP out of range: {mcp}"
        raise ValueError(msg)
    return mcp


def mcp_from_ranking(ranking: Mapping[int, int], winners: Sequence[int]) -> int:
    return max_winner_rank(winner_ranks(ranking, winners))


def empirical_tail_rate(ks: Sequence[int], threshold: int) -> float:
    if not ks:
        return 0.0
    return sum(1 for k in ks if k >= threshold) / len(ks)
