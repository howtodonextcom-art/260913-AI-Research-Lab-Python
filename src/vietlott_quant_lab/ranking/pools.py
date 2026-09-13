"""Nested top-m candidate pools from a frozen ranking."""

from __future__ import annotations

from vietlott_quant_lab.config.constants import POOL_SIZES
from vietlott_quant_lab.ranking.types import RankingResult


def nested_pools(
    ranking: RankingResult,
    sizes: tuple[int, ...] = POOL_SIZES,
) -> dict[int, frozenset[int]]:
    """Build S7 ⊂ S8 ⊂ … ⊂ S18 from the same ranking.

    Returns mapping pool_size → frozenset of numbers.
    """
    by_rank = ranking.by_rank()
    pools: dict[int, frozenset[int]] = {}
    prev: frozenset[int] | None = None
    for m in sorted(sizes):
        pool = frozenset(r.number for r in by_rank[:m])
        if prev is not None and not prev <= pool:
            msg = f"nested invariant broken at m={m}"
            raise AssertionError(msg)
        pools[m] = pool
        prev = pool
    return pools


def assert_nested(pools: dict[int, frozenset[int]]) -> None:
    ordered = sorted(pools)
    for i in range(1, len(ordered)):
        smaller = pools[ordered[i - 1]]
        larger = pools[ordered[i]]
        if not smaller <= larger:
            msg = f"S{ordered[i - 1]} not subset of S{ordered[i]}"
            raise AssertionError(msg)
